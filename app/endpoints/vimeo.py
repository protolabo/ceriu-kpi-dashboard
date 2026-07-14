from fastapi import APIRouter, Query
from typing import Optional

from app.config.settings import settings
from kpi_connectors.models.vimeo import VimeoVideosResponse, VimeoQueryParams
from kpi_connectors.connectors.vimeo import fetch_vimeo_videos

router = APIRouter(prefix="/vimeo", tags=["vimeo"])

@router.get("/videos", response_model=VimeoVideosResponse)
def list_vimeo_videos(
    per_page: int = Query(100, ge=1, le=100, description="Vidéos par page (1-100)"),
    sort: Optional[str] = Query(None, description="date, plays, alphabetical, duration"),
    direction: Optional[str] = Query(None, description="asc ou desc"),
    query: Optional[str] = Query(None, description="Recherche sur le nom"),
):
    params = VimeoQueryParams(per_page=per_page, sort=sort, direction=direction, query=query)
    videos = fetch_vimeo_videos(access_token=settings.VIMEO_ACCESS_TOKEN, params=params)
    return VimeoVideosResponse(total_videos=len(videos), videos=videos)