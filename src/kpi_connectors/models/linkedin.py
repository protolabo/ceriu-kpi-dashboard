from typing import List, Optional
from pydantic import BaseModel


class LinkedInFollowerCount(BaseModel):
    organization_urn: str
    follower_count: int


class LinkedInShareStat(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    impressions: Optional[int] = None
    unique_impressions: Optional[int] = None
    clicks: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    engagement: Optional[float] = None


class LinkedInShareStatsResponse(BaseModel):
    organization_urn: str
    stats: List[LinkedInShareStat]


class LinkedInPostStats(BaseModel):
    impressions: Optional[int] = None
    unique_impressions: Optional[int] = None
    clicks: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    engagement: Optional[float] = None


class LinkedInPost(BaseModel):
    id: str
    created_at: Optional[int] = None
    published_at: Optional[int] = None
    commentary: Optional[str] = None
    visibility: Optional[str] = None
    stats: Optional[LinkedInPostStats] = None


class LinkedInPostsResponse(BaseModel):
    organization_urn: str
    posts: List[LinkedInPost]