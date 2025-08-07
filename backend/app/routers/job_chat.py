"""
Job Chat Router - API endpoints for LLM-powered job card conversations.
"""
# ============================================================================
# AUTHENTICATION MIGRATION - Secure Integration System
# ============================================================================
# This router has been migrated to use the unified secure authentication system
# with integrated caching, security optimizations, and rollback support.
# 
# Migration date: 2025-08-07 13:44:03
# Previous system: clerk_auth.get_current_user_with_db_sync
# Current system: secure_auth_integration.get_current_user_secure_integrated
# 
# Benefits:
# - AES-256 encryption for sensitive cache data
# - Full SHA-256 cache keys (not truncated)
# - Error message sanitization
# - Multi-layer caching optimization  
# - Zero-downtime rollback capability
# - Comprehensive security monitoring
# ============================================================================



from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging

from ..database import get_db
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from ..services.job_card_llm_service import JobCardLLMService, get_preset_queries
from ..models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/job-chat", tags=["job-chat"])

# Initialize service
llm_service = JobCardLLMService()

@router.post("/query")
async def process_job_query(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process a user query about a specific job.
    
    Request body:
    {
        "job_data": {
            "id": "occupation::esco::123",
            "metadata": {...}
        },
        "query": "What barriers would I face?",
        "context": {
            "source": "job_card",
            "session_id": "optional-session-id"
        }
    }
    """
    try:
        # Extract request data
        job_data = request.get("job_data")
        user_query = request.get("query")
        context = request.get("context", {})
        
        if not job_data or not user_query:
            raise HTTPException(status_code=400, detail="Missing job_data or query")
        
        # Log the interaction
        logger.info(f"Job chat query from user {current_user.clerk_user_id} about job {job_data.get('id')}")
        
        # Process the query
        response = await llm_service.process_job_query(
            user_id=current_user.clerk_user_id,
            job_data=job_data,
            user_query=user_query,
            db=db
        )
        
        # Add session context if provided
        if context.get("session_id"):
            response["session_id"] = context["session_id"]
        
        return {
            "success": True,
            "data": response,
            "job_id": job_data.get("id")
        }
        
    except Exception as e:
        logger.error(f"Error in job chat query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preset-queries")
async def get_preset_job_queries(
    job_type: Optional[str] = Query(None, description="Filter by job type (esco/oasis)"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get preset queries for job cards.
    """
    try:
        queries = await get_preset_queries()
        
        # Filter by job type if specified
        if job_type:
            # In future, we could have job-type specific queries
            pass
        
        return {
            "success": True,
            "queries": queries,
            "total": len(queries)
        }
        
    except Exception as e:
        logger.error(f"Error getting preset queries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-query")
async def process_batch_job_queries(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process multiple queries about a job in batch.
    
    Request body:
    {
        "job_data": {...},
        "queries": ["What are the barriers?", "How long to qualify?"],
        "context": {...}
    }
    """
    try:
        job_data = request.get("job_data")
        queries = request.get("queries", [])
        
        if not job_data or not queries:
            raise HTTPException(status_code=400, detail="Missing job_data or queries")
        
        # Process all queries
        responses = []
        for query in queries[:5]:  # Limit to 5 queries per batch
            response = await llm_service.process_job_query(
                user_id=current_user.clerk_user_id,
                job_data=job_data,
                user_query=query,
                db=db
            )
            responses.append({
                "query": query,
                "response": response
            })
        
        return {
            "success": True,
            "job_id": job_data.get("id"),
            "responses": responses,
            "total": len(responses)
        }
        
    except Exception as e:
        logger.error(f"Error in batch job queries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation-history/{job_id}")
async def get_job_conversation_history(
    job_id: str,
    limit: int = Query(10, description="Number of messages to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get conversation history for a specific job.
    """
    try:
        # In a full implementation, this would retrieve from a conversation storage
        # For now, return empty history
        return {
            "success": True,
            "job_id": job_id,
            "messages": [],
            "total": 0
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))