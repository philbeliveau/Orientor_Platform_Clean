from sqlalchemy import Column, Integer, Date, Float, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from ..utils.database import Base


class UserChatAnalytics(Base):
    __tablename__ = "user_chat_analytics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    messages_sent = Column(Integer, default=0)
    conversations_started = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    avg_response_time_ms = Column(Float, nullable=True)
    most_used_category_id = Column(Integer, ForeignKey("conversation_categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Unique constraint on user_id and date
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='_user_date_analytics_uc'),
    )
    
    # Relationships
    user = relationship("User", back_populates="chat_analytics")
    most_used_category = relationship("ConversationCategory")
    
    def __repr__(self):
        return f"<UserChatAnalytics(id={self.id}, user_id={self.user_id}, date={self.date})>"