from fastapi import APIRouter, Query
from typing import Optional

from app.config.settings import settings
from kpi_connectors.models.mailchimp import MailchimpAudienceResponse, MailchimpCampaignSummaryResponse, MailchimpCampaignParams
from kpi_connectors.connectors.mailchimp import fetch_mailchimp_audiences, fetch_mailchimp_campaign_summaries

router = APIRouter(
    prefix="/mailchimp",
    tags=["mailchimp"],
)

@router.get("/campaigns/summary", response_model=MailchimpCampaignSummaryResponse)
def list_mailchimp_campaign_summaries(
    status: Optional[str] = Query("sent", description="sent, draft, scheduled..."),
    count: int = Query(1000, ge=1, le=1000, description="Nombre max de campagnes"),
    since_send_time: Optional[str] = Query(None, description="Date min (Format Asked: 2025-01-01T00:00:00+00:00)"),
    before_send_time: Optional[str] = Query(None, description="Date max "),
):
    params = MailchimpCampaignParams(
        status=status, count=count,
        since_send_time=since_send_time, before_send_time=before_send_time,
    )
    summaries = fetch_mailchimp_campaign_summaries(api_key=settings.MAILCHIMP_API_KEY, params=params)
    return MailchimpCampaignSummaryResponse(total_campaigns=len(summaries), campaigns=summaries)

@router.get("/audiences", response_model=MailchimpAudienceResponse)
def list_mailchimp_audiences():
    return fetch_mailchimp_audiences(api_key=settings.MAILCHIMP_API_KEY)
