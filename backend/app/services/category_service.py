from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

from ..models import ConversationCategory, Conversation

logger = logging.getLogger(__name__)


class CategoryService:
    """Service for managing conversation categories"""
    
    @staticmethod
    async def create_category(
        db: Session,
        user_id: int,
        name: str,
        color: Optional[str] = None,
        icon: Optional[str] = None
    ) -> Optional[ConversationCategory]:
        """Create a new category for a user"""
        try:
            category = ConversationCategory(
                user_id=user_id,
                name=name,
                color=color,
                icon=icon
            )
            db.add(category)
            db.commit()
            db.refresh(category)
            
            return category
            
        except IntegrityError:
            logger.error(f"Category with name '{name}' already exists for user {user_id}")
            db.rollback()
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error creating category: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    async def get_user_categories(
        db: Session,
        user_id: int
    ) -> List[ConversationCategory]:
        """Get all categories for a user"""
        return db.query(ConversationCategory).filter(
            ConversationCategory.user_id == user_id
        ).order_by(ConversationCategory.name).all()
    
    @staticmethod
    async def get_category_by_id(
        db: Session,
        category_id: int,
        user_id: int
    ) -> Optional[ConversationCategory]:
        """Get a specific category if it belongs to the user"""
        return db.query(ConversationCategory).filter(
            and_(
                ConversationCategory.id == category_id,
                ConversationCategory.user_id == user_id
            )
        ).first()
    
    @staticmethod
    async def update_category(
        db: Session,
        category_id: int,
        user_id: int,
        updates: Dict[str, any]
    ) -> bool:
        """Update category properties"""
        category = await CategoryService.get_category_by_id(
            db, category_id, user_id
        )
        if not category:
            return False
        
        # Update allowed fields
        allowed_fields = ["name", "color", "icon"]
        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                setattr(category, field, value)
        
        try:
            db.commit()
            return True
        except IntegrityError:
            logger.error(f"Category name '{updates.get('name')}' already exists")
            db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error updating category: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    async def delete_category(
        db: Session,
        category_id: int,
        user_id: int
    ) -> bool:
        """Delete a category and remove it from all conversations"""
        category = await CategoryService.get_category_by_id(
            db, category_id, user_id
        )
        if not category:
            return False
        
        try:
            # Remove category from all conversations
            db.query(Conversation).filter(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.category_id == category_id
                )
            ).update({"category_id": None})
            
            # Delete the category
            db.delete(category)
            db.commit()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting category: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    async def get_category_statistics(
        db: Session,
        category_id: int,
        user_id: int
    ) -> Optional[Dict[str, any]]:
        """Get statistics for a category"""
        category = await CategoryService.get_category_by_id(
            db, category_id, user_id
        )
        if not category:
            return None
        
        # Get conversation count
        conversation_count = db.query(func.count(Conversation.id)).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.category_id == category_id
            )
        ).scalar() or 0
        
        # Get message count and token usage
        stats = db.query(
            func.sum(Conversation.message_count).label("total_messages"),
            func.sum(Conversation.total_tokens_used).label("total_tokens")
        ).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.category_id == category_id
            )
        ).first()
        
        # Get most recent conversation
        recent_conversation = db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.category_id == category_id
            )
        ).order_by(Conversation.last_message_at.desc()).first()
        
        return {
            "category_id": category_id,
            "category_name": category.name,
            "conversation_count": conversation_count,
            "total_messages": stats.total_messages or 0,
            "total_tokens_used": stats.total_tokens or 0,
            "last_activity": recent_conversation.last_message_at if recent_conversation else None
        }