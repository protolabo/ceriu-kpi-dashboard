import requests
from datetime import date, datetime, timezone
from typing import Optional
from urllib.parse import quote

from kpi_connectors.auth.oauth import OAuthService

BASE_URL = "https://api.linkedin.com/rest"
LINKEDIN_API_VERSION = "202607"  # format YYYYMM, à mettre à jour périodiquement


def _headers(oauth_service: OAuthService) -> dict:
    return {
        "Authorization": f"Bearer {oauth_service.get_access_token()}",
        "Linkedin-Version": LINKEDIN_API_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }


def _to_epoch_millis(d: date) -> int:
    dt = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def fetch_follower_count(
    oauth_service: OAuthService,
    organization_urn: str,
) -> dict:
    """
    Nombre total de followers (lifetime), via l'endpoint networkSizes.
    Seule source fiable pour le total depuis 2026 : organizationalEntityFollowerStatistics
    ne retourne plus de total agrégé, seulement des ventilations démographiques
    plafonnées au top 100 par facette.
    """
    encoded_urn = quote(organization_urn, safe="")  # encode les ':' en '%3A'
    params = {"edgeType": "COMPANY_FOLLOWED_BY_MEMBER"}
    response = requests.get(
        f"{BASE_URL}/networkSizes/{encoded_urn}",
        headers=_headers(oauth_service),
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    return {
        "organization_urn": organization_urn,
        "follower_count": data.get("firstDegreeSize", 0),
    }


def fetch_share_statistics(
    oauth_service: OAuthService,
    organization_urn: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> dict:
    """
    Statistiques agrégées de toutes les publications (impressions, clics, engagement...).
    Si start_date/end_date sont omis, retourne les stats à vie.
    """
    params = {
        "q": "organizationalEntity",
        "organizationalEntity": organization_urn,
    }

    if start_date and end_date:
        params["timeIntervals"] = (
            f"(timeRange:(start:{_to_epoch_millis(start_date)},"
            f"end:{_to_epoch_millis(end_date)}),timeGranularityType:DAY)"
        )

    response = requests.get(
        f"{BASE_URL}/organizationalEntityShareStatistics",
        headers=_headers(oauth_service),
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    stats: list[dict] = []
    for element in data.get("elements", []):
        totals = element.get("totalShareStatistics", {})
        time_range = element.get("timeRange", {})
        stats.append({
            "start_date": time_range.get("start"),
            "end_date": time_range.get("end"),
            "impressions": totals.get("impressionCount"),
            "unique_impressions": totals.get("uniqueImpressionsCounts"),
            "clicks": totals.get("clickCount"),
            "likes": totals.get("likeCount"),
            "comments": totals.get("commentCount"),
            "shares": totals.get("shareCount"),
            "engagement": totals.get("engagement"),
        })

    return {
        "organization_urn": organization_urn,
        "stats": stats,
    }


def fetch_organization_posts(
    oauth_service: OAuthService,
    organization_urn: str,
    page_size: int = 50,
    max_posts: Optional[int] = None,
) -> list[dict]:
    """
    Liste les posts publiés par l'organisation, avec pagination complète.
    Nécessite le scope r_organization_social (en plus de rw_organization_admin).

    - page_size : nombre de posts par appel HTTP.
    - max_posts : si fourni, arrête la pagination une fois ce nombre atteint.
      Si None, récupère tout l'historique (peut représenter plusieurs milliers
      de posts et donc plusieurs dizaines d'appels HTTP -> prévoir un timeout élevé
      côté appelant).
    """
    posts: list[dict] = []
    start = 0

    while True:
        params = {
            "q": "author",
            "author": organization_urn,
            "count": page_size,
            "start": start,
        }
        response = requests.get(
            f"{BASE_URL}/posts",
            headers=_headers(oauth_service),
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        elements = data.get("elements", [])
        for el in elements:
            posts.append({
                "id": el.get("id"),  # ex: "urn:li:share:1234567890"
                "created_at": el.get("createdAt"),
                "published_at": el.get("publishedAt"),
                "commentary": el.get("commentary"),
                "visibility": el.get("visibility"),
            })

        total = data.get("paging", {}).get("total", len(posts))
        start += len(elements)

        if not elements:
            break
        if start >= total:
            break
        if max_posts is not None and len(posts) >= max_posts:
            posts = posts[:max_posts]
            break

    return posts


def _build_list_param(urns: list[str]) -> str:
    """
    Construit la syntaxe Rest.li List(...) attendue par LinkedIn :
    chaque URN doit avoir ses ':' encodés en '%3A', mais les virgules
    et parenthèses séparant les éléments doivent rester tels quels.
    """
    encoded_urns = ",".join(quote(u, safe="") for u in urns)
    return f"List({encoded_urns})"


def _fetch_stats_batch(
    oauth_service: OAuthService,
    organization_urn: str,
    urns: list[str],
    param_name: str,
    batch_size: int,
) -> list[dict]:
    all_stats: list[dict] = []

    for i in range(0, len(urns), batch_size):
        batch = urns[i:i + batch_size]
        if not batch:
            continue

        list_param = _build_list_param(batch)
        encoded_org_urn = quote(organization_urn, safe="")

        url = (
            f"{BASE_URL}/organizationalEntityShareStatistics"
            f"?q=organizationalEntity"
            f"&organizationalEntity={encoded_org_urn}"
            f"&{param_name}={list_param}"
        )

        response = requests.get(url, headers=_headers(oauth_service), timeout=30)
        response.raise_for_status()
        data = response.json()

        for el in data.get("elements", []):
            totals = el.get("totalShareStatistics", {})
            all_stats.append({
                "share_urn": el.get("share") or el.get("ugcPost"),
                "impressions": totals.get("impressionCount"),
                "unique_impressions": totals.get("uniqueImpressionsCounts"),
                "clicks": totals.get("clickCount"),
                "likes": totals.get("likeCount"),
                "comments": totals.get("commentCount"),
                "shares": totals.get("shareCount"),
                "engagement": totals.get("engagement"),
            })

    return all_stats


def fetch_share_statistics_by_posts(
    oauth_service: OAuthService,
    organization_urn: str,
    share_urns: list[str],
    batch_size: int = 50,
) -> list[dict]:
    """
    Récupère les statistiques individuelles pour une liste de posts.
    Les URN peuvent être de type 'share' ou 'ugcPost' selon comment le post
    a été créé -> il faut les envoyer dans des paramètres séparés
    (shares[] vs ugcPosts[]), LinkedIn rejette un lot qui mélange les deux.
    """
    shares = [u for u in share_urns if u.startswith("urn:li:share:")]
    ugc_posts = [u for u in share_urns if u.startswith("urn:li:ugcPost:")]

    all_stats: list[dict] = []
    all_stats += _fetch_stats_batch(oauth_service, organization_urn, shares, "shares", batch_size)
    all_stats += _fetch_stats_batch(oauth_service, organization_urn, ugc_posts, "ugcPosts", batch_size)

    return all_stats