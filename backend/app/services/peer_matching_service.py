import os
import logging
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, select
import ast
import subprocess
import json
from datetime import datetime, timezone

from app.models.user_profile import UserProfile
from app.models.personality_profiles import PersonalityProfile
from app.services.Oasisembedding_service import generate_embedding
from app.services.LLMcompatibility_service import compatibility_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_embedding(embedding_data: Any) -> Optional[List[float]]:
    """
    Parse embedding data into a list of floats
    
    Args:
        embedding_data: Embedding data from the database
        
    Returns:
        List of floats or None if parsing fails
    """
    try:
        if isinstance(embedding_data, (list, np.ndarray)):
            return list(embedding_data)
        elif isinstance(embedding_data, str):
            # Handle string representation of list
            embedding_data = embedding_data.strip()
            if embedding_data.startswith('[') and embedding_data.endswith(']'):
                return [float(x) for x in embedding_data[1:-1].split(',')]
            else:
                # Try using ast.literal_eval for safer parsing
                return ast.literal_eval(embedding_data)
        else:
            logger.error(f"Unexpected embedding type: {type(embedding_data)}")
            return None
    except Exception as e:
        logger.error(f"Error parsing embedding: {str(e)}")
        return None

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Cosine similarity score (between -1 and 1)
    """
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_users_with_embeddings(db: Session) -> List[Dict[str, Any]]:
    """
    Get all users and generate their embeddings on-the-fly
    
    Args:
        db: Database session
        
    Returns:
        List of user data including embeddings
    """
    try:
        # Get all user profiles
        profiles = db.query(UserProfile).all()
        users = []
        
        for profile in profiles:
            # Generate embedding for this profile
            profile_data = {
                "job_title": profile.job_title,
                "industry": profile.industry,
                "years_experience": profile.years_experience,
                "education_level": profile.education_level,
                "career_goals": profile.career_goals,
                "skills": profile.skills if profile.skills else [],
                "interests": profile.interests if isinstance(profile.interests, str) else " ".join(profile.interests) if profile.interests else ""
            }
            
            embedding = generate_embedding(profile_data)
            if embedding is not None:
                users.append({
                    "user_id": profile.user_id,
                    "embedding": embedding
                })
        
        logger.info(f"Generated embeddings for {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error getting users with embeddings: {str(e)}")
        return []

def find_similar_peers(db: Session, user_id: str, embedding: List[float], top_n: int = 5) -> List[Tuple[str, float]]:
    """
    Find similar peers for a given user
    
    Args:
        db: Database session
        user_id: Clerk user ID of the user
        embedding: User's embedding
        top_n: Number of similar peers to find
        
    Returns:
        List of tuples (peer_id, similarity_score)
    """
    try:
        # Get all other users
        other_profiles = db.query(UserProfile).join(User).filter(User.clerk_user_id != user_id).all()
        
        # Calculate similarities
        similarities = []
        for profile in other_profiles:
            try:
                # Generate embedding for this profile
                profile_data = {
                    "job_title": profile.job_title,
                    "industry": profile.industry,
                    "years_experience": profile.years_experience,
                    "education_level": profile.education_level,
                    "career_goals": profile.career_goals,
                    "skills": profile.skills if profile.skills else [],
                    "interests": profile.interests if isinstance(profile.interests, str) else " ".join(profile.interests) if profile.interests else ""
                }
                
                other_embedding = generate_embedding(profile_data)
                if other_embedding is not None:
                    other_embedding = np.array(other_embedding, dtype=float)
                    user_embedding = np.array(embedding, dtype=float)
                    similarity = cosine_similarity(user_embedding, other_embedding)
                    similarities.append((profile.user_id, similarity))
            except Exception as e:
                logger.error(f"Error calculating similarity for user {profile.user_id}: {str(e)}")
                continue
        
        # Sort by similarity and get top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]
    except Exception as e:
        logger.error(f"Error finding similar peers: {str(e)}")
        return []

def update_suggested_peers(db: Session, user_id: str, similar_peers: List[Tuple[str, float]]) -> bool:
    """
    Update the suggested_peers table for a user
    
    Args:
        db: Database session
        user_id: ID of the user
        similar_peers: List of tuples (peer_id, similarity_score)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Delete existing suggestions
        query = text("""
            DELETE FROM suggested_peers
            WHERE user_id = :user_id
        """)
        
        db.execute(query, {"user_id": user_id})
        
        # Insert new suggestions
        for peer_id, similarity in similar_peers:
            query = text("""
                INSERT INTO suggested_peers (user_id, suggested_id, similarity)
                VALUES (:user_id, :peer_id, :similarity)
            """)
            
            db.execute(query, {
                "user_id": user_id,
                "peer_id": peer_id,
                "similarity": float(similarity)
            })
        
        db.commit()
        logger.info(f"Updated suggested peers for user {user_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating suggested peers: {str(e)}")
        return False

