# Foundation Protocol

[English](README.md) | [中文](README.zh.md) | [한국어](README.ko.md) | 日本語 | [Español](README.es.md) | [Tiếng Việt](README.vi.md)

[![GitHub Stars](https://img.shields.io/github/stars/FoundationAgents/foundation-protocol)](https://github.com/FoundationAgents/foundation-protocol) [![License](https://img.shields.io/github/license/FoundationAgents/foundation-protocol)](LICENSE) [![Docs](https://img.shields.io/badge/docs-online-5b3fb6?logo=materialformkdocs&logoColor=white)](https://foundationagents.github.io/foundation-protocol/) [![arXiv](https://img.shields.io/badge/arXiv-2605.23218-b31b1b?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2605.23218) [![HuggingFace](https://img.shields.io/badge/🤗-Paper-yellow)](https://huggingface.co/papers/2605.23218)

マルチエンティティAIコラボレーションのためのPythonランタイム — エージェント、人間、ツールが共通のプロトコルレイヤー上で連携します。

> [AI-Link-Net](https://github.com/FoundationAgents/ai-link-net)は、このプロトコル上に構築されたフルスタックアプリケーションです。

## 特徴

- **統一エンティティモデル** — エージェント、人間、ツール、サービスが共通のIDとアドレス体系を共有
- **マルチパーティセッション** — 厳格なライフサイクル管理とイベントリプレイによる構造化コラボレーション
- **ポリシーとガバナンス** — 信頼とアクセス制御のためのチェックポイントフックと来歴記録
- **取引と決済** — ステートマシンによる契約、エスクロー、精算、紛争解決
- **フェデレーション** — 分散ホストノード間のローカル・リモートエンティティルーティング

## マニフェスト

https://github.com/user-attachments/assets/ceab2515-b8f2-47ec-8d7f-10452759c32a

## インストール

推奨：PyPIから安定版をインストール：

```bash
pip install foundation-protocol
```

開発者はGitHubの最新ソースもインストールできます：

```bash
pip install "foundation-protocol @ git+https://github.com/FoundationAgents/foundation-protocol.git"
```

## 使い方

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

クロスホストメッセージング、MCPツール統合、取引ワークフローなどのシナリオは[`example/`](example/)ディレクトリをご覧ください。

## ドキュメント

完全なドキュメントは [foundationagents.github.io/foundation-protocol](https://foundationagents.github.io/foundation-protocol/) で公開されています。クイックリンク：

- [クイックスタート](docs/develop/quickstart.md) — インストールして2エンティティ間でメッセージ送受信
- [チェックポイントパイプライン](docs/learn/checkpoint.md) — 信頼とガバナンスの中核
- [取引と信頼](docs/trade-and-trust/index.md) — 契約、仲裁、評価
- [セキュリティノート](docs/security/index.md) — 既知の境界とリスク

## ライセンス

MIT
