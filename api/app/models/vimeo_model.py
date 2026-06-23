from typing import List
from pydantic import BaseModel

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