def generate_peer_suggestions(db: Session, user_id: str, top_n: int = 5) -> bool:
    """
    Generate peer suggestions for a user
    
    Args:
        db: Database session
        user_id: ID of the user
        top_n: Number of similar peers to find
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get user's embedding
        query = text("""
            SELECT embedding
            FROM user_profiles
            WHERE user_id = :user_id
        """)
        
        result = db.execute(query, {"user_id": user_id}).fetchone()
        
        if not result or not result.embedding:
            logger.error(f"No embedding found for user {user_id}")
            return False
        
        # Parse embedding
        embedding = parse_embedding(result.embedding)
        if not embedding:
            logger.error(f"Failed to parse embedding for user {user_id}")
            return False
        
        # Find similar peers
        similar_peers = find_similar_peers(db, user_id, embedding, top_n)
        
        if not similar_peers:
            logger.warning(f"No similar peers found for user {user_id}")
            return False
        
        # Update suggested_peers table
        success = update_suggested_peers(db, user_id, similar_peers)
        
        return success
    except Exception as e:
        logger.error(f"Error generating peer suggestions: {str(e)}")
        return False

async def ensure_compatibility_vector(db: Session, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Ensure user has a compatibility vector, generating if needed.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Compatibility vector or None if failed
    """
    try:
        # Check if compatibility vector exists
        query = text("""
            SELECT compatibility_vector
            FROM user_profiles
            WHERE user_id = :user_id
        """)
        
        result = db.execute(query, {"user_id": user_id}).fetchone()
        
        if result and result.compatibility_vector:
            vector = result.compatibility_vector
            # Check if vector is fresh (less than 30 days old)
            if isinstance(vector, dict) and "generated_at" in vector:
                generated_at = datetime.fromisoformat(vector["generated_at"].replace('Z', '+00:00'))
                days_old = (datetime.now(timezone.utc) - generated_at).days
                if days_old < 30:
                    return vector
        
        # Generate new compatibility vector
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            logger.error(f"User profile not found for user {user_id}")
            return None
        
        compatibility_vector = await compatibility_service.extract_compatibility_vector(profile, db)
        
        # Store in database
        update_query = text("""
            UPDATE user_profiles
            SET compatibility_vector = :vector
            WHERE user_id = :user_id
        """)
        
        db.execute(update_query, {
            "user_id": user_id,
            "vector": json.dumps(compatibility_vector)
        })
        db.commit()
        
        logger.info(f"Generated and stored compatibility vector for user {user_id}")
        return compatibility_vector
        
    except Exception as e:
        logger.error(f"Error ensuring compatibility vector for user {user_id}: {e}")
        return None

