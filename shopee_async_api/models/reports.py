from typing import Optional, List
from pydantic import BaseModel
from .base import PageInfo, BaseConnection

# --- Validated Report ---

class ValidatedReportOrderItem(BaseModel):
    shopId: int
    shopName: str
    completeTime: int
    promotionId: str
    modelId: int
    itemId: int
    itemName: str
    itemPrice: str
    displayItemStatus: str
    actualAmount: str
    refundAmount: str
    qty: int
    imageUrl: str
    itemTotalCommission: str
    itemSellerCommission: str
    itemSellerCommissionRate: str
    itemShopeeCommissionCapped: str
    itemShopeeCommissionRate: str
    itemNotes: str
    globalCategoryLv1Name: Optional[str] = None
    globalCategoryLv2Name: Optional[str] = None
    globalCategoryLv3Name: Optional[str] = None
    fraudStatus: str
    fraudReason: str
    attributionType: str
    channelType: str
    campaignPartnerName: str
    campaignType: str

class ValidatedReportOrder(BaseModel):
    orderId: str
    shopType: Optional[str] = None
    orderStatus: Optional[str] = None
    items: List[ValidatedReportOrderItem]

class ValidatedReport(BaseModel):
    clickTime: int
    purchaseTime: int
    conversionId: int
    shopeeCommissionCapped: str
    sellerCommission: str
    totalCommission: str
    buyerType: str
    utmContent: str
    device: str
    productType: str
    referrer: str
    netCommission: str
    mcnManagementFeeRate: str
    mcnManagementFee: str
    mcnContractId: int
    linkedMcnName: str
    orders: List[ValidatedReportOrder]

class ValidatedReportConnection(BaseConnection[ValidatedReport]):
    pass

# --- Partner Order Report ---

class PartnerReportOrderItem(BaseModel):
    itemId: int
    itemName: str
    categoryLv1Name: Optional[str] = None
    categoryLv2Name: Optional[str] = None
    categoryLv3Name: Optional[str] = None
    itemPrice: str
    qty: int
    actualAmount: str
    refundAmount: str

class ExtInfo(BaseModel):
    clickId: Optional[str] = None
    videoId: Optional[str] = None
    userType: Optional[str] = None

class PartnerOrder(BaseModel):
    orderId: int
    purchaseTime: int
    completeTime: int
    orderStatus: str
    buyerType: str
    shopId: int
    shopName: str
    productType: str
    items: List[PartnerReportOrderItem]
    extInfo: Optional[ExtInfo] = None

class SearchNextPageInfo(BaseModel):
    size: int
    limit: int
    searchNextToken: Optional[str] = None
    debugId: Optional[str] = None

class PartnerOrderReportConnection(BaseModel):
    nodes: List[PartnerOrder]
    searchNextPageInfo: SearchNextPageInfo

# --- Conversion Report ---

class ConversionReportOrderItem(BaseModel):
    shopId: Optional[int] = None
    shopName: Optional[str] = None
    completeTime: Optional[int] = None
    itemId: int
    itemName: str
    itemPrice: str
    displayItemStatus: Optional[str] = None
    actualAmount: Optional[str] = None
    qty: int
    imageUrl: Optional[str] = None
    itemTotalCommission: Optional[str] = None
    itemSellerCommission: Optional[str] = None
    itemSellerCommissionRate: Optional[str] = None
    itemShopeeCommissionCapped: Optional[str] = None
    itemShopeeCommissionRate: Optional[str] = None
    itemNotes: Optional[str] = None
    channelType: Optional[str] = None
    attributionType: Optional[str] = None
    globalCategoryLv1Name: Optional[str] = None
    globalCategoryLv2Name: Optional[str] = None
    globalCategoryLv3Name: Optional[str] = None
    fraudStatus: Optional[str] = None
    modelId: Optional[int] = None
    promotionId: Optional[str] = None
    campaignPartnerName: Optional[str] = None
    campaignType: Optional[str] = None

class ConversionReportOrder(BaseModel):
    orderId: str
    orderStatus: str
    shopType: Optional[str] = None
    items: List[ConversionReportOrderItem]

class ConversionReport(BaseModel):
    purchaseTime: int
    clickTime: Optional[int] = None
    conversionId: int
    shopeeCommissionCapped: Optional[str] = None
    sellerCommission: Optional[str] = None
    totalCommission: Optional[str] = None
    buyerType: Optional[str] = None
    utmContent: Optional[str] = None
    device: Optional[str] = None
    referrer: Optional[str] = None
    orders: List[ConversionReportOrder]
    linkedMcnName: Optional[str] = None
    mcnContractId: Optional[int] = None
    mcnManagementFeeRate: Optional[str] = None
    mcnManagementFee: Optional[str] = None
    netCommission: Optional[str] = None
    campaignType: Optional[str] = None

class ConversionReportConnection(BaseConnection[ConversionReport]):
    pass
