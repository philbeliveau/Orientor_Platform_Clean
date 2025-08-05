from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID  # ✅ SQLAlchemy's UUID type
from uuid import uuid4        

class TreePath(Base):
    __tablename__ = "tree_paths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # user_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) 
    tree_type = Column(String, nullable=False)
    tree_json = Column(JSONB, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="tree_paths")