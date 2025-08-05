from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ShareOptions(BaseModel):
    """Options for creating or updating a share"""
    is_public: bool = False
    password: Optional[str] = None
    expires_in_hours: Optional[int] = None  # None means no expiration
    base_url: Optional[str] = None


class ShareLink(BaseModel):
    """Response for created share link"""
    share_id: int
    conversation_id: int
    share_token: str
    full_url: str
    is_public: bool
    has_password: bool
    expires_at: Optional[datetime]
    created_at: datetime


class ShareAnalytics(BaseModel):
    """Analytics for a share"""
    share_id: int
    conversation_id: int
    total_views: int
    created_at: datetime
    last_viewed: datetime
    expires_at: Optional[datetime]
    is_active: bool


class SharedConversationRequest(BaseModel):
    """Request for accessing a shared conversation"""
    password: Optional[str] = None