from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
import time

if TYPE_CHECKING:
    from prisma import Prisma
from app.utils.error_handling import handle_prisma_error, log_database_operation
import logging
import json
from io import BytesIO

# Optional imports for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..models import ChatMessage, Conversation, User
from ..schemas.chat_message import SearchFilters, MessageStats

logger = logging.getLogger(__name__)


class ChatMessageService:
    """Service for managing chat messages"""
    
    @staticmethod
    async def add_message(
        prisma: 'Prisma',
        conversation_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tokens_used: Optional[int] = None,
        model_used: Optional[str] = None,
        response_time_ms: Optional[int] = None
    ) -> 'ChatMessage':
        """Add a new message to a conversation"""
        try:
            from datetime import datetime
            
            # Create message data with proper Prisma JSON field handling
            message_data = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "tokens_used": tokens_used,
                "model_used": model_used,
                "response_time_ms": response_time_ms,
                "created_at": datetime.utcnow()
            }
            
            # Handle JSON metadata field properly for Prisma
            if metadata is not None:
                message_data["message_metadata"] = metadata
            # If metadata is None, don't include the field at all (Prisma will set to null)
            
            # Create the message
            message = await prisma.chatmessage.create(data=message_data)
            
            # Update conversation statistics
            conversation = await prisma.conversation.find_first(
                where={"id": conversation_id}
            )
            
            if conversation:
                update_data = {
                    "last_message_at": datetime.utcnow(),
                    "message_count": conversation.message_count + 1
                }
                if tokens_used:
                    update_data["total_tokens_used"] = (conversation.total_tokens_used or 0) + tokens_used
                
                await prisma.conversation.update(
                    where={"id": conversation_id},
                    data=update_data
                )
            
            return message
            
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            raise
    
    @staticmethod
    async def get_conversation_messages(
        prisma: 'Prisma',
        conversation_id: int,
        limit: int = 50,
        offset: int = 0,
        include_system: bool = True
    ) -> List['ChatMessage']:
        """Get messages for a conversation with pagination"""
        try:
            # Build where clause
            where_clause = {"conversation_id": conversation_id}
            
            if not include_system:
                where_clause["role"] = {"not": "system"}
            
            # Query messages with proper ordering
            messages = await prisma.chatmessage.find_many(
                where=where_clause,
                skip=offset,
                take=limit,
                order_by={'created_at': 'asc'}
            )
            
            return messages
        except Exception as e:
            logger.error(f"Error getting conversation messages: {str(e)}")
            return []
    
    @staticmethod
    async def search_messages(
        prisma: 'Prisma',
        user_id: int,
        query: str,
        filters: Optional[SearchFilters] = None
    ) -> List[Dict[str, Any]]:
        """Search messages across user's conversations using full-text search"""
        try:
            # For now, implement basic search without full-text until we can use raw SQL
            # Get user's conversations first
            conversations = await prisma.conversation.find_many(
                where={"user_id": user_id}
            )
            
            conversation_ids = [conv.id for conv in conversations]
            
            if not conversation_ids:
                return []
            
            # Build where clause for messages
            where_clause = {
                "conversation_id": {"in": conversation_ids},
                "content": {"contains": query, "mode": "insensitive"}
            }
            
            # Add filters
            if filters:
                if filters.conversation_id:
                    where_clause["conversation_id"] = filters.conversation_id
                if filters.role:
                    where_clause["role"] = filters.role
                if filters.date_from:
                    where_clause["created_at"] = {"gte": filters.date_from}
                if filters.date_to:
                    if "created_at" in where_clause:
                        where_clause["created_at"]["lte"] = filters.date_to
                    else:
                        where_clause["created_at"] = {"lte": filters.date_to}
            
            # Find matching messages
            messages = await prisma.chatmessage.find_many(
                where=where_clause,
                take=100,
                order_by={"created_at": "desc"}
            )
            
            # Convert to search result format
            results = []
            for msg in messages:
                # Find conversation title
                conversation = next((c for c in conversations if c.id == msg.conversation_id), None)
                
                results.append({
                    "id": msg.id,
                    "conversation_id": msg.conversation_id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at,
                    "conversation_title": conversation.title if conversation else "Unknown",
                    "highlighted_content": msg.content,  # Basic content for now
                    "rank": 1.0  # Basic ranking for now
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return []
    
    @staticmethod
    async def get_message_statistics(
        prisma: 'Prisma',
        conversation_id: int
    ) -> MessageStats:
        """Get statistics for messages in a conversation"""
        try:
            # Get all messages for the conversation
            messages = await prisma.chatmessage.find_many(
                where={"conversation_id": conversation_id}
            )
            
            if not messages:
                return MessageStats(
                    total_messages=0,
                    messages_by_role={},
                    total_tokens=0,
                    avg_response_time_ms=0,
                    first_message_at=None,
                    last_message_at=None
                )
            
            # Calculate role counts
            messages_by_role = {}
            total_tokens = 0
            assistant_messages = []
            
            for msg in messages:
                role = msg.role
                messages_by_role[role] = messages_by_role.get(role, 0) + 1
                
                if msg.tokens_used:
                    total_tokens += msg.tokens_used
                
                if role == "assistant" and msg.response_time_ms:
                    assistant_messages.append(msg.response_time_ms)
            
            # Calculate average response time
            avg_response_time = 0
            if assistant_messages:
                avg_response_time = sum(assistant_messages) / len(assistant_messages)
            
            # Get first and last message timestamps
            sorted_messages = sorted(messages, key=lambda x: x.created_at)
            first_message_at = sorted_messages[0].created_at
            last_message_at = sorted_messages[-1].created_at
            
            return MessageStats(
                total_messages=len(messages),
                messages_by_role=messages_by_role,
                total_tokens=total_tokens,
                avg_response_time_ms=avg_response_time,
                first_message_at=first_message_at,
                last_message_at=last_message_at
            )
            
        except Exception as e:
            logger.error(f"Error getting message statistics: {str(e)}")
            raise
    
    @staticmethod
    async def export_conversation(
        prisma: 'Prisma',
        conversation_id: int,
        format: str = "json"
    ) -> bytes:
        """Export conversation in various formats"""
        try:
            # Get conversation and messages
            conversation = await prisma.conversation.find_first(
                where={"id": conversation_id}
            )
            
            if not conversation:
                raise ValueError("Conversation not found")
            
            messages = await prisma.chatmessage.find_many(
                where={"conversation_id": conversation_id},
                order_by={"created_at": "asc"}
            )
            
            if format == "json":
                return ChatMessageService._export_as_json(conversation, messages)
            elif format == "txt":
                return ChatMessageService._export_as_txt(conversation, messages)
            elif format == "pdf":
                return ChatMessageService._export_as_pdf(conversation, messages)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting conversation: {str(e)}")
            raise
    
    @staticmethod
    def _export_as_json(conversation: Conversation, messages: List[ChatMessage]) -> bytes:
        """Export conversation as JSON"""
        data = {
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "message_count": conversation.message_count,
                "total_tokens_used": conversation.total_tokens_used
            },
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "tokens_used": msg.tokens_used,
                    "model_used": msg.model_used
                }
                for msg in messages
            ]
        }
        return json.dumps(data, indent=2).encode('utf-8')
    
    @staticmethod
    def _export_as_txt(conversation: Conversation, messages: List[ChatMessage]) -> bytes:
        """Export conversation as plain text"""
        lines = [
            f"Conversation: {conversation.title}",
            f"Date: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Messages: {conversation.message_count}",
            "=" * 80,
            ""
        ]
        
        for msg in messages:
            if msg.role != "system":  # Skip system messages in text export
                lines.extend([
                    f"[{msg.role.upper()}] {msg.created_at.strftime('%H:%M:%S')}",
                    msg.content,
                    ""
                ])
        
        return "\n".join(lines).encode('utf-8')
    
    @staticmethod
    def _export_as_pdf(conversation: Conversation, messages: List[ChatMessage]) -> bytes:
        """Export conversation as PDF"""
        if not REPORTLAB_AVAILABLE:
            raise ValueError("PDF export is not available. Please install reportlab: pip install reportlab")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>{conversation.title}</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Metadata
        meta = Paragraph(
            f"Date: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}<br/>"
            f"Messages: {conversation.message_count}<br/>"
            f"Tokens Used: {conversation.total_tokens_used}",
            styles['Normal']
        )
        story.append(meta)
        story.append(Spacer(1, 20))
        
        # Messages
        for msg in messages:
            if msg.role != "system":
                role_style = styles['Heading2'] if msg.role == "user" else styles['Normal']
                role_para = Paragraph(
                    f"<b>{msg.role.upper()}</b> - {msg.created_at.strftime('%H:%M:%S')}",
                    role_style
                )
                story.append(role_para)
                
                content_para = Paragraph(msg.content.replace('\n', '<br/>'), styles['Normal'])
                story.append(content_para)
                story.append(Spacer(1, 12))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()