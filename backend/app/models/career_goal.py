"""
Career Goal Model - Tracks user's selected career objectives
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from ..utils.database import Base


class CareerGoal(Base):
    """
    Model for storing user's career goals selected from job cards
    """
    __tablename__ = "career_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Job identifiers
    esco_occupation_id = Column(String, nullable=True)  # ESCO ID for European jobs
    oasis_code = Column(String, nullable=True)  # OASIS code for other jobs
    
    # Goal details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_date = Column(DateTime, nullable=True)
    
    # Status tracking
    is_active = Column(Boolean, default=True)  # Only one active goal at a time
    progress_percentage = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    achieved_at = Column(DateTime, nullable=True)
    
    # Source tracking
    source = Column(String, nullable=True)  # 'oasis', 'saved', 'swipe', 'tree', etc.
    source_metadata = Column(Text, nullable=True)  # JSON string for additional source data
    
    # Relationships
    user = relationship("User", back_populates="career_goals")
    milestones = relationship("CareerMilestone", back_populates="goal", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CareerGoal(id={self.id}, user_id={self.user_id}, title='{self.title}', active={self.is_active})>"


class CareerMilestone(Base):
    """
    Model for tracking milestones/skills within a career goal
    """
    __tablename__ = "career_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("career_goals.id"), nullable=False)
    
    # Milestone details
    skill_id = Column(String, nullable=False)  # ESCO skill ID
    skill_name = Column(String, nullable=False)
    tier_level = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    
    # Progress tracking
    is_completed = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.0)  # GraphSage confidence
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # XP rewards
    xp_value = Column(Integer, default=100)
    xp_awarded = Column(Boolean, default=False)
    
    # Relationships
    goal = relationship("CareerGoal", back_populates="milestones")
    
    def __repr__(self):
        return f"<CareerMilestone(id={self.id}, skill='{self.skill_name}', tier={self.tier_level}, completed={self.is_completed})>"