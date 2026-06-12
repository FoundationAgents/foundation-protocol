# Foundation Protocol

[English](README.md) | [中文](README.zh.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [Español](README.es.md) | Tiếng Việt

[![GitHub Stars](https://img.shields.io/github/stars/FoundationAgents/foundation-protocol)](https://github.com/FoundationAgents/foundation-protocol) [![License](https://img.shields.io/github/license/FoundationAgents/foundation-protocol)](LICENSE) [![Docs](https://img.shields.io/badge/docs-online-5b3fb6?logo=materialformkdocs&logoColor=white)](https://foundationagents.github.io/foundation-protocol/) [![arXiv](https://img.shields.io/badge/arXiv-2605.23218-b31b1b?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2605.23218) [![HuggingFace](https://img.shields.io/badge/🤗-Paper-yellow)](https://huggingface.co/papers/2605.23218)

Runtime Python cho cộng tác AI đa thực thể — agent, con người và công cụ hoạt động trên một lớp giao thức chung.

> [AI-Link-Net](https://github.com/FoundationAgents/ai-link-net) là ứng dụng full-stack được xây dựng trên giao thức này.

## Tính năng

- **Mô hình thực thể thống nhất** — agent, con người, công cụ và dịch vụ chia sẻ hệ thống định danh và địa chỉ chung
- **Phiên đa bên** — cộng tác có cấu trúc với quản lý vòng đời nghiêm ngặt và phát lại sự kiện
- **Chính sách và quản trị** — hook checkpoint với ghi nhận nguồn gốc cho tin cậy và kiểm soát truy cập
- **Giao dịch và thanh toán** — hợp đồng, ký quỹ, quyết toán và giải quyết tranh chấp qua máy trạng thái
- **Liên bang** — định tuyến thực thể cục bộ và từ xa qua các node host phân tán

## Tuyên ngôn

https://github.com/user-attachments/assets/ceab2515-b8f2-47ec-8d7f-10452759c32a

## Cài đặt

Khuyến nghị: cài đặt bản ổn định từ PyPI:

```bash
pip install foundation-protocol
```

Nhà phát triển cũng có thể cài đặt mã nguồn mới nhất từ GitHub:

```bash
pip install "foundation-protocol @ git+https://github.com/FoundationAgents/foundation-protocol.git"
```

## Sử dụng

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

Xem thư mục [`example/`](example/) để biết thêm các tình huống bao gồm nhắn tin xuyên host, tích hợp công cụ MCP và quy trình giao dịch.

## Tài liệu

Tài liệu đầy đủ được xuất bản tại [foundationagents.github.io/foundation-protocol](https://foundationagents.github.io/foundation-protocol/). Liên kết nhanh:

- [Khởi động nhanh](docs/develop/quickstart.md) — cài đặt và chạy trao đổi giữa hai thực thể
- [Pipeline checkpoint](docs/learn/checkpoint.md) — trục tin cậy và quản trị
- [Giao dịch và tin cậy](docs/trade-and-trust/index.md) — hợp đồng, trọng tài, danh tiếng
- [Ghi chú bảo mật](docs/security/index.md) — ranh giới và rủi ro đã biết

## Giấy phép

MIT
