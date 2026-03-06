import json
import httpx
from typing import Optional, Dict, Any, List

from .auth import get_auth_headers
from .exceptions import handle_api_error, ShopeeAPIError
from .models import (
    GraphQLResponse,
    GenerateShortLinkInput,
    ShortLinkResult,
    BatchShortLinkResult,
    ShopeeOfferConnectionV2,
    ShopOfferConnectionV2,
    ProductOfferConnectionV2,
    ConversionReportConnection,
    ValidatedReportConnection,
    PartnerOrderReportConnection,
    ItemFeedListConnection,
    ItemFeedDataConnection,
)

class ShopeeAffiliateClient:
    """
    Asynchronous client for the Shopee Affiliate Open API (GraphQL).
    """
    BASE_URL = "https://open-api.affiliate.shopee.com.br/graphql"

    @staticmethod
    def _dynamic_query(
        op_type: str,
        name: str,
        var_type_map: Dict[str, str],
        return_fields: str,
        variables: Dict[str, Any],
    ) -> str:
        """
        Build a GraphQL query/mutation that only declares the variables actually
        provided.  This avoids Shopee's "got null for non-null" error (code 10010)
        for parameters that are non-null internally but optional in the schema
        (e.g. listType, shopType).
        """
        active = [(k, var_type_map[k]) for k in variables if k in var_type_map]
        decl = ", ".join(f"${k}: {t}" for k, t in active)
        args = ", ".join(f"{k}: ${k}" for k, _ in active)
        header = f"{op_type} {name}({decl})" if decl else f"{op_type} {name}"
        return f"{header} {{ {name}({args}) {{ {return_fields} }} }}"

    def __init__(self, app_id: str, secret: str, timeout: int = 30):
        self.app_id = app_id
        self.secret = secret
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def _request(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a GraphQL query/mutation with proper authentication headers.
        """
        if not self._client:
            self._client = httpx.AsyncClient(timeout=self.timeout)

        payload_dict = {"query": query}
        if variables:
            payload_dict["variables"] = variables
            
        # Shopee requires the payload to be exactly matching the one signed.
        # Ensure separators don't have spaces to match the most compact JSON string if that was intended,
        # but json.dumps defaults space separating. We will stick to the tightest representation.
        payload = json.dumps(payload_dict, separators=(',', ':'))
        
        headers = get_auth_headers(self.app_id, self.secret, payload)

        response = await self._client.post(self.BASE_URL, headers=headers, content=payload)
        
        if response.status_code >= 500:
            raise ShopeeAPIError(f"Server Error {response.status_code}: {response.text}")

        data = response.json()
        
        # Depending on how shopee wraps errors, sometimes there are HTTP 200 with error codes inside extensions
        if "errors" in data and len(data["errors"]) > 0:
            err = data["errors"][0]
            extensions = err.get("extensions", {})
            error_code = extensions.get("code", -1)
            error_message = err.get("message", "Unknown GraphQL Error")
            if error_code != -1:
                handle_api_error(error_code, error_message)
            else:
                # Direct GraphQL error without custom Shopee extension code
                raise ShopeeAPIError(f"GraphQL Error: {error_message}")
                
        return data.get("data", {})

    # --- Endpoints ---

    async def generate_short_link(self, origin_url: str, sub_ids: Optional[List[str]] = None) -> ShortLinkResult:
        query = """
        mutation generateShortLink($originUrl: String!, $subIds: [String!]) {
            generateShortLink(input: {originUrl: $originUrl, subIds: $subIds}) {
                shortLink
            }
        }
        """
        variables = {"originUrl": origin_url}
        if sub_ids is not None:
            variables["subIds"] = sub_ids

        data = await self._request(query, variables)
        return ShortLinkResult(**data.get("generateShortLink", {}))

    async def get_shopee_offer_list(
        self, keyword: Optional[str] = None, sortType: int = 1, page: int = 1, limit: int = 10
    ) -> ShopeeOfferConnectionV2:
        query = """
        query shopeeOfferV2($keyword: String, $sortType: Int, $page: Int, $limit: Int) {
            shopeeOfferV2(keyword: $keyword, sortType: $sortType, page: $page, limit: $limit) {
                nodes {
                    commissionRate
                    imageUrl
                    offerLink
                    originalLink
                    offerName
                    offerType
                    categoryId
                    collectionId
                    periodStartTime
                    periodEndTime
                }
                pageInfo {
                    page
                    limit
                    hasNextPage
                }
            }
        }
        """
        variables = {"sortType": sortType, "page": page, "limit": limit}
        if keyword:
            variables["keyword"] = keyword

        data = await self._request(query, variables)
        return ShopeeOfferConnectionV2(**data.get("shopeeOfferV2", {}))

    async def get_shop_offer_list(
        self, 
        page: int = 1, 
        limit: int = 10,
        keyword: Optional[str] = None, 
        shopId: Optional[int] = None,
        sortType: int = 1,
        shopType: Optional[List[int]] = None,
        isKeySeller: Optional[bool] = None,
        sellerCommCoveRatio: Optional[str] = None
    ) -> ShopOfferConnectionV2:
        _VAR_TYPES = {
            "keyword": "String", "shopId": "Int64", "sortType": "Int",
            "shopType": "[Int]", "isKeySeller": "Boolean",
            "sellerCommCoveRatio": "String", "page": "Int", "limit": "Int",
        }
        _RETURN_FIELDS = """nodes {
                    commissionRate imageUrl offerLink originalLink shopId shopName
                    ratingStar shopType remainingBudget periodStartTime periodEndTime
                    sellerCommCoveRatio
                    bannerInfo { count banners { fileName imageUrl imageSize imageWidth imageHeight } }
                }
                pageInfo { page limit hasNextPage }"""
        variables = {k: v for k, v in locals().items() if v is not None and k not in ("self", "_VAR_TYPES", "_RETURN_FIELDS")}
        query = self._dynamic_query("query", "shopOfferV2", _VAR_TYPES, _RETURN_FIELDS, variables)
        data = await self._request(query, variables)
        return ShopOfferConnectionV2(**data.get("shopOfferV2", {}))

    async def get_product_offer_list(
        self, 
        page: int = 1, 
        limit: int = 10,
        keyword: Optional[str] = None,
        shopId: Optional[int] = None,
        itemId: Optional[int] = None,
        productCatId: Optional[int] = None,
        listType: Optional[int] = None,
        matchId: Optional[int] = None,
        sortType: Optional[int] = None,
        isAMSOffer: Optional[bool] = None,
        isKeySeller: Optional[bool] = None
    ) -> ProductOfferConnectionV2:
        _VAR_TYPES = {
            "keyword": "String", "shopId": "Int64", "itemId": "Int64",
            "productCatId": "Int", "listType": "Int", "matchId": "Int64",
            "sortType": "Int", "isAMSOffer": "Boolean", "isKeySeller": "Boolean",
            "page": "Int", "limit": "Int",
        }
        _RETURN_FIELDS = """nodes {
                    itemId commissionRate sellerCommissionRate shopeeCommissionRate
                    commission sales priceMax priceMin productCatIds ratingStar
                    priceDiscountRate imageUrl productName shopId shopName shopType
                    productLink offerLink periodStartTime periodEndTime
                }
                pageInfo { page limit hasNextPage }"""
        variables = {k: v for k, v in locals().items() if v is not None and k not in ("self", "_VAR_TYPES", "_RETURN_FIELDS")}
        query = self._dynamic_query("query", "productOfferV2", _VAR_TYPES, _RETURN_FIELDS, variables)
        data = await self._request(query, variables)
        return ProductOfferConnectionV2(**data.get("productOfferV2", {}))

    async def get_conversion_report(
        self,
        purchaseTimeStart: Optional[int] = None,
        purchaseTimeEnd: Optional[int] = None,
        completeTimeStart: Optional[int] = None,
        completeTimeEnd: Optional[int] = None,
        shopName: Optional[str] = None,
        shopId: Optional[int] = None,
        shopType: Optional[List[str]] = None,
        conversionId: Optional[int] = None,
        orderId: Optional[str] = None,
        productName: Optional[str] = None,
        productId: Optional[int] = None,
        categoryLv1Id: Optional[int] = None,
        categoryLv2Id: Optional[int] = None,
        categoryLv3Id: Optional[int] = None,
        orderStatus: Optional[str] = None,
        buyerType: Optional[str] = None,
        attributionType: Optional[str] = None,
        device: Optional[str] = None,
        fraudStatus: Optional[str] = None,
        campaignPartnerName: Optional[str] = None,
        campaignType: Optional[str] = None,
        limit: int = 500,
        scrollId: Optional[str] = None
    ) -> ConversionReportConnection:
        query = """
        query conversionReport($purchaseTimeStart: Int, $purchaseTimeEnd: Int, $completeTimeStart: Int, $completeTimeEnd: Int, $shopName: String, $shopId: Int64, $shopType: [String], $conversionId: Int64, $orderId: String, $productName: String, $productId: Int64, $categoryLv1Id: Int64, $categoryLv2Id: Int64, $categoryLv3Id: Int64, $orderStatus: String, $buyerType: String, $attributionType: String, $device: String, $fraudStatus: String, $campaignPartnerName: String, $campaignType: String, $limit: Int, $scrollId: String) {
            conversionReport(purchaseTimeStart: $purchaseTimeStart, purchaseTimeEnd: $purchaseTimeEnd, completeTimeStart: $completeTimeStart, completeTimeEnd: $completeTimeEnd, shopName: $shopName, shopId: $shopId, shopType: $shopType, conversionId: $conversionId, orderId: $orderId, productName: $productName, productId: $productId, categoryLv1Id: $categoryLv1Id, categoryLv2Id: $categoryLv2Id, categoryLv3Id: $categoryLv3Id, orderStatus: $orderStatus, buyerType: $buyerType, attributionType: $attributionType, device: $device, fraudStatus: $fraudStatus, campaignPartnerName: $campaignPartnerName, campaignType: $campaignType, limit: $limit, scrollId: $scrollId) {
                nodes {
                    purchaseTime
                    clickTime
                    conversionId
                    shopeeCommissionCapped
                    sellerCommission
                    totalCommission
                    buyerType
                    utmContent
                    device
                    referrer
                    orders {
                        orderId
                        orderStatus
                        shopType
                        items {
                            shopId
                            shopName
                            completeTime
                            itemId
                            itemName
                            itemPrice
                            displayItemStatus
                            actualAmount
                            qty
                            imageUrl
                            itemTotalCommission
                            itemSellerCommission
                            itemSellerCommissionRate
                            itemShopeeCommissionCapped
                            itemShopeeCommissionRate
                            itemNotes
                            channelType
                            attributionType
                            globalCategoryLv1Name
                            globalCategoryLv2Name
                            globalCategoryLv3Name
                            fraudStatus
                            modelId
                            promotionId
                            campaignPartnerName
                            campaignType
                        }
                    }
                    linkedMcnName
                    mcnContractId
                    mcnManagementFeeRate
                    mcnManagementFee
                    netCommission
                    campaignType
                }
                pageInfo {
                    limit
                    hasNextPage
                    scrollId
                }
            }
        }
        """
        variables = {k: v for k, v in locals().items() if v is not None and k not in ("self", "query")}
        data = await self._request(query, variables)
        return ConversionReportConnection(**data.get("conversionReport", {}))

    async def get_validated_report(
        self,
        validationId: int,
        limit: int = 20,
        scrollId: Optional[str] = None,
    ) -> ValidatedReportConnection:
        query = """
        query validatedReport($validationId: Int64!, $limit: Int, $scrollId: String) {
            validatedReport(validationId: $validationId, limit: $limit, scrollId: $scrollId) {
                nodes {
                    clickTime
                    purchaseTime
                    conversionId
                    shopeeCommissionCapped
                    sellerCommission
                    totalCommission
                    buyerType
                    utmContent
                    device
                    productType
                    referrer
                    netCommission
                    mcnManagementFeeRate
                    mcnManagementFee
                    mcnContractId
                    linkedMcnName
                    orders {
                        orderId
                        shopType
                        orderStatus
                        items {
                            shopId
                            shopName
                            completeTime
                            promotionId
                            modelId
                            itemId
                            itemName
                            itemPrice
                            displayItemStatus
                            actualAmount
                            refundAmount
                            qty
                            imageUrl
                            itemTotalCommission
                            itemSellerCommission
                            itemSellerCommissionRate
                            itemShopeeCommissionCapped
                            itemShopeeCommissionRate
                            itemNotes
                            globalCategoryLv1Name
                            globalCategoryLv2Name
                            globalCategoryLv3Name
                            fraudStatus
                            fraudReason
                            attributionType
                            channelType
                            campaignPartnerName
                            campaignType
                        }
                    }
                }
                pageInfo {
                    limit
                    hasNextPage
                    scrollId
                }
            }
        }
        """
        variables: Dict[str, Any] = {"validationId": validationId, "limit": limit}
        if scrollId is not None:
            variables["scrollId"] = scrollId
        data = await self._request(query, variables)
        return ValidatedReportConnection(**data.get("validatedReport", {}))

    async def get_partner_order_report(
        self,
        purchaseTimeStart: Optional[int] = None,
        purchaseTimeEnd: Optional[int] = None,
        completeTimeStart: Optional[int] = None,
        completeTimeEnd: Optional[int] = None,
        limit: int = 500,
        searchNextToken: Optional[str] = None,
    ) -> PartnerOrderReportConnection:
        """
        Note: This endpoint requires MCN/partner-level access in Shopee.
        Int64 timestamp arguments are serialised as strings per the API contract.
        """
        query = """
        query partnerOrderReport($purchaseTimeStart: Int64, $purchaseTimeEnd: Int64, $completeTimeStart: Int64, $completeTimeEnd: Int64, $limit: Int, $searchNextToken: String) {
            partnerOrderReport(purchaseTimeStart: $purchaseTimeStart, purchaseTimeEnd: $purchaseTimeEnd, completeTimeStart: $completeTimeStart, completeTimeEnd: $completeTimeEnd, limit: $limit, searchNextToken: $searchNextToken) {
                nodes {
                    orderId
                    purchaseTime
                    completeTime
                    orderStatus
                    buyerType
                    shopId
                    shopName
                    productType
                    items {
                        itemId
                        itemName
                        categoryLv1Name
                        categoryLv2Name
                        categoryLv3Name
                        itemPrice
                        qty
                        actualAmount
                        refundAmount
                    }
                    extInfo {
                        clickId
                        videoId
                        userType
                    }
                }
                searchNextPageInfo {
                    size
                    limit
                    searchNextToken
                    debugId
                }
            }
        }
        """
        # Shopee's Int64 custom scalar must be sent as a JSON string
        variables: Dict[str, Any] = {"limit": limit}
        if purchaseTimeStart is not None:
            variables["purchaseTimeStart"] = str(purchaseTimeStart)
        if purchaseTimeEnd is not None:
            variables["purchaseTimeEnd"] = str(purchaseTimeEnd)
        if completeTimeStart is not None:
            variables["completeTimeStart"] = str(completeTimeStart)
        if completeTimeEnd is not None:
            variables["completeTimeEnd"] = str(completeTimeEnd)
        if searchNextToken is not None:
            variables["searchNextToken"] = searchNextToken
        data = await self._request(query, variables)
        return PartnerOrderReportConnection(**data.get("partnerOrderReport", {}))

    async def list_item_feeds(
        self,
        feedMode: Optional[str] = None,
    ) -> ItemFeedListConnection:
        query = """
        query listItemFeeds($feedMode: FeedMode) {
            listItemFeeds(feedMode: $feedMode) {
                feeds {
                    datafeedId
                    referenceId
                    datafeedName
                    description
                    totalCount
                    date
                    feedMode
                }
            }
        }
        """
        variables: Dict[str, Any] = {}
        if feedMode is not None:
            variables["feedMode"] = feedMode
        data = await self._request(query, variables)
        return ItemFeedListConnection(**data.get("listItemFeeds", {}))

    async def get_item_feed_data(
        self,
        datafeedId: str,
        offset: int = 0,
        limit: int = 500,
    ) -> ItemFeedDataConnection:
        query = """
        query getItemFeedData($datafeedId: String!, $offset: Int, $limit: Int) {
            getItemFeedData(datafeedId: $datafeedId, offset: $offset, limit: $limit) {
                rows {
                    columns
                    updateType
                }
                pageInfo {
                    offset
                    limit
                    totalCount
                    hasMore
                }
            }
        }
        """
        variables: Dict[str, Any] = {"datafeedId": datafeedId, "offset": offset, "limit": limit}
        data = await self._request(query, variables)
        return ItemFeedDataConnection(**data.get("getItemFeedData", {}))

    async def generate_batch_short_link(
        self,
        links: List[Dict[str, Any]],
    ) -> BatchShortLinkResult:
        """
        Generate multiple affiliate short links in a single request.

        :param links: List of dicts with keys ``originUrl`` (str, required) and
                      ``subIds`` (list[str], optional).
        """
        query = """
        mutation generateBatchShortLink($input: BatchShortLinkInput!) {
            generateBatchShortLink(input: $input) {
                links {
                    originUrl
                    shortLink
                    longLink
                    success
                    errorMessage
                }
                total
                successCount
            }
        }
        """
        variables: Dict[str, Any] = {"input": {"links": links}}
        data = await self._request(query, variables)
        return BatchShortLinkResult(**data.get("generateBatchShortLink", {}))
