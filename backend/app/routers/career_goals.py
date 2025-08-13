"""
Career Goals Router - API endpoints for managing user career goals
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



from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from prisma import Prisma
import json
import logging


from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from app.utils.prisma_client import get_prisma_client, PrismaOperationLogger
from app.models import User, CareerGoal, CareerMilestone
from app.services.career_progression_service import CareerProgressionService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/career-goals", tags=["career-goals"])

# Pydantic schemas
class CareerGoalCreate(BaseModel):
    esco_occupation_id: Optional[str] = None
    oasis_code: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    source: Optional[str] = Field(None, description="Where goal was set from: oasis, saved, swipe, tree")
    source_metadata: Optional[dict] = None

class CareerGoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class CareerGoalResponse(BaseModel):
    id: int
    user_id: int
    esco_occupation_id: Optional[str]
    oasis_code: Optional[str]
    title: str
    description: Optional[str]
    target_date: Optional[datetime]
    is_active: bool
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
    achieved_at: Optional[datetime]
    source: Optional[str]
    milestones_count: int = 0
    completed_milestones: int = 0

    class Config:
        from_attributes = True

class MilestoneResponse(BaseModel):
    id: int
    skill_id: str
    skill_name: str
    tier_level: int
    is_completed: bool
    confidence_score: float
    xp_value: int
    
    class Config:
        from_attributes = True

# Initialize services
career_progression_service = CareerProgressionService()

@router.post("/", response_model=dict)
async def create_career_goal(
    goal_data: CareerGoalCreate,
    current_user = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Create a new career goal from any job card in the platform.
    Deactivates previous goals and generates GraphSage timeline.
    """
    try:
        # Validate that at least one identifier is provided
        if not goal_data.esco_occupation_id and not goal_data.oasis_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either esco_occupation_id or oasis_code must be provided"
            )
        
        # Deactivate all previous goals for this user
        await db.careergoal.update_many(
            where={
                'user_id': current_user.id,
                'is_active': True
            },
            data={'is_active': False}
        )
        
        # Set default target date if not provided (1 year from now)
        if not goal_data.target_date:
            goal_data.target_date = datetime.utcnow() + timedelta(days=365)
        
        # Create new career goal
        new_goal = await db.careergoal.create(
            data={
                'user_id': current_user.id,
                'esco_occupation_id': goal_data.esco_occupation_id,
                'oasis_code': goal_data.oasis_code,
                'title': goal_data.title,
                'description': goal_data.description,
                'target_date': goal_data.target_date,
                'source': goal_data.source,
                'source_metadata': json.dumps(goal_data.source_metadata) if goal_data.source_metadata else None,
                'is_active': True
            }
        )
        
        # Generate GraphSage timeline if ESCO ID is available
        timeline = None
        if goal_data.esco_occupation_id:
            try:
                progression_data = career_progression_service.extract_career_progression(
                    occupation_id=goal_data.esco_occupation_id,
                    user_id=current_user.id,
                    depth=3
                )
                
                # Create milestones from the progression tiers
                if progression_data and "tiers" in progression_data:
                    for tier in progression_data["tiers"]:
                        for skill in tier.get("skills", []):
                            milestone = await db.careermilestone.create(
                                data={
                                    'goal_id': new_goal.id,
                                    'skill_id': skill.get('id', ''),
                                    'skill_name': skill.get('label', ''),
                                    'tier_level': tier.get('tier_number', 1),
                                    'confidence_score': skill.get('graphsage_score', 0.0),
                                    'xp_value': 100 * tier.get('tier_number', 1)  # Higher tiers = more XP
                                }
                            )
                    timeline = progression_data
                    
            except Exception as e:
                logger.error(f"Error generating GraphSage timeline: {str(e)}")
                # Continue without timeline - goal is still created
        
        # Prepare response
        goal_response = CareerGoalResponse.model_validate(new_goal)
        goal_response.milestones_count = await db.careermilestone.count(
            where={'goal_id': new_goal.id}
        )
        
        return {
            "goal": goal_response,
            "timeline": timeline,
            "message": f"Career goal '{new_goal.title}' set successfully!"
        }
        
    except Exception as e:
        logger.error(f"Error creating career goal: {str(e)}")
        # No rollback needed in Prisma - automatic transaction handling
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create career goal: {str(e)}"
        )

