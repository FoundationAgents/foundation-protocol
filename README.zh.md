# Foundation Protocol

[English](README.md) | 中文 | [한국어](README.ko.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md)

[![GitHub Stars](https://img.shields.io/github/stars/FoundationAgents/foundation-protocol)](https://github.com/FoundationAgents/foundation-protocol) [![License](https://img.shields.io/github/license/FoundationAgents/foundation-protocol)](LICENSE) [![Docs](https://img.shields.io/badge/docs-online-5b3fb6?logo=materialformkdocs&logoColor=white)](https://foundationagents.github.io/foundation-protocol/) [![arXiv](https://img.shields.io/badge/arXiv-2605.23218-b31b1b?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2605.23218) [![HuggingFace](https://img.shields.io/badge/🤗-Paper-yellow)](https://huggingface.co/papers/2605.23218)

多实体 AI 协作的 Python 运行时 —— 让 Agent、人类和工具在统一协议层上协同工作。

> [AI-Link-Net](https://github.com/FoundationAgents/ai-link-net) 是基于此协议构建的全栈应用。

## 特性

- **统一实体模型** —— Agent、人类、工具和服务共享通用的身份与寻址体系
- **多方会话** —— 结构化协作，严格的生命周期管理与事件回放
- **策略与治理** —— 检查点钩子与溯源记录，用于信任和访问控制
- **交易与支付** —— 合约、托管、结算与争议解决，基于状态机驱动
- **联邦路由** —— 跨分布式 Host 节点的本地与远程实体路由

## 宣言

https://github.com/user-attachments/assets/ceab2515-b8f2-47ec-8d7f-10452759c32a

## 安装

推荐：从 PyPI 安装稳定版本：

```bash
pip install foundation-protocol
```

开发者也可以安装 GitHub 上的最新源码：

```bash
pip install "foundation-protocol @ git+https://github.com/FoundationAgents/foundation-protocol.git"
```

## 使用

```python
import asyncio
from fp import EntityKind, Host, Message, MessageKind

async def main():
    host = Host(name="LocalHost")

    alice = host.register_entity(name="Alice", kind=EntityKind.HUMAN)
    bot = host.register_entity(name="Bot", kind=EntityKind.AGENT)

    await alice.send_message(
        to=bot.entity_card,
        message=Message(kind=MessageKind.INVOKE, payload={"text": "Hello!"}),
    )

asyncio.run(main())
```

更多示例请查看 [`example/`](example/) 目录，包括跨 Host 通信、MCP 工具集成和交易流程。

## 文档

完整文档发布在 [foundationagents.github.io/foundation-protocol](https://foundationagents.github.io/foundation-protocol/)。快速链接：

- [快速开始](docs/develop/quickstart.md) —— 安装并运行双实体消息收发
- [检查点流水线](docs/learn/checkpoint.md) —— 信任与治理的核心抓手
- [交易与信任](docs/trade-and-trust/index.md) —— 合约、仲裁与声誉
- [安全说明](docs/security/index.md) —— 当前的边界与已知风险

## 许可证

MIT
