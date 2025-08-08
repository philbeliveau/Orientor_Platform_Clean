from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..utils.database import Base


class UserJourneyMilestone(Base):
    """
    Tracks significant milestones in a user's career exploration journey.
    These milestones are automatically extracted from conversations and saved items.
    """
    __tablename__ = "user_journey_milestones"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    milestone_type = Column(String(50), nullable=False, index=True)
    milestone_data = Column(JSONB, nullable=False)
    
    # Milestone details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True, index=True)  # career, skill, assessment, peer, challenge
    
    # Progress tracking
    progress_percentage = Column(Float, nullable=True, default=0.0)
    status = Column(String(20), nullable=True, default="active", index=True)  # active, completed, abandoned
    
    # Source tracking
    source_type = Column(String(50), nullable=True)  # conversation, saved_item, tool_result
    source_id = Column(Integer, nullable=True)  # ID of the source (conversation_id, saved_recommendation_id, etc.)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Timestamps
    achieved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # AI-generated insights
    ai_insights = Column(JSONB, nullable=True)
    next_steps = Column(JSONB, nullable=True, default=list)
    
    # Relationships
    user = relationship("User", back_populates="journey_milestones")
    conversation = relationship("Conversation", back_populates="journey_milestones")
    
    def __repr__(self):
        return f"<UserJourneyMilestone(id={self.id}, user_id={self.user_id}, type='{self.milestone_type}')>"
    
    def to_dict(self):
        """Convert the milestone to a dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "milestone_type": self.milestone_type,
            "milestone_data": self.milestone_data,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "progress_percentage": self.progress_percentage,
            "status": self.status,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "conversation_id": self.conversation_id,
            "achieved_at": self.achieved_at.isoformat() if self.achieved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "ai_insights": self.ai_insights,
            "next_steps": self.next_steps or []
        }