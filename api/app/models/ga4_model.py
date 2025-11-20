from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class GA4QueryParams(BaseModel):
    property_id: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    metrics: List[str] = Field(default_factory=lambda: ["activeUsers"])
    dimensions: Optional[List[str]] = None
    limit: int = 1000