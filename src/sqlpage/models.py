from typing import List, TypeVar, Generic

from pydantic import BaseModel

T = TypeVar('T')

class PageData(BaseModel, Generic[T]):
    items: List[T]
    next_page_token: str
    total_items: int


class PageToken(BaseModel):
    total_count: int
    page_size: int
    remaining: int
    page_num: int
    offset: int
    elements_fetched: int
