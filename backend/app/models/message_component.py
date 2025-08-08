from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..utils.database import Base


class MessageComponent(Base):
    """
    Stores rich interactive components associated with chat messages.
    These components represent tool outputs that can be rendered in the UI.
    """
    __tablename__ = "message_components"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    component_type = Column(String(50), nullable=False, index=True)
    component_data = Column(JSONB, nullable=False)
    tool_source = Column(String(50), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Additional metadata for component rendering and interaction
    actions = Column(JSONB, nullable=True, default=list)
    saved = Column(JSONB, nullable=True, default=False)
    component_metadata = Column(JSONB, nullable=True)
    
    # Relationships
    message = relationship("ChatMessage", back_populates="components")
    
    def __repr__(self):
        return f"<MessageComponent(id={self.id}, type='{self.component_type}', message_id={self.message_id})>"
    
    def to_dict(self):
        """Convert the component to a dictionary for API responses."""
        return {
            "id": self.id,
            "message_id": self.message_id,
            "component_type": self.component_type,
            "component_data": self.component_data,
            "tool_source": self.tool_source,
            "actions": self.actions or [],
            "saved": self.saved or False,
            "metadata": self.component_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None
        }