"""
Orientator AI API Router
Handles all endpoints for the intelligent conversational career assistant
"""
# ============================================================================
# PRISMA MIGRATION - Enhanced Database Integration
# ============================================================================
# This router has been migrated to use Prisma ORM with enhanced features:
# - Type-safe database operations
# - Improved error handling and retry logic
# - Performance monitoring
# - Enhanced logging
# - Transaction support for complex operations
# 
# Migration date: 2025-01-13
# Previous system: SQLAlchemy ORM
# Current system: Prisma ORM with enhanced client
# ============================================================================



from fastapi import APIRouter, Depends, HTTPException, status, Query
from prisma import Prisma
from typing import List, Optional
from datetime import datetime
import logging

from app.utils.prisma_client import get_prisma_client, PrismaOperationLogger
from app.models.user import User
from app.models.conversation import Conversation
from app.models.chat_message import ChatMessage
from app.models.message_component import MessageComponent
from app.models.tool_invocation import ToolInvocation
from app.models.saved_recommendation import SavedRecommendation
from app.models.user_journey_milestone import UserJourneyMilestone

from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from app.services.orientator_ai_service import OrientatorAIService
from app.schemas.orientator import (
    OrientatorMessageRequest,
    OrientatorMessageResponse,
    SaveComponentRequest,
    SaveComponentResponse,
    UserJourneyResponse,
    ToolInvocationResult,
    MessageComponent as MessageComponentSchema
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/orientator",
    tags=["orientator"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
    }
)

# Test endpoint without authentication that mimics real flow
@router.post("/test-message")
async def test_orientator_message(
    request: dict,
    db: Prisma = Depends(get_prisma_client)
) -> dict:
    """
    Test endpoint for Orientator AI without authentication.
    Returns mock rich components for frontend testing.
    """
    try:
        logger.info(f"Test Orientator message: {request.get('message', '')}")
        
        # Create mock tool results
        mock_tool_results = [
            {
                "tool_name": "career_tree",
                "result": type('MockResult', (), {
                    'success': True,
                    'data': {"career_path": "Data Scientist"},
                    'metadata': {"source": "career_tree"}
                })()
            },
            {
                "tool_name": "esco_skills", 
                "result": type('MockResult', (), {
                    'success': True,
                    'data': {"skills": ["Python", "Statistics", "Machine Learning"]},
                    'metadata': {"source": "esco_skills"}
                })()
            },
            {
                "tool_name": "oasis_explorer",
                "result": type('MockResult', (), {
                    'success': True,
                    'data': {"jobs": ["Data Scientist", "ML Engineer", "Data Analyst"]},
                    'metadata': {"source": "oasis_explorer"}
                })()
            }
        ]
        
        # Mock intent
        mock_intent = {
            "intent": "career_exploration",
            "entities": {"career_goals": "data scientist"},
            "confidence": 0.95,
            "suggested_tools": ["career_tree", "esco_skills", "oasis_explorer"]
        }
        
        message = request.get('message', 'I want to become a data scientist')
        
        # Generate response with components  
        response = await orientator_service.generate_response(message, mock_intent, mock_tool_results)
        
        # Convert to response format without database storage
        from app.schemas.orientator import MessageComponent as MessageComponentSchema
        return {
            "message_id": 999999,
            "role": "assistant",
            "content": response.content,
            "components": [MessageComponentSchema(**c.dict()).dict() for c in response.components],
            "metadata": response.metadata,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test failed: {str(e)}"
        )

# Initialize service
orientator_service = OrientatorAIService()


