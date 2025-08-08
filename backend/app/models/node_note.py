from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base

class NodeNote(Base):
    __tablename__ = "node_notes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    node_id = Column(String(100), nullable=False)
    action_index = Column(Integer, nullable=False)
    note_text = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="node_notes") 