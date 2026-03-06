# Architecture

## Component Map

```
shopee_async_api/
├── __init__.py         # Public surface: ShopeeAffiliateClient + all models + exceptions
├── auth.py             # SHA-256 signature generation
├── client.py           # ShopeeAffiliateClient — all 10 API methods
├── exceptions.py       # 7 exception classes + handle_api_error()
└── models/
    ├── __init__.py     # Re-exports all models
    ├── base.py         # PageInfo, BaseConnection[T], GraphQLResponse[T]
    ├── links.py        # ShortLinkResult, BatchShortLinkItemResult, BatchShortLinkResult
    ├── offers.py       # ShopeeOfferConnectionV2, ShopOfferConnectionV2, ProductOfferConnectionV2
    ├── reports.py      # ConversionReport*, ValidatedReport*, PartnerOrderReport* models
    └── feeds.py        # ItemFeed, ItemFeedListConnection, ItemFeedDataConnection
```

## Authentication Flow

Every request is individually signed:

```
sig_input = app_id + timestamp + payload_body + secret
signature = SHA256(sig_input).hexdigest()
Authorization: SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}
```

Key: `payload_body` is the **compact JSON** (no whitespace) of the GraphQL request body.
Implementation: [auth.py](../../shopee_async_api/auth.py)

## Dynamic Query Builder

Shopee's API has a known bug: certain `Int` and `[Int]` parameters are internally non-null
but exposed as optional in the schema. Passing them as `null` (undeclared in variables)
causes error 10010 ("got null for non-null").

**Solution**: `_dynamic_query()` static method on `ShopeeAffiliateClient`.
It builds the GraphQL query string using *only* the parameters that are actually provided,
so undeclared variables never appear in the query declaration.

Affected parameters confirmed during live testing:
- `listType: Int` in `productOfferV2`
- `shopType: [Int]` in `shopOfferV2`
- `sortType: Int` in `shopeeOfferV2` (safe because it always has a default value of 1)

Methods that use `_dynamic_query`: `get_shop_offer_list`, `get_product_offer_list`.

## Int64 Serialization

Shopee defines a custom `Int64` scalar. When passed as GraphQL variables, Int64 values
**must be JSON strings** (not numbers). This applies to `partnerOrderReport` timestamps.

## Error Handling

`handle_api_error(code, message)` in [exceptions.py](../../shopee_async_api/exceptions.py):

| Code | Exception |
|------|-----------|
| 10020 | `ShopeeAuthError` |
| 10030 | `ShopeeRateLimitError` |
| 10031–10035 | `ShopeeAccessDeniedError` |
| 11000 | `ShopeeBusinessError` |
| 11001 | `ShopeeParamsError` |
| 11002 | `ShopeeBindAccountError` |
| other | `ShopeeAPIError` |

HTTP 5xx responses also raise `ShopeeAPIError`.

## Data Models (Pydantic v2)

All models inherit from `pydantic.BaseModel`. The `BaseConnection[T]` generic wraps
paginated endpoints with `nodes: List[T]` and `pageInfo: PageInfo`. `PageInfo` has
`page`, `limit`, `hasNextPage`, and optionally `scrollId`.

Exceptions: `PartnerOrderReportConnection` uses `searchNextPageInfo: SearchNextPageInfo`
instead (Shopee token-based pagination) and `ItemFeedDataConnection` uses `ItemFeedPageInfo`
with `offset`, `limit`, `totalCount`, `hasMore`.
