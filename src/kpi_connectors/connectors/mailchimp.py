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
        "fields": "lists.name,lists.stats.member_count",
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
    params: MailchimpCampaignParams | None = None,
    ) -> list[dict]:
    params = params or MailchimpCampaignParams()

    data_center = api_key.split("-")[-1]
    base_url = "https://" + data_center + ".api.mailchimp.com/3.0/"
    auth = ("", api_key)

    campaigns_params = {
        "count": params.count,
        "fields": (
            "reports.id,reports.campaign_title,reports.list_id,"
            "reports.send_time,reports.emails_sent,"
            "reports.opens.opens_total,reports.opens.open_rate,"
            "reports.clicks.clicks_total,reports.clicks.click_rate"
        ),
    }
    if params.status:
        campaigns_params["status"] = params.status
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

        summaries.append(
            {
                "id": r.get("id"),
                "name": r.get("campaign_title"),
                "list_id": r.get("list_id"),
                "send_time": r.get("send_time"),
                "emails_sent": r.get("emails_sent"),

                # valeurs dans "opens"
                "open_rate": opens.get("open_rate"),
                "opens_total": opens.get("opens_total"),

                # valeurs dans "clicks"
                "click_rate": clicks.get("click_rate"),
                "clicks_total": clicks.get("clicks_total"),
            }
        )

    return summaries


