from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..utils.database import Base


class ToolInvocation(Base):
    """
    Tracks all tool invocations made by the Orientator AI during conversations.
    This table is essential for analytics, debugging, and understanding AI behavior.
    """
    __tablename__ = "tool_invocations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String(50), nullable=False, index=True)
    input_params = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    execution_time_ms = Column(Integer, nullable=True, index=True)
    
    # Additional tracking fields
    success = Column(String(20), nullable=True, default="success")  # success, failed, timeout
    error_message = Column(String(500), nullable=True)
    relevance_score = Column(Float, nullable=True)  # AI confidence in tool choice
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="tool_invocations")
    user = relationship("User", back_populates="tool_invocations")
    
    def __repr__(self):
        return f"<ToolInvocation(id={self.id}, tool='{self.tool_name}', conversation_id={self.conversation_id})>"
    
    def to_dict(self):
        """Convert the invocation to a dictionary for API responses."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "tool_name": self.tool_name,
            "input_params": self.input_params,
            "output_data": self.output_data,
            "execution_time_ms": self.execution_time_ms,
            "success": self.success,
            "error_message": self.error_message,
            "relevance_score": self.relevance_score,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }