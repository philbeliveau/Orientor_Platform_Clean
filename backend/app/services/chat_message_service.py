from typing import List, Optional, Dict, Any
from datetime import datetime
import time
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from sqlalchemy.exc import SQLAlchemyError
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
        db: Session,
        conversation_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tokens_used: Optional[int] = None,
        model_used: Optional[str] = None,
        response_time_ms: Optional[int] = None
    ) -> ChatMessage:
        """Add a new message to a conversation"""
        try:
            message = ChatMessage(
                conversation_id=conversation_id,
                role=role,
                content=content,
                message_metadata=metadata or {},
                tokens_used=tokens_used,
                model_used=model_used,
                response_time_ms=response_time_ms
            )
            db.add(message)
            
            # Update conversation statistics
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                conversation.last_message_at = datetime.utcnow()
                conversation.message_count += 1
                if tokens_used:
                    conversation.total_tokens_used += tokens_used
            
            db.commit()
            db.refresh(message)
            
            return message
            
        except SQLAlchemyError as e:
            logger.error(f"Error adding message: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    async def get_conversation_messages(
        db: Session,
        conversation_id: int,
        limit: int = 50,
        offset: int = 0,
        include_system: bool = True
    ) -> List[ChatMessage]:
        """Get messages for a conversation with pagination"""
        query = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        )
        
        if not include_system:
            query = query.filter(ChatMessage.role != "system")
        
        return query.order_by(
            ChatMessage.created_at.asc()
        ).offset(offset).limit(limit).all()
    
    @staticmethod
    async def search_messages(
        db: Session,
        user_id: int,
        query: str,
        filters: Optional[SearchFilters] = None
    ) -> List[Dict[str, Any]]:
        """Search messages across user's conversations using full-text search"""
        try:
            # Base query with full-text search
            search_query = text("""
                SELECT 
                    cm.id,
                    cm.conversation_id,
                    cm.role,
                    cm.content,
                    cm.created_at,
                    c.title as conversation_title,
                    ts_headline('english', cm.content, plainto_tsquery('english', :query),
                        'MaxWords=50, MinWords=20, StartSel=<mark>, StopSel=</mark>') as highlighted_content,
                    ts_rank(to_tsvector('english', cm.content), 
                        plainto_tsquery('english', :query)) as rank
                FROM chat_messages cm
                JOIN conversations c ON cm.conversation_id = c.id
                WHERE c.user_id = :user_id
                AND to_tsvector('english', cm.content) @@ plainto_tsquery('english', :query)
            """)
            
            params = {"user_id": user_id, "query": query}
            
            # Add filters
            filter_conditions = []
            if filters:
                if filters.conversation_id:
                    filter_conditions.append("cm.conversation_id = :conversation_id")
                    params["conversation_id"] = filters.conversation_id
                if filters.role:
                    filter_conditions.append("cm.role = :role")
                    params["role"] = filters.role
                if filters.date_from:
                    filter_conditions.append("cm.created_at >= :date_from")
                    params["date_from"] = filters.date_from
                if filters.date_to:
                    filter_conditions.append("cm.created_at <= :date_to")
                    params["date_to"] = filters.date_to
                if filters.category_id:
                    filter_conditions.append("c.category_id = :category_id")
                    params["category_id"] = filters.category_id
            
            if filter_conditions:
                search_query = text(str(search_query) + " AND " + " AND ".join(filter_conditions))
            
            # Order by relevance and limit results
            search_query = text(str(search_query) + " ORDER BY rank DESC, cm.created_at DESC LIMIT 100")
            
            result = db.execute(search_query, params)
            
            return [dict(row._mapping) for row in result]
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching messages: {str(e)}")
            return []
    
    @staticmethod
    async def get_message_statistics(
        db: Session,
        conversation_id: int
    ) -> MessageStats:
        """Get statistics for messages in a conversation"""
        try:
            # Get message counts by role
            role_counts = db.query(
                ChatMessage.role,
                func.count(ChatMessage.id).label("count")
            ).filter(
                ChatMessage.conversation_id == conversation_id
            ).group_by(ChatMessage.role).all()
            
            # Get total tokens and average response time
            stats = db.query(
                func.sum(ChatMessage.tokens_used).label("total_tokens"),
                func.avg(ChatMessage.response_time_ms).label("avg_response_time")
            ).filter(
                and_(
                    ChatMessage.conversation_id == conversation_id,
                    ChatMessage.role == "assistant"
                )
            ).first()
            
            # Get message timeline
            first_message = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conversation_id
            ).order_by(ChatMessage.created_at).first()
            
            last_message = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conversation_id
            ).order_by(ChatMessage.created_at.desc()).first()
            
            return MessageStats(
                total_messages=sum(count for _, count in role_counts),
                messages_by_role={role: count for role, count in role_counts},
                total_tokens=stats.total_tokens or 0,
                avg_response_time_ms=stats.avg_response_time or 0,
                first_message_at=first_message.created_at if first_message else None,
                last_message_at=last_message.created_at if last_message else None
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting message statistics: {str(e)}")
            raise
    
    @staticmethod
    async def export_conversation(
        db: Session,
        conversation_id: int,
        format: str = "json"
    ) -> bytes:
        """Export conversation in various formats"""
        try:
            # Get conversation and messages
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                raise ValueError("Conversation not found")
            
            messages = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conversation_id
            ).order_by(ChatMessage.created_at).all()
            
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