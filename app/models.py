# Pydantic models for data validation 
from pydantic import BaseModel
from typing import Optional, List

class LegoSet(BaseModel):
    set_id: str
    name: str
    theme: str
    piece_count: int
    price: Optional[float]
    release_year: Optional[int]
    description: Optional[str]

class SearchResult(BaseModel):
    sets: List[LegoSet]
    ai_response: Optional[str]