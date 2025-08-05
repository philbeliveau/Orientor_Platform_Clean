from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import secrets
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..models import ConversationShare, Conversation, ChatMessage, User
from ..schemas.share import ShareOptions, ShareLink, ShareAnalytics

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ShareService:
    """Service for managing conversation sharing"""
    
    @staticmethod
    async def create_share_link(
        db: Session,
        conversation_id: int,
        user_id: int,
        options: ShareOptions
    ) -> Optional[ShareLink]:
        """Create a share link for a conversation"""
        try:
            # Verify the conversation belongs to the user
            conversation = db.query(Conversation).filter(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            ).first()
            
            if not conversation:
                return None
            
            # Create share with optional password
            share = ConversationShare(
                conversation_id=conversation_id,
                shared_by=user_id,
                is_public=options.is_public,
                password_hash=pwd_context.hash(options.password) if options.password else None,
                expires_at=datetime.utcnow() + timedelta(hours=options.expires_in_hours) if options.expires_in_hours else None
            )
            
            db.add(share)
            db.commit()
            db.refresh(share)
            
            # Create the share link
            base_url = options.base_url or "http://localhost:3000"
            share_link = ShareLink(
                share_id=share.id,
                conversation_id=conversation_id,
                share_token=share.share_token,
                full_url=f"{base_url}/shared/conversation/{share.share_token}",
                is_public=share.is_public,
                has_password=bool(share.password_hash),
                expires_at=share.expires_at,
                created_at=share.created_at
            )
            
            return share_link
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating share link: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    async def get_shared_conversation(
        db: Session,
        share_token: str,
        password: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a shared conversation by token"""
        try:
            # Find the share
            share = db.query(ConversationShare).filter(
                ConversationShare.share_token == share_token
            ).first()
            
            if not share:
                return None
            
            # Check if share has expired
            if share.expires_at and share.expires_at < datetime.utcnow():
                return None
            
            # Check password if required
            if share.password_hash:
                if not password or not pwd_context.verify(password, share.password_hash):
                    return {"error": "invalid_password", "requires_password": True}
            
            # Get the conversation and messages
            conversation = db.query(Conversation).filter(
                Conversation.id == share.conversation_id
            ).first()
            
            if not conversation:
                return None
            
            # Get messages (excluding system messages for shared views)
            messages = db.query(ChatMessage).filter(
                and_(
                    ChatMessage.conversation_id == share.conversation_id,
                    ChatMessage.role != "system"
                )
            ).order_by(ChatMessage.created_at).all()
            
            # Update view count
            share.view_count += 1
            db.commit()
            
            # Get sharer info
            sharer = db.query(User).filter(User.id == share.shared_by).first()
            
            return {
                "conversation": {
                    "id": conversation.id,
                    "title": conversation.title,
                    "created_at": conversation.created_at,
                    "message_count": conversation.message_count,
                    "shared_by": sharer.email if sharer else "Unknown"
                },
                "messages": [
                    {
                        "id": msg.id,
                        "role": msg.role,
                        "content": msg.content,
                        "created_at": msg.created_at
                    }
                    for msg in messages
                ],
                "share_info": {
                    "view_count": share.view_count,
                    "shared_at": share.created_at,
                    "expires_at": share.expires_at
                }
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting shared conversation: {str(e)}")
            return None
    
    @staticmethod
    async def update_share_settings(
        db: Session,
        share_id: int,
        user_id: int,
        options: ShareOptions
    ) -> bool:
        """Update share settings"""
        try:
            # Find the share and verify ownership
            share = db.query(ConversationShare).filter(
                and_(
                    ConversationShare.id == share_id,
                    ConversationShare.shared_by == user_id
                )
            ).first()
            
            if not share:
                return False
            
            # Update settings
            if options.is_public is not None:
                share.is_public = options.is_public
            
            if options.password is not None:
                share.password_hash = pwd_context.hash(options.password) if options.password else None
            
            if options.expires_in_hours is not None:
                share.expires_at = datetime.utcnow() + timedelta(hours=options.expires_in_hours)
            
            db.commit()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating share settings: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    async def revoke_share(
        db: Session,
        share_id: int,
        user_id: int
    ) -> bool:
        """Revoke a share link"""
        try:
            # Find and delete the share
            share = db.query(ConversationShare).filter(
                and_(
                    ConversationShare.id == share_id,
                    ConversationShare.shared_by == user_id
                )
            ).first()
            
            if not share:
                return False
            
            db.delete(share)
            db.commit()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error revoking share: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    async def get_user_shares(
        db: Session,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get all shares created by a user"""
        try:
            shares = db.query(ConversationShare).filter(
                ConversationShare.shared_by == user_id
            ).order_by(ConversationShare.created_at.desc()).all()
            
            share_list = []
            for share in shares:
                conversation = db.query(Conversation).filter(
                    Conversation.id == share.conversation_id
                ).first()
                
                if conversation:
                    share_list.append({
                        "share_id": share.id,
                        "conversation_id": share.conversation_id,
                        "conversation_title": conversation.title,
                        "share_token": share.share_token,
                        "is_public": share.is_public,
                        "has_password": bool(share.password_hash),
                        "view_count": share.view_count,
                        "expires_at": share.expires_at,
                        "created_at": share.created_at
                    })
            
            return share_list
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user shares: {str(e)}")
            return []
    
    @staticmethod
    async def get_share_analytics(
        db: Session,
        share_id: int,
        user_id: int
    ) -> Optional[ShareAnalytics]:
        """Get analytics for a share"""
        try:
            share = db.query(ConversationShare).filter(
                and_(
                    ConversationShare.id == share_id,
                    ConversationShare.shared_by == user_id
                )
            ).first()
            
            if not share:
                return None
            
            return ShareAnalytics(
                share_id=share.id,
                conversation_id=share.conversation_id,
                total_views=share.view_count,
                created_at=share.created_at,
                last_viewed=share.created_at,  # Would need to track this separately
                expires_at=share.expires_at,
                is_active=not (share.expires_at and share.expires_at < datetime.utcnow())
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting share analytics: {str(e)}")
            return None