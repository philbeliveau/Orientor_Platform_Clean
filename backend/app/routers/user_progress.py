
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

from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from app.utils.prisma_client import get_prisma_client, PrismaOperationLogger
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from app.models.user import User
from app.models.user_progress import UserProgress
from app.schemas.tree import UserProgressCreate, UserProgressUpdate, UserProgress as UserProgressSchema
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/user-progress",
    tags=["user-progress"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/", response_model=UserProgressSchema)
async def get_user_progress(
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    # Get existing progress or create new
    progress = await db.userprogress.find_first(
        where={"user_id": current_user.id}
    )
    
    if not progress:
        # Initialize user progress
        progress = await db.userprogress.create(
            data={
                "user_id": current_user.id,
                "total_xp": 0,
                "level": 1,
                "completed_actions": {}  # Initialize empty completed actions
            }
        )
    
    logger.info(f"Retrieved user progress for user {current_user.id}: {progress.completed_actions}")
    return progress

@router.post("/update", response_model=UserProgressSchema)
async def update_user_progress(
    update: UserProgressUpdate,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Received update request for user {current_user.id}: {update}")
    
    # Get existing progress or create new
    progress = await db.userprogress.find_first(
        where={"user_id": current_user.id}
    )
    
    if not progress:
        # Initialize user progress
        progress = await db.userprogress.create(
            data={
                "user_id": current_user.id,
                "total_xp": update.xp_gained,
                "level": 1,
                "last_completed_node": update.node_id,
                "completed_actions": update.completed_actions or {}
            }
        )
        logger.info(f"Created new progress with completed_actions: {progress.completed_actions}")
        return progress
    
    # Update existing progress
    new_total_xp = progress.total_xp + update.xp_gained
    
    # Update completed actions if provided
    updated_actions = progress.completed_actions
    if update.completed_actions:
        if not updated_actions:
            updated_actions = {}
        
        # Ensure we're working with a dictionary
        current_actions = updated_actions if isinstance(updated_actions, dict) else {}
        new_actions = update.completed_actions if isinstance(update.completed_actions, dict) else {}
        
        logger.info(f"Current completed_actions: {current_actions}")
        logger.info(f"Updating with new actions: {new_actions}")
        
        # Update the dictionary
        current_actions.update(new_actions)
        updated_actions = current_actions
        
        logger.info(f"Updated completed_actions: {updated_actions}")
    
    # Calculate level based on XP
    new_level = 1
    if new_total_xp <= 50:
        new_level = 1
    elif new_total_xp <= 150:
        new_level = 2
    elif new_total_xp <= 300:
        new_level = 3
    elif new_total_xp <= 500:
        new_level = 4
    elif new_total_xp <= 750:
        new_level = 5
    else:
        new_level = 6
    
    try:
        # Update the progress record in the database
        progress = await db.userprogress.update(
            where={"id": progress.id},
            data={
                "total_xp": new_total_xp,
                "level": new_level,
                "last_completed_node": update.node_id,
                "completed_actions": updated_actions
            }
        )
        logger.info(f"Final progress state: {progress.completed_actions}")
        return progress
    except Exception as e:
        # No rollback needed in Prisma - automatic transaction handling
        logger.error(f"Error updating progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update progress: {str(e)}"
        ) 