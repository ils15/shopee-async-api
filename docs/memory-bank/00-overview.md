# Project Overview

## What This Is
`shopee-async-api` is a modern, fully async Python client for the **Shopee Affiliate Open API** (GraphQL, Brazil region). It provides 100% coverage of all API endpoints as of v0.2.0.

## Purpose
Enable Python developers to interact with the Shopee Affiliate program programmatically: generate affiliate links, browse offers/shops/products, access commission reports, and iterate over product data feeds.

## Key Constraints
- **API Protocol**: GraphQL over HTTPS POST — `https://open-api.affiliate.shopee.com.br/graphql`
- **Authentication**: SHA-256 HMAC signature per request (see [01-architecture.md](01-architecture.md))
- **Python requirement**: ≥ 3.8, asyncio-only (no sync wrapper)
- **Credentials**: `SHOPEE_APP_ID` + `SHOPEE_SECRET` (obtained from the Shopee Affiliate portal)

## API Endpoint Matrix (v0.2.0)

| Method | GraphQL Operation | Permissions |
|--------|-----------------|-------------|
| `generate_short_link` | `generateShortLink` mutation | Standard |
| `generate_batch_short_link` | `generateBatchShortLink` mutation | **MCN required** |
| `get_shopee_offer_list` | `shopeeOfferV2` query | Standard |
| `get_shop_offer_list` | `shopOfferV2` query | Standard |
| `get_product_offer_list` | `productOfferV2` query | Standard |
| `get_conversion_report` | `conversionReport` query | Standard |
| `get_validated_report` | `validatedReport` query | Standard |
| `get_partner_order_report` | `partnerOrderReport` query | **MCN required** |
| `list_item_feeds` | `listItemFeeds` query | Standard |
| `get_item_feed_data` | `getItemFeedData` query | Standard |

## Quick Start
```python
import asyncio, os
from shopee_async_api import ShopeeAffiliateClient

async def main():
    async with ShopeeAffiliateClient(
        app_id=os.environ["SHOPEE_APP_ID"],
        secret=os.environ["SHOPEE_SECRET"],
    ) as client:
        link = await client.generate_short_link(origin_url="https://shopee.com.br/...")
        print(link.shortLink)

asyncio.run(main())
```
