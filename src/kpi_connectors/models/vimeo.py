from typing import List
from pydantic import BaseModel
from typing import Optional


class VimeoVideo(BaseModel):
    id: str
    name: str | None = None 
    duration: int | None = None
    created_time: str | None = None
    link: str | None = None
    plays: int | None = None

class VimeoVideosResponse(BaseModel):
    total_videos: int
    videos: List[VimeoVideo]


class VimeoQueryParams(BaseModel):
    per_page: int = 100
    sort: Optional[str] = None        # "date", "plays", "alphabetical", "duration"
    direction: Optional[str] = None   # "asc" ou "desc"
    query: Optional[str] = None       # recherche sur le nom