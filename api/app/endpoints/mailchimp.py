# app/endpoints/mailchimp.py
from fastapi import APIRouter

from app.models.mailchimp_model import MailchimpAudienceResponse, MailchimpCampaignSummaryResponse
from app.services.mailchimp_services import get_mailchimp_audiences, get_mailchimp_campaign_summaries

router = APIRouter(
    prefix="/mailchimp",
    tags=["mailchimp"],
)


@router.get("/audiences", response_model=MailchimpAudienceResponse)
def list_mailchimp_audiences():

    return get_mailchimp_audiences()

@router.get("/campaigns/summary")
def list_mailchimp_campaign_summaries():
    
    return get_mailchimp_campaign_summaries()
