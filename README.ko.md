# Foundation Protocol

[English](README.md) | [中文](README.zh.md) | 한국어 | [日本語](README.ja.md) | [Español](README.es.md) | [Tiếng Việt](README.vi.md)

[![GitHub Stars](https://img.shields.io/github/stars/FoundationAgents/foundation-protocol)](https://github.com/FoundationAgents/foundation-protocol) [![License](https://img.shields.io/github/license/FoundationAgents/foundation-protocol)](LICENSE) [![Docs](https://img.shields.io/badge/docs-online-5b3fb6?logo=materialformkdocs&logoColor=white)](https://foundationagents.github.io/foundation-protocol/) [![arXiv](https://img.shields.io/badge/arXiv-2605.23218-b31b1b?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2605.23218) [![HuggingFace](https://img.shields.io/badge/🤗-Paper-yellow)](https://huggingface.co/papers/2605.23218)

다중 엔티티 AI 협업을 위한 Python 런타임 — 에이전트, 인간, 도구가 하나의 프로토콜 레이어에서 함께 작동합니다.

> [AI-Link-Net](https://github.com/FoundationAgents/ai-link-net)은 이 프로토콜 위에 구축된 풀스택 애플리케이션입니다.

## 특징

- **통합 엔티티 모델** — 에이전트, 인간, 도구, 서비스가 공통 ID 및 주소 체계를 공유
- **다자간 세션** — 엄격한 생명주기 관리와 이벤트 리플레이를 갖춘 구조화된 협업
- **정책 및 거버넌스** — 신뢰와 접근 제어를 위한 체크포인트 훅 및 출처 기록
- **거래 및 결제** — 상태 머신 기반의 계약, 에스크로, 정산 및 분쟁 해결
- **페더레이션** — 분산 호스트 노드 간 로컬 및 원격 엔티티 라우팅

## 선언문

https://github.com/user-attachments/assets/ceab2515-b8f2-47ec-8d7f-10452759c32a

## 설치

권장: PyPI에서 안정 버전 설치:

```bash
pip install foundation-protocol
```

개발자는 GitHub의 최신 소스도 설치할 수 있습니다:

```bash
pip install "foundation-protocol @ git+https://github.com/FoundationAgents/foundation-protocol.git"
```

## 사용법

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

크로스 호스트 메시징, MCP 도구 통합, 거래 워크플로우 등 더 많은 시나리오는 [`example/`](example/) 디렉토리를 참고하세요.

## 문서

전체 문서는 [foundationagents.github.io/foundation-protocol](https://foundationagents.github.io/foundation-protocol/)에서 확인할 수 있습니다. 빠른 링크:

- [퀵스타트](docs/develop/quickstart.md) — 설치 후 두 엔티티 메시지 교환 실행
- [체크포인트 파이프라인](docs/learn/checkpoint.md) — 신뢰와 거버넌스의 핵심
- [거래 및 신뢰](docs/trade-and-trust/index.md) — 계약, 중재, 평판
- [보안 노트](docs/security/index.md) — 알려진 경계와 위험

## 라이선스

MIT
