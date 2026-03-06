from typing import Optional, List
from pydantic import BaseModel

class GenerateShortLinkInput(BaseModel):
    originUrl: str
    subIds: Optional[List[str]] = None

class ShortLinkResult(BaseModel):
    shortLink: str
    longLink: str = ""

class BatchShortLinkItemResult(BaseModel):
    originUrl: str
    shortLink: str
    longLink: str
    success: bool
    errorMessage: Optional[str] = None

class BatchShortLinkResult(BaseModel):
    links: List[BatchShortLinkItemResult]
    total: int
    successCount: int
