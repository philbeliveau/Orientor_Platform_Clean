from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
import secrets
from ..utils.database import Base


class ConversationShare(Base):
    __tablename__ = "conversation_shares"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    shared_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    share_token = Column(String(255), unique=True, nullable=False, index=True)
    is_public = Column(Boolean, default=False)
    password_hash = Column(String(255), nullable=True)  # For password-protected shares
    expires_at = Column(DateTime(timezone=True), nullable=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="shares")
    user = relationship("User", back_populates="conversation_shares")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.share_token:
            self.share_token = self._generate_share_token()
    
    @staticmethod
    def _generate_share_token():
        """Generate a secure, unique share token"""
        return secrets.token_urlsafe(32)
    
    def __repr__(self):
        return f"<ConversationShare(id={self.id}, conversation_id={self.conversation_id}, token='{self.share_token[:8]}...')>"