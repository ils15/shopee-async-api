from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field

T = TypeVar('T')

class PageInfo(BaseModel):
    page: Optional[int] = None
    limit: int
    hasNextPage: bool
    scrollId: Optional[str] = None

class BaseConnection(BaseModel, Generic[T]):
    nodes: List[T]
    pageInfo: PageInfo

class GraphQLErrorLocation(BaseModel):
    line: int
    column: int

class GraphQLError(BaseModel):
    message: str
    locations: Optional[List[GraphQLErrorLocation]] = None
    path: Optional[List[str]] = None
    extensions: Optional[Dict[str, Any]] = None

class GraphQLResponse(BaseModel, Generic[T]):
    data: Optional[Dict[str, T]] = None
    errors: Optional[List[GraphQLError]] = None
