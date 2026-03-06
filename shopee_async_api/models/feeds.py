from typing import Optional, List
from pydantic import BaseModel


class ItemFeed(BaseModel):
    datafeedId: str
    referenceId: str
    datafeedName: str
    description: str
    totalCount: int
    date: str
    feedMode: str  # "FULL" | "DELTA"


class ItemFeedListConnection(BaseModel):
    feeds: List[ItemFeed]


class ItemFeedDataRow(BaseModel):
    columns: str
    updateType: Optional[str] = None  # "UNKNOWN" | "NEW" | "UPDATE" | "DELETE"


class ItemFeedPageInfo(BaseModel):
    offset: int
    limit: int
    totalCount: int
    hasMore: bool


class ItemFeedDataConnection(BaseModel):
    rows: List[ItemFeedDataRow]
    pageInfo: ItemFeedPageInfo
