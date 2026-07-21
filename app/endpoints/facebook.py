from fastapi import APIRouter, Header, HTTPException, Query
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.exceptions import FacebookRequestError
from typing import List
from datetime import date, timedelta
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


router = APIRouter(prefix="/facebook", tags=["facebook"])

DEFAULT_METRICS = [
    "page_post_engagements",
    "page_follows",
    "page_total_media_view_unique",
    "page_views_total",
]

@router.get("/page-insights")
def get_page_insights(
    page_id: str = Query(...),
    metric: List[str] = Query(DEFAULT_METRICS),
    period: str = Query("day"),
    since: date = Query(default_factory=lambda: date.today() - timedelta(days=90)),
    until: date = Query(default_factory=date.today),
    x_facebook_page_access_token: str = Header(...),
):
    try:
        FacebookAdsApi.init(access_token=x_facebook_page_access_token)
        page = Page(page_id)
        insights = page.get_insights(params={
            "metric": metric,
            "period": period,
            "since": since.isoformat(),
            "until": until.isoformat(),
        })
        return [i.export_all_data() for i in insights]
    except FacebookRequestError as e:
        raise HTTPException(status_code=400, detail=f"Facebook API error: {e.api_error_message()}")
    
DEFAULT_POST_METRICS = [
    "post_reactions_like_total",
    "post_reactions_love_total",
    "post_total_media_view_unique",
    "post_clicks",
]
GRAPH_API_VERSION = "v25.0"

@router.get("/posts-insights")
def get_posts_with_insights(
    page_id: str = Query(...),
    limit: int = Query(25),
    x_facebook_page_access_token: str = Header(...),
):
    try:
        FacebookAdsApi.init(access_token=x_facebook_page_access_token)
        page = Page(page_id)
        posts = list(page.get_posts(
            fields=["id", "message", "created_time", "shares"],
            params={"limit": limit},
        ))

        def fetch_insights(post):
            try:
                insights = post.get_insights(params={"metric": DEFAULT_POST_METRICS})
                values = {i["name"]: i["values"][0]["value"] for i in insights}
            except FacebookRequestError:
                values = {}
            return post, values

        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_insights, post) for post in posts]
            for future in as_completed(futures):
                post, values = future.result()
                results.append({
                    "post_id": post["id"],
                    "message": post.get("message", ""),
                    "created_time": post.get("created_time"),
                    "likes_total": values.get("post_reactions_like_total", 0),
                    "love_total": values.get("post_reactions_love_total", 0),
                    "views_unique": values.get("post_total_media_view_unique", 0),
                    "clicks": values.get("post_clicks", 0),
                    "shares_count": (post.get("shares") or {}).get("count", 0),
                })
        return {"total_posts": len(results), "posts": results}
    except FacebookRequestError as e:
        raise HTTPException(status_code=400, detail=f"Facebook API error: {e.api_error_message()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")