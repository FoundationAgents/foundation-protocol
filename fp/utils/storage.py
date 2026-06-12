"""FP存储管理器 - 负责所有文件的读写操作"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

if os.name == "nt":
    import msvcrt
else:
    import fcntl

from loguru import logger
from pydantic import BaseModel, Field


@contextmanager
def _config_file_lock(lock_path: Path, *, exclusive: bool):
    """Lock the config lock file on Windows and POSIX systems."""
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            lock_file.seek(0, os.SEEK_END)
            if lock_file.tell() == 0:
                lock_file.write(b"\0")
                lock_file.flush()
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            operation = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(lock_file.fileno(), operation)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


# ============================================================================
# 存储数据模型
# ============================================================================

class GlobalSettings(BaseModel):
    """全局设置"""
    auto_backup: bool = False
    log_level: str = "INFO"
    encrypt_keys: bool = False


class HostConfigEntry(BaseModel):
    """config.json中的host条目"""
    name: str
    bind_host: str
    advertise_host: str | None = None
    port: int
    address: str | None = None
    url: str | None = None
    parent_uid: str | None = None
    parent_url: str | None = None
    enabled: bool = True

    def get_url(self) -> str:
        """获取 URL，优先使用保存的 url，否则动态生成"""
        return self.url or f"http://{self.bind_host}:{self.port}"


class EntityConfigEntry(BaseModel):
    """config.json中的entity条目"""
    name: str
    kind: str
    host_uid: str
    is_public: bool
    enabled: bool
    metadata: dict[str, Any] = Field(default_factory=dict)


class GlobalConfig(BaseModel):
    """全局配置文件 (config.json)"""
    version: str = "1.0"
    default_host: str | None = None
    hosts: dict[str, HostConfigEntry] = Field(default_factory=dict)
    entities: dict[str, EntityConfigEntry] = Field(default_factory=dict)
    settings: GlobalSettings = Field(default_factory=GlobalSettings)


class RuntimeState(BaseModel):
    """运行时状态 (runtime.json)"""
    pids: dict[str, int] = Field(default_factory=dict)
    ui_pid: int | None = None
    last_sync: dict[str, str] = Field(default_factory=dict)
    updated_at: str | None = None


class HostMeta(BaseModel):
    """Host元数据 (hosts/{uid}/meta.json)"""
    uid: str
    name: str
    address: str
    bind_host: str
    port: int
    url: str
    parent_uid: str | None = None
    parent_url: str | None = None
    default_owner: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ChildHostEntry(BaseModel):
    """Child host条目"""
    uid: str
    name: str
    url: str
    last_seen: str | None = None
    public_entities: list[dict] = Field(default_factory=list)


class HostChildren(BaseModel):
    """Host children列表 (hosts/{uid}/children.json)"""
    children: list[ChildHostEntry] = Field(default_factory=list)


class OfflineMailQueueEntry(BaseModel):
    """One entity offline mail queue entry."""

    entity_uid: str
    mails: list[dict[str, Any]] = Field(default_factory=list)


class HostOfflineMailQueues(BaseModel):
    """Host offline mail queues (hosts/{uid}/offline_mail_queues.json)."""

    queues: list[OfflineMailQueueEntry] = Field(default_factory=list)


class EntityKeyInfo(BaseModel):
    """Entity密钥信息（公钥）"""
    sign_public_key: str
    encrypt_public_key: str
    key_file: str


class EntityMeta(BaseModel):
    """Entity元数据 (entities/{uid}/meta.json)"""
    uid: str
    name: str
    kind: str
    host_uid: str
    address: str
    keys: EntityKeyInfo
    mailbox_path: str
    description: str = ""
    is_public: bool = False
    visible: bool = True
    enabled: bool = True
    owner: str | None = None  # Owner entity address for carbon copy
    arbiter: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class EntityKeys(BaseModel):
    """Entity私钥 (keys/entities/{uid}.key)"""
    uid: str
    sign_private_key: str
    decrypt_private_key: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class FriendEntry(BaseModel):
    """好友条目"""
    entity_uid: str
    name: str
    address: str
    kind: str
    host_uid: str
    sign_public_key: str
    encrypt_public_key: str
    description: str = ""
    is_public: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    added_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class EntityFriends(BaseModel):
    """Entity好友列表 (entities/{uid}/friends.json)"""
    friends: list[FriendEntry] = Field(default_factory=list)


class EntitySessions(BaseModel):
    """Entity sessions (entities/{uid}/sessions.json)"""
    sessions: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 存储管理器
# ============================================================================

class StorageManager:
    """FP存储管理器 - 统一管理所有文件的读写操作

    职责：
    1. 初始化目录结构
    2. 读写配置文件（使用BaseModel）
    3. 读写entity和host数据（使用BaseModel）
    4. 管理密钥文件
    5. 权限设置
    """

    def __init__(self, fp_home: Path | None = None):
        """初始化存储管理器"""
        self.fp_home = fp_home or self._get_fp_home()
        self._ensure_directory_structure()

    @staticmethod
    def _get_fp_home() -> Path:
        """获取FP根目录"""
        value = os.getenv("FP_HOME", "~/.fp")
        return Path(value).expanduser().resolve()

    # ========================================================================
    # 路径方法（实例方法，不依赖path.py）
    # ========================================================================

    def _config_path(self) -> Path:
        """config.json路径"""
        return self.fp_home / "config.json"

    def _runtime_path(self) -> Path:
        """runtime.json路径"""
        return self.fp_home / "runtime.json"

    def _host_dir(self, host_uid: str) -> Path:
        """host目录"""
        return self.fp_home / "hosts" / host_uid

    def _host_meta_path(self, host_uid: str) -> Path:
        """host meta.json路径"""
        return self._host_dir(host_uid) / "meta.json"

    def _host_children_path(self, host_uid: str) -> Path:
        """host children.json路径"""
        return self._host_dir(host_uid) / "children.json"

    def _host_offline_mail_queues_path(self, host_uid: str) -> Path:
        """host offline_mail_queues.json路径"""
        return self._host_dir(host_uid) / "offline_mail_queues.json"

    def _arbiter_state_path(self, host_uid: str) -> Path:
        """host arbiter_state.json路径"""
        return self._host_dir(host_uid) / "arbiter_state.json"

    def _market_state_path(self, host_uid: str) -> Path:
        """host market_state.json路径"""
        return self._host_dir(host_uid) / "market_state.json"

    def _entity_dir(self, entity_uid: str) -> Path:
        """entity目录"""
        return self.fp_home / "entities" / entity_uid

    def _entity_meta_path(self, entity_uid: str) -> Path:
        """entity meta.json路径"""
        return self._entity_dir(entity_uid) / "meta.json"

    def _entity_friends_path(self, entity_uid: str) -> Path:
        """entity friends.json路径"""
        return self._entity_dir(entity_uid) / "friends.json"

    def _entity_sessions_path(self, entity_uid: str) -> Path:
        """entity sessions.json路径"""
        return self._entity_dir(entity_uid) / "sessions.json"

    def _entity_pending_approvals_path(self, entity_uid: str) -> Path:
        return self._entity_dir(entity_uid) / "pending_approvals.json"

    def _entity_key_path(self, entity_uid: str) -> Path:
        """entity密钥文件路径"""
        return self.fp_home / "keys" / "entities" / f"{entity_uid}.key"

    def _entity_avatar_path(self, entity_uid: str) -> Path:
        """entity头像文件路径（不含扩展名）"""
        return self._entity_dir(entity_uid) / "avatar"

    def _entity_mailbox_path(self, entity_uid: str) -> Path:
        """entity邮箱文件路径"""
        # Get entity's host_uid
        config = self.load_config()
        entity_entry = config.entities.get(entity_uid)
        if not entity_entry:
            raise ValueError(f"Entity not found: {entity_uid}")
        host_uid = entity_entry.host_uid
        return self.fp_home / "hosts" / host_uid / "mailboxes" / f"{entity_uid}.jsonl"

    def _host_log_path(self, host_uid: str) -> Path:
        """host日志文件路径"""
        return self.fp_home / "logs" / "hosts" / f"{host_uid}.log"

    # ========================================================================
    # 辅助方法
    # ========================================================================

    @staticmethod
    def _ensure_parent_dir(file_path: Path) -> Path:
        """确保文件的父目录存在"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        return file_path

    @staticmethod
    def _ensure_dir(dir_path: Path) -> Path:
        """确保目录存在"""
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    def _ensure_directory_structure(self) -> None:
        """确保所有必要的目录存在"""
        self._ensure_dir(self.fp_home / "hosts")
        self._ensure_dir(self.fp_home / "entities")
        self._ensure_dir(self.fp_home / "mailboxes")
        self._ensure_dir(self.fp_home / "logs")
        self._ensure_dir(self.fp_home / "logs" / "hosts")
        self._ensure_dir(self.fp_home / "cache")

        # keys目录需要特殊权限
        keys_dir = self._ensure_dir(self.fp_home / "keys")
        self._set_secure_permissions(keys_dir)
        self._ensure_dir(keys_dir / "hosts")
        self._ensure_dir(keys_dir / "entities")

    @staticmethod
    def _set_secure_permissions(path: Path) -> None:
        """设置安全权限（仅owner可访问）"""
        try:
            path.chmod(0o700)
        except Exception as e:
            logger.warning(f"Failed to set secure permissions on {path}: {e}")

    @staticmethod
    def _read_json_model[T](path: Path, model_class: type[T]) -> T:
        """读取JSON文件并转换为BaseModel"""
        with path.open("r", encoding="utf-8") as f:
            data = f.read()
            return model_class.model_validate_json(data)

    @staticmethod
    def _write_json_model(path: Path, model: BaseModel) -> None:
        """将BaseModel写入JSON文件"""
        with path.open("w", encoding="utf-8") as f:
            f.write(model.model_dump_json(indent=2, exclude_none=True))

    # ========================================================================
    # 全局配置文件操作
    # TODO: v0.2版本添加缓存机制，减少频繁读取config.json
    # ========================================================================

    def load_config(self) -> GlobalConfig:
        """加载全局配置文件（带文件锁保护）"""
        config_path = self._config_path()
        if not config_path.exists():
            return self._create_default_config()

        # 使用文件锁保护并发读取
        lock_path = config_path.parent / ".config.lock"
        try:
            with _config_file_lock(lock_path, exclusive=False):
                return self._read_json_model(config_path, GlobalConfig)
        except Exception as e:
            logger.error(f"Failed to parse config.json: {e}")
            raise

    def save_config(self, config: GlobalConfig) -> None:
        """保存全局配置文件（带文件锁保护）"""
        config_path = self._config_path()
        self._ensure_parent_dir(config_path)

        # 使用文件锁保护并发写入
        lock_path = config_path.parent / ".config.lock"
        with _config_file_lock(lock_path, exclusive=True):
            self._write_json_model(config_path, config)

    def _create_default_config(self) -> GlobalConfig:
        """创建默认配置文件"""
        default_config = GlobalConfig()
        self.save_config(default_config)
        return default_config

    # ========================================================================
    # Runtime状态文件操作
    # ========================================================================

    def load_runtime(self) -> RuntimeState:
        """加载运行时状态文件"""
        runtime_path = self._runtime_path()
        if not runtime_path.exists():
            return RuntimeState()

        return self._read_json_model(runtime_path, RuntimeState)

    def save_runtime(self, runtime: RuntimeState) -> None:
        """保存运行时状态文件"""
        runtime.updated_at = datetime.now().isoformat()
        self._write_json_model(self._runtime_path(), runtime)

    def update_host_pid(self, host_uid: str, pid: int | None) -> None:
        """更新host的PID"""
        runtime = self.load_runtime()
        if pid is None:
            runtime.pids.pop(host_uid, None)
        else:
            runtime.pids[host_uid] = pid
        self.save_runtime(runtime)

    # ========================================================================
    # Host数据操作
    # ========================================================================

    def save_host_meta(self, meta: HostMeta) -> None:
        """保存host元数据"""
        meta.updated_at = datetime.now().isoformat()
        self._ensure_parent_dir(self._host_meta_path(meta.uid))
        self._write_json_model(self._host_meta_path(meta.uid), meta)

    def load_host_meta(self, host_uid: str) -> HostMeta | None:
        """加载host元数据"""
        meta_path = self._host_meta_path(host_uid)
        if not meta_path.exists():
            return None

        return self._read_json_model(meta_path, HostMeta)

    def save_host_children(self, host_uid: str, children: list[ChildHostEntry]) -> None:
        """保存host的children列表"""
        self._ensure_parent_dir(self._host_children_path(host_uid))
        host_children = HostChildren(children=children)
        self._write_json_model(self._host_children_path(host_uid), host_children)

    def load_host_children(self, host_uid: str) -> list[ChildHostEntry]:
        """加载host的children列表"""
        children_path = self._host_children_path(host_uid)
        if not children_path.exists():
            return []

        host_children = self._read_json_model(children_path, HostChildren)
        return host_children.children

    def save_host_offline_mail_queues(
        self,
        host_uid: str,
        queues: list[OfflineMailQueueEntry],
    ) -> None:
        """保存host的离线邮件队列。"""
        self._ensure_parent_dir(self._host_offline_mail_queues_path(host_uid))
        queue_data = HostOfflineMailQueues(queues=queues)
        self._write_json_model(self._host_offline_mail_queues_path(host_uid), queue_data)

    def load_host_offline_mail_queues(self, host_uid: str) -> list[OfflineMailQueueEntry]:
        """加载host的离线邮件队列。"""
        queue_path = self._host_offline_mail_queues_path(host_uid)
        if not queue_path.exists():
            return []

        queue_data = self._read_json_model(queue_path, HostOfflineMailQueues)
        return queue_data.queues

    # ========================================================================
    # Arbiter State 持久化
    # ========================================================================

    def save_arbiter_state(self, host_uid: str, state: BaseModel) -> None:
        """保存 Arbiter 状态（contracts, payments, ledger）"""
        path = self._arbiter_state_path(host_uid)
        self._ensure_parent_dir(path)
        self._write_json_model(path, state)

    def load_arbiter_state_raw(self, host_uid: str) -> str | None:
        """加载 Arbiter 状态的原始 JSON 字符串"""
        path = self._arbiter_state_path(host_uid)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    # ========================================================================
    # Market State 持久化
    # ========================================================================

    def save_market_state(self, host_uid: str, state: BaseModel) -> None:
        """保存 MarketStore 状态"""
        path = self._market_state_path(host_uid)
        self._ensure_parent_dir(path)
        self._write_json_model(path, state)

    def load_market_state_raw(self, host_uid: str) -> str | None:
        """加载 MarketStore 状态的原始 JSON 字符串"""
        path = self._market_state_path(host_uid)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    # ========================================================================
    # Entity数据操作
    # ========================================================================

    def save_entity_meta(self, meta: EntityMeta) -> None:
        """保存entity元数据"""
        meta.updated_at = datetime.now().isoformat()
        self._ensure_parent_dir(self._entity_meta_path(meta.uid))
        self._write_json_model(self._entity_meta_path(meta.uid), meta)

    def load_entity_meta(self, entity_uid: str) -> EntityMeta | None:
        """加载entity元数据"""
        meta_path = self._entity_meta_path(entity_uid)
        if not meta_path.exists():
            return None

        return self._read_json_model(meta_path, EntityMeta)

    def save_entity_friends(self, entity_uid: str, friends: list[FriendEntry]) -> None:
        """保存entity的friends列表"""
        self._ensure_parent_dir(self._entity_friends_path(entity_uid))
        entity_friends = EntityFriends(friends=friends)
        self._write_json_model(self._entity_friends_path(entity_uid), entity_friends)

    def load_entity_friends(self, entity_uid: str) -> list[FriendEntry]:
        """加载entity的friends列表"""
        friends_path = self._entity_friends_path(entity_uid)
        if not friends_path.exists():
            return []

        entity_friends = self._read_json_model(friends_path, EntityFriends)
        return entity_friends.friends

    def save_entity_sessions(self, entity_uid: str, sessions: dict[str, Any]) -> None:
        """保存entity的sessions"""
        if not sessions:
            sessions_path = self._entity_sessions_path(entity_uid)
            if sessions_path.exists():
                sessions_path.unlink()
            return

        self._ensure_parent_dir(self._entity_sessions_path(entity_uid))
        entity_sessions = EntitySessions(sessions=sessions)
        self._write_json_model(self._entity_sessions_path(entity_uid), entity_sessions)

    def load_entity_sessions(self, entity_uid: str) -> dict[str, Any]:
        """加载entity的sessions"""
        sessions_path = self._entity_sessions_path(entity_uid)
        if not sessions_path.exists():
            return {}

        entity_sessions = self._read_json_model(sessions_path, EntitySessions)
        return entity_sessions.sessions

    def save_entity_pending_approvals(self, entity_uid: str, data: dict[str, Any]) -> None:
        """Save pending_approvals for an entity."""
        if not data:
            path = self._entity_pending_approvals_path(entity_uid)
            if path.exists():
                path.unlink()
            return
        path = self._entity_pending_approvals_path(entity_uid)
        self._ensure_parent_dir(path)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_entity_pending_approvals(self, entity_uid: str) -> dict[str, Any]:
        """Load pending_approvals for an entity."""
        path = self._entity_pending_approvals_path(entity_uid)
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    # ========================================================================
    # 密钥操作
    # ========================================================================

    def save_entity_keys(self, keys: EntityKeys) -> None:
        """保存entity密钥（私钥）"""
        key_path = self._entity_key_path(keys.uid)
        self._ensure_parent_dir(key_path)
        self._write_json_model(key_path, keys)

        # 设置密钥文件权限为600（仅owner可读写）
        self._set_secure_permissions(key_path)

    def load_entity_keys(self, entity_uid: str) -> EntityKeys | None:
        """加载entity密钥（私钥）"""
        key_path = self._entity_key_path(entity_uid)
        if not key_path.exists():
            return None

        return self._read_json_model(key_path, EntityKeys)

    def delete_entity_keys(self, entity_uid: str) -> None:
        """删除entity密钥"""
        key_path = self._entity_key_path(entity_uid)
        if key_path.exists():
            key_path.unlink()

    # ========================================================================
    # 头像操作
    # ========================================================================

    def save_entity_avatar(self, entity_uid: str, data: bytes, ext: str = "png") -> Path:
        """保存entity头像"""
        avatar_path = self._entity_avatar_path(entity_uid).with_suffix(f".{ext}")
        self._ensure_parent_dir(avatar_path)
        avatar_path.write_bytes(data)
        logger.info(f"Saved avatar for entity {entity_uid}: {avatar_path}")
        return avatar_path

    def load_entity_avatar(self, entity_uid: str) -> tuple[bytes, str] | None:
        """加载entity头像（自动检测扩展名）

        Returns:
            tuple[bytes, str] | None: (头像数据, 扩展名) 或 None
        """
        avatar_base = self._entity_avatar_path(entity_uid)
        for ext in ["png", "jpg", "jpeg", "gif", "webp"]:
            avatar_path = avatar_base.with_suffix(f".{ext}")
            if avatar_path.exists():
                return (avatar_path.read_bytes(), ext)
        return None

    def delete_entity_avatar(self, entity_uid: str) -> bool:
        """删除entity头像

        Returns:
            bool: 是否成功删除（找到并删除了文件）
        """
        avatar_base = self._entity_avatar_path(entity_uid)
        deleted = False
        for ext in ["png", "jpg", "jpeg", "gif", "webp"]:
            avatar_path = avatar_base.with_suffix(f".{ext}")
            if avatar_path.exists():
                avatar_path.unlink()
                logger.info(f"Deleted avatar for entity {entity_uid}: {avatar_path}")
                deleted = True
        return deleted

    def get_entity_avatar_url(self, entity_uid: str) -> str | None:
        """获取entity头像URL（如果存在）"""
        avatar_base = self._entity_avatar_path(entity_uid)
        for ext in ["png", "jpg", "jpeg", "gif", "webp"]:
            if avatar_base.with_suffix(f".{ext}").exists():
                return f"/api/v1/entities/{entity_uid}/avatar"
        return None

    # ========================================================================
    # 批量操作
    # ========================================================================

    def delete_entity_all_data(self, entity_uid: str) -> None:
        """删除entity的所有数据（meta、friends、sessions、keys、avatar）"""
        import shutil

        # 删除entity目录（包含头像）
        entity_dir = self._entity_dir(entity_uid)
        if entity_dir.exists():
            shutil.rmtree(entity_dir)

        # 删除密钥
        self.delete_entity_keys(entity_uid)

        logger.info(f"Deleted all data for entity {entity_uid}")

    def delete_host_all_data(self, host_uid: str) -> None:
        """删除host的所有数据"""
        import shutil

        host_dir = self._host_dir(host_uid)
        if host_dir.exists():
            shutil.rmtree(host_dir)

        logger.info(f"Deleted all data for host {host_uid}")

    def get_entities_for_host(self, host_uid: str) -> list[str]:
        """获取某个host下的所有entity uid"""
        config = self.load_config()
        return [
            entity_uid
            for entity_uid, entity_config in config.entities.items()
            if entity_config.host_uid == host_uid
        ]

    def delete_host_from_config(self, host_uid: str) -> None:
        """从config中删除host及其所有entities配置"""
        config = self.load_config()

        # 删除该host下的所有entities
        entities_to_delete = self.get_entities_for_host(host_uid)
        for entity_uid in entities_to_delete:
            config.entities.pop(entity_uid, None)
            self.delete_entity_all_data(entity_uid)

        # 删除host配置
        config.hosts.pop(host_uid, None)

        # 如果删除的是default host，清空default
        if config.default_host == host_uid:
            remaining_hosts = list(config.hosts.keys())
            config.default_host = remaining_hosts[0] if remaining_hosts else None

        # 删除runtime中的PID
        runtime = self.load_runtime()
        runtime.pids.pop(host_uid, None)
        self.save_runtime(runtime)

        self.save_config(config)

        # 删除host文件数据
        self.delete_host_all_data(host_uid)
        logger.info(f"Deleted host {host_uid} from config")

    # ========================================================================
    # CLI便捷方法
    # ========================================================================

    def get_host_by_name(self, host_name: str) -> tuple[str, HostConfigEntry] | None:
        """通过name获取host配置，返回(host_uid, host_entry)"""
        config = self.load_config()
        for host_uid, host_entry in config.hosts.items():
            if host_entry.name == host_name:
                return (host_uid, host_entry)
        return None

    def resolve_host_name(self, host_name: str) -> str:
        """解析host_name为host_uid，如果是uid直接返回，如果是name则查找"""
        config = self.load_config()

        # 处理特殊值 "default"
        if host_name == "default":
            if config.default_host:
                return config.default_host
            raise ValueError("No default host configured")

        # 先检查是否是uid
        if host_name in config.hosts:
            return host_name

        # 再查找name
        result = self.get_host_by_name(host_name)
        if result:
            return result[0]

        raise ValueError(f"Host not found: {host_name}")

    def get_host_url(self, host_name: str) -> str:
        """获取host URL（通过name或uid）"""
        host_uid = self.resolve_host_name(host_name)
        config = self.load_config()
        host_entry = config.hosts.get(host_uid)
        if not host_entry:
            raise ValueError(f"Host not found: {host_name}")
        # 将 0.0.0.0 转换为 127.0.0.1 以便浏览器访问
        bind_host = host_entry.bind_host
        if bind_host == "0.0.0.0":
            bind_host = "127.0.0.1"
        return f"http://{bind_host}:{host_entry.port}"

    def get_all_hosts(self) -> dict[str, HostConfigEntry]:
        """获取所有hosts"""
        config = self.load_config()
        return config.hosts

    def get_default_host(self) -> str | None:
        """获取默认host uid"""
        config = self.load_config()
        return config.default_host

    def set_default_host(self, host_name_or_uid: str) -> None:
        """设置默认host"""
        host_uid = self.resolve_host_name(host_name_or_uid)
        config = self.load_config()
        config.default_host = host_uid
        self.save_config(config)

    def create_or_update_host(
        self,
        host_name: str,
        host_uid: str | None = None,
        bind_host: str | None = None,
        advertise_host: str | None = None,
        port: int | None = None,
        address: str | None = None,
        url: str | None = None,
        parent_uid: str | None = None,
        parent_url: str | None = None,
    ) -> None:
        """创建或更新host配置"""
        config = self.load_config()

        # 如果没有提供host_uid，尝试通过name查找
        if host_uid is None:
            result = self.get_host_by_name(host_name)
            if result:
                host_uid = result[0]
            else:
                # 从address中提取uid
                if address:
                    host_uid = address.split(":")[0]
                else:
                    raise ValueError("Must provide host_uid or address")

        # 获取现有配置或创建新配置
        existing = config.hosts.get(host_uid)

        config.hosts[host_uid] = HostConfigEntry(
            name=host_name,
            bind_host=bind_host if bind_host is not None else (existing.bind_host if existing else "0.0.0.0"),
            advertise_host=advertise_host if advertise_host is not None else (existing.advertise_host if existing else None),
            port=port if port is not None else (existing.port if existing else 7001),
            address=address if address is not None else (existing.address if existing else None),
            url=url if url is not None else (existing.url if existing else None),
            parent_uid=parent_uid if parent_uid is not None else (existing.parent_uid if existing else None),
            parent_url=parent_url if parent_url is not None else (existing.parent_url if existing else None),
            enabled=True,
        )

        # 如果是第一个host，设为默认
        if config.default_host is None:
            config.default_host = host_uid

        self.save_config(config)

    def get_host(self, host_name: str) -> HostConfigEntry:
        """获取host配置（通过name或uid）"""
        host_uid = self.resolve_host_name(host_name)
        config = self.load_config()
        host_entry = config.hosts.get(host_uid)
        if not host_entry:
            raise ValueError(f"Host not found: {host_name}")
        return host_entry

    def get_host_state_path(self, host_name_or_uid: str) -> Path:
        """获取host state路径（旧接口兼容）"""
        host_uid = self.resolve_host_name(host_name_or_uid)
        return self._host_meta_path(host_uid)

    def get_host_log_path(self, host_name_or_uid: str) -> Path:
        """获取host日志路径"""
        host_uid = self.resolve_host_name(host_name_or_uid)
        return self._host_log_path(host_uid)

    def get_host_pid(self, host_name_or_uid: str) -> int | None:
        """获取host的PID"""
        try:
            host_uid = self.resolve_host_name(host_name_or_uid)
        except ValueError:
            # Host not found, no PID
            return None
        runtime = self.load_runtime()
        return runtime.pids.get(host_uid)

    def set_host_pid(self, host_name_or_uid: str, pid: int) -> None:
        """设置host的PID"""
        host_uid = self.resolve_host_name(host_name_or_uid)
        self.update_host_pid(host_uid, pid)

    def delete_host_pid(self, host_name_or_uid: str) -> None:
        """删除host的PID"""
        host_uid = self.resolve_host_name(host_name_or_uid)
        self.update_host_pid(host_uid, None)

    def exists(self) -> bool:
        """检查config.json是否存在"""
        return self._config_path().exists()


# 全局单例
_storage_manager: StorageManager | None = None


def get_storage_manager() -> StorageManager:
    """获取全局StorageManager单例"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager
