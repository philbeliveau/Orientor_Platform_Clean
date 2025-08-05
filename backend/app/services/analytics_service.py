from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..models import (
    UserChatAnalytics, Conversation, ChatMessage, 
    ConversationCategory, User
)
from ..schemas.analytics import UserAnalytics, UsageTrends, Topic

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for managing chat analytics"""
    
    @staticmethod
    async def record_message_sent(
        db: Session,
        user_id: int,
        tokens_used: int,
        response_time: int,
        category_id: Optional[int] = None
    ):
        """Record analytics when a message is sent"""
        try:
            today = date.today()
            
            # Get or create today's analytics record
            analytics = db.query(UserChatAnalytics).filter(
                and_(
                    UserChatAnalytics.user_id == user_id,
                    UserChatAnalytics.date == today
                )
            ).first()
            
            if not analytics:
                analytics = UserChatAnalytics(
                    user_id=user_id,
                    date=today,
                    messages_sent=0,
                    conversations_started=0,
                    total_tokens_used=0,
                    avg_response_time_ms=0,
                    most_used_category_id=category_id
                )
                db.add(analytics)
            
            # Update metrics
            total_response_time = (analytics.avg_response_time_ms or 0) * analytics.messages_sent
            analytics.messages_sent += 1
            analytics.total_tokens_used += tokens_used
            analytics.avg_response_time_ms = (total_response_time + response_time) / analytics.messages_sent
            
            # Update most used category if provided
            if category_id and not analytics.most_used_category_id:
                analytics.most_used_category_id = category_id
            
            db.commit()
            
        except SQLAlchemyError as e:
            logger.error(f"Error recording message analytics: {str(e)}")
            db.rollback()
    
    @staticmethod
    async def record_conversation_started(
        db: Session,
        user_id: int,
        category_id: Optional[int] = None
    ):
        """Record when a new conversation is started"""
        try:
            today = date.today()
            
            # Get or create today's analytics record
            analytics = db.query(UserChatAnalytics).filter(
                and_(
                    UserChatAnalytics.user_id == user_id,
                    UserChatAnalytics.date == today
                )
            ).first()
            
            if not analytics:
                analytics = UserChatAnalytics(
                    user_id=user_id,
                    date=today,
                    conversations_started=0,
                    most_used_category_id=category_id
                )
                db.add(analytics)
            
            analytics.conversations_started += 1
            
            db.commit()
            
        except SQLAlchemyError as e:
            logger.error(f"Error recording conversation start: {str(e)}")
            db.rollback()
    
    @staticmethod
    async def get_user_analytics(
        db: Session,
        user_id: int,
        period: str = "week"
    ) -> UserAnalytics:
        """Get user analytics for a specific period"""
        try:
            # Calculate date range
            end_date = date.today()
            if period == "day":
                start_date = end_date
            elif period == "week":
                start_date = end_date - timedelta(days=7)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            elif period == "year":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=7)
            
            # Get analytics for period
            analytics = db.query(UserChatAnalytics).filter(
                and_(
                    UserChatAnalytics.user_id == user_id,
                    UserChatAnalytics.date >= start_date,
                    UserChatAnalytics.date <= end_date
                )
            ).all()
            
            # Aggregate metrics
            total_messages = sum(a.messages_sent for a in analytics)
            total_conversations = sum(a.conversations_started for a in analytics)
            total_tokens = sum(a.total_tokens_used for a in analytics)
            
            # Calculate average response time
            weighted_sum = sum(
                a.avg_response_time_ms * a.messages_sent 
                for a in analytics 
                if a.avg_response_time_ms
            )
            avg_response_time = (
                weighted_sum / total_messages if total_messages > 0 else 0
            )
            
            # Get most active day
            most_active_day = max(
                analytics, 
                key=lambda a: a.messages_sent,
                default=None
            )
            
            # Get conversation count
            conversation_count = db.query(func.count(Conversation.id)).filter(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.created_at >= datetime.combine(start_date, datetime.min.time()),
                    Conversation.created_at <= datetime.combine(end_date, datetime.max.time())
                )
            ).scalar() or 0
            
            # Get favorite categories
            category_usage = db.query(
                ConversationCategory.name,
                func.count(Conversation.id).label("count")
            ).join(
                Conversation,
                Conversation.category_id == ConversationCategory.id
            ).filter(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.created_at >= datetime.combine(start_date, datetime.min.time())
                )
            ).group_by(ConversationCategory.name).all()
            
            return UserAnalytics(
                period=period,
                start_date=start_date,
                end_date=end_date,
                total_messages=total_messages,
                total_conversations=total_conversations,
                total_tokens_used=total_tokens,
                avg_response_time_ms=avg_response_time,
                active_days=len(analytics),
                most_active_date=most_active_day.date if most_active_day else None,
                conversation_count=conversation_count,
                favorite_categories=[
                    {"name": name, "count": count}
                    for name, count in category_usage
                ]
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user analytics: {str(e)}")
            # Return empty analytics on error
            return UserAnalytics(
                period=period,
                start_date=date.today(),
                end_date=date.today(),
                total_messages=0,
                total_conversations=0,
                total_tokens_used=0,
                avg_response_time_ms=0,
                active_days=0,
                conversation_count=0,
                favorite_categories=[]
            )
    
    @staticmethod
    async def get_usage_trends(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> UsageTrends:
        """Get usage trends over time"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Get daily analytics
            daily_stats = db.query(UserChatAnalytics).filter(
                and_(
                    UserChatAnalytics.user_id == user_id,
                    UserChatAnalytics.date >= start_date,
                    UserChatAnalytics.date <= end_date
                )
            ).order_by(UserChatAnalytics.date).all()
            
            # Convert to trend data
            daily_messages = [
                {"date": str(stat.date), "count": stat.messages_sent}
                for stat in daily_stats
            ]
            
            daily_tokens = [
                {"date": str(stat.date), "count": stat.total_tokens_used}
                for stat in daily_stats
            ]
            
            # Get weekly aggregates
            weekly_messages = []
            weekly_tokens = []
            
            for i in range(0, days, 7):
                week_start = start_date + timedelta(days=i)
                week_end = min(week_start + timedelta(days=6), end_date)
                
                week_stats = [
                    s for s in daily_stats 
                    if week_start <= s.date <= week_end
                ]
                
                if week_stats:
                    weekly_messages.append({
                        "week": f"{week_start} - {week_end}",
                        "count": sum(s.messages_sent for s in week_stats)
                    })
                    weekly_tokens.append({
                        "week": f"{week_start} - {week_end}",
                        "count": sum(s.total_tokens_used for s in week_stats)
                    })
            
            # Calculate growth rate
            if len(daily_stats) >= 2:
                first_week_msgs = sum(
                    s.messages_sent for s in daily_stats[:7]
                )
                last_week_msgs = sum(
                    s.messages_sent for s in daily_stats[-7:]
                )
                growth_rate = (
                    ((last_week_msgs - first_week_msgs) / first_week_msgs * 100)
                    if first_week_msgs > 0 else 0
                )
            else:
                growth_rate = 0
            
            return UsageTrends(
                period_days=days,
                daily_messages=daily_messages,
                daily_tokens=daily_tokens,
                weekly_messages=weekly_messages,
                weekly_tokens=weekly_tokens,
                growth_rate_percent=growth_rate
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting usage trends: {str(e)}")
            return UsageTrends(
                period_days=days,
                daily_messages=[],
                daily_tokens=[],
                weekly_messages=[],
                weekly_tokens=[],
                growth_rate_percent=0
            )
    
    @staticmethod
    async def get_popular_topics(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[Topic]:
        """Get popular conversation topics based on titles"""
        try:
            # Get recent conversations
            conversations = db.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(Conversation.created_at.desc()).limit(100).all()
            
            # Simple word frequency analysis on titles
            word_count: Dict[str, int] = {}
            
            for conv in conversations:
                # Skip auto-generated titles
                if conv.auto_generated_title:
                    continue
                
                # Simple tokenization (in production, use proper NLP)
                words = conv.title.lower().split()
                for word in words:
                    # Skip common words
                    if len(word) > 3 and word not in ["the", "and", "for", "with", "about"]:
                        word_count[word] = word_count.get(word, 0) + 1
            
            # Get top topics
            sorted_topics = sorted(
                word_count.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:limit]
            
            return [
                Topic(
                    name=word.capitalize(),
                    count=count,
                    percentage=(count / len(conversations) * 100) if conversations else 0
                )
                for word, count in sorted_topics
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting popular topics: {str(e)}")
            return []