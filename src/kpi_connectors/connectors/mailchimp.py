import requests
from kpi_connectors.models.mailchimp import MailchimpCampaignParams


def fetch_mailchimp_audiences(api_key: str) -> dict:
    # Construit l'URL d'API à partir du data center
    data_center = api_key.split("-")[-1]
    base_url = "https://"+ data_center + ".api.mailchimp.com/3.0/"
    auth = ("", api_key)

    # Appel /lists pour récupérer les audiences
    params = {
        "count": 1000,
        "fields": "lists.id,lists.name,lists.stats.member_count",  
    }
    response = requests.get(base_url + "lists", params=params, auth=auth, timeout=30)
    response.raise_for_status()

    data = response.json()
    audience_list = data.get("lists", [])

    # On additionne member_count pour avoir le total
    subscriber_total = 0
    audiences: list[dict] = []
    for audience in audience_list:
        stats = audience.get("stats", {})
        count = stats.get("member_count", 0)
        subscriber_total += count
        audiences.append(
            {
                "id": audience.get("id"),
                "name": audience.get("name", ""),
                "member_count": count,
            }
        )

    return {
        "total_subscribers": subscriber_total,
        "audiences": audiences,
    }

def fetch_mailchimp_campaign_summaries(
    api_key: str,
    params: MailchimpCampaignParams,
) -> list[dict]:
    data_center = api_key.split("-")[-1]
    base_url = f"https://{data_center}.api.mailchimp.com/3.0/"
    auth = ("", api_key)

    campaigns_params = {
        "status": params.status,
        "count": params.count,
        "fields": (
            "reports.id,"
            "reports.campaign_title,"
            "reports.list_id,"
            "reports.send_time,"
            "reports.emails_sent,"
            "reports.opens.opens_total,"
            "reports.opens.open_rate,"
            "reports.opens.unique_opens,"
            "reports.clicks.clicks_total,"
            "reports.clicks.click_rate,"
            "reports.clicks.unique_clicks,"
            "reports.bounces.hard_bounces,"
            "reports.bounces.soft_bounces"
        ),
    }
    if params.since_send_time:
        campaigns_params["since_send_time"] = params.since_send_time
    if params.before_send_time:
        campaigns_params["before_send_time"] = params.before_send_time

    resp = requests.get(base_url + "reports", params=campaigns_params, auth=auth, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    reports = data.get("reports", [])

    summaries: list[dict] = []
    for r in reports:
        opens = r.get("opens") or {}
        clicks = r.get("clicks") or {}
        bounces = r.get("bounces") or {}

        summaries.append(
            {
                "id": r.get("id"),
                "name": r.get("campaign_title"),
                "list_id": r.get("list_id"),
                "send_time": r.get("send_time"),
                "emails_sent": r.get("emails_sent"),
                "open_rate": opens.get("open_rate"),
                "opens_total": opens.get("opens_total"),
                "unique_opens": opens.get("unique_opens"),
                "click_rate": clicks.get("click_rate"),
                "clicks_total": clicks.get("clicks_total"),
                "unique_clicks": clicks.get("unique_clicks"),
                "hard_bounces": bounces.get("hard_bounces"),
                "soft_bounces": bounces.get("soft_bounces"),
            }
        )
    return summaries


def fetch_mailchimp_click_details(
    api_key: str,
    campaign_id: str | None = None,
    count: int = 1000,
) -> list[dict]:
    data_center = api_key.split("-")[-1]
    base_url = f"https://{data_center}.api.mailchimp.com/3.0/"
    auth = ("", api_key)

    if campaign_id:
        campaign_ids = [campaign_id]
    else:
        campaigns_params = {"status": "sent", "count": count, "fields": "reports.id"}
        resp = requests.get(base_url + "reports", params=campaigns_params, auth=auth, timeout=30)
        resp.raise_for_status()
        campaign_ids = [r["id"] for r in resp.json().get("reports", [])]

    click_details: list[dict] = []
    for cid in campaign_ids:
        params = {
            "count": count,
            "fields": (
                "urls_clicked.url,"
                "urls_clicked.total_clicks,"
                "urls_clicked.unique_clicks,"
                "urls_clicked.click_percentage"
            ),
        }
        resp = requests.get(
            base_url + f"reports/{cid}/click-details",
            params=params,
            auth=auth,
            timeout=30,
        )
        resp.raise_for_status()
        for url_entry in resp.json().get("urls_clicked", []):
            click_details.append(
                {
                    "campaign_id": cid,
                    "url": url_entry.get("url"),
                    "total_clicks": url_entry.get("total_clicks"),
                    "unique_clicks": url_entry.get("unique_clicks"),
                    "click_percentage": url_entry.get("click_percentage"),
                }
            )

    return click_details