from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..utils.database import Base
import uuid  # Added import for uuid

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    total_xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    last_completed_node = Column(String(100), nullable=True)
    completed_actions = Column(JSON, nullable=True, default=dict)  
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="progress", uselist=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.completed_actions is None:
            self.completed_actions = {} 