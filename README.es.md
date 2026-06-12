# Foundation Protocol

[English](README.md) | [中文](README.zh.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | Español | [Tiếng Việt](README.vi.md)

[![GitHub Stars](https://img.shields.io/github/stars/FoundationAgents/foundation-protocol)](https://github.com/FoundationAgents/foundation-protocol) [![License](https://img.shields.io/github/license/FoundationAgents/foundation-protocol)](LICENSE) [![Docs](https://img.shields.io/badge/docs-online-5b3fb6?logo=materialformkdocs&logoColor=white)](https://foundationagents.github.io/foundation-protocol/) [![arXiv](https://img.shields.io/badge/arXiv-2605.23218-b31b1b?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2605.23218) [![HuggingFace](https://img.shields.io/badge/🤗-Paper-yellow)](https://huggingface.co/papers/2605.23218)

Un runtime de Python para la colaboración de IA multi-entidad — agentes, humanos y herramientas en una capa de protocolo compartida.

> [AI-Link-Net](https://github.com/FoundationAgents/ai-link-net) es una aplicación full-stack construida sobre este protocolo.

## Características

- **Modelo de entidad unificado** — agentes, humanos, herramientas y servicios comparten un sistema común de identidad y direccionamiento
- **Sesiones multipartitas** — colaboración estructurada con gestión estricta del ciclo de vida y reproducción de eventos
- **Políticas y gobernanza** — hooks de checkpoint con registro de procedencia para confianza y control de acceso
- **Comercio y pagos** — contratos, custodia, liquidación y resolución de disputas mediante máquinas de estado
- **Federación** — enrutamiento de entidades locales y remotas a través de nodos host distribuidos

## Manifiesto

https://github.com/user-attachments/assets/ceab2515-b8f2-47ec-8d7f-10452759c32a

## Instalación

Recomendado: instalar la versión estable desde PyPI:

```bash
pip install foundation-protocol
```

Los desarrolladores también pueden instalar el código fuente más reciente desde GitHub:

```bash
pip install "foundation-protocol @ git+https://github.com/FoundationAgents/foundation-protocol.git"
```

## Uso

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

Consulte el directorio [`example/`](example/) para más escenarios, incluyendo mensajería entre hosts, integración de herramientas MCP y flujos de comercio.

## Documentación

La documentación completa se publica en [foundationagents.github.io/foundation-protocol](https://foundationagents.github.io/foundation-protocol/). Enlaces rápidos:

- [Inicio rápido](docs/develop/quickstart.md) — instalar y ejecutar un intercambio entre dos entidades
- [Pipeline de checkpoints](docs/learn/checkpoint.md) — la base de confianza y gobernanza
- [Comercio y confianza](docs/trade-and-trust/index.md) — contratos, arbitraje, reputación
- [Notas de seguridad](docs/security/index.md) — límites y riesgos conocidos

## Licencia

MIT
