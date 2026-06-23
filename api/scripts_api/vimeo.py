import requests

base_url = "https://api.vimeo.com"

def fetch_vimeo_videos(access_token : str) -> list[dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.vimeo.*+json;version=3.4",
    }

    # demande que le necessaire (allege la reponse)
    params = {
        "fields": "uri,name,duration,created_time,link,stats.plays",
        "per_page": 100, # max autorise par vimeo
    }

    videos: list[dict] = []
    url = base_url + "/me/videos"

    while url:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        for v in data.get("data", []):
            stats = v.get("stats") or {}
            uri = v.get("uri", "")
            videos.append(
                {
                    "id": uri.split("/")[-1], # "/videos/123" devient "123"
                    "name": v.get("name"),
                    "duration": v.get("duration"),
                    "created_time": v.get("created_time"),
                    "link": v.get("link"),
                    "plays": stats.get("plays"),
                }
            )
    
        next_path = (data.get("paging") or {}).get("next")
        url = (base_url + next_path) if next_path else None
        params = None # reinitialise puisque deja encode dans next_path

    return videos