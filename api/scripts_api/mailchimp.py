# scripts_api/mailchimp.py
import requests


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
    status: str = "sent",
    count: int = 1000,
) -> list[dict]:
    data_center = api_key.split("-")[-1]
    base_url = "https://" + data_center + ".api.mailchimp.com/3.0/"
    auth = ("", api_key)

    campaigns_params = {
        "status": status,
        "count": count,
        "fields": (
            "reports.id,"
            "reports.campaign_title,"
            "reports.list_id,"
            "reports.send_time,"
            "reports.emails_sent,"
            "reports.opens.opens_total,"
            "reports.opens.open_rate,"
            "reports.clicks.clicks_total,"
            "reports.clicks.click_rate"
        ),
    }

    resp = requests.get(
        base_url + "reports",
        params=campaigns_params,
        auth=auth,
        timeout=30,
    )
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
    
""" def fetch_mailchimp_campaign_summaries(
    api_key: str,
    status: str = "sent",
    count: int = 1000,
) -> list[dict]:
    
    data_center = api_key.split("-")[-1]
    base_url = "https://" + data_center + ".api.mailchimp.com/3.0/"
    auth = ("", api_key)


    campaigns_params = {
        "status": status,
        "count": count,
        "fields": (
            "reports.id,"
            "reports.campaign_title,"
            "reports.list_id,"
            "reports.send_time,"
            "reports.emails_sent,"
            "reports.opens.open_rate,"
            "reports.opens.opens_total,"
            "reports.clicks.click_rate,"
            "reports.clicks.clicks_total"
        ),
    }

    resp = requests.get(
        base_url + "reports",
        params=campaigns_params,
        auth=auth,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    reports = data.get("reports", [])

    # On reconstruit une liste de dicts
    summaries: list[dict] = []
    for r in reports:
        summary = r.get("report_summary", {}) or {}
        summaries.append(
            {
                "id": r.get("id"),
                "name": r.get("campaign_title"),
                "list_id": r.get("list_id"),
                "send_time": r.get("send_time"),
                "emails_sent": r.get("emails_sent"),
                "open_rate": summary.get("open_rate"),
                "opens_total": summary.get("opens_total"),
                "click_rate": summary.get("click_rate"),
                "clicks_total": summary.get("clicks_total"),
            }
        )

    return summaries """
    
""" def fetch_mailchimp_campaign_summaries(
    api_key: str,
    status: str = "sent",
    count: int = 1000,
) -> list[dict]:

    # Data center à partir de la clé
    data_center = api_key.split("-")[-1]
    base_url = "https://" + data_center + ".api.mailchimp.com/3.0/"
    auth = ("", api_key)

    #On Liste les campagnes
    campaigns_params = {
        "status": status,
        "count": count,
        "fields": (
            "campaigns.id,"
            "campaigns.settings.subject_line,"
            "campaigns.send_time,"
            "campaigns.recipients.list_id"
        ),
    }

    campaigns_resp = requests.get(
        base_url + "reports",
        #params=campaigns_params,
        auth=auth,
        timeout=30,
    )
    campaigns_resp.raise_for_status()
    campaigns_data = campaigns_resp.json()
    #campaigns_list = campaigns_data.get("campaigns", [])
    return campaigns_data """

    #summaries: list[dict] = []

    #Pour chaque campagne on récupére le report
    # for camp in campaigns_list:
    #     camp_id = camp.get("id")
    #     if not camp_id:
    #         continue

    #     subject = camp.get("settings", {}).get("subject_line")
    #     send_time = camp.get("send_time")
    #     list_id = camp.get("recipients", {}).get("list_id")

    #     # Appel /reports/{campaign_id}
    #     report_resp = requests.get(
    #         base_url + f"reports/",{camp_id}
    #         auth=auth,
    #         timeout=30,
    #     )

    #     # Si le report n'existe pas on ignore les stats
    #     if report_resp.status_code == 404:
    #         emails_sent = None
    #         open_rate = None
    #         open_count = None
    #         click_rate = None
    #         click_count = None
    #     else:
    #         report_resp.raise_for_status()
    #         rep = report_resp.json()
    #         emails_sent = rep.get("emails_sent")
    #         opens = rep.get("opens", {})
    #         clicks = rep.get("clicks", {})

    #         open_rate = opens.get("open_rate")
    #         open_count = opens.get("opens_total")
    #         click_rate = clicks.get("click_rate")
    #         click_count = clicks.get("clicks_total")

    #     summaries.append(
    #         {
    #             "campaign_id": camp_id,
    #             "subject": subject,
    #             "send_time": send_time,
    #             "list_id": list_id,
    #             "emails_sent": emails_sent,
    #             "subscribers": emails_sent,
    #             "open_rate": open_rate,
    #             "open_count": open_count,
    #             "click_rate": click_rate,
    #             "click_count": click_count,
    #         }
    #     )

    #return summaries

