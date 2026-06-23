from fastapi import APIRouter

from app.models.vimeo_model import VimeoVideosResponse
from app.services.vimeo_service import get_vimeo_videos

router = APIRouter(
    prefix="/vimeo",
    tags=["vimeo"],
)

@router.get("/videos", response_model=VimeoVideosResponse)
def list_vimeo_videos():
    return get_vimeo_videos()