from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from ..utils.database import Base

class UserRepresentation(Base):
    __tablename__ = "user_representation"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = Column(String(50), nullable=False)  # 'llm_insight', etc.
    format_version = Column(String(10), nullable=False, default='v1')
    data = Column(JSONB, nullable=False)  # Structure: {preview, full_text, if_you_accept}
    summary = Column(Text)
    notes = Column(Text)
    
    # Champs pour l'avatar
    avatar_name = Column(String(255))
    avatar_description = Column(Text)
    avatar_image_url = Column(String(500))
    
    # Relation avec l'utilisateur
    user = relationship("User", back_populates="representations")