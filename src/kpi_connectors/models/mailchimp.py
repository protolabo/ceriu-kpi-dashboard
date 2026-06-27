from typing import List
from pydantic import BaseModel


class MailchimpAudience(BaseModel):
    name: str
    member_count: int


class MailchimpAudienceResponse(BaseModel):
    total_subscribers: int
    audiences: List[MailchimpAudience]
    

class MailchimpCampaignSummary(BaseModel):
    id: str | None = None
    name: str | None = None
    list_id: str | None = None
    send_time: str | None = None
    emails_sent: int | None = None
    open_rate: float | None = None
    opens_total: int | None = None
    click_rate: float | None = None
    clicks_total: int | None = None


class MailchimpCampaignSummaryResponse(BaseModel):
    total_campaigns: int
    campaigns: List[MailchimpCampaignSummary]


class MailchimpCampaignParams(BaseModel):
    status: str | None = "sent"
    count: int = 1000
    since_send_time: str | None = None    # ex "2025-01-01T00:00:00+00:00"
    before_send_time: str | None = None