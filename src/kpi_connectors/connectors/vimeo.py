import requests
from kpi_connectors.models.vimeo import VimeoQueryParams

base_url = "https://api.vimeo.com"

def fetch_vimeo_videos(access_token: str, params: VimeoQueryParams | None = None) -> list[dict]:
    params = params or VimeoQueryParams()   # défauts si rien n'est fourni

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.vimeo.*+json;version=3.4",
    }

    # fields reste fixe (alimente des visuels précis) ; le reste vient des params
    query = {
        "fields": "uri,name,duration,created_time,link,stats.plays",
        "per_page": params.per_page,
    }
    if params.sort:
        query["sort"] = params.sort
    if params.direction:
        query["direction"] = params.direction
    if params.query:
        query["query"] = params.query

    videos: list[dict] = []
    url = base_url + "/me/videos"

    while url:
        response = requests.get(url, headers=headers, params=query, timeout=30)
        response.raise_for_status()
        data = response.json()

        for v in data.get("data", []):
            stats = v.get("stats") or {}
            uri = v.get("uri", "")
            videos.append({
                "id": uri.split("/")[-1],
                "name": v.get("name"),
                "duration": v.get("duration"),
                "created_time": v.get("created_time"),
                "link": v.get("link"),
                "plays": stats.get("plays"),
            })

        next_path = (data.get("paging") or {}).get("next")
        url = (base_url + next_path) if next_path else None
        query = None   # déjà encodé dans next_path

    return videos

def fetch_vimeo_follower_count(access_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.vimeo.*+json;version=3.4",
    }
    params = {"fields": "uri,name,metadata.connections.followers.total"}

    response = requests.get(
        f"{base_url}/me",
        headers=headers,
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    followers = (
        data.get("metadata", {})
        .get("connections", {})
        .get("followers", {})
        .get("total", 0)
    )

    return {
        "follower_count": followers,
    }