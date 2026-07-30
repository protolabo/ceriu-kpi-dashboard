from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
from datetime import date

from kpi_connectors.auth.oauth import OAuthCredentials, OAuthService
from kpi_connectors.connectors.linkedin import (
    fetch_follower_count,
    fetch_share_statistics,
    fetch_organization_posts,
    fetch_share_statistics_by_posts,
)
from app.endpoints.analytics import parse_oauth_credentials

router = APIRouter(
    prefix="/linkedin",
    tags=["linkedin"],
)


@router.get("/followers")
def get_linkedin_follower_count(
    organization_urn: str = Query(..., description="ex: urn:li:organization:12345678"),
    credentials: OAuthCredentials = Depends(parse_oauth_credentials),
):
    try:
        oauth_service = OAuthService(credentials)
        return fetch_follower_count(oauth_service, organization_urn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/shares")
def get_linkedin_share_stats(
    organization_urn: str = Query(..., description="ex: urn:li:organization:12345678"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    credentials: OAuthCredentials = Depends(parse_oauth_credentials),
):
    try:
        oauth_service = OAuthService(credentials)
        return fetch_share_statistics(oauth_service, organization_urn, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/posts")
def get_linkedin_posts_with_stats(
    organization_urn: str = Query(..., description="ex: urn:li:organization:12345678"),
    max_posts: Optional[int] = Query(None, description="Limite le nombre de posts (None = tout l'historique)"),
    credentials: OAuthCredentials = Depends(parse_oauth_credentials),
):
    try:
        oauth_service = OAuthService(credentials)
        posts = fetch_organization_posts(oauth_service, organization_urn, max_posts=max_posts)
        share_urns = [p["id"] for p in posts if p.get("id")]
        stats = fetch_share_statistics_by_posts(oauth_service, organization_urn, share_urns)

        stats_by_urn = {s["share_urn"]: s for s in stats}
        for post in posts:
            post["stats"] = stats_by_urn.get(post["id"])

        return {"organization_urn": organization_urn, "posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")