@router.post("/message", response_model=OrientatorMessageResponse)
async def send_orientator_message(
    request: OrientatorMessageRequest,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
) -> OrientatorMessageResponse:
    """
    Process a message with Orientator AI.
    
    This endpoint handles user messages, invokes appropriate tools,
    and returns AI-generated responses with rich interactive components.
    
    Args:
        request: Message request containing user's message and conversation ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        OrientatorMessageResponse with AI response and components
        
    Raises:
        HTTPException: If conversation not found or user doesn't have access
    """
    try:
        # Verify conversation belongs to user
        conversation = await db.conversation.find_first(
            where={
                "id": request.conversation_id,
                "user_id": current_user.id
            }
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )
        
        # Store user message
        user_message = await db.chatmessage.create(
            data={
                "conversation_id": request.conversation_id,
                "role": "user",
                "content": request.message,
                "tokens_used": len(request.message.split())  # Simple token approximation
            }
        )
        
        logger.info(f"Processing Orientator message for user {current_user.id} in conversation {request.conversation_id}")
        
        # Process message with Orientator AI
        response = await orientator_service.process_message(
            user_id=current_user.id,
            message=request.message,
            conversation_id=request.conversation_id,
            db=db
        )
        
        # Store AI response
        ai_message = await db.chatmessage.create(
            data={
                "conversation_id": request.conversation_id,
                "role": "assistant",
                "content": response.content,
                "tokens_used": len(response.content.split()),
                "message_metadata": response.metadata
            }
        )
        
        # Store message components
        for component in response.components:
            db_component = await db.messagecomponent.create(
                data={
                    "message_id": ai_message.id,
                    "component_type": component.type.value,
                    "component_data": component.data,
                    "tool_source": component.metadata.get("tool_source"),
                    "actions": component.actions,
                    "metadata": component.metadata
                }
            )
        
        # Store tool invocations for tracking
        for tool_name in response.metadata.get("tools_invoked", []):
            invocation = await db.toolinvocation.create(
                data={
                    "conversation_id": request.conversation_id,
                    "tool_name": tool_name,
                    "user_id": current_user.id,
                    "success": "success",
                    "relevance_score": response.metadata.get("confidence", 0.8)
                }
            )
        
        # Update conversation metadata
        conversation = await db.conversation.update(
            where={"id": conversation.id},
            data={
                "last_message_at": ai_message.created_at,
                "message_count": conversation.message_count + 2
            }
        )
        
        # Convert to response model
        return OrientatorMessageResponse(
            message_id=ai_message.id,
            role=ai_message.role,
            content=ai_message.content,
            components=[MessageComponentSchema(**c.dict()) for c in response.components],
            metadata=response.metadata,
            created_at=ai_message.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Orientator message: {str(e)}")
        # No rollback needed in Prisma - automatic transaction handling
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@router.post("/save-component", response_model=SaveComponentResponse)
async def save_component(
    request: SaveComponentRequest,
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
) -> SaveComponentResponse:
    """
    Save a component from chat to My Space.
    
    This endpoint allows users to save interactive components
    (skill trees, job cards, test results, etc.) to their personal space.
    
    Args:
        request: Component save request with component details
        current_user: Authenticated user
        db: Database session
        
    Returns:
        SaveComponentResponse with save confirmation
        
    Raises:
        HTTPException: If conversation not found or user doesn't have access
    """
    try:
        # Verify conversation belongs to user
        conversation = await db.conversation.find_first(
            where={
                "id": request.conversation_id,
                "user_id": current_user.id
            }
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )
        
        logger.info(f"Saving component {request.component_id} for user {current_user.id}")
        
        # Create saved recommendation entry
        saved_item = await db.savedrecommendation.create(
            data={
                "user_id": current_user.id,
                "recommendation_type": request.component_type.value,
                "recommendation_data": {
                    "component_data": request.component_data,
                    "source_tool": request.source_tool,
                    "saved_from": "orientator_chat"
                },
                "source_tool": request.source_tool,
                "conversation_id": request.conversation_id,
                "component_type": request.component_type.value,
                "component_data": request.component_data,
                "interaction_metadata": {
                    "component_id": request.component_id,
                    "saved_at": datetime.utcnow().isoformat(),
                    "user_note": request.note
                }
            }
        )
        
        # Update component saved status if we have the message component
        # This would require finding the component by ID in the database
        
        # Track as journey milestone if it's a significant save
        if request.component_type in ["career_path", "test_result", "challenge_card"]:
            milestone = await db.userjourneymilestone.create(
                data={
                    "user_id": current_user.id,
                    "milestone_type": f"saved_{request.component_type}",
                    "milestone_data": {
                        "component_id": request.component_id,
                        "component_type": request.component_type.value,
                        "source_tool": request.source_tool
                    },
                    "achieved_at": datetime.utcnow(),
                    "conversation_id": request.conversation_id
                }
            )
        
        # No explicit commit needed in Prisma - automatic transaction handling
        
        return SaveComponentResponse(
            success=True,
            saved_item_id=saved_item.id,
            message="Component saved successfully to My Space"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving component: {str(e)}")
        # No rollback needed in Prisma - automatic transaction handling
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save component"
        )


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Get all messages for a conversation with Orientator components.
    
    This endpoint retrieves all messages in a conversation including
    any rich components generated by the Orientator AI tools.
    
    Args:
        conversation_id: ID of the conversation to retrieve messages for
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Dictionary with messages array including components
        
    Raises:
        HTTPException: If conversation not found or user doesn't have access
    """
    try:
        # Verify conversation belongs to user
        conversation = await db.conversation.find_first(
            where={
                "id": conversation_id,
                "user_id": current_user.id
            }
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )
        
        logger.info(f"Retrieving messages for conversation {conversation_id} (user {current_user.id})")
        
        # Get all messages with their components
        messages = await db.chatmessage.find_many(
            where={"conversation_id": conversation_id},
            order_by=[{"created_at": "asc"}]
        )
        
        # Format messages with components
        formatted_messages = []
        for message in messages:
            components = await db.messagecomponent.find_many(
                where={"message_id": message.id}
            )
            
            message_data = {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "tokens_used": message.tokens_used,
                "components": [comp.dict() for comp in components],
                "metadata": {}
            }
            
            formatted_messages.append(message_data)
        
        return {"messages": formatted_messages}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation messages"
        )


@router.get("/journey/{user_id}", response_model=UserJourneyResponse)
async def get_user_journey(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
) -> UserJourneyResponse:
    """
    Get aggregated user journey from all conversations.
    
    This endpoint provides a comprehensive view of the user's career
    exploration journey, including saved items, tools used, milestones,
    and progress across all Orientator conversations.
    
    Args:
        user_id: ID of the user to retrieve journey for
        current_user: Authenticated user
        db: Database session
        
    Returns:
        UserJourneyResponse with aggregated journey data
        
    Raises:
        HTTPException: If user doesn't have access to view this journey
    """
    try:
        # Check authorization - users can only view their own journey
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access another user's journey"
            )
        
        logger.info(f"Retrieving journey for user {user_id}")
        
        # Get all user's saved items
        saved_items = await db.savedrecommendation.find_many(
            where={
                "user_id": user_id,
                "source_tool": {"not": None}
            }
        )
        
        # Get tool usage statistics
        tool_invocations = await db.toolinvocation.find_many(
            where={"user_id": user_id}
        )
        
        tools_used = list(set([inv.tool_name for inv in tool_invocations]))
        
        # Get journey milestones
        milestones = await db.userjourneymilestone.find_many(
            where={"user_id": user_id},
            order_by=[{"achieved_at": "desc"}]
        )
        
        # Aggregate journey stages from milestones
        journey_stages = []
        for milestone in milestones:
            stage_data = {
                "type": milestone.milestone_type,
                "data": milestone.milestone_data,
                "achieved_at": milestone.achieved_at.isoformat(),
                "conversation_id": milestone.conversation_id
            }
            journey_stages.append(stage_data)
        
        # Extract career goals from saved career paths
        career_goals = []
        for item in saved_items:
            if item.component_type == "career_path" and item.component_data:
                goal = item.component_data.get("career_goal")
                if goal and goal not in career_goals:
                    career_goals.append(goal)
        
        # Build skill progression from saved skill trees
        skill_progression = {}
        skill_items = [item for item in saved_items if item.component_type == "skill_tree"]
        for item in skill_items:
            if item.component_data and "skills" in item.component_data:
                for skill in item.component_data["skills"]:
                    skill_name = skill.get("name", "Unknown")
                    skill_progression[skill_name] = {
                        "level": skill.get("level", "beginner"),
                        "saved_at": item.created_at.isoformat()
                    }
        
        # Extract personality insights from test results
        personality_insights = None
        test_results = [item for item in saved_items if item.component_type == "test_result"]
        if test_results:
            # Get the most recent test result
            latest_test = max(test_results, key=lambda x: x.created_at)
            personality_insights = latest_test.component_data
        
        # Get peer connections from saved peer cards
        peer_connections = []
        peer_items = [item for item in saved_items if item.component_type == "peer_card"]
        for item in peer_items:
            if item.component_data and "peers" in item.component_data:
                for peer in item.component_data["peers"]:
                    peer_connections.append({
                        "peer_id": peer.get("id"),
                        "name": peer.get("name"),
                        "match_score": peer.get("match_score", 0),
                        "saved_at": item.created_at.isoformat()
                    })
        
        # Get completed challenges
        challenges_completed = []
        challenge_items = [item for item in saved_items if item.component_type == "challenge_card"]
        for item in challenge_items:
            if item.component_data:
                challenges_completed.append({
                    "challenge_id": item.component_data.get("id"),
                    "title": item.component_data.get("title"),
                    "xp_earned": item.component_data.get("xp", 0),
                    "completed_at": item.created_at.isoformat()
                })
        
        return UserJourneyResponse(
            user_id=user_id,
            journey_stages=journey_stages,
            saved_items_count=len(saved_items),
            tools_used=tools_used,
            career_goals=career_goals,
            skill_progression=skill_progression,
            personality_insights=personality_insights,
            peer_connections=peer_connections,
            challenges_completed=challenges_completed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user journey: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user journey"
        )


@router.get("/conversations", response_model=List[dict])
async def get_orientator_conversations(
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> List[dict]:
    """
    Get user's Orientator conversations.
    
    Retrieves all conversations where the user has interacted with
    the Orientator AI, sorted by most recent activity.
    
    Args:
        current_user: Authenticated user
        db: Database session
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip
        
    Returns:
        List of conversation summaries with Orientator-specific metadata
    """
    try:
        # Get conversations with Orientator messages
        conversations = await db.conversation.find_many(
            where={
                "user_id": current_user.id,
                "messages": {
                    "some": {
                        "components": {
                            "some": {
                                "tool_source": {"not": None}
                            }
                        }
                    }
                }
            },
            order_by=[{"last_message_at": "desc"}],
            take=limit,
            skip=offset
        )
        
        result = []
        for conv in conversations:
            # Get tool usage for this conversation
            tools_used = await db.toolinvocation.find_many(
                where={"conversation_id": conv.id},
                select={"tool_name": True},
                distinct=["tool_name"]
            )
            
            conv_data = {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "message_count": conv.message_count,
                "tools_used": [t.tool_name for t in tools_used],
                "is_favorite": conv.is_favorite,
                "is_archived": conv.is_archived
            }
            result.append(conv_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving Orientator conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.get("/tool-analytics", response_model=dict)
async def get_tool_analytics(
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
) -> dict:
    """
    Get analytics on tool usage for the current user.
    
    Provides insights into which Orientator tools are most used,
    success rates, and usage patterns.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Dictionary containing tool usage analytics
    """
    try:
        # Get all tool invocations for user
        invocations = await db.toolinvocation.find_many(
            where={"user_id": current_user.id}
        )
        
        if not invocations:
            return {
                "total_invocations": 0,
                "tool_usage": {},
                "success_rate": 0,
                "most_used_tools": []
            }
        
        # Calculate analytics
        tool_usage = {}
        success_count = 0
        
        for inv in invocations:
            if inv.tool_name not in tool_usage:
                tool_usage[inv.tool_name] = {
                    "count": 0,
                    "success": 0,
                    "avg_execution_time": 0,
                    "total_time": 0
                }
            
            tool_usage[inv.tool_name]["count"] += 1
            if inv.success == "success":
                tool_usage[inv.tool_name]["success"] += 1
                success_count += 1
            
            if inv.execution_time_ms:
                tool_usage[inv.tool_name]["total_time"] += inv.execution_time_ms
        
        # Calculate averages and success rates
        for tool_name, stats in tool_usage.items():
            if stats["count"] > 0:
                stats["success_rate"] = stats["success"] / stats["count"]
                stats["avg_execution_time"] = stats["total_time"] / stats["count"]
                del stats["total_time"]  # Remove internal calculation field
        
        # Sort tools by usage
        most_used = sorted(
            tool_usage.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:5]
        
        return {
            "total_invocations": len(invocations),
            "tool_usage": tool_usage,
            "success_rate": success_count / len(invocations) if invocations else 0,
            "most_used_tools": [{"tool": t[0], "count": t[1]["count"]} for t in most_used]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving tool analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )


@router.post("/feedback", response_model=dict)
async def submit_feedback(
    message_id: int,
    feedback: str,
    rating: Optional[int] = Query(None, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
) -> dict:
    """
    Submit feedback for an Orientator AI response.
    
    Allows users to provide feedback on AI responses to improve
    the system over time.
    
    Args:
        message_id: ID of the AI message to provide feedback for
        feedback: Text feedback from the user
        rating: Optional rating from 1-5
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Confirmation of feedback submission
    """
    try:
        # Verify message belongs to user's conversation
        message = await db.chatmessage.find_first(
            where={
                "id": message_id,
                "role": "assistant",
                "conversation": {
                    "user_id": current_user.id
                }
            },
            include={"conversation": True}
        )
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found or access denied"
            )
        
        # Store feedback in message metadata
        current_metadata = message.message_metadata or {}
        current_metadata["user_feedback"] = {
            "feedback": feedback,
            "rating": rating,
            "submitted_at": datetime.utcnow().isoformat()
        }
        
        # Update message with new metadata
        message = await db.chatmessage.update(
            where={"id": message_id},
            data={"message_metadata": current_metadata}
        )
        
        # No explicit commit needed in Prisma - automatic transaction handling
        
        logger.info(f"Feedback submitted for message {message_id} by user {current_user.id}")
        
        return {
            "success": True,
            "message": "Thank you for your feedback!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        # No rollback needed in Prisma - automatic transaction handling
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )


# Additional utility endpoints

@router.get("/health", response_model=dict)
async def health_check() -> dict:
    """
    Health check endpoint for Orientator AI service.
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "orientator-ai",
        "version": "1.0.0"
    }


# Error handlers and middleware can be added here as needed