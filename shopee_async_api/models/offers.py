from typing import List, Optional

from pydantic import BaseModel

from .base import BaseConnection, PageInfo

# --- Shopee Offer V2 ---


class ShopeeOfferV2(BaseModel):
    commissionRate: str
    imageUrl: str
    offerLink: str
    originalLink: str
    offerName: str
    offerType: int
    categoryId: Optional[int] = None
    collectionId: Optional[int] = None
    periodStartTime: int
    periodEndTime: int


class ShopeeOfferConnectionV2(BaseConnection[ShopeeOfferV2]):
    pass


# --- Shop Offer V2 ---


class Banner(BaseModel):
    fileName: str
    imageUrl: str
    imageSize: int
    imageWidth: int
    imageHeight: int


class BannerInfo(BaseModel):
    count: int
    banners: List[Banner]


class ShopOfferV2(BaseModel):
    commissionRate: str
    imageUrl: str
    offerLink: str
    originalLink: str
    shopId: int
    shopName: str
    ratingStar: Optional[str] = None
    shopType: Optional[List[int]] = None
    remainingBudget: Optional[int] = None
    periodStartTime: int
    periodEndTime: int
    sellerCommCoveRatio: Optional[str] = None
    bannerInfo: Optional[BannerInfo] = None


class ShopOfferConnectionV2(BaseConnection[ShopOfferV2]):
    pass


# --- Product Offer V2 ---


class ProductOfferV2(BaseModel):
    itemId: int
    commissionRate: str
    sellerCommissionRate: Optional[str] = None
    shopeeCommissionRate: Optional[str] = None
    commission: Optional[str] = None
    sales: Optional[int] = None
    priceMax: Optional[str] = None
    priceMin: Optional[str] = None
    productCatIds: Optional[List[int]] = None
    ratingStar: Optional[str] = None
    priceDiscountRate: Optional[int] = None
    imageUrl: str
    productName: str
    shopId: Optional[int] = None
    shopName: str
    shopType: Optional[List[int]] = None
    productLink: str
    offerLink: str
    periodStartTime: int
    periodEndTime: int


class ProductOfferConnectionV2(BaseConnection[ProductOfferV2]):
    pass
