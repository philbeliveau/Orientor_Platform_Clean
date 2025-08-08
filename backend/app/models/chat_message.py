from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..utils.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String(50), nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    message_metadata = Column(JSONB, nullable=True)
    
    # Check constraint for role
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="check_role_values"),
    )
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    components = relationship("MessageComponent", back_populates="message", cascade="all, delete-orphan", lazy="selectin")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"