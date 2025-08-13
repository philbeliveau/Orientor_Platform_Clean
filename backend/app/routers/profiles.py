from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
import logging
from prisma import Prisma
from app.utils.prisma_client import get_prisma_client, PrismaOperationLogger, get_prisma_transaction
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
import uuid
from app.services.profile_completion_service import ProfileCompletionCalculator, CompletionAction

# Configure logging FIRST
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Optional ML services - graceful fallback if not available
try:
    from app.services.Oasisembedding_service import process_user_embedding, process_user_oasis_embedding
    OASIS_EMBEDDING_AVAILABLE = True
    logger.info("✅ OaSIS embedding service available")
except ImportError as e:
    logger.warning(f"⚠️ OaSIS embedding service not available (requires torch): {e}")
    OASIS_EMBEDDING_AVAILABLE = False

try:
    from app.services.esco_embedding_service384 import process_user_esco_embeddings
    ESCO_EMBEDDING_AVAILABLE = True
    logger.info("✅ ESCO embedding service available")
except ImportError as e:
    logger.warning(f"⚠️ ESCO embedding service not available (requires torch): {e}")
    ESCO_EMBEDDING_AVAILABLE = False

try:
    from app.services.peer_matching_service import generate_peer_suggestions
    PEER_MATCHING_AVAILABLE = True
    logger.info("✅ Peer matching service available")
except ImportError as e:
    logger.warning(f"⚠️ Peer matching service not available (requires ML dependencies): {e}")
    PEER_MATCHING_AVAILABLE = False

# Add a more detailed log message to help with debugging
logger.info("Profiles router module loaded with unified authentication")

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = None
    gpa: Optional[float] = None
    hobbies: Optional[str] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    unique_quality: Optional[str] = None
    story: Optional[str] = None
    favorite_movie: Optional[str] = None
    favorite_book: Optional[str] = None
    favorite_celebrities: Optional[str] = None
    learning_style: Optional[str] = None
    interests: Optional[Union[str, List[str]]] = None
    # Add skill fields
    creativity: Optional[float] = None
    leadership: Optional[float] = None
    digital_literacy: Optional[float] = None
    critical_thinking: Optional[float] = None
    problem_solving: Optional[float] = None
    # Job-related fields for embeddings
    job_title: Optional[str] = None
    industry: Optional[str] = None
    years_experience: Optional[int] = None
    education_level: Optional[str] = None
    career_goals: Optional[str] = None
    skills: Optional[List[str]] = None
    analytical_thinking: Optional[float] = None
    attention_to_detail: Optional[float] = None
    collaboration: Optional[float] = None
    adaptability: Optional[float] = None
    independence: Optional[float] = None
    evaluation: Optional[float] = None
    decision_making: Optional[float] = None
    stress_tolerance: Optional[float] = None

    class Config:
        from_attributes = True


class CompletionActionResponse(BaseModel):
    """Response model for a completion action."""
    id: str
    title: str
    description: str
    url: str
    category: str
    weight: float
    estimated_time: str


class ProfileCompletionResponse(BaseModel):
    """Response model for profile completion analysis."""
    overall_percentage: float
    category_scores: Dict[str, float]
    next_actions: List[CompletionActionResponse]
    recommendation_eligible: bool
    missing_critical_data: List[str]

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/test")
def test_profiles_route():
    return {"message": "Profiles router is working"}

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0)
    sex: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = Field(None, ge=1)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    hobbies: Optional[str] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    unique_quality: Optional[str] = None
    story: Optional[str] = None
    favorite_movie: Optional[str] = None
    favorite_book: Optional[str] = None
    favorite_celebrities: Optional[str] = None
    learning_style: Optional[str] = None
    interests: Optional[Union[str, List[str]]] = None
    # Add skill fields
    creativity: Optional[float] = Field(None, ge=0, le=5)
    leadership: Optional[float] = Field(None, ge=0, le=5)
    digital_literacy: Optional[float] = Field(None, ge=0, le=5)
    critical_thinking: Optional[float] = Field(None, ge=0, le=5)
    problem_solving: Optional[float] = Field(None, ge=0, le=5)
    # Add cognitive traits
    analytical_thinking: Optional[float] = Field(None, ge=0, le=5)
    attention_to_detail: Optional[float] = Field(None, ge=0, le=5)
    collaboration: Optional[float] = Field(None, ge=0, le=5)
    adaptability: Optional[float] = Field(None, ge=0, le=5)
    independence: Optional[float] = Field(None, ge=0, le=5)
    evaluation: Optional[float] = Field(None, ge=0, le=5)
    decision_making: Optional[float] = Field(None, ge=0, le=5)
    stress_tolerance: Optional[float] = Field(None, ge=0, le=5)
    # Job-related fields for embeddings
    job_title: Optional[str] = None
    industry: Optional[str] = None
    years_experience: Optional[int] = Field(None, ge=0)
    education_level: Optional[str] = None
    career_goals: Optional[str] = None
    skills: Optional[List[str]] = None

