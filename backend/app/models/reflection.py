from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base

class StrengthsReflectionResponse(Base):
    __tablename__ = "strengths_reflection_responses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, nullable=False)
    prompt_text = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="reflection_responses")

class ReflectionQuestion(Base):
    __tablename__ = "reflection_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class HexacoQuestion(Base):
    __tablename__ = "hexaco_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, nullable=False)
    item_text = Column(Text, nullable=False)
    response_min = Column(Integer, nullable=False, default=1)
    response_max = Column(Integer, nullable=False, default=5)
    version = Column(String(50), nullable=False)  # e.g., 'hexaco_60_en'
    language = Column(String(10), nullable=False)  # 'en' or 'fr'
    reverse_keyed = Column(Boolean, nullable=False, default=False)
    facet = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Add index for common queries
    __table_args__ = (
        Index('idx_hexaco_version_language', 'version', 'language'),
        Index('idx_hexaco_item_id', 'item_id'),
    )
