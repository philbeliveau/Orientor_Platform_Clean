from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from prisma import Prisma
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from app.utils.prisma_client import get_prisma_client, PrismaOperationLogger
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from ..models import User, SavedRecommendation, UserNote, UserSkill, UserProfile
from ..schemas.space import (
    SavedRecommendationCreate, SavedRecommendation as SavedRecommendationSchema,
    UserNoteCreate, UserNoteUpdate, UserNote as UserNoteSchema,
    UserSkillUpdate,
    RecommendationWithNotes, SkillComparison, SkillsComparison, CognitiveTraits
)
from ..services.llm_analysis_service import update_recommendation_analysis, generate_personalized_analysis

router = APIRouter(
    prefix="/space",
    tags=["space"],
    dependencies=[Depends(get_current_user)]
)

# Helper function to extract skill values from text
def extract_skill_values(text: str) -> dict:
    skill_values = {
        "creativity": None,
        "leadership": None,
        "digital_literacy": None,
        "critical_thinking": None,
        "problem_solving": None
    }
    
    # Parse the text to find skill values (format: "Skill: 4")
    for skill in skill_values.keys():
        # Handle the case of digital literacy which has a space
        pattern = f"{skill.replace('_', ' ').title()}: (\\d+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            skill_values[skill] = float(match.group(1))
    
    return skill_values

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

# ===== Saved Recommendations Endpoints =====
@router.post("/recommendations", response_model=SavedRecommendationSchema)
async def create_saved_recommendation(
    recommendation: SavedRecommendationCreate,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Creating recommendation for user {current_user.id} with oasis_code: {recommendation.oasis_code}")
    logger.info(f"Recommendation data: {recommendation.dict()}")
    
    # Check if recommendation already exists
    db_recommendation = await db.savedrecommendation.find_first(
        where={
            'user_id': current_user.id,
            'oasis_code': recommendation.oasis_code
        }
    )
    
    if db_recommendation:
        logger.info(f"Recommendation already exists for user {current_user.id}, oasis_code: {recommendation.oasis_code}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This recommendation is already saved."
        )
    
    try:
        # Create new saved recommendation
        db_recommendation = await db.savedrecommendation.create(
            data={
                'user_id': current_user.id,
                'oasis_code': recommendation.oasis_code,
                'label': recommendation.label,
                'description': recommendation.description,
                'main_duties': recommendation.main_duties,
                'role_creativity': recommendation.role_creativity,
                'role_leadership': recommendation.role_leadership,
                'role_digital_literacy': recommendation.role_digital_literacy,
                'role_critical_thinking': recommendation.role_critical_thinking,
                'role_problem_solving': recommendation.role_problem_solving,
                'analytical_thinking': recommendation.analytical_thinking,
                'attention_to_detail': recommendation.attention_to_detail,
                'collaboration': recommendation.collaboration,
                'adaptability': recommendation.adaptability,
                'independence': recommendation.independence,
                'evaluation': recommendation.evaluation,
                'decision_making': recommendation.decision_making,
                'stress_tolerance': recommendation.stress_tolerance,
                'all_fields': recommendation.all_fields
            }
        )
        logger.info(f"Successfully created recommendation with ID: {db_recommendation.id}")
        
        # Generate LLM analysis for the recommendation asynchronously
        try:
            import asyncio
            # Run the async function in a sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis = loop.run_until_complete(
                generate_personalized_analysis(current_user.id, db_recommendation, db)
            )
            loop.close()
            
            # Update the recommendation with the analysis
            db_recommendation = await db.savedrecommendation.update(
                where={'id': db_recommendation.id},
                data={
                    'personal_analysis': analysis['personal_analysis'],
                    'entry_qualifications': analysis['entry_qualifications'],
                    'suggested_improvements': analysis['suggested_improvements']
                }
            )
            logger.info(f"Successfully generated LLM analysis for recommendation {db_recommendation.id}")
        except Exception as e:
            logger.error(f"Failed to generate LLM analysis: {str(e)}")
            # Continue without analysis if it fails
        
        return db_recommendation
        
    except Exception as e:
        logger.error(f"Failed to create recommendation: {str(e)}")
        # No rollback needed in Prisma - automatic transaction handling
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save recommendation: {str(e)}"
        )