@router.get("/me", response_model=ProfileResponse)
async def get_profile(
    current_user = Depends(get_current_user), 
    db: Prisma = Depends(get_prisma_client)
):
    # Initialize operation logger
    operation_logger = PrismaOperationLogger("profiles")
    
    try:
        logger.info(f"Attempting to get profile for user ID: {current_user.id}")
        
        # Convert SQLAlchemy query to Prisma
        profile = await db.user_profiles.find_first(
            where={"user_id": current_user.id}
        )
        
        operation_logger.log_query_conversion(
            f"db.query(UserProfile).filter(UserProfile.user_id == {current_user.id}).first()",
            f"db.user_profiles.find_first(where={{\"user_id\": {current_user.id}}})",
            "profile_lookup"
        )
        
        if not profile:
            logger.info(f"No profile found for user ID: {current_user.id}, creating a new one")
            # Create a blank profile using Prisma
            profile = await db.user_profiles.create(
                data={"user_id": current_user.id}
            )
            
            operation_logger.log_query_conversion(
                "UserProfile(user_id=current_user.id); db.add(profile); db.commit()",
                f"db.user_profiles.create(data={{\"user_id\": {current_user.id}}})",
                "profile_creation"
            )
        
        # Get user skills using Prisma
        skills = await db.user_skills.find_first(
            where={"user_id": current_user.id}
        )
        
        operation_logger.log_query_conversion(
            f"db.query(UserSkill).filter(UserSkill.user_id == {current_user.id}).first()",
            f"db.user_skills.find_first(where={{\"user_id\": {current_user.id}}})",
            "skills_lookup"
        )
        
        response = ProfileResponse.model_validate(profile)
        response.id = current_user.id
        
        # Add all skills to response if they exist
        if skills:
            response.creativity = skills.creativity
            response.leadership = skills.leadership
            response.digital_literacy = skills.digital_literacy
            response.critical_thinking = skills.critical_thinking
            response.problem_solving = skills.problem_solving
            response.analytical_thinking = skills.analytical_thinking
            response.attention_to_detail = skills.attention_to_detail
            response.collaboration = skills.collaboration
            response.adaptability = skills.adaptability
            response.independence = skills.independence
            response.evaluation = skills.evaluation
            response.decision_making = skills.decision_making
            response.stress_tolerance = skills.stress_tolerance
        
        return response
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")

