from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from ..utils.database import Base
from uuid import uuid4

class UserSkillTree(Base):
    __tablename__ = "user_skill_trees"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    graph_id = Column(String, nullable=False, unique=True, default=lambda: str(uuid4()))
    tree_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="skill_trees") 