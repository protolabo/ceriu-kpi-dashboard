from fastapi import HTTPException

from app.config.settings import settings
from app.models.vimeo_model import VimeoVideo, VimeoVideosResponse
from scripts_api.vimeo import fetch_vimeo_videos

def get_vimeo_videos() -> VimeoVideosResponse:
    access_token = settings.VIMEO_ACCESS_TOKEN
    if not access_token:
        raise HTTPException(
            status_code=500,
            detail="VIMEO_ACCESS_TOKEN n'est pas configurée sur le serveur.",
        )
    
    try:
        raw = fetch_vimeo_videos(access_token)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Erreur lors de l'appel à l'API Vimeo: {e}",
        )
    
    videos = [VimeoVideo(**v) for v in raw]

    return VimeoVideosResponse(
        total_videos=len(videos),
        videos=videos,
    )