@router.put("/update")
async def update_profile(
    profile_update: ProfileUpdate,
    db: Prisma = Depends(get_prisma_client),
    current_user = Depends(get_current_user)
):
    # Initialize operation logger
    operation_logger = PrismaOperationLogger("profiles")
    
    try:
        logger.info(f"Attempting to update profile for user ID: {current_user.id}")
        
        # Use transaction for complex update operation
        async with get_prisma_transaction() as transaction_db:
            # Get the current profile using Prisma
            profile = await transaction_db.user_profiles.find_first(
                where={"user_id": current_user.id}
            )
            
            operation_logger.log_query_conversion(
                f"db.query(UserProfile).filter(UserProfile.user_id == {current_user.id}).first()",
                f"transaction_db.user_profiles.find_first(where={{\"user_id\": {current_user.id}}})",
                "profile_lookup_for_update"
            )
            
            if not profile:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            # Extract skill fields from profile update
            skill_fields = {
                "creativity": profile_update.creativity,
                "leadership": profile_update.leadership,
                "digital_literacy": profile_update.digital_literacy,
                "critical_thinking": profile_update.critical_thinking,
                "problem_solving": profile_update.problem_solving,
                "analytical_thinking": profile_update.analytical_thinking,
                "attention_to_detail": profile_update.attention_to_detail,
                "collaboration": profile_update.collaboration,
                "adaptability": profile_update.adaptability,
                "independence": profile_update.independence,
                "evaluation": profile_update.evaluation,
                "decision_making": profile_update.decision_making,
                "stress_tolerance": profile_update.stress_tolerance
            }
            
            # Update user skills using Prisma
            skills = await transaction_db.user_skills.find_first(
                where={"user_id": current_user.id}
            )
            
            if not skills:
                # Create new skills record
                skills_data = {"user_id": current_user.id}
                skills_data.update({k: v for k, v in skill_fields.items() if v is not None})
                skills = await transaction_db.user_skills.create(data=skills_data)
                
                operation_logger.log_query_conversion(
                    "UserSkill(user_id=current_user.id); db.add(skills)",
                    f"transaction_db.user_skills.create(data={{...}})",
                    "skills_creation"
                )
            else:
                # Update existing skills
                update_skills_data = {k: v for k, v in skill_fields.items() if v is not None}
                if update_skills_data:
                    skills = await transaction_db.user_skills.update(
                        where={"id": skills.id},
                        data=update_skills_data
                    )
                    
                    operation_logger.log_query_conversion(
                        "setattr(skills, field, value) for each field",
                        f"transaction_db.user_skills.update(where={{\"id\": {skills.id}}}, data={{...}})",
                        "skills_update"
                    )
            
            # Update profile fields (excluding skill fields)
            update_data = profile_update.dict(
                exclude={
                    "creativity", "leadership", "digital_literacy", "critical_thinking",
                    "problem_solving", "analytical_thinking", "attention_to_detail",
                    "collaboration", "adaptability", "independence", "evaluation",
                    "decision_making", "stress_tolerance"
                },
                exclude_unset=True
            )
            
            logger.info(f"Updating profile fields: {list(update_data.keys())}")
            
            if update_data:
                profile = await transaction_db.user_profiles.update(
                    where={"id": profile.id},
                    data=update_data
                )
                
                operation_logger.log_query_conversion(
                    "setattr(profile, field, value) for each field; db.commit()",
                    f"transaction_db.user_profiles.update(where={{\"id\": {profile.id}}}, data={{...}})",
                    "profile_update"
                )
        
        # Generate new embedding using the centralized service
        try:
            # Create a UUID v5 based on the user ID (namespace UUID + user ID)
            user_id_str = str(current_user.id)
            namespace_uuid = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # UUID namespace DNS
            user_uuid = str(uuid.uuid5(namespace_uuid, user_id_str))
            
            logger.info(f"Original user ID: {user_id_str}, Generated UUID: {user_uuid}")
            
            # Fetch RIASEC scores using Prisma raw query
            riasec_result = await db.execute_raw(
                """
                SELECT r_score, i_score, a_score, s_score, e_score, c_score, top_3_code
                FROM gca_results 
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT 1
                """,
                current_user.id
            )
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

            operation_logger.log_query_conversion(
                "db.execute(riasec_query, {'user_id': current_user.id}).fetchone()",
                f"db.execute_raw(query, {current_user.id})",
                "riasec_lookup"
            )
            
            # Fetch saved recommendations using Prisma raw query
            recommendations_result = await db.execute_raw(
                """
                SELECT label 
                FROM saved_recommendations 
                WHERE user_id = $1
                """,
                current_user.id
            )
            
            operation_logger.log_query_conversion(
                "db.execute(recommendations_query, {'user_id': current_user.id}).fetchall()",
                f"db.execute_raw(query, {current_user.id})",
                "recommendations_lookup"
            )
            
            # Prepare complete profile data for embedding generation
            profile_data = {
                "profile": {
                    "user_id": current_user.id,
                    "name": profile.name,
                    "age": profile.age,
                    "sex": profile.sex,
                    "major": profile.major,
                    "year": profile.year,
                    "gpa": profile.gpa,
                    "hobbies": profile.hobbies,
                    "country": profile.country,
                    "state_province": profile.state_province,
                    "unique_quality": profile.unique_quality,
                    "story": profile.story,
                    "favorite_movie": profile.favorite_movie,
                    "favorite_book": profile.favorite_book,
                    "favorite_celebrities": profile.favorite_celebrities,
                    "learning_style": profile.learning_style,
                    "interests": profile.interests,
                    "job_title": profile.job_title,
                    "industry": profile.industry,
                    "years_experience": profile.years_experience,
                    "education_level": profile.education_level,
                    "career_goals": profile.career_goals,
                    "skills": profile.skills
                },
                "skills": {
                    "creativity": skills.creativity,
                    "leadership": skills.leadership,
                    "digital_literacy": skills.digital_literacy,
                    "critical_thinking": skills.critical_thinking,
                    "problem_solving": skills.problem_solving,
                    "analytical_thinking": skills.analytical_thinking,
                    "attention_to_detail": skills.attention_to_detail,
                    "collaboration": skills.collaboration,
                    "adaptability": skills.adaptability,
                    "independence": skills.independence,
                    "evaluation": skills.evaluation,
                    "decision_making": skills.decision_making,
                    "stress_tolerance": skills.stress_tolerance
                }
            }

            # Add RIASEC data if available (Prisma raw query returns list of dicts)
            if riasec_result and len(riasec_result) > 0:
                riasec_row = riasec_result[0]
                profile_data["riasec"] = {
                    "r_score": float(riasec_row["r_score"]),
                    "i_score": float(riasec_row["i_score"]),
                    "a_score": float(riasec_row["a_score"]),
                    "s_score": float(riasec_row["s_score"]),
                    "e_score": float(riasec_row["e_score"]),
                    "c_score": float(riasec_row["c_score"]),
                    "top_3_code": riasec_row["top_3_code"]
                }
                logger.info(f"RIASEC scores added to profile data: {profile_data['riasec']}")
            else:
                logger.warning("No RIASEC scores found for user")
                profile_data["riasec"] = {}

            # Add saved recommendations if available (Prisma raw query returns list of dicts)
            if recommendations_result and len(recommendations_result) > 0:
                profile_data["saved_recommendations"] = [
                    {"label": row["label"]}
                    for row in recommendations_result
                ]
                logger.info(f"Added {len(recommendations_result)} saved recommendations to profile data")
            else:
                logger.warning("No saved recommendations found for user")
                profile_data["saved_recommendations"] = []
            
            # Log the complete profile data
            logger.info("Complete profile data for embedding generation:")
            logger.info(f"Profile data: {profile_data}")
            
            # Optional embedding generation - only if ML services available
            if OASIS_EMBEDDING_AVAILABLE:
                try:
                    success = process_user_embedding(db, current_user.id, profile_data)
                    if not success:
                        logger.warning(f"Failed to generate embedding for user ID: {current_user.id}")
                    else:
                        logger.info(f"Successfully generated new embedding for user ID: {current_user.id}")
                except Exception as e:
                    logger.error(f"Error in embedding generation: {str(e)}")
                    success = False
            else:
                logger.info("⚠️ Embedding generation skipped - ML services not available")
                success = True  # Don't block profile update
                
            # Generate peer suggestions if available and embedding succeeded
            if PEER_MATCHING_AVAILABLE and success:
                try:
                    peer_success = generate_peer_suggestions(db, current_user.id)
                    if peer_success:
                        logger.info(f"Successfully generated peer suggestions for user ID: {current_user.id}")
                    else:
                        logger.warning(f"Failed to generate peer suggestions for user ID: {current_user.id}")
                except Exception as e:
                    logger.error(f"Error in peer matching: {str(e)}")
            elif not PEER_MATCHING_AVAILABLE:
                logger.info("⚠️ Peer matching skipped - service not available")
                
            # Generate the OaSIS embedding if available
            if OASIS_EMBEDDING_AVAILABLE:
                try:
                    logger.info(f"Generating OaSIS embedding for user ID: {current_user.id}")
                    oasis_success = process_user_oasis_embedding(db, current_user.id)
                    if oasis_success:
                        logger.info(f"OaSIS embedding generated and stored successfully for user ID: {current_user.id}")
                    else:
                        logger.warning(f"Failed to generate or store OaSIS embedding for user ID: {current_user.id}")
                except Exception as e:
                    logger.error(f"Error in OaSIS embedding process: {str(e)}")
            else:
                logger.info("⚠️ OaSIS embedding skipped - service not available")
                
            # Generate the ESCO embeddings if available
            if ESCO_EMBEDDING_AVAILABLE:
                try:
                    logger.info(f"Generating ESCO embeddings for user ID: {current_user.id}")
                    esco_success = process_user_esco_embeddings(db, current_user.id)
                    if esco_success:
                        logger.info(f"ESCO embeddings generated and stored successfully for user ID: {current_user.id}")
                    else:
                        logger.warning(f"Failed to generate or store ESCO embeddings for user ID: {current_user.id}")
                except Exception as e:
                    logger.error(f"Error in ESCO embedding process: {str(e)}")
            else:
                logger.info("⚠️ ESCO embedding skipped - service not available")
                
        except Exception as e:
            logger.error(f"Error in embedding/peer suggestion process: {str(e)}")
            # Don't fail the profile update if embedding generation fails
        
        logger.info(f"Successfully updated profile for user ID: {current_user.id}")
        return {"message": "Profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        # Prisma handles transaction rollback automatically on exception
        operation_logger.log_performance_metric("profile_update_error", 0, 0)
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Profile Completion Endpoints - MUST come BEFORE parameterized routes
@router.get("/completion", response_model=ProfileCompletionResponse)
async def get_profile_completion(
    current_user = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """Get profile completion analysis for the current user."""
    try:
        logger.info(f"Getting profile completion for user {current_user.clerk_user_id}")
        
        # Calculate profile completion
        completion_result = ProfileCompletionCalculator.calculate_completion(
            db, current_user.clerk_user_id
        )
        
        # Convert CompletionAction objects to response models
        next_actions = [
            CompletionActionResponse(
                id=action.id,
                title=action.title,
                description=action.description,
                url=action.url,
                category=action.category,
                weight=action.weight,
                estimated_time=action.estimated_time
            )
            for action in completion_result.next_actions
        ]
        
        return ProfileCompletionResponse(
            overall_percentage=completion_result.overall_percentage,
            category_scores=completion_result.category_scores,
            next_actions=next_actions,
            recommendation_eligible=completion_result.recommendation_eligible,
            missing_critical_data=completion_result.missing_critical_data
        )
        
    except Exception as e:
        logger.error(f"Error getting profile completion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating profile completion: {str(e)}")


@router.get("/completion/recommendations", response_model=List[CompletionActionResponse])
async def get_completion_recommendations(
    limit: int = 5,
    current_user = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """Get next recommended actions for profile completion."""
    try:
        logger.info(f"Getting completion recommendations for user {current_user.clerk_user_id}")
        
        # Calculate profile completion
        completion_result = ProfileCompletionCalculator.calculate_completion(
            db, current_user.clerk_user_id
        )
        
        # Convert CompletionAction objects to response models
        recommendations = [
            CompletionActionResponse(
                id=action.id,
                title=action.title,
                description=action.description,
                url=action.url,
                category=action.category,
                weight=action.weight,
                estimated_time=action.estimated_time
            )
            for action in completion_result.next_actions[:limit]
        ]
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting completion recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting completion recommendations: {str(e)}")


# Parameterized routes MUST come LAST to avoid conflicts with specific routes
@router.get("/{user_id}", response_model=ProfileResponse)
async def get_user_profile(
    user_id: int,
    current_user = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """Get profile information for a specific user."""
    # Initialize operation logger
    operation_logger = PrismaOperationLogger("profiles")
    
    try:
        logger.info(f"Attempting to get profile for user ID: {user_id}")
        
        # Convert SQLAlchemy query to Prisma
        profile = await db.user_profiles.find_first(
            where={"user_id": user_id}
        )
        
        operation_logger.log_query_conversion(
            f"db.query(UserProfile).filter(UserProfile.user_id == {user_id}).first()",
            f"db.user_profiles.find_first(where={{\"user_id\": {user_id}}})",
            "user_profile_lookup"
        )
        
        if not profile:
            logger.info(f"No profile found for user ID: {user_id}, creating a new one")
            # Create a new profile using Prisma
            profile = await db.user_profiles.create(
                data={"user_id": user_id}
            )
            
            operation_logger.log_query_conversion(
                "UserProfile(user_id=user_id); db.add(profile); db.commit()",
                f"db.user_profiles.create(data={{\"user_id\": {user_id}}})",
                "user_profile_creation"
            )
        
        # Get user skills using Prisma
        skills = await db.user_skills.find_first(
            where={"user_id": user_id}
        )
        
        operation_logger.log_query_conversion(
            f"db.query(UserSkill).filter(UserSkill.user_id == {user_id}).first()",
            f"db.user_skills.find_first(where={{\"user_id\": {user_id}}})",
            "user_skills_lookup"
        )
        
        response = ProfileResponse.model_validate(profile)
        
        # Add skills to response if they exist
        if skills:
            response.creativity = skills.creativity
            response.leadership = skills.leadership
            response.digital_literacy = skills.digital_literacy
            response.critical_thinking = skills.critical_thinking
            response.problem_solving = skills.problem_solving
            response.analytical_thinking = skills.analytical_thinking
            response.attention_to_detail = skills.attention_to_detail
            response.collaboration = skills.collaboration
            response.adaptability = skills.adaptability
            response.independence = skills.independence
            response.evaluation = skills.evaluation
            response.decision_making = skills.decision_making
            response.stress_tolerance = skills.stress_tolerance
        
        return response
    except Exception as e:
        operation_logger.log_performance_metric("user_profile_lookup_error", 0, 0)
        logger.error(f"Error retrieving profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")


# Add module-level debug message after routes are defined
logger.debug("Initializing profiles router module")
logger.debug(f"Created profiles router with routes: {[route.path for route in router.routes]}") 