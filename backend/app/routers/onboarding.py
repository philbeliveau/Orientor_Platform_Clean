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

@router.get("/onboarding/status", response_model=OnboardingStatus)
async def get_onboarding_status(
    current_user: User = Depends(get_current_user_with_onboarding),
    db: Prisma = Depends(get_prisma_client)
):
    """Get the current onboarding status for a user"""
    try:
        logger.info(f"🔍 ONBOARDING ROUTER: Getting status for user ID: {current_user.id}")
        
        # FIRST: Check the database field (authoritative source)
        onboarding_completed_field = getattr(current_user, 'onboarding_completed', None)
        logger.info(f"🔍 Database field onboarding_completed: {onboarding_completed_field}")
        
        if onboarding_completed_field:
            logger.info(f"✅ User {current_user.id} completed onboarding (database field = True)")
            # If database says complete, return complete status
            return OnboardingStatus(
                isComplete=True,
                hasStarted=True,
                currentStep=None,  # No current step if complete
                completedAt=current_user.updated_at  # Use user update time as fallback
            )
        
        # FALLBACK: Check if user has completed onboarding by looking for personality profile
        personality_profile = await db.personalityprofile.find_first(
            where={'user_id': current_user.id}
        )
        
        # Check if user has started onboarding
        assessment = await db.personality_assessments.find_first(
            where={
                'user_id': current_user.id,
                'assessment_type': 'onboarding'
            }
        )
        
        has_started = assessment is not None
        is_complete = personality_profile is not None
        
        logger.info(f"🔍 Fallback check - has_started: {has_started}, is_complete: {is_complete}")
        
        # If they have a profile but database field is not set, update it
        if is_complete and not onboarding_completed_field:
            logger.info(f"🔄 Updating database field for user {current_user.id} based on personality profile")
            current_user.onboarding_completed = True
            # No need for explicit commit in Prisma
            db.refresh(current_user)
        
        return OnboardingStatus(
            isComplete=is_complete,
            hasStarted=has_started,
            currentStep="profile_generation" if has_started and not is_complete else None,
            completedAt=personality_profile.created_at if personality_profile else None
        )
        
    except Exception as e:
        logger.error(f"Error getting onboarding status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get onboarding status: {str(e)}")

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
                'response_value': {
                    'question': response_data.question,
                    'response': response_data.response
                },
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
        
        # Get the assessment session - first try in_progress, then any onboarding session
        assessment = await db.personality_assessments.find_first(
            where={
                'user_id': current_user.id,
                'assessment_type': 'onboarding',
                'status': 'in_progress'
            }
        )
        
        if not assessment:
            # Try to find any onboarding assessment for this user
            assessment = await db.personality_assessments.find_first(
                where={
                    'user_id': current_user.id,
                    'assessment_type': 'onboarding'
                }
            )
            
            if assessment:
                # Update the found assessment to in_progress so we can complete it
                assessment.status = "in_progress"
                assessment.updated_at = datetime.utcnow()
            else:
                # Create a new assessment session if none exists
                logger.info(f"Creating new assessment session for user {current_user.id} during completion")
                assessment = await db.personality_assessments.create(
                    data={
                        'user_id': current_user.id,
                        'assessment_type': 'onboarding',
                        'assessment_version': 'v1.0',
                        'session_id': str(uuid.uuid4()),
                        'status': 'in_progress',
                        'started_at': datetime.utcnow(),
                        'total_items': max(len(onboarding_data.responses), 1),  # At least 1 to avoid division by zero
                        'completed_items': len(onboarding_data.responses)
                    }
                )
        
        # Save any remaining responses (only if responses provided)
        if onboarding_data.responses:
            for response_data in onboarding_data.responses:
                existing_response = await db.personality_responses.find_first(
                    where={
                        'assessment_id': assessment.id,
                        'item_id': response_data.questionId
                    }
                )
                
                if not existing_response:
                    personality_response = await db.personality_responses.create(
                        data={
                            'assessment_id': assessment.id,
                            'item_id': response_data.questionId,
                            'item_type': 'open_ended',  # Use valid constraint value
                            'response_value': {
                                'question': response_data.question,
                                'response': response_data.response
                            },
                            'created_at': datetime.utcnow()
                        }
                    )
        
        # Create psychological profile if one doesn't already exist
        existing_profile = await db.personalityprofile.find_first(
            where={
                'user_id': current_user.id,
                'assessment_id': assessment.id
            }
        )
        
        if onboarding_data.psychProfile and not existing_profile:
            personality_profile = await db.personalityprofile.create(
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
            # Update existing profile
            await db.personalityprofile.update(
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
        
        # CRITICAL: Mark the user as having completed onboarding
        logger.info(f"🔄 BEFORE UPDATE: user {current_user.id} onboarding_completed = {getattr(current_user, 'onboarding_completed', 'FIELD_NOT_FOUND')}")
        
        # Update user onboarding completion status
        await db.user.update(
            where={'id': current_user.id},
            data={'onboarding_completed': True}
        )
        logger.info(f"✅ Database update successful for user {current_user.id}")
        
        # Refresh the current_user object to ensure we have the latest data
        try:
            db.refresh(current_user)
            logger.info(f"✅ User object refreshed from database")
        except Exception as refresh_error:
            logger.error(f"⚠️ Failed to refresh user object: {refresh_error}")
        
        # Verify the database update was successful
        logger.info(f"🔍 FINAL VERIFICATION: user {current_user.id} onboarding_completed = {current_user.onboarding_completed}")
        
        # Double-check by querying the database directly
        try:
            verification_result = db.execute(
                text("SELECT onboarding_completed FROM users WHERE id = :user_id"),
                {"user_id": current_user.id}
            ).fetchone()
            if verification_result:
                db_value = verification_result[0]
                logger.info(f"🔍 DATABASE DIRECT QUERY: user {current_user.id} onboarding_completed = {db_value}")
                if not db_value:
                    logger.error(f"❌ CRITICAL: Database still shows onboarding_completed=False after commit!")
            else:
                logger.error(f"❌ CRITICAL: Could not find user {current_user.id} in database!")
        except Exception as verify_error:
            logger.error(f"⚠️ Could not verify database update: {verify_error}")
        
        # CRITICAL FIX: Invalidate user cache using the proper auth system function
        # This MUST happen AFTER successful database commit to ensure cache reflects new data
        cache_invalidation_success = False
        try:
            import asyncio
            from ..utils.optimized_clerk_auth import invalidate_user_session_cache
            
            if hasattr(current_user, 'clerk_user_id') and current_user.clerk_user_id:
                logger.info(f"🔄 Starting cache invalidation for clerk_user_id: {current_user.clerk_user_id}")
                
                # Run the async cache invalidation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(invalidate_user_session_cache(current_user.clerk_user_id))
                    cache_invalidation_success = result
                    if result:
                        logger.info(f"✅ Successfully invalidated user session cache for {current_user.clerk_user_id}")
                    else:
                        logger.warning(f"⚠️ Cache invalidation returned False for {current_user.clerk_user_id} (user may not have been cached)")
                except Exception as invalidation_error:
                    logger.error(f"❌ Cache invalidation function failed: {invalidation_error}")
                    raise invalidation_error
                finally:
                    loop.close()
            else:
                logger.warning(f"⚠️ No clerk_user_id found for user {current_user.id}, cannot invalidate cache")
                logger.info(f"🔍 User attributes: {[attr for attr in dir(current_user) if not attr.startswith('_')]}")
        except Exception as cache_error:
            logger.error(f"❌ Could not invalidate user cache: {cache_error}")
            # Don't fail the request due to cache issues, but log it prominently
            logger.error(f"⚠️ IMPORTANT: Cache invalidation failed - subsequent status checks may return stale data!")
        
        logger.info(f"✅ Completed onboarding for user {current_user.id}")
        logger.info(f"📋 COMPLETION SUMMARY:")
        logger.info(f"📋   - Database updated: {current_user.onboarding_completed}")
        logger.info(f"📋   - Cache invalidated: {cache_invalidation_success}")
        logger.info(f"📋   - Assessment ID: {assessment.id}")
        logger.info(f"📋   - Profile created: {onboarding_data.psychProfile is not None}")
        
        return {
            "message": "Onboarding completed successfully",
            "assessment_id": assessment.id,
            "profile_created": onboarding_data.psychProfile is not None
        }
        
    except HTTPException:
        raise
    except Exception as db_e:
        raise handle_prisma_error(db_e, "completing onboarding")
    except Exception as e:
        logger.error(f"Error completing onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete onboarding: {str(e)}")

@router.get("/onboarding/profile")
async def get_onboarding_profile(
    current_user: User = Depends(get_current_user_with_onboarding),
    db: Prisma = Depends(get_prisma_client)
):
    """Get the user's onboarding psychological profile"""
    try:
        logger.info(f"Getting onboarding profile for user ID: {current_user.id}")
        
        personality_profile = await db.personalityprofile.find_first(
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
            await db.personalityprofile.delete_many(
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
        existing_profile = await db.personalityprofile.find_first(
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
        default_profile = await db.personalityprofile.create(
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
        await db.user.update(
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
