from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base

class UserSkill(Base):
    __tablename__ = "user_skills"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    creativity = Column(Float, nullable=True)
    leadership = Column(Float, nullable=True)
    digital_literacy = Column(Float, nullable=True)
    critical_thinking = Column(Float, nullable=True)
    problem_solving = Column(Float, nullable=True)
    analytical_thinking = Column(Float, nullable=True)
    attention_to_detail = Column(Float, nullable=True)
    collaboration = Column(Float, nullable=True)
    adaptability = Column(Float, nullable=True)
    independence = Column(Float, nullable=True)
    evaluation = Column(Float, nullable=True)
    decision_making = Column(Float, nullable=True)
    stress_tolerance = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="skills") 