# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- CI workflows aligned with gold standard: `gpt-5-mini` classification, OIDC PyPI publishing (no API token), PR label-driven version bump
- `publish.yml`: reads merged PR label (`enhancement`/`bug`/`refactor`) to determine bump type; fallback to commit message
- `auto-pr.yml`: improved AI system prompt with prioritized SemVer categories and strict rules
- `ci.yml`: style checks (`black`, `isort`, `mypy`) non-blocking via `continue-on-error`
- `autoformat.yml`: new workflow — applies Black + isort automatically on every push and commits back
- `bump_version.py`: accepts `BUMP_TYPE` env var from PR label as priority over commit message
- Automatic `develop` ← `master` sync after every release (no manual pull needed)

---

## [0.2.1] - 2026-03-06

---

## [0.2.0] - 2026-03-06

### Added
- **100% API coverage** — all 8 queries and 2 mutations from the Shopee Affiliate Open API GraphQL schema are now implemented.
- New endpoint `generate_batch_short_link`: generate multiple affiliate links in a single mutation (`BatchShortLinkResult`).
- New endpoint `get_validated_report`: fetch validated/approved conversion reports by `validationId` with scroll-based pagination (`ValidatedReportConnection`).
- New endpoint `get_partner_order_report`: fetch partner order reports with cursor-based pagination via `searchNextToken` (`PartnerOrderReportConnection`).
- New endpoint `list_item_feeds`: list available product data feeds, filtering by `FeedMode` (`FULL` or `DELTA`) (`ItemFeedListConnection`).
- New endpoint `get_item_feed_data`: stream rows from a product data feed by `datafeedId` with offset pagination (`ItemFeedDataConnection`).
- New Pydantic models: `ValidatedReport`, `ValidatedReportOrder`, `ValidatedReportOrderItem`, `PartnerOrder`, `PartnerReportOrderItem`, `ExtInfo`, `SearchNextPageInfo`, `PartnerOrderReportConnection`, `ItemFeed`, `ItemFeedListConnection`, `ItemFeedDataRow`, `ItemFeedPageInfo`, `ItemFeedDataConnection`, `BatchShortLinkItemResult`, `BatchShortLinkResult`.
- `ShortLinkResult` now includes the `longLink` field returned by the API.

## [0.1.0] - 2026-03-06

### Added
- Initial release of the `shopee-async-api` library.
- Comprehensive `asyncio` and `httpx` based client (`ShopeeAffiliateClient`).
- Transparent SHA256 Signature Authentication handling natively via Pythons hashlib.
- Wrapped mapping for top-level GraphQL Affiliate Endpoints:
  - `generate_short_link`
  - `get_shopee_offer_list`
  - `get_shop_offer_list`
  - `get_product_offer_list`
  - `get_conversion_report`
- Complete typing validation with `pydantic` schemas representing API responses.
- Granular Exceptions like `ShopeeRateLimitError` and `ShopeeAuthError`.
