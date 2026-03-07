from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shopee_async_api import ShopeeAffiliateClient
from shopee_async_api.exceptions import (
    ShopeeAccessDeniedError,
    ShopeeAPIError,
    ShopeeAuthError,
    ShopeeBindAccountError,
    ShopeeBusinessError,
    ShopeeParamsError,
    ShopeeRateLimitError,
)
from shopee_async_api.models import (
    BatchShortLinkResult,
    ConversionReportConnection,
    ItemFeedDataConnection,
    ItemFeedListConnection,
    PartnerOrderReportConnection,
    ProductOfferConnectionV2,
    ShopeeOfferConnectionV2,
    ShopOfferConnectionV2,
    ShortLinkResult,
    ValidatedReportConnection,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_post(response_body: dict, status_code: int = 200):
    """Return a context-manager-compatible patch that mocks httpx.AsyncClient.post."""
    mock_resp = AsyncMock()
    mock_resp.status_code = status_code
    mock_resp.json = lambda: response_body
    mock_resp.text = str(response_body)
    return patch("httpx.AsyncClient.post", return_value=mock_resp)


def _error_body(code: int, message: str) -> dict:
    return {
        "data": None,
        "errors": [{"message": message, "extensions": {"code": code}}],
    }


# ---------------------------------------------------------------------------
# --- generate_short_link ---
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_short_link_success():
    body = {
        "data": {
            "generateShortLink": {
                "shortLink": "https://s.shopee.com.br/abc123",
                "longLink": "https://shopee.com.br/product",
            }
        }
    }
    with _mock_post(body) as mock_post:
        async with ShopeeAffiliateClient(
            app_id="test_app", secret="test_secret"
        ) as client:
            result = await client.generate_short_link(
                origin_url="https://shopee.com.br/product"
            )

        assert isinstance(result, ShortLinkResult)
        assert result.shortLink == "https://s.shopee.com.br/abc123"
        assert result.longLink == "https://shopee.com.br/product"

        call_args = mock_post.call_args
        assert "SHA256" in call_args.kwargs["headers"]["Authorization"]


@pytest.mark.asyncio
async def test_generate_short_link_with_sub_ids():
    body = {"data": {"generateShortLink": {"shortLink": "https://s.shopee.com.br/xyz"}}}
    with _mock_post(body):
        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            result = await client.generate_short_link(
                origin_url="https://shopee.com.br/p", sub_ids=["sub1", "sub2"]
            )
    assert result.shortLink == "https://s.shopee.com.br/xyz"


# ---------------------------------------------------------------------------
# --- generate_batch_short_link ---
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_batch_short_link_success():
    body = {
        "data": {
            "generateBatchShortLink": {
                "links": [
                    {
                        "originUrl": "https://shopee.com.br/p1",
                        "shortLink": "https://s.shopee.com.br/aaa",
                        "longLink": "",
                        "success": True,
                        "errorMessage": "",
                    },
                    {
                        "originUrl": "https://shopee.com.br/p2",
                        "shortLink": "https://s.shopee.com.br/bbb",
                        "longLink": "",
                        "success": True,
                        "errorMessage": "",
                    },
                ],
                "total": 2,
                "successCount": 2,
            }
        }
    }
    with _mock_post(body):
        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            result = await client.generate_batch_short_link(
                [
                    {"originUrl": "https://shopee.com.br/p1"},
                    {"originUrl": "https://shopee.com.br/p2"},
                ]
            )

    assert isinstance(result, BatchShortLinkResult)
    assert result.total == 2
    assert result.successCount == 2
    assert len(result.links) == 2
    assert result.links[0].shortLink == "https://s.shopee.com.br/aaa"


# ---------------------------------------------------------------------------
# --- get_shopee_offer_list ---
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_shopee_offer_list_success():
    body = {
        "data": {
            "shopeeOfferV2": {
                "nodes": [
                    {
                        "commissionRate": "0.10",
                        "imageUrl": "https://img.shopee.com",
                        "offerLink": "https://s.shopee.com.br/x",
                        "originalLink": "https://shopee.com.br",
                        "offerName": "Promo Test",
                        "offerType": 1,
                        "categoryId": None,
                        "collectionId": None,
                        "periodStartTime": 0,
                        "periodEndTime": 0,
                    }
                ],
                "pageInfo": {"page": 1, "limit": 10, "hasNextPage": False},
            }
        }
    }
    with _mock_post(body):
        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            result = await client.get_shopee_offer_list(limit=1)

    assert isinstance(result, ShopeeOfferConnectionV2)
    assert len(result.nodes) == 1
    assert result.nodes[0].commissionRate == "0.10"
    assert result.pageInfo.hasNextPage is False


# ---------------------------------------------------------------------------
# --- get_shop_offer_list ---
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_shop_offer_list_success():
    body = {
        "data": {
            "shopOfferV2": {
                "nodes": [
                    {
                        "commissionRate": "0.07",
                        "imageUrl": "https://img",
                        "offerLink": "https://link",
                        "originalLink": "https://orig",
                        "shopId": 123,
                        "shopName": "Test Shop",
                        "ratingStar": "4.9",
                        "shopType": [2],
                        "remainingBudget": 0,
                        "periodStartTime": 0,
                        "periodEndTime": 0,
                        "sellerCommCoveRatio": "0.9",
                        "bannerInfo": None,
                    }
                ],
                "pageInfo": {"page": 1, "limit": 10, "hasNextPage": True},
            }
        }
    }
    with _mock_post(body):
        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            result = await client.get_shop_offer_list(limit=1)

    assert isinstance(result, ShopOfferConnectionV2)
    assert result.nodes[0].shopId == 123
    assert result.pageInfo.hasNextPage is True


@pytest.mark.asyncio
async def test_get_shop_offer_list_dynamic_query_excludes_null_shoptype():
    """shopType=[Int] must not appear in the query when not provided (avoids error 10010)."""
    body = {
        "data": {
            "shopOfferV2": {
                "nodes": [],
                "pageInfo": {"page": 1, "limit": 10, "hasNextPage": False},
            }
        }
    }
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: body
        mock_post.return_value = mock_resp

        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            await client.get_shop_offer_list(limit=10)

        payload_sent = mock_post.call_args.kwargs["content"]
        if isinstance(payload_sent, bytes):
            payload_sent = payload_sent.decode()
        # $shopType (variable declaration) must not appear, even though 'shopType' appears in return fields
        assert "$shopType" not in payload_sent


# ---------------------------------------------------------------------------
# --- get_product_offer_list ---
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_product_offer_list_success():
    body = {
        "data": {
            "productOfferV2": {
                "nodes": [
                    {
                        "itemId": 99999,
                        "commissionRate": "0.18",
                        "sellerCommissionRate": "0.15",
                        "shopeeCommissionRate": "0.03",
                        "commission": "10.0",
                        "sales": 50,
                        "priceMax": "89.90",
                        "priceMin": "89.90",
                        "productCatIds": [101],
                        "ratingStar": "4.8",
                        "priceDiscountRate": 10,
                        "imageUrl": "https://img",
                        "productName": "Test Product",
                        "shopId": 555,
                        "shopName": "Best Shop",
                        "shopType": [],
                        "productLink": "https://shopee.com.br/p",
                        "offerLink": "https://s.shopee.com.br/y",
                        "periodStartTime": 0,
                        "periodEndTime": 0,
                    }
                ],
                "pageInfo": {"page": 1, "limit": 10, "hasNextPage": False},
            }
        }
    }
    with _mock_post(body):
        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            result = await client.get_product_offer_list(limit=1)

    assert isinstance(result, ProductOfferConnectionV2)
    assert result.nodes[0].itemId == 99999
    assert result.nodes[0].productName == "Test Product"


@pytest.mark.asyncio
async def test_get_product_offer_list_dynamic_query_excludes_null_listtype():
    """listType must not appear in query when not provided (avoids error 10010)."""
    body = {
        "data": {
            "productOfferV2": {
                "nodes": [],
                "pageInfo": {"page": 1, "limit": 10, "hasNextPage": False},
            }
        }
    }
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: body
        mock_post.return_value = mock_resp

        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            await client.get_product_offer_list(limit=10)  # listType not provided

        payload_sent = mock_post.call_args.kwargs["content"]
        if isinstance(payload_sent, bytes):
            payload_sent = payload_sent.decode()
        assert "listType" not in payload_sent


# ---------------------------------------------------------------------------
# --- get_conversion_report ---
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_conversion_report_empty():
    body = {
        "data": {
            "conversionReport": {
                "nodes": [],
                "pageInfo": {"limit": 500, "hasNextPage": False, "scrollId": None},
            }
        }
    }
    with _mock_post(body):
        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            result = await client.get_conversion_report(limit=500)

    assert isinstance(result, ConversionReportConnection)
    assert result.nodes == []
    assert result.pageInfo.hasNextPage is False


# ---------------------------------------------------------------------------
# --- get_validated_report ---
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_validated_report_empty():
    body = {
        "data": {
            "validatedReport": {
                "nodes": [],
                "pageInfo": {"limit": 20, "hasNextPage": False, "scrollId": None},
            }
        }
    }
    with _mock_post(body):
        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            result = await client.get_validated_report(validationId=12345)

    assert isinstance(result, ValidatedReportConnection)
    assert result.nodes == []


# ---------------------------------------------------------------------------
# --- get_partner_order_report ---
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_partner_order_report_empty():
    body = {
        "data": {
            "partnerOrderReport": {
                "nodes": [],
                "searchNextPageInfo": {
                    "size": 0,
                    "limit": 500,
                    "searchNextToken": None,
                    "debugId": "",
                },
            }
        }
    }
    with _mock_post(body):
        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            result = await client.get_partner_order_report(limit=500)

    assert isinstance(result, PartnerOrderReportConnection)
    assert result.nodes == []


@pytest.mark.asyncio
async def test_get_partner_order_report_int64_serialized_as_string():
    """purchaseTimeStart must be serialized as a string (Shopee Int64 contract)."""
    body = {
        "data": {
            "partnerOrderReport": {
                "nodes": [],
                "searchNextPageInfo": {
                    "size": 0,
                    "limit": 500,
                    "searchNextToken": None,
                    "debugId": "",
                },
            }
        }
    }
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: body
        mock_post.return_value = mock_resp

        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            await client.get_partner_order_report(
                purchaseTimeStart=1700000000, purchaseTimeEnd=1700086400
            )

        import json

        raw = mock_post.call_args.kwargs["content"]
        payload = json.loads(raw if isinstance(raw, str) else raw.decode())
        assert payload["variables"]["purchaseTimeStart"] == "1700000000"
        assert payload["variables"]["purchaseTimeEnd"] == "1700086400"


# ---------------------------------------------------------------------------
# --- list_item_feeds ---
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_item_feeds_success():
    body = {
        "data": {
            "listItemFeeds": {
                "feeds": [
                    {
                        "datafeedId": "feed_001",
                        "referenceId": "ref_001",
                        "datafeedName": "Full Feed",
                        "description": "All products",
                        "totalCount": 10000,
                        "date": "2024-01-01",
                        "feedMode": "FULL",
                    },
                ]
            }
        }
    }
    with _mock_post(body):
        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            result = await client.list_item_feeds()

    assert isinstance(result, ItemFeedListConnection)
    assert len(result.feeds) == 1
    assert result.feeds[0].datafeedId == "feed_001"
    assert result.feeds[0].feedMode == "FULL"


# ---------------------------------------------------------------------------
# --- get_item_feed_data ---
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_item_feed_data_success():
    body = {
        "data": {
            "getItemFeedData": {
                "rows": [
                    {"columns": '["123", "Product A", "99.90"]', "updateType": "NEW"},
                    {
                        "columns": '["456", "Product B", "49.90"]',
                        "updateType": "UPDATE",
                    },
                ],
                "pageInfo": {
                    "offset": 0,
                    "limit": 2,
                    "totalCount": 5000,
                    "hasMore": True,
                },
            }
        }
    }
    with _mock_post(body):
        async with ShopeeAffiliateClient(app_id="a", secret="b") as client:
            result = await client.get_item_feed_data(datafeedId="feed_001", limit=2)

    assert isinstance(result, ItemFeedDataConnection)
    assert len(result.rows) == 2
    assert result.pageInfo.totalCount == 5000
    assert result.pageInfo.hasMore is True
    assert result.rows[0].updateType == "NEW"


# ---------------------------------------------------------------------------
# --- Exception handling ---
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_auth_error_code_10020():
    with _mock_post(_error_body(10020, "Invalid Signature")):
        async with ShopeeAffiliateClient(app_id="x", secret="y") as client:
            with pytest.raises(ShopeeAuthError) as exc_info:
                await client.generate_short_link(origin_url="https://shopee.com.br")
    assert "10020" in str(exc_info.value)


@pytest.mark.asyncio
async def test_rate_limit_error_code_10030():
    with _mock_post(_error_body(10030, "Rate limit exceeded")):
        async with ShopeeAffiliateClient(app_id="x", secret="y") as client:
            with pytest.raises(ShopeeRateLimitError):
                await client.get_shopee_offer_list()


@pytest.mark.asyncio
async def test_access_denied_error_code_10031():
    with _mock_post(_error_body(10031, "access deny")):
        async with ShopeeAffiliateClient(app_id="x", secret="y") as client:
            with pytest.raises(ShopeeAccessDeniedError):
                await client.generate_batch_short_link(
                    [{"originUrl": "https://shopee.com.br/p"}]
                )


@pytest.mark.asyncio
async def test_business_error_code_11000():
    with _mock_post(_error_body(11000, "business error")):
        async with ShopeeAffiliateClient(app_id="x", secret="y") as client:
            with pytest.raises(ShopeeBusinessError):
                await client.get_product_offer_list()


@pytest.mark.asyncio
async def test_params_error_code_11001():
    with _mock_post(_error_body(11001, "invalid params")):
        async with ShopeeAffiliateClient(app_id="x", secret="y") as client:
            with pytest.raises(ShopeeParamsError):
                await client.generate_short_link(origin_url="bad_url")


@pytest.mark.asyncio
async def test_bind_account_error_code_11002():
    with _mock_post(_error_body(11002, "bind account required")):
        async with ShopeeAffiliateClient(app_id="x", secret="y") as client:
            with pytest.raises(ShopeeBindAccountError):
                await client.list_item_feeds()


@pytest.mark.asyncio
async def test_server_error_5xx_raises_shopee_api_error():
    with _mock_post({}, status_code=500):
        async with ShopeeAffiliateClient(app_id="x", secret="y") as client:
            with pytest.raises(ShopeeAPIError) as exc_info:
                await client.generate_short_link(origin_url="https://shopee.com.br")
    assert "500" in str(exc_info.value)


@pytest.mark.asyncio
async def test_unknown_error_code_raises_shopee_api_error():
    with _mock_post(_error_body(99999, "unexpected error")):
        async with ShopeeAffiliateClient(app_id="x", secret="y") as client:
            with pytest.raises(ShopeeAPIError):
                await client.generate_short_link(origin_url="https://shopee.com.br")


# ---------------------------------------------------------------------------
# --- _dynamic_query helper ---
# ---------------------------------------------------------------------------


def test_dynamic_query_only_includes_provided_vars():
    client = ShopeeAffiliateClient(app_id="a", secret="b")
    var_map = {
        "keyword": "String",
        "shopId": "Int64",
        "listType": "Int",
        "page": "Int",
        "limit": "Int",
    }
    variables = {"page": 1, "limit": 10}  # keyword, shopId, listType NOT provided
    query = client._dynamic_query(
        "query", "productOfferV2", var_map, "nodes { itemId }", variables
    )
    assert "$page: Int" in query
    assert "$limit: Int" in query
    assert "keyword" not in query
    assert "shopId" not in query
    assert "listType" not in query


def test_dynamic_query_includes_all_when_all_provided():
    client = ShopeeAffiliateClient(app_id="a", secret="b")
    var_map = {"keyword": "String", "page": "Int", "limit": "Int"}
    variables = {"keyword": "test", "page": 1, "limit": 5}
    query = client._dynamic_query("query", "testOp", var_map, "nodes { id }", variables)
    assert "$keyword: String" in query
    assert "$page: Int" in query
    assert "$limit: Int" in query
    assert "keyword: $keyword" in query
