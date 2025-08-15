from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
from app.utils.error_handling import handle_prisma_error, log_database_operation
import logging

if TYPE_CHECKING:
    from prisma import Prisma
from ..models import Conversation, ChatMessage, User
from ..schemas.conversation import ConversationFilters

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations"""
    
    @staticmethod
    async def create_conversation(
        prisma: 'Prisma',
        user_id: int,
        initial_message: str,
        title: Optional[str] = None
    ) -> 'Conversation':
        """Create a new conversation with an initial message"""
        try:
            # Create conversation data
            conversation_data = {
                "user_id": user_id,
                "title": title or "New Conversation",
                "auto_generated_title": (title is None),
                "last_message_at": datetime.utcnow(),
                "message_count": 1,
                "total_tokens_used": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create conversation
            conversation = await prisma.conversation.create(data=conversation_data)
            
            # Add the initial system message and user message
            system_message_data = {
                "conversation_id": conversation.id,
                "role": "system",
                "content": "You are a helpful AI assistant.",
                "created_at": datetime.utcnow()
            }
            await prisma.chatmessage.create(data=system_message_data)
            
            user_message_data = {
                "conversation_id": conversation.id,
                "role": "user",
                "content": initial_message,
                "created_at": datetime.utcnow()
            }
            await prisma.chatmessage.create(data=user_message_data)
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise
    
    @staticmethod
    async def get_user_conversations(
        prisma: 'Prisma',
        user_id: int,
        filters: Optional[ConversationFilters] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List['Conversation']:
        """Get conversations for a user with optional filters"""
        try:
            # Build where clause
            where_clause = {"user_id": user_id}
            
            if filters:
                if filters.is_favorite is not None:
                    where_clause["is_favorite"] = filters.is_favorite
                if filters.is_archived is not None:
                    where_clause["is_archived"] = filters.is_archived
                if filters.category_id is not None:
                    where_clause["category_id"] = filters.category_id
                if filters.search_query:
                    where_clause["title"] = {"contains": filters.search_query, "mode": "insensitive"}
                if filters.date_from:
                    where_clause["created_at"] = {"gte": filters.date_from}
                if filters.date_to:
                    if "created_at" in where_clause:
                        where_clause["created_at"]["lte"] = filters.date_to
                    else:
                        where_clause["created_at"] = {"lte": filters.date_to}
            
            # Get conversations with ordering
            conversations = await prisma.conversation.find_many(
                where=where_clause,
                skip=offset,
                take=limit,
                order_by=[
                    {"last_message_at": "desc"},
                    {"created_at": "desc"}
                ]
            )
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            return []
    
    @staticmethod
    async def get_conversation_by_id(
        prisma: 'Prisma',
        conversation_id: int,
        user_id: int
    ) -> Optional['Conversation']:
        """Get a specific conversation if it belongs to the user"""
        try:
            conversation = await prisma.conversation.find_first(
                where={
                    "id": conversation_id,
                    "user_id": user_id
                }
            )
            return conversation
        except Exception as e:
            logger.error(f"Error getting conversation by id: {str(e)}")
            return None
    
    @staticmethod
    async def update_conversation_title(
        prisma: 'Prisma',
        conversation_id: int,
        title: str,
        user_id: int
    ) -> bool:
        """Update conversation title"""
        try:
            conversation = await ConversationService.get_conversation_by_id(
                prisma, conversation_id, user_id
            )
            if not conversation:
                return False
            
            await prisma.conversation.update(
                where={"id": conversation_id},
                data={
                    "title": title,
                    "auto_generated_title": False,
                    "updated_at": datetime.utcnow()
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error updating conversation title: {str(e)}")
            return False
    
    @staticmethod
    async def auto_generate_title(
        prisma: 'Prisma',
        conversation_id: int,
        user_id: int
    ) -> Optional[str]:
        """Generate a title based on the first few messages"""
        try:
            conversation = await ConversationService.get_conversation_by_id(
                prisma, conversation_id, user_id
            )
            if not conversation:
                return None
            
            # Get the first few messages
            messages = await prisma.chatmessage.find_many(
                where={"conversation_id": conversation_id},
                order_by={"created_at": "asc"},
                take=5
            )
            
            if len(messages) < 2:  # Need at least system and user message
                return None
            
            # Extract user messages for title generation
            user_messages = [msg.content for msg in messages if msg.role == "user"]
            
            if not user_messages:
                return None
            
            # Simple title generation - take first few words of first user message
            # In production, this would use an LLM
            first_message = user_messages[0]
            words = first_message.split()[:6]
            generated_title = " ".join(words)
            if len(first_message) > len(generated_title):
                generated_title += "..."
            
            # Update the conversation
            await prisma.conversation.update(
                where={"id": conversation_id},
                data={
                    "title": generated_title,
                    "auto_generated_title": True,
                    "updated_at": datetime.utcnow()
                }
            )
            
            return generated_title
        except Exception as e:
            logger.error(f"Error auto-generating title: {str(e)}")
            return None
    
    @staticmethod
    async def archive_conversation(
        prisma: 'Prisma',
        conversation_id: int,
        user_id: int,
        archive: bool = True
    ) -> bool:
        """Archive or unarchive a conversation"""
        try:
            conversation = await ConversationService.get_conversation_by_id(
                prisma, conversation_id, user_id
            )
            if not conversation:
                return False
            
            await prisma.conversation.update(
                where={"id": conversation_id},
                data={
                    "is_archived": archive,
                    "updated_at": datetime.utcnow()
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error archiving conversation: {str(e)}")
            return False
    
    @staticmethod
    async def delete_conversation(
        prisma: 'Prisma',
        conversation_id: int,
        user_id: int
    ) -> bool:
        """Delete a conversation and all its messages"""
        try:
            conversation = await ConversationService.get_conversation_by_id(
                prisma, conversation_id, user_id
            )
            if not conversation:
                return False
            
            # Delete conversation (cascade should handle messages)
            await prisma.conversation.delete(
                where={"id": conversation_id}
            )
            
            return True
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False
    
    @staticmethod
    async def toggle_favorite(
        prisma: 'Prisma',
        conversation_id: int,
        user_id: int
    ) -> Optional[bool]:
        """Toggle favorite status of a conversation"""
        try:
            conversation = await ConversationService.get_conversation_by_id(
                prisma, conversation_id, user_id
            )
            if not conversation:
                return None
            
            new_favorite_status = not conversation.is_favorite
            
            await prisma.conversation.update(
                where={"id": conversation_id},
                data={
                    "is_favorite": new_favorite_status,
                    "updated_at": datetime.utcnow()
                }
            )
            
            return new_favorite_status
        except Exception as e:
            logger.error(f"Error toggling favorite: {str(e)}")
            return None
    
    @staticmethod
    async def set_category(
        prisma: 'Prisma',
        conversation_id: int,
        category_id: Optional[int],
        user_id: int
    ) -> bool:
        """Set or remove category for a conversation"""
        try:
            conversation = await ConversationService.get_conversation_by_id(
                prisma, conversation_id, user_id
            )
            if not conversation:
                return False
            
            await prisma.conversation.update(
                where={"id": conversation_id},
                data={
                    "category_id": category_id,
                    "updated_at": datetime.utcnow()
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error setting category: {str(e)}")
            return False
    
    @staticmethod
    async def get_conversation_count(
        prisma: 'Prisma',
        user_id: int,
        filters: Optional[ConversationFilters] = None
    ) -> int:
        """Get total count of conversations for pagination"""
        try:
            where_clause = {"user_id": user_id}
            
            if filters:
                if filters.is_favorite is not None:
                    where_clause["is_favorite"] = filters.is_favorite
                if filters.is_archived is not None:
                    where_clause["is_archived"] = filters.is_archived
                if filters.category_id is not None:
                    where_clause["category_id"] = filters.category_id
            
            count = await prisma.conversation.count(where=where_clause)
            return count
        except Exception as e:
            logger.error(f"Error getting conversation count: {str(e)}")
            return 0
    
    @staticmethod
    async def update_conversation_stats(
        prisma: 'Prisma',
        conversation_id: int,
        tokens_used: int
    ) -> bool:
        """Update conversation statistics after adding a message"""
        try:
            conversation = await prisma.conversation.find_first(
                where={"id": conversation_id}
            )
            
            if not conversation:
                return False
            
            # Update message count and tokens
            await prisma.conversation.update(
                where={"id": conversation_id},
                data={
                    "message_count": conversation.message_count + 2,  # user + assistant message
                    "total_tokens_used": (conversation.total_tokens_used or 0) + tokens_used,
                    "last_message_at": datetime.utcnow()
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating conversation stats: {str(e)}")
            return False