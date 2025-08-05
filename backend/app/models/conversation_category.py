from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from ..utils.database import Base


class ConversationCategory(Base):
    __tablename__ = "conversation_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=True)  # Hex color code
    icon = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Unique constraint on user_id and name
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='_user_category_uc'),
    )
    
    # Relationships
    user = relationship("User", back_populates="conversation_categories")
    conversations = relationship("Conversation", back_populates="category")
    
    def __repr__(self):
        return f"<ConversationCategory(id={self.id}, name='{self.name}', user_id={self.user_id})>"