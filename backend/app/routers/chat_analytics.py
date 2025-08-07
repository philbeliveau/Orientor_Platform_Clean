from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session

from app.utils.secure_auth_integration import get_current_user_secure_integrated as get_current_user
from app.models import User
from app.utils.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    UserAnalytics, UsageTrends, Topic, AnalyticsSummary
)

router = APIRouter(
    prefix="/chat/analytics",
    tags=["analytics"]
)

@router.get("/usage", response_model=UserAnalytics)
async def get_usage_analytics(
    period: str = Query("week", regex="^(day|week|month|year)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat usage analytics for a specific period"""
# ============================================================================
# AUTHENTICATION MIGRATION - Secure Integration System
# ============================================================================
# This router has been migrated to use the unified secure authentication system
# with integrated caching, security optimizations, and rollback support.
# 
# Migration date: 2025-08-07 13:44:03
# Previous system: clerk_auth.get_current_user_with_db_sync
# Current system: secure_auth_integration.get_current_user_secure_integrated
# 
# Benefits:
# - AES-256 encryption for sensitive cache data
# - Full SHA-256 cache keys (not truncated)
# - Error message sanitization
# - Multi-layer caching optimization  
# - Zero-downtime rollback capability
# - Comprehensive security monitoring
# ============================================================================


    return await AnalyticsService.get_user_analytics(
        db, current_user.id, period
    )

@router.get("/trends", response_model=UsageTrends)
async def get_usage_trends(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage trends over time"""
    return await AnalyticsService.get_usage_trends(
        db, current_user.id, days
    )

@router.get("/topics", response_model=List[Topic])
async def get_popular_topics(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get popular conversation topics"""
    return await AnalyticsService.get_popular_topics(
        db, current_user.id, limit
    )

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete analytics summary dashboard"""
    user_analytics = await AnalyticsService.get_user_analytics(
        db, current_user.id, "month"
    )
    usage_trends = await AnalyticsService.get_usage_trends(
        db, current_user.id, 30
    )
    popular_topics = await AnalyticsService.get_popular_topics(
        db, current_user.id, 10
    )
    
    return AnalyticsSummary(
        user_analytics=user_analytics,
        usage_trends=usage_trends,
        popular_topics=popular_topics
    )