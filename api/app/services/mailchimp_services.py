# app/services/mailchimp_service.py
from fastapi import HTTPException

from app.config.settings import settings
from app.models.mailchimp_model import MailchimpAudience,MailchimpAudienceResponse,MailchimpCampaignSummary,MailchimpCampaignSummaryResponse
from scripts_api.mailchimp import fetch_mailchimp_audiences,fetch_mailchimp_campaign_summaries


def get_mailchimp_audiences() -> MailchimpAudienceResponse:
    api_key = settings.MAILCHIMP_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="MAILCHIMP_API_KEY n'est pas configurée sur le serveur.",
        )

    try:
        raw = fetch_mailchimp_audiences(api_key)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Erreur lors de l'appel à l'API Mailchimp: {e}",
        )

    audiences = [MailchimpAudience(**a) for a in raw.get("audiences", [])]

    return MailchimpAudienceResponse(
        total_subscribers=raw.get("total_subscribers", 0),
        audiences=audiences,
    )
    
def get_mailchimp_campaign_summaries():

    api_key = settings.MAILCHIMP_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="MAILCHIMP_API_KEY n'est pas configurée sur le serveur.",
        )

    try:
        raw_list = fetch_mailchimp_campaign_summaries(api_key=api_key)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Erreur lors de l'appel à l'API Mailchimp (campaigns): {e}",
        )
    return raw_list
    #campaigns_models = [MailchimpCampaignSummary(**c) for c in raw_list]

    # return MailchimpCampaignSummaryResponse(
    #     total_campaigns=len(campaigns_models),
    #     campaigns=campaigns_models,
    # )
