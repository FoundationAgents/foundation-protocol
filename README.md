# Foundation Protocol

English | [中文](README.zh.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md)

[![GitHub Stars](https://img.shields.io/github/stars/FoundationAgents/foundation-protocol)](https://github.com/FoundationAgents/foundation-protocol) [![License](https://img.shields.io/github/license/FoundationAgents/foundation-protocol)](LICENSE) [![Docs](https://img.shields.io/badge/docs-online-5b3fb6?logo=materialformkdocs&logoColor=white)](https://foundationagents.github.io/foundation-protocol/) [![arXiv](https://img.shields.io/badge/arXiv-2605.23218-b31b1b?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2605.23218) [![HuggingFace](https://img.shields.io/badge/🤗-Paper-yellow)](https://huggingface.co/papers/2605.23218)

A Python runtime for multi-entity AI collaboration — agents, humans, and tools on a shared protocol layer.

> [AI-Link-Net](https://github.com/FoundationAgents/ai-link-net) is a full-stack application built on this protocol.

## Features

- **Unified entity model** — agents, humans, tools, and services share a common identity and addressing system
- **Multi-party sessions** — structured collaboration with strict lifecycle enforcement and event replay
- **Policy & governance** — checkpoint hooks with provenance recording for trust and access control
- **Trade & payment** — contracts, escrow, settlement, and dispute resolution via state machines
- **Federation** — local and remote entity routing across distributed host nodes

## Manifesto

https://github.com/user-attachments/assets/ceab2515-b8f2-47ec-8d7f-10452759c32a

## Installation

Recommended: install the stable release from PyPI:

```bash
pip install foundation-protocol
```

Developers can install the latest source from GitHub:

```bash
pip install "foundation-protocol @ git+https://github.com/FoundationAgents/foundation-protocol.git"
```

## Usage

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

See the [`example/`](example/) directory for more scenarios including cross-host messaging, MCP tool integration, and trade workflows.

## Documentation

Full documentation is published at [foundationagents.github.io/foundation-protocol](https://foundationagents.github.io/foundation-protocol/). Quick links:

- [Quickstart](docs/develop/quickstart.md) — install and run a two-entity exchange
- [Checkpoint Pipeline](docs/learn/checkpoint.md) — the trust and governance seam
- [Trade & Trust](docs/trade-and-trust/index.md) — contracts, arbitration, reputation
- [Security Notes](docs/security/index.md) — known boundaries and risks

## License

MIT
