# Quick Start Guide

This guide will walk you through the primary features and advanced use cases of the `shopee-async-api`.

## 1. Authentication
The Shopee Affiliate Open API requires an `AppId` and a `Secret`. You can obtain these from the Shopee Affiliate Open API Platform.
The `ShopeeAffiliateClient` handles the complex SHA256 GraphQL signature generation automatically behind the scenes.

```python
import asyncio
from shopee_async_api import ShopeeAffiliateClient

async def main():
    async with ShopeeAffiliateClient(app_id="YOUR_APP_ID", secret="YOUR_SECRET") as client:
        # Client is ready to perform queries
        pass
```

## 2. Generating Affiliate Short Links
To generate affiliate links with custom UTM tracking (`subIds`), use `generate_short_link`.

```python
result = await client.generate_short_link(
    origin_url="https://shopee.com.br/Xiaomi-S40...",
    sub_ids=["instagram_bio", "post1"]
)

print(result.shortLink) # https://s.shopee.com.br/xxxxx
```

## 3. Retrieving Offers
You can retrieve trending offers using various filters like `keyword` and `sortType`.

### Shopee Platform Offers
```python
offers = await client.get_shopee_offer_list(
    limit=5,
    keyword="roupas",
    sortType=2 # HIGHEST_COMMISSION_DESC
)

for node in offers.nodes:
    print(f"Produto: {node.offerName} - Comissão: {node.commissionRate}%")
```

### Specific Product Offers
```python
products = await client.get_product_offer_list(
    keyword="iphone",
    limit=10,
    sortType=2 # ITEM_SOLD_DESC
)

for product in products.nodes:
    print(product.productName, product.priceMin)
```

## 4. Conversion Reports (Tracking Sales)
If you want to track the clicks, orders, and commissions earned, you can use the conversion report API.
The API uses `scrollId` for pagination over 500 limits.

```python
# Fetch initial batch
report = await client.get_conversion_report(limit=500)

for node in report.nodes:
    print(f"Commission: {node.netCommission}")

# If hasNextPage is True, fetch next batch within 30 seconds
if report.pageInfo.hasNextPage and report.pageInfo.scrollId:
    next_report = await client.get_conversion_report(
        limit=500, 
        scrollId=report.pageInfo.scrollId
    )
```

## 5. Exception Handling
The library exports custom Pydantic-mapped exceptions so you can trap specific GraphQL/API issues (like Rate Limits or Signature Errors).

```python
from shopee_async_api import ShopeeAuthError, ShopeeRateLimitError

try:
    await client.generate_short_link("https://shopee.com.br/product/123")
except ShopeeAuthError as e:
    print("Suas credenciais estão inválidas:", e)
except ShopeeRateLimitError as e:
    print("Você atingiu o limite da API da Shopee:", e)
```
