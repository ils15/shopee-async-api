# Shopee Async API

[![Tests](https://github.com/ils15/shopee-async-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ils15/shopee-async-api/actions/workflows/ci.yml)
[![Publish](https://github.com/ils15/shopee-async-api/actions/workflows/publish.yml/badge.svg)](https://github.com/ils15/shopee-async-api/actions/workflows/publish.yml)
[![PyPI](https://img.shields.io/pypi/v/shopee-async-api.svg)](https://pypi.org/project/shopee-async-api/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, fast, and fully asynchronous Python wrapper for the **Shopee Affiliate Open API**.

## ✨ Features

- ⚡️ **Asynchronous First**: Built natively with `httpx` and `asyncio` for maximum performance and non-blocking I/O.
- 🔐 **Type Safety**: Fully type-hinted and uses `Pydantic` v2 for advanced data validation.
- 🔑 **Developer Friendly**: Simplifies Shopee's complex SHA256 Authentication logic dynamically.
- 📡 **Comprehensive GraphQL**: Wraps the GraphQL schemas safely, allowing easy integration with Python logic.
- 🛡️ **Custom Exceptions**: Structured error handling for all Shopee API error codes.

## 📡 Supported Endpoints

**Links**
- `generate_short_link`: Generate a single affiliate tracking link for any Shopee product.
- `generate_batch_short_link`: Generate multiple affiliate tracking links in one request.

**Offers**
- `get_shopee_offer_list`: Get platform-wide top commission offers.
- `get_shop_offer_list`: Get specific shop offers and banners.
- `get_product_offer_list`: Get targeted product commissions.

**Reports**
- `get_conversion_report`: Get detailed reports linking user purchases and earned commissions.
- `get_validated_report`: Get validated (approved) commission reports by validation ID.
- `get_partner_order_report`: Get partner-level order reports with cursor-based pagination.

**Product Feeds**
- `list_item_feeds`: List available product data feeds (full or delta mode).
- `get_item_feed_data`: Stream rows from a product data feed by feed ID.

## 📦 Installation

```bash
pip install shopee-async-api
```

**Requires Python 3.8+**

## 🚀 Quick Start

```python
import asyncio
from shopee_async_api import ShopeeAffiliateClient

async def main():
    # Replace with your Shopee App ID and Secret
    app_id = "your_app_id"
    secret = "your_secret"
    
    async with ShopeeAffiliateClient(app_id=app_id, secret=secret) as client:
        # Generate a short link for an affiliate product
        link = await client.generate_short_link(
            origin_url="https://shopee.com.br/product-url", 
            sub_ids=["campaign1", "social-media"]
        )
        print(f"Shortlink: {link.shortLink}")
        
        # Get your recent conversions
        report = await client.get_conversion_report(limit=10)
        for node in report.nodes:
            print(node.shopeeCommissionCapped)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📖 Advanced Usage

See [QUICK_START.md](QUICK_START.md) for detailed workflows on API pagination, exception handling, and custom error types.

## 🛠️ Development & Testing

We use `pytest` for testing with full async support.

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ils15/shopee-async-api.git
   cd shopee-async-api
   ```

2. Install dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run tests:
   ```bash
   pytest --cov=shopee_async_api tests/
   ```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to set up your environment, write tests, and submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
