from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
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