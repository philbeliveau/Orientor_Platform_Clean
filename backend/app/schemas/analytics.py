from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date


class UserAnalytics(BaseModel):
    """User analytics for a specific period"""
    period: str
    start_date: date
    end_date: date
    total_messages: int
    total_conversations: int
    total_tokens_used: int
    avg_response_time_ms: float
    active_days: int
    most_active_date: Optional[date]
    conversation_count: int
    favorite_categories: List[Dict[str, Any]]


class UsageTrends(BaseModel):
    """Usage trends over time"""
    period_days: int
    daily_messages: List[Dict[str, Any]]
    daily_tokens: List[Dict[str, Any]]
    weekly_messages: List[Dict[str, Any]]
    weekly_tokens: List[Dict[str, Any]]
    growth_rate_percent: float


class Topic(BaseModel):
    """Popular topic"""
    name: str
    count: int
    percentage: float


class AnalyticsSummary(BaseModel):
    """Summary analytics dashboard"""
    user_analytics: UserAnalytics
    usage_trends: UsageTrends
    popular_topics: List[Topic]