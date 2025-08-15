from fastapi import APIRouter, Depends, HTTPException, status, Header
from prisma import Prisma
from sqlalchemy import text
from app.utils.error_handling import handle_prisma_error, log_database_operation
from app.utils.prisma_client import get_prisma_client, PrismaOperationLogger
from app.models import User, UserProfile
from app.models.personality_profiles import PersonalityAssessment, PersonalityResponse, PersonalityProfile
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid
import json
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["onboarding"])

from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user

async def get_current_user_with_onboarding(
    current_user: User = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """Get user info from Clerk and sync with local database"""
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


    try:
        # The get_current_user already returns a User object, so we can return it directly
        # No need for additional database lookup as it's already synced
        return current_user
    except Exception as e:
        logger.error(f"Error getting user from Clerk: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication")

# Pydantic schemas for onboarding
class OnboardingResponse(BaseModel):
    questionId: str
    question: str
    response: str
    timestamp: Optional[str] = None

class OnboardingData(BaseModel):
    responses: List[OnboardingResponse] = []  # Make optional with default empty list
    psychProfile: Optional[Dict[str, Any]] = None

class OnboardingStatus(BaseModel):
    isComplete: bool
    hasStarted: bool
    currentStep: Optional[str] = None
    completedAt: Optional[datetime] = None

class PsychProfileCreate(BaseModel):
    hexaco: Dict[str, float]
    riasec: Dict[str, float]
    topTraits: List[str]
    description: str

@router.get("/onboarding/status")
async def get_onboarding_status(
    current_user: User = Depends(get_current_user_with_onboarding),
    db: Prisma = Depends(get_prisma_client)
):
    """Get the current onboarding status for a user - STANDARDIZED RESPONSE"""
    try:
        logger.info(f"🔍 Getting onboarding status for user ID: {current_user.id}")
        
        # SIMPLIFIED: Single source of truth - database field
        onboarding_completed = getattr(current_user, 'onboarding_completed', False)
        logger.info(f"📊 User {current_user.id} onboarding_completed: {onboarding_completed}")
        
        # If not completed, check if they have started
        has_started = False
        if not onboarding_completed:
            assessment = await db.personality_assessments.find_first(
                where={
                    'user_id': current_user.id,
                    'assessment_type': 'onboarding'
                }
            )
            has_started = assessment is not None
        
        # FALLBACK FIX: If they have a profile but database field is False, fix it
        if not onboarding_completed:
            personality_profile = await db.personality_profile.find_first(
                where={'user_id': current_user.id}
            )
            
            if personality_profile:
                logger.info(f"🔧 Fixing onboarding_completed for user {current_user.id} - has profile but field is False")
                await db.users.update(
                    where={'id': current_user.id},
                    data={'onboarding_completed': True}
                )
                onboarding_completed = True
        
        # STANDARDIZED RESPONSE: Always return same format for consistency
        return {
            "onboarding_completed": onboarding_completed,
            "has_started": has_started or onboarding_completed,
            "is_complete": onboarding_completed,
            "message": "Onboarding completed" if onboarding_completed else "Onboarding needed"
        }
        
    except Exception as e:
        logger.error(f"Error getting onboarding status: {str(e)}")
        # Safe fallback response
        return {
            "onboarding_completed": False,
            "has_started": False,
            "is_complete": False,
            "message": "Error checking status - assuming onboarding needed"
        }

@router.post("/onboarding/start")
async def start_onboarding(
    current_user: User = Depends(get_current_user_with_onboarding),
    db: Prisma = Depends(get_prisma_client)
):
    """Start a new onboarding session"""
    try:
        log_database_operation("start_onboarding", current_user.id)
        logger.info(f"Starting onboarding for user ID: {current_user.id}")
        
        # Check if user already has an active onboarding session
        existing_assessment = await db.personality_assessments.find_first(
            where={
                'user_id': current_user.id,
                'assessment_type': 'onboarding',
                'status': 'in_progress'
            }
        )
        
        if existing_assessment:
            logger.info(f"User {current_user.id} already has active onboarding session")
            return {
                "session_id": str(existing_assessment.session_id),
                "message": "Onboarding session already in progress"
            }
        
        # Create new assessment session
        assessment = await db.personality_assessments.create(
            data={
                'user_id': current_user.id,
                'assessment_type': 'onboarding',
                'assessment_version': 'v1.0',
                'session_id': str(uuid.uuid4()),
                'status': 'in_progress',
                'started_at': datetime.utcnow(),
                'total_items': 9,  # 9 onboarding questions
                'completed_items': 0
            }
        )
        
        logger.info(f"Created onboarding session {assessment.session_id} for user {current_user.id}")
        
        return {
            "session_id": str(assessment.session_id),
            "message": "Onboarding session started successfully"
        }
        
    except Exception as e:
        raise handle_prisma_error(e, "starting onboarding session")

@router.post("/onboarding/response")
async def save_onboarding_response(
    response_data: OnboardingResponse,
    current_user: User = Depends(get_current_user_with_onboarding),
    db: Prisma = Depends(get_prisma_client)
):
    """Save a single onboarding response"""
    try:
        logger.info(f"Saving onboarding response for user ID: {current_user.id}")
        
        # Get the current assessment session
        assessment = await db.personality_assessments.find_first(
            where={
                'user_id': current_user.id,
                'assessment_type': 'onboarding',
                'status': 'in_progress'
            }
        )
        
        if not assessment:
            # Create a new assessment session if none exists
            logger.info(f"Creating new onboarding session for user {current_user.id}")
            assessment = await db.personality_assessments.create(
                data={
                    'user_id': current_user.id,
                    'assessment_type': 'onboarding',
                    'assessment_version': 'v1.0',
                    'session_id': str(uuid.uuid4()),
                    'status': 'in_progress',
                    'started_at': datetime.utcnow(),
                    'total_items': 9,  # 9 onboarding questions
                    'completed_items': 0
                }
            )
        
        # Save the response
        personality_response = await db.personality_responses.create(
            data={
                'assessment_id': assessment.id,
                'item_id': response_data.questionId,
                'item_type': 'open_ended',  # Use valid constraint value
                'response_value': json.dumps({
                    'question': response_data.question,
                    'response': response_data.response
                }),
                'created_at': datetime.utcnow()
            }
        )
        
        # Update assessment progress
        await db.personality_assessments.update(
            where={'id': assessment.id},
            data={
                'completed_items': assessment.completed_items + 1,
                'updated_at': datetime.utcnow()
            }
        )
        
        # No need for explicit commit in Prisma
        
        logger.info(f"Saved response for question {response_data.questionId}")
        
        return {
            "message": "Response saved successfully",
            "progress": assessment.completed_items,
            "total": assessment.total_items
        }
        
    except HTTPException:
        raise
    except Exception as db_e:
        raise handle_prisma_error(db_e, "saving onboarding response")
    except Exception as e:
        logger.error(f"Error saving response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save response: {str(e)}")

@router.post("/onboarding/complete")
async def complete_onboarding(
    onboarding_data: OnboardingData,
    current_user: User = Depends(get_current_user_with_onboarding),
    db: Prisma = Depends(get_prisma_client)
):
    """Complete the onboarding process and generate psychological profile"""
    try:
        logger.info(f"Completing onboarding for user ID: {current_user.id}")
        
        # Get or create assessment session
        assessment = await db.personality_assessments.find_first(
            where={
                'user_id': current_user.id,
                'assessment_type': 'onboarding'
            }
        )
        
        if not assessment:
            # Create new assessment session
            assessment = await db.personality_assessments.create(
                data={
                    'user_id': current_user.id,
                    'assessment_type': 'onboarding',
                    'assessment_version': 'v1.0',
                    'session_id': str(uuid.uuid4()),
                    'status': 'in_progress',
                    'started_at': datetime.utcnow(),
                    'total_items': max(len(onboarding_data.responses), 1),
                    'completed_items': len(onboarding_data.responses)
                }
            )
        
        # Save responses if provided
        if onboarding_data.responses:
            for response_data in onboarding_data.responses:
                existing_response = await db.personality_responses.find_first(
                    where={
                        'assessment_id': assessment.id,
                        'item_id': response_data.questionId
                    }
                )
                
                if not existing_response:
                    await db.personality_responses.create(
                        data={
                            'assessment_id': assessment.id,
                            'item_id': response_data.questionId,
                            'item_type': 'open_ended',
                            'response_value': json.dumps({
                                'question': response_data.question,
                                'response': response_data.response
                            }),
                            'created_at': datetime.utcnow()
                        }
                    )
        
        # Create or update psychological profile
        existing_profile = await db.personality_profile.find_first(
            where={
                'user_id': current_user.id,
                'assessment_id': assessment.id
            }
        )
        
        if onboarding_data.psychProfile and not existing_profile:
            await db.personality_profile.create(
                data={
                    'user_id': current_user.id,
                    'assessment_id': assessment.id,
                    'profile_type': 'hexaco',
                    'scores': onboarding_data.psychProfile,
                    'narrative_description': onboarding_data.psychProfile.get('description', ''),
                    'assessment_version': 'v1.0',
                    'computed_at': datetime.utcnow(),
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            )
        elif existing_profile and onboarding_data.psychProfile:
            await db.personality_profile.update(
                where={'id': existing_profile.id},
                data={
                    'scores': onboarding_data.psychProfile,
                    'narrative_description': onboarding_data.psychProfile.get('description', ''),
                    'updated_at': datetime.utcnow()
                }
            )
        
        # Mark assessment as completed
        await db.personality_assessments.update(
            where={'id': assessment.id},
            data={
                'status': 'completed',
                'completed_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        )
        
        # SIMPLIFIED: Update user onboarding completion (no complex cache logic)
        logger.info(f"🔄 Updating onboarding_completed for user {current_user.id}")
        
        await db.users.update(
            where={'id': current_user.id},
            data={'onboarding_completed': True}
        )
        
        logger.info(f"✅ Successfully marked user {current_user.id} onboarding as completed")
        
        return {
            "message": "Onboarding completed successfully",
            "assessment_id": assessment.id,
            "profile_created": onboarding_data.psychProfile is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during completing onboarding: {str(e)}")
        raise handle_prisma_error(e, "completing onboarding")

@router.get("/onboarding/profile")
async def get_onboarding_profile(
    current_user: User = Depends(get_current_user_with_onboarding),
    db: Prisma = Depends(get_prisma_client)
):
    """Get the user's onboarding psychological profile"""
    try:
        logger.info(f"Getting onboarding profile for user ID: {current_user.id}")
        
        personality_profile = await db.personality_profile.find_first(
            where={'user_id': current_user.id}
        )
        
        if not personality_profile:
            raise HTTPException(status_code=404, detail="No onboarding profile found")
        
        return {
            "profile": personality_profile.scores,
            "description": personality_profile.narrative_description,
            "created_at": personality_profile.created_at,
            "assessment_version": personality_profile.assessment_version
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting onboarding profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

@router.get("/onboarding/responses")
async def get_onboarding_responses(
    current_user: User = Depends(get_current_user_with_onboarding),
    db: Prisma = Depends(get_prisma_client)
):
    """Get all onboarding responses for a user"""
    try:
        logger.info(f"Getting onboarding responses for user ID: {current_user.id}")
        
        # Get the assessment
        assessment = await db.personality_assessments.find_first(
            where={
                'user_id': current_user.id,
                'assessment_type': 'onboarding'
            }
        )
        
        if not assessment:
            return {"responses": []}
        
        # Get all responses
        responses = await db.personality_responses.find_many(
            where={'assessment_id': assessment.id}
        )
        
        formatted_responses = []
        for response in responses:
            formatted_responses.append({
                "questionId": response.item_id,
                "question": response.response_value.get("question", ""),
                "response": response.response_value.get("response", ""),
                "timestamp": response.created_at
            })
        
        return {
            "responses": formatted_responses,
            "assessment_status": assessment.status,
            "completed_items": assessment.completed_items,
            "total_items": assessment.total_items
        }
        
    except Exception as e:
        logger.error(f"Error getting onboarding responses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get responses: {str(e)}")

@router.delete("/onboarding/reset")
async def reset_onboarding(
    current_user: User = Depends(get_current_user_with_onboarding),
    db: Prisma = Depends(get_prisma_client)
):
    """Reset onboarding progress for a user"""
    try:
        logger.info(f"Resetting onboarding for user ID: {current_user.id}")
        
        # Delete existing assessment and responses
        assessments = await db.personality_assessments.find_many(
            where={
                'user_id': current_user.id,
                'assessment_type': 'onboarding'
            }
        )
        
        for assessment in assessments:
            # Delete responses first (foreign key constraint)
            await db.personality_responses.delete_many(
                where={'assessment_id': assessment.id}
            )
            
            # Delete profiles
            await db.personality_profile.delete_many(
                where={'assessment_id': assessment.id}
            )
            
            # Delete assessment
            await db.personality_assessments.delete(
                where={'id': assessment.id}
            )
        
        # No need for explicit commit in Prisma
        
        logger.info(f"Reset onboarding for user {current_user.id}")
        
        return {"message": "Onboarding reset successfully"}
        
    except Exception as db_e:
        logger.error(f"Database error resetting onboarding: {str(db_e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_e)}")
    except Exception as e:
        logger.error(f"Error resetting onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset onboarding: {str(e)}")

@router.post("/onboarding/skip")
async def skip_onboarding(
    current_user: User = Depends(get_current_user_with_onboarding),
    db: Prisma = Depends(get_prisma_client)
):
    """Skip onboarding for a user by creating a default profile"""
    try:
        logger.info(f"Skipping onboarding for user ID: {current_user.id}")
        
        # Check if user already has a profile
        existing_profile = await db.personality_profile.find_first(
            where={'user_id': current_user.id}
        )
        
        if existing_profile:
            logger.info(f"User {current_user.id} already has a profile, skipping")
            return {"message": "User already has a profile"}
        
        # Create a fake assessment for tracking
        assessment = await db.personality_assessments.create(
            data={
                'user_id': current_user.id,
                'assessment_type': 'onboarding',
                'assessment_version': 'v1.0',
                'session_id': str(uuid.uuid4()),
                'status': 'completed',
                'started_at': datetime.utcnow(),
                'completed_at': datetime.utcnow(),
                'total_items': 1,
                'completed_items': 1
            }
        )
        
        # Create a default personality profile
        default_profile = await db.personality_profile.create(
            data={
                'user_id': current_user.id,
                'assessment_id': assessment.id,
                'profile_type': 'hexaco',
                'scores': {
                    'hexaco': {
                        'honesty': 0.5,
                        'emotionality': 0.5,
                        'extraversion': 0.5,
                        'agreeableness': 0.5,
                        'conscientiousness': 0.5,
                        'openness': 0.5
                    },
                    'riasec': {
                        'realistic': 0.5,
                        'investigative': 0.5,
                        'artistic': 0.5,
                        'social': 0.5,
                        'enterprising': 0.5,
                        'conventional': 0.5
                    },
                    'topTraits': ['Balanced', 'Adaptable', 'Versatile']
                },
                'narrative_description': 'This user chose to skip the onboarding assessment. Default balanced profile assigned.',
                'assessment_version': 'v1.0',
                'computed_at': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        )
        
        # Update user onboarding completion status
        await db.users.update(
            where={'id': current_user.id},
            data={'onboarding_completed': True}
        )
        # No need for explicit commit in Prisma
        
        logger.info(f"Successfully skipped onboarding for user {current_user.id}")
        
        return {
            "message": "Onboarding skipped successfully",
            "profile_created": True,
            "assessment_id": assessment.id
        }
        
    except Exception as db_e:
        raise handle_prisma_error(db_e, "skipping onboarding")
    except Exception as e:
        logger.error(f"Error skipping onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to skip onboarding: {str(e)}")