def calculate_compatibility_score(
    user_vector: Dict[str, Any], 
    peer_vector: Dict[str, Any],
    user_personality: Optional[Dict[str, Any]] = None,
    peer_personality: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculate multi-dimensional compatibility score between two users.
    
    Args:
        user_vector: User's compatibility vector
        peer_vector: Peer's compatibility vector
        user_personality: User's personality scores (optional)
        peer_personality: Peer's personality scores (optional)
        
    Returns:
        Compatibility score between 0 and 1
    """
    try:
        total_score = 0.0
        weight_sum = 0.0
        
        # RIASEC compatibility (weight: 0.25)
        user_riasec = set(user_vector.get("desired_riasec_codes", []))
        peer_riasec = set(peer_personality.get("riasec_scores", {}).keys() if peer_personality else [])
        if user_riasec and peer_riasec:
            riasec_overlap = len(user_riasec.intersection(peer_riasec)) / len(user_riasec.union(peer_riasec))
            total_score += riasec_overlap * 0.25
            weight_sum += 0.25
        
        # Skill complementarity (weight: 0.20)
        user_target_skills = set([skill.lower() for skill in user_vector.get("target_skill_deltas", [])])
        peer_skills = set([skill.lower() for skill in peer_vector.get("target_skill_deltas", [])])
        if user_target_skills and peer_skills:
            skill_overlap = len(user_target_skills.intersection(peer_skills)) / max(len(user_target_skills), len(peer_skills))
            total_score += skill_overlap * 0.20
            weight_sum += 0.20
        
        # Goal alignment (weight: 0.20)
        user_goals = set([goal.lower() for goal in user_vector.get("goal_overlap_keywords", [])])
        peer_goals = set([goal.lower() for goal in peer_vector.get("goal_overlap_keywords", [])])
        if user_goals and peer_goals:
            goal_overlap = len(user_goals.intersection(peer_goals)) / len(user_goals.union(peer_goals))
            total_score += goal_overlap * 0.20
            weight_sum += 0.20
        
        # Career stage compatibility (weight: 0.15)
        user_stage = user_vector.get("career_stage_preference", "any")
        peer_stage = peer_vector.get("career_stage_preference", "any")
        if user_stage == "any" or peer_stage == "any" or user_stage == peer_stage:
            total_score += 1.0 * 0.15
            weight_sum += 0.15
        
        # Industry overlap (weight: 0.10)
        user_industries = set([ind.lower() for ind in user_vector.get("industry_overlap", [])])
        peer_industries = set([ind.lower() for ind in peer_vector.get("industry_overlap", [])])
        if user_industries and peer_industries:
            industry_overlap = len(user_industries.intersection(peer_industries)) / len(user_industries.union(peer_industries))
            total_score += industry_overlap * 0.10
            weight_sum += 0.10
        
        # Personality compatibility (weight: 0.10)
        if user_personality and peer_personality:
            personality_score = calculate_personality_compatibility(
                user_vector.get("personality_compatibility", {}),
                user_personality,
                peer_personality
            )
            total_score += personality_score * 0.10
            weight_sum += 0.10
        
        # Normalize by actual weights used
        if weight_sum > 0:
            return min(total_score / weight_sum, 1.0)
        else:
            return 0.0
            
    except Exception as e:
        logger.error(f"Error calculating compatibility score: {e}")
        return 0.0

def calculate_personality_compatibility(
    user_preferences: Dict[str, Any],
    user_personality: Dict[str, Any],
    peer_personality: Dict[str, Any]
) -> float:
    """Calculate personality-based compatibility score."""
    try:
        hexaco_preferences = user_preferences.get("hexaco_preferences", {})
        user_hexaco = user_personality.get("hexaco_scores", {})
        peer_hexaco = peer_personality.get("hexaco_scores", {})
        
        if not hexaco_preferences or not peer_hexaco:
            return 0.5  # Neutral score if no data
        
        compatibility_scores = []
        
        for trait, preference in hexaco_preferences.items():
            peer_score = peer_hexaco.get(trait, 0.5)
            
            if preference == "high" and peer_score >= 0.7:
                compatibility_scores.append(1.0)
            elif preference == "medium" and 0.3 <= peer_score <= 0.7:
                compatibility_scores.append(1.0)
            elif preference == "low" and peer_score <= 0.3:
                compatibility_scores.append(1.0)
            else:
                # Partial compatibility based on distance from preference
                if preference == "high":
                    compatibility_scores.append(max(0, peer_score))
                elif preference == "low":
                    compatibility_scores.append(max(0, 1 - peer_score))
                else:  # medium
                    compatibility_scores.append(1 - abs(peer_score - 0.5) * 2)
        
        return sum(compatibility_scores) / len(compatibility_scores) if compatibility_scores else 0.5
        
    except Exception as e:
        logger.error(f"Error calculating personality compatibility: {e}")
        return 0.5

async def find_compatible_peers(
    db: Session, 
    user_id: str, 
    top_n: int = 5
) -> List[Tuple[str, float, Dict[str, Any]]]:
    """
    Find compatible peers using enhanced compatibility analysis.
    
    Args:
        db: Database session
        user_id: ID of the user
        top_n: Number of compatible peers to find
        
    Returns:
        List of tuples (peer_id, compatibility_score, explanation)
    """
    try:
        # Ensure user has compatibility vector
        user_vector = await ensure_compatibility_vector(db, user_id)
        if not user_vector:
            logger.error(f"Failed to get compatibility vector for user {user_id}")
            return []
        
        # Get user's personality data
        user_personality_stmt = select(PersonalityProfile).where(
            PersonalityProfile.user_id == user_id
        ).order_by(PersonalityProfile.computed_at.desc())
        
        user_personality_result = db.execute(user_personality_stmt).first()
        user_personality = None
        if user_personality_result:
            personality_profile = user_personality_result[0]
            user_personality = {
                "hexaco_scores": personality_profile.scores.get("hexaco", {}) if personality_profile.scores else {},
                "riasec_scores": personality_profile.scores.get("riasec", {}) if personality_profile.scores else {}
            }
        
        # Get all other users with their compatibility vectors and personality data
        query = text("""
            SELECT 
                up.user_id,
                up.compatibility_vector,
                up.name,
                up.major,
                up.year,
                up.job_title,
                up.industry
            FROM user_profiles up
            WHERE up.user_id != :user_id
            AND up.compatibility_vector IS NOT NULL
        """)
        
        results = db.execute(query, {"user_id": user_id}).fetchall()
        
        compatibility_scores = []
        
        for result in results:
            try:
                peer_id = result.user_id
                peer_vector = result.compatibility_vector
                
                if isinstance(peer_vector, str):
                    peer_vector = json.loads(peer_vector)
                
                # Get peer's personality data
                peer_personality_stmt = select(PersonalityProfile).where(
                    PersonalityProfile.user_id == peer_id
                ).order_by(PersonalityProfile.computed_at.desc())
                
                peer_personality_result = db.execute(peer_personality_stmt).first()
                peer_personality = None
                if peer_personality_result:
                    personality_profile = peer_personality_result[0]
                    peer_personality = {
                        "hexaco_scores": personality_profile.scores.get("hexaco", {}) if personality_profile.scores else {},
                        "riasec_scores": personality_profile.scores.get("riasec", {}) if personality_profile.scores else {}
                    }
                
                # Calculate compatibility score
                compatibility_score = calculate_compatibility_score(
                    user_vector, peer_vector, user_personality, peer_personality
                )
                
                # Generate explanation
                explanation = generate_compatibility_explanation(
                    user_vector, peer_vector, compatibility_score
                )
                
                compatibility_scores.append((peer_id, compatibility_score, {
                    "name": result.name,
                    "major": result.major,
                    "year": result.year,
                    "job_title": result.job_title,
                    "industry": result.industry,
                    "explanation": explanation,
                    "score_details": {
                        "overall_compatibility": compatibility_score,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }))
                
            except Exception as e:
                logger.error(f"Error processing peer {result.user_id}: {e}")
                continue
        
        # Sort by compatibility score and return top N
        compatibility_scores.sort(key=lambda x: x[1], reverse=True)
        return compatibility_scores[:top_n]
        
    except Exception as e:
        logger.error(f"Error finding compatible peers for user {user_id}: {e}")
        return []

def generate_compatibility_explanation(
    user_vector: Dict[str, Any],
    peer_vector: Dict[str, Any],
    score: float
) -> str:
    """Generate human-readable explanation for compatibility."""
    try:
        explanations = []
        
        # RIASEC overlap
        user_riasec = set(user_vector.get("desired_riasec_codes", []))
        peer_interests = peer_vector.get("desired_riasec_codes", [])
        if user_riasec and peer_interests:
            common_interests = user_riasec.intersection(set(peer_interests))
            if common_interests:
                explanations.append(f"Shared career interests in {', '.join(common_interests)} areas")
        
        # Goal alignment
        user_goals = user_vector.get("goal_overlap_keywords", [])
        peer_goals = peer_vector.get("goal_overlap_keywords", [])
        common_goals = set([g.lower() for g in user_goals]).intersection(set([g.lower() for g in peer_goals]))
        if common_goals:
            explanations.append(f"Aligned goals in {', '.join(common_goals)}")
        
        # Complementary skills
        user_skills = user_vector.get("target_skill_deltas", [])
        peer_skills = peer_vector.get("target_skill_deltas", [])
        if user_skills and peer_skills:
            explanations.append("Complementary skill development interests")
        
        # Career stage
        user_stage = user_vector.get("career_stage_preference", "any")
        peer_stage = peer_vector.get("career_stage_preference", "any")
        if user_stage == peer_stage and user_stage != "any":
            explanations.append(f"Both in {user_stage} career stage")
        
        if not explanations:
            if score >= 0.7:
                explanations.append("Strong overall compatibility across multiple dimensions")
            elif score >= 0.5:
                explanations.append("Good potential for collaboration and mutual growth")
            else:
                explanations.append("Some shared interests with room for diverse perspectives")
        
        return ". ".join(explanations) + "."
        
    except Exception as e:
        logger.error(f"Error generating compatibility explanation: {e}")
        return "Compatible based on profile analysis."

async def update_suggested_peers_enhanced(
    db: Session, 
    user_id: str, 
    compatible_peers: List[Tuple[str, float, Dict[str, Any]]]
) -> bool:
    """
    Update suggested_peers table with enhanced compatibility data.
    
    Args:
        db: Database session
        user_id: ID of the user
        compatible_peers: List of tuples (peer_id, score, explanation)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Delete existing suggestions
        delete_query = text("""
            DELETE FROM suggested_peers
            WHERE user_id = :user_id
        """)
        db.execute(delete_query, {"user_id": user_id})
        
        # Insert new suggestions
        for peer_id, score, explanation in compatible_peers:
            insert_query = text("""
                INSERT INTO suggested_peers (user_id, suggested_id, similarity, created_at)
                VALUES (:user_id, :peer_id, :similarity, :created_at)
            """)
            
            db.execute(insert_query, {
                "user_id": user_id,
                "peer_id": peer_id,
                "similarity": float(score),
                "created_at": datetime.now(timezone.utc)
            })
        
        db.commit()
        logger.info(f"Updated enhanced suggested peers for user {user_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating enhanced suggested peers: {e}")
        return False

async def generate_enhanced_peer_suggestions(db: Session, user_id: str, top_n: int = 5) -> bool:
    """
    Generate enhanced peer suggestions using compatibility analysis.
    
    Args:
        db: Database session
        user_id: ID of the user
        top_n: Number of suggestions to generate
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Find compatible peers
        compatible_peers = await find_compatible_peers(db, user_id, top_n)
        
        if not compatible_peers:
            logger.warning(f"No compatible peers found for user {user_id}")
            return False
        
        # Update suggested_peers table
        success = await update_suggested_peers_enhanced(db, user_id, compatible_peers)
        return success
        
    except Exception as e:
        logger.error(f"Error generating enhanced peer suggestions for user {user_id}: {e}")
        return False

def run_peer_matching_script() -> bool:
    """
    Run the peer matching script to update suggested peers for all users
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the path to the script
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "find_similar_peers.py")
        
        # Run the script using subprocess
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error running peer matching script: {result.stderr}")
            return False
        
        logger.info("Peer matching script completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error running peer matching script: {str(e)}")
        return False
