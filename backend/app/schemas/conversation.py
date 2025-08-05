from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConversationFilters(BaseModel):
    """Filters for querying conversations"""
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None
    category_id: Optional[int] = None
    search_query: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: str
    category_id: Optional[int] = None
    is_favorite: bool = False
    is_archived: bool = False


class ConversationCreate(BaseModel):
    """Schema for creating a conversation"""
    initial_message: str
    title: Optional[str] = None


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation"""
    title: Optional[str] = None
    category_id: Optional[int] = None
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None


class ConversationResponse(ConversationBase):
    """Schema for conversation response"""
    id: int
    user_id: int
    auto_generated_title: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime]
    message_count: int
    total_tokens_used: int
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Schema for paginated conversation list"""
    conversations: List[ConversationResponse]
    total: int
    limit: int
    offset: int