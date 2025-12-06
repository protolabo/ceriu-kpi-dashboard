from typing import List
from pydantic import BaseModel


class MailchimpAudience(BaseModel):
    name: str
    member_count: int


class MailchimpAudienceResponse(BaseModel):
    total_subscribers: int
    audiences: List[MailchimpAudience]
    

class MailchimpCampaignSummary(BaseModel):
    campaign_id: str
    subject: str | None = None
    send_time: str | None = None
    list_id: str | None = None
    emails_sent: int | None = None
    subscribers: int | None = None
    open_rate: float | None = None
    open_count: int | None = None
    click_rate: float | None = None
    click_count: int | None = None


class MailchimpCampaignSummaryResponse(BaseModel):
    total_campaigns: int
    campaigns: List[MailchimpCampaignSummary]