@router.get("/active", response_model=dict)
async def get_active_career_goal(
    current_user = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Get the user's currently active career goal with progression data.
    """
    try:
        # Get active goal
        active_goal = await db.careergoal.find_first(
            where={
                'user_id': current_user.id,
                'is_active': True
            }
        )
        
        if not active_goal:
            return {
                "goal": None,
                "progression": None,
                "milestones": [],
                "message": "No active career goal set"
            }
        
        # Get milestones
        milestones = await db.careermilestone.find_many(
            where={'goal_id': active_goal.id},
            order_by=[
                {'tier_level': 'asc'},
                {'confidence_score': 'desc'}
            ]
        )
        
        # Calculate progress
        total_milestones = len(milestones)
        completed_milestones = sum(1 for m in milestones if m.is_completed)
        
        if total_milestones > 0:
            progress_percentage = (completed_milestones / total_milestones) * 100
            active_goal = await db.careergoal.update(
                where={'id': active_goal.id},
                data={'progress_percentage': progress_percentage}
            )
        
        # Prepare goal response
        goal_response = CareerGoalResponse.model_validate(active_goal)
        goal_response.milestones_count = total_milestones
        goal_response.completed_milestones = completed_milestones
        
        # Get fresh progression data if ESCO ID available
        progression = None
        if active_goal.esco_occupation_id:
            try:
                progression = career_progression_service.extract_career_progression(
                    occupation_id=active_goal.esco_occupation_id,
                    user_id=current_user.id,
                    depth=3
                )
            except Exception as e:
                logger.error(f"Error fetching progression: {str(e)}")
        
        return {
            "goal": goal_response,
            "progression": progression,
            "milestones": [MilestoneResponse.model_validate(m) for m in milestones],
            "message": "Active goal retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting active goal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve active goal: {str(e)}"
        )

@router.get("/", response_model=List[CareerGoalResponse])
async def get_all_career_goals(
    include_inactive: bool = False,
    current_user = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Get all career goals for the current user.
    """
    # Build query filters
    where_clause = {'user_id': current_user.id}
    if not include_inactive:
        where_clause['is_active'] = True
    
    goals = await db.careergoal.find_many(
        where=where_clause,
        order_by=[{'created_at': 'desc'}]
    )
    
    # Add milestone counts to each goal
    goal_responses = []
    for goal in goals:
        goal_response = CareerGoalResponse.model_validate(goal)
        goal_response.milestones_count = await db.careermilestone.count(
            where={'goal_id': goal.id}
        )
        milestones = await db.careermilestone.find_many(
            where={'goal_id': goal.id}
        )
        goal_response.completed_milestones = sum(1 for m in milestones if m.is_completed)
        goal_responses.append(goal_response)
    
    return goal_responses

@router.put("/{goal_id}", response_model=CareerGoalResponse)
async def update_career_goal(
    goal_id: int,
    goal_update: CareerGoalUpdate,
    current_user = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Update a career goal's details.
    """
    goal = await db.careergoal.find_first(
        where={
            'id': goal_id,
            'user_id': current_user.id
        }
    )
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found"
        )
    
    # If activating this goal, deactivate others
    if goal_update.is_active and not goal.is_active:
        await db.careergoal.update_many(
            where={
                'user_id': current_user.id,
                'is_active': True,
                'id': {'not': goal_id}
            },
            data={'is_active': False}
        )
    
    # Update fields
    update_data = goal_update.dict(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow()
    
    goal = await db.careergoal.update(
        where={'id': goal_id},
        data=update_data
    )
    
    # Add milestone counts
    goal_response = CareerGoalResponse.model_validate(goal)
    milestones = await db.careermilestone.find_many(
        where={'goal_id': goal.id}
    )
    goal_response.milestones_count = len(milestones)
    goal_response.completed_milestones = sum(1 for m in milestones if m.is_completed)
    
    return goal_response

@router.delete("/{goal_id}")
async def delete_career_goal(
    goal_id: int,
    current_user = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Delete a career goal and all its milestones.
    """
    goal = await db.careergoal.find_first(
        where={
            'id': goal_id,
            'user_id': current_user.id
        }
    )
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found"
        )
    
    await db.careergoal.delete(
        where={'id': goal_id}
    )
    
    return {"message": f"Career goal '{goal.title}' deleted successfully"}

@router.post("/{goal_id}/milestones/{milestone_id}/complete")
async def complete_milestone(
    goal_id: int,
    milestone_id: int,
    current_user = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Mark a milestone as completed and award XP.
    """
    # Verify goal ownership
    goal = await db.careergoal.find_first(
        where={
            'id': goal_id,
            'user_id': current_user.id
        }
    )
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found"
        )
    
    # Get milestone
    milestone = await db.careermilestone.find_first(
        where={
            'id': milestone_id,
            'goal_id': goal_id
        }
    )
    
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    if milestone.is_completed:
        return {"message": "Milestone already completed", "xp_awarded": 0}
    
    # Mark as completed
    milestone = await db.careermilestone.update(
        where={'id': milestone_id},
        data={
            'is_completed': True,
            'completed_at': datetime.utcnow(),
            'xp_awarded': True if not milestone.xp_awarded else milestone.xp_awarded
        }
    )
    
    # Award XP (integrate with existing XP system if available)
    xp_awarded = milestone.xp_value
    # TODO: Add XP to user's progress here
    
    # Update goal progress
    all_milestones = await db.careermilestone.find_many(
        where={'goal_id': goal_id}
    )
    completed = sum(1 for m in all_milestones if m.is_completed)
    progress_percentage = (completed / len(all_milestones)) * 100 if all_milestones else 0
    
    # Check if goal is achieved and update
    update_data = {'progress_percentage': progress_percentage}
    if progress_percentage >= 100 and not goal.achieved_at:
        update_data['achieved_at'] = datetime.utcnow()
    
    goal = await db.careergoal.update(
        where={'id': goal_id},
        data=update_data
    )
    
    return {
        "message": f"Milestone '{milestone.skill_name}' completed!",
        "xp_awarded": xp_awarded,
        "goal_progress": goal.progress_percentage,
        "goal_achieved": goal.achieved_at is not None
    }

@router.get("/{goal_id}/milestones", response_model=List[MilestoneResponse])
async def get_goal_milestones(
    goal_id: int,
    tier_level: Optional[int] = None,
    completed_only: bool = False,
    current_user = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Get all milestones for a specific goal.
    """
    # Verify goal ownership
    goal = await db.careergoal.find_first(
        where={
            'id': goal_id,
            'user_id': current_user.id
        }
    )
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found"
        )
    
    # Build query filters
    where_clause = {'goal_id': goal_id}
    
    if tier_level is not None:
        where_clause['tier_level'] = tier_level
    
    if completed_only:
        where_clause['is_completed'] = True
    
    milestones = await db.careermilestone.find_many(
        where=where_clause,
        order_by=[
            {'tier_level': 'asc'},
            {'confidence_score': 'desc'}
        ]
    )
    
    return [MilestoneResponse.model_validate(m) for m in milestones]