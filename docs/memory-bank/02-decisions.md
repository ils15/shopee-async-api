# Architecture Decision Records

## ADR-001: `httpx` over `requests` for HTTP transport
**Status**: Accepted  
**Date**: 2024  
**Decision**: Use `httpx.AsyncClient` instead of `aiohttp` or `requests`.  
**Rationale**: `httpx` provides a familiar `requests`-like API while being natively async. Avoids the extra complexity of `aiohttp`'s session management. Supports HTTP/2 automatically.

---

## ADR-002: Pydantic v2 for model validation
**Status**: Accepted  
**Date**: 2024  
**Decision**: Use `pydantic>=2.0.0` for all response models.  
**Rationale**: Strong type safety, IDE autocomplete, and automatic coercion. v2 is significantly faster than v1. GraphQL responses map cleanly to pydantic models with Optional fields for nullable API responses.

---

## ADR-003: Async-only design (no sync wrapper)
**Status**: Accepted  
**Date**: 2024  
**Decision**: The client is async-only, using `async with` context manager.  
**Rationale**: The Shopee Affiliate API is typically called from async web backends (FastAPI, Django Channels, etc.). Providing a sync wrapper adds complexity; users who need sync can use `asyncio.run()`.

---

## ADR-004: Dynamic GraphQL query construction
**Status**: Accepted  
**Date**: 2025  
**Decision**: `get_shop_offer_list` and `get_product_offer_list` build their GraphQL query strings dynamically via `_dynamic_query()`, including only variables that are actually provided.  
**Rationale**: Shopee's API returns error 10010 ("got null for non-null") when certain parameters (specifically `listType: Int`, `shopType: [Int]`) are declared in the query but absent from the variables object. This is a Shopee server-side bug — they treat undeclared variables as explicit null for some parameters. The dynamic builder is future-proof against other similar parameters.  
**Alternatives considered**: Providing default values for all parameters; only using `None`-filtered variables with a static query (insufficient — the declaration itself causes the error).

---

## ADR-005: Int64 serialization as JSON strings
**Status**: Accepted  
**Date**: 2025  
**Decision**: `get_partner_order_report` passes Int64 timestamp values as JSON **strings** in the variables object (e.g., `"purchaseTimeStart": "1700000000"`).  
**Rationale**: The Shopee `Int64` custom scalar expects string representation in JSON variables. Passing as a JSON number fails silently or produces unexpected results.

---

## ADR-006: MCN-gated endpoints documented but not tested live
**Status**: Accepted  
**Date**: 2025  
**Decision**: `generate_batch_short_link` and `get_partner_order_report` are implemented but return `ShopeeAccessDeniedError` for standard accounts.  
**Rationale**: These endpoints require MCN (Multi-Channel Network) partner status. The implementation is architecturally correct (verified by the error progression from auth errors to access-denied, not validation errors). Tests mock the access-denied behavior.