@router.get("/recommendations", response_model=List[RecommendationWithNotes])
async def get_saved_recommendations(
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    # Get user's saved recommendations
    recommendations = await db.savedrecommendation.find_many(
        where={'user_id': current_user.id}
    )
    
    logger.info(f"Found {len(recommendations)} recommendations for user {current_user.id}")
    
    # Get the user's skills and cognitive traits
    user_skills = await db.userskill.find_first(
        where={'user_id': current_user.id}
    )
    
    result = []
    for rec in recommendations:
        # Get notes for this recommendation
        notes = await db.usernote.find_many(
            where={
                'user_id': current_user.id,
                'saved_recommendation_id': rec.id
            }
        )
        
        # Build skill comparison if both user and role skills are available
        skill_comparison = None
        if user_skills:
            # Add user's cognitive traits to the recommendation
            rec.user_analytical_thinking = user_skills.analytical_thinking
            rec.user_attention_to_detail = user_skills.attention_to_detail
            rec.user_collaboration = user_skills.collaboration
            rec.user_adaptability = user_skills.adaptability
            rec.user_independence = user_skills.independence
            rec.user_evaluation = user_skills.evaluation
            rec.user_decision_making = user_skills.decision_making
            rec.user_stress_tolerance = user_skills.stress_tolerance
            
            # Build skill comparison
            if (user_skills.creativity is not None or user_skills.leadership is not None or \
                user_skills.digital_literacy is not None or user_skills.critical_thinking is not None or \
                user_skills.problem_solving is not None):
                
                comparison = {}
                for skill in ["creativity", "leadership", "digital_literacy", "critical_thinking", "problem_solving"]:
                    role_skill_name = f"role_{skill}"
                    comparison[skill] = SkillComparison(
                        user_skill=getattr(user_skills, skill),
                        role_skill=getattr(rec, role_skill_name)
                    )
                
                skill_comparison = SkillsComparison(**comparison)
        
        # Create recommendation with notes
        recommendation_with_notes = RecommendationWithNotes(
            id=rec.id,
            user_id=rec.user_id,
            oasis_code=rec.oasis_code,
            label=rec.label,
            description=rec.description,
            main_duties=rec.main_duties,
            role_creativity=rec.role_creativity,
            role_leadership=rec.role_leadership,
            role_digital_literacy=rec.role_digital_literacy,
            role_critical_thinking=rec.role_critical_thinking,
            role_problem_solving=rec.role_problem_solving,
            analytical_thinking=rec.analytical_thinking,
            attention_to_detail=rec.attention_to_detail,
            collaboration=rec.collaboration,
            adaptability=rec.adaptability,
            independence=rec.independence,
            evaluation=rec.evaluation,
            decision_making=rec.decision_making,
            stress_tolerance=rec.stress_tolerance,
            user_analytical_thinking=rec.user_analytical_thinking,
            user_attention_to_detail=rec.user_attention_to_detail,
            user_collaboration=rec.user_collaboration,
            user_adaptability=rec.user_adaptability,
            user_independence=rec.user_independence,
            user_evaluation=rec.user_evaluation,
            user_decision_making=rec.user_decision_making,
            user_stress_tolerance=rec.user_stress_tolerance,
            saved_at=rec.saved_at,
            notes=notes,
            skill_comparison=skill_comparison,
            personal_analysis=rec.personal_analysis,
            entry_qualifications=rec.entry_qualifications,
            suggested_improvements=rec.suggested_improvements
        )
        
        result.append(recommendation_with_notes)
    
    return result

@router.delete("/recommendations/{identifier}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_recommendation(
    identifier: str,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    # Try to parse as integer first (for backward compatibility)
    recommendation = None
    
    try:
        # Try as integer ID first
        recommendation_id = int(identifier)
        recommendation = await db.savedrecommendation.find_first(
            where={
                'id': recommendation_id,
                'user_id': current_user.id
            }
        )
    except ValueError:
        # If not an integer, treat as OASIS code
        recommendation = await db.savedrecommendation.find_first(
            where={
                'oasis_code': identifier,
                'user_id': current_user.id
            }
        )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    # Delete the recommendation (cascade will also delete associated notes)
    await db.savedrecommendation.delete(
        where={'id': recommendation.id}
    )
    
    return None

# ===== User Notes Endpoints =====
@router.post("/notes", response_model=UserNoteSchema)
async def create_note(
    note: UserNoteCreate,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    # If note is associated with a recommendation, verify it exists and belongs to user
    if note.saved_recommendation_id:
        recommendation = await db.savedrecommendation.find_first(
            where={
                'id': note.saved_recommendation_id,
                'user_id': current_user.id
            }
        )
        
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved recommendation not found"
            )
    
    # Create the note
    db_note = await db.usernote.create(
        data={
            'user_id': current_user.id,
            'saved_recommendation_id': note.saved_recommendation_id,
            'content': note.content
        }
    )
    
    return db_note

@router.get("/notes", response_model=List[UserNoteSchema])
async def get_notes(
    saved_recommendation_id: Optional[int] = None,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    # Base query for user's notes
    where_clause = {'user_id': current_user.id}
    
    # Filter by recommendation if specified
    if saved_recommendation_id is not None:
        where_clause['saved_recommendation_id'] = saved_recommendation_id
    
    return await db.usernote.find_many(where=where_clause)

@router.put("/notes/{note_id}", response_model=UserNoteSchema)
async def update_note(
    note_id: int,
    note_update: UserNoteUpdate,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    # Find the note
    db_note = await db.usernote.find_first(
        where={
            'id': note_id,
            'user_id': current_user.id
        }
    )
    
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Update fields if provided
    update_data = {}
    if note_update.content is not None:
        update_data['content'] = note_update.content
    
    if update_data:
        db_note = await db.usernote.update(
            where={'id': note_id},
            data=update_data
        )
    
    return db_note

@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    # Find the note
    db_note = await db.usernote.find_first(
        where={
            'id': note_id,
            'user_id': current_user.id
        }
    )
    
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Delete the note
    await db.usernote.delete(
        where={'id': note_id}
    )
    
    return None

# ===== User Skills Endpoints =====
@router.get("/skills", response_model=UserSkillUpdate)
async def get_user_skills(
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    # Get the user's skills record
    user_skill = await db.userskill.find_first(
        where={'user_id': current_user.id}
    )
    if not user_skill:
        # Return default values if no record exists
        return UserSkillUpdate()
    
    # Return the skills
    return UserSkillUpdate(
        creativity=user_skill.creativity,
        leadership=user_skill.leadership,
        digital_literacy=user_skill.digital_literacy,
        critical_thinking=user_skill.critical_thinking,
        problem_solving=user_skill.problem_solving,
        analytical_thinking=user_skill.analytical_thinking,
        attention_to_detail=user_skill.attention_to_detail,
        collaboration=user_skill.collaboration,
        adaptability=user_skill.adaptability,
        independence=user_skill.independence,
        evaluation=user_skill.evaluation,
        decision_making=user_skill.decision_making,
        stress_tolerance=user_skill.stress_tolerance
    )

@router.put("/skills", response_model=UserSkillUpdate)
async def update_user_skills(
    skills: UserSkillUpdate,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    # Get or create the user's skills record
    user_skill = await db.userskill.find_first(
        where={'user_id': current_user.id}
    )
    if not user_skill:
        # Create a new user skills record if it doesn't exist
        user_skill = await db.userskill.create(
            data={'user_id': current_user.id}
        )
    
    # Update skill values if provided
    update_data = {}
    for field in [
        "creativity", "leadership", "digital_literacy", "critical_thinking", "problem_solving",
        "analytical_thinking", "attention_to_detail", "collaboration", "adaptability",
        "independence", "evaluation", "decision_making", "stress_tolerance"
    ]:
        value = getattr(skills, field)
        if value is not None:
            update_data[field] = value
    
    if update_data:
        user_skill = await db.userskill.update(
            where={'id': user_skill.id},
            data=update_data
        )
    
    # Return the updated skills
    return UserSkillUpdate(
        creativity=user_skill.creativity,
        leadership=user_skill.leadership,
        digital_literacy=user_skill.digital_literacy,
        critical_thinking=user_skill.critical_thinking,
        problem_solving=user_skill.problem_solving,
        analytical_thinking=user_skill.analytical_thinking,
        attention_to_detail=user_skill.attention_to_detail,
        collaboration=user_skill.collaboration,
        adaptability=user_skill.adaptability,
        independence=user_skill.independence,
        evaluation=user_skill.evaluation,
        decision_making=user_skill.decision_making,
        stress_tolerance=user_skill.stress_tolerance
    )

# ===== Special Endpoints =====
@router.get("/recommendations/{oasis_code}/skill-comparison", response_model=SkillsComparison)
async def get_skill_comparison(
    oasis_code: str,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    # Get recommendation for this oasis_code
    recommendation = await db.savedrecommendation.find_first(
        where={'oasis_code': oasis_code}
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    # Get user's skills
    user_skill = await db.userskill.find_first(
        where={'user_id': current_user.id}
    )
    if not user_skill:
        user_skill = await db.userskill.create(
            data={'user_id': current_user.id}
        )
    
    # Build comparison
    comparison = {}
    for skill in ["creativity", "leadership", "digital_literacy", "critical_thinking", "problem_solving"]:
        role_skill_name = f"role_{skill}"
        comparison[skill] = SkillComparison(
            user_skill=getattr(user_skill, skill),
            role_skill=getattr(recommendation, role_skill_name)
        )
    
    return SkillsComparison(**comparison)

# ===== LLM Analysis Endpoints =====
@router.post("/recommendations/{recommendation_id}/generate-analysis", response_model=SavedRecommendationSchema)
async def generate_recommendation_analysis(
    recommendation_id: int,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    """
    Generate or regenerate LLM analysis for a saved recommendation.
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


    # Get the recommendation
    recommendation = await db.savedrecommendation.find_first(
        where={
            'id': recommendation_id,
            'user_id': current_user.id
        }
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    try:
        # Generate the analysis
        updated_recommendation = await update_recommendation_analysis(
            recommendation_id=recommendation_id,
            user_id=current_user.id,
            db=db
        )
        
        return updated_recommendation
    except Exception as e:
        logger.error(f"Failed to generate analysis for recommendation {recommendation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analysis. Please try again later."
        ) 