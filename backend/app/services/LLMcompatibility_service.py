"""
LLM-based peer compatibility analysis service.

Extracts structured compatibility vectors from user profiles using GPT-4,
combining personality traits, career interests, and aspirational goals for
enhanced peer matching.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

import openai
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.models.user_profile import UserProfile
from app.models.personality_profiles import PersonalityProfile
from app.utils.database import get_db

logger = logging.getLogger(__name__)

class LLMCompatibilityService:
    """Service for extracting compatibility vectors using LLM analysis."""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def extract_compatibility_vector(
        self, 
        profile: UserProfile, 
        db: Session
    ) -> Dict[str, Any]:
        """
        Extract structured compatibility vector from user profile.
        
        Args:
            profile: UserProfile instance
            db: Database session
            
        Returns:
            Dict containing compatibility dimensions for peer matching
        """
        try:
            # Gather comprehensive profile data
            profile_data = await self._gather_profile_data(profile, db)
            
            # Generate LLM prompt
            prompt = self._build_compatibility_prompt(profile_data)
            
            # Call OpenAI API
            response = await self._call_openai_api(prompt)
            
            # Parse and validate response
            compatibility_vector = self._parse_compatibility_response(response)
            
            logger.info(f"Extracted compatibility vector for user {profile.user_id}")
            return compatibility_vector
            
        except Exception as e:
            logger.error(f"Failed to extract compatibility vector for user {profile.user_id}: {e}")
            return self._get_fallback_compatibility_vector()
    
    async def _gather_profile_data(
        self, 
        profile: UserProfile, 
        db: Session
    ) -> Dict[str, Any]:
        """Gather comprehensive user data for LLM analysis."""
        
        # Get personality profile if available
        personality_stmt = select(PersonalityProfile).where(
            PersonalityProfile.user_id == profile.user_id
        ).order_by(PersonalityProfile.computed_at.desc())
        
        personality_result = db.execute(personality_stmt).first()
        personality_data = {}
        
        if personality_result:
            personality_profile = personality_result[0]
            personality_data = {
                "hexaco_scores": personality_profile.scores.get("hexaco", {}) if personality_profile.scores else {},
                "riasec_scores": personality_profile.scores.get("riasec", {}) if personality_profile.scores else {},
                "narrative_description": personality_profile.narrative_description
            }
        
        return {
            "basic_info": {
                "name": profile.name,
                "age": profile.age,
                "major": profile.major,
                "year": profile.year,
                "job_title": profile.job_title,
                "industry": profile.industry,
                "years_experience": profile.years_experience,
                "education_level": profile.education_level
            },
            "personal_data": {
                "interests": profile.interests,
                "hobbies": profile.hobbies,
                "career_goals": profile.career_goals,
                "story": profile.story,
                "unique_quality": profile.unique_quality,
                "skills": profile.skills or []
            },
            "personality": personality_data,
            "preferences": {
                "learning_style": profile.learning_style,
                "favorite_movie": profile.favorite_movie,
                "favorite_book": profile.favorite_book
            }
        }
    
    def _build_compatibility_prompt(self, profile_data: Dict[str, Any]) -> str:
        """Build structured prompt for compatibility analysis."""
        
        basic_info = profile_data.get("basic_info", {})
        personal_data = profile_data.get("personal_data", {})
        personality = profile_data.get("personality", {})
        preferences = profile_data.get("preferences", {})
        
        hexaco_scores = personality.get("hexaco_scores", {})
        riasec_scores = personality.get("riasec_scores", {})
        
        prompt = f"""
Analyze this user's profile to extract peer compatibility preferences for career mentorship and collaboration.

USER PROFILE:
Basic Info: {basic_info.get('name', 'N/A')}, {basic_info.get('age', 'N/A')} years old
Career: {basic_info.get('job_title', 'N/A')} in {basic_info.get('industry', 'N/A')}
Education: {basic_info.get('major', 'N/A')}, {basic_info.get('education_level', 'N/A')}
Experience: {basic_info.get('years_experience', 'N/A')} years

Personal Interests: {personal_data.get('interests', 'N/A')}
Career Goals: {personal_data.get('career_goals', 'N/A')}
Unique Quality: {personal_data.get('unique_quality', 'N/A')}
Skills: {', '.join(personal_data.get('skills', [])) if personal_data.get('skills') else 'N/A'}

Personality (HEXACO): {hexaco_scores}
Career Interests (RIASEC): {riasec_scores}
Learning Style: {preferences.get('learning_style', 'N/A')}

EXTRACT COMPATIBILITY PREFERENCES:
Based on this profile, determine what this person would value in peer connections for career growth and collaboration.

Return ONLY a valid JSON object with these exact keys:
{{
  "desired_riasec_codes": ["list of 2-3 RIASEC codes they'd want in peers"],
  "target_skill_deltas": ["list of 3-4 skills they want to learn from others"],
  "goal_overlap_keywords": ["list of 3-5 keywords describing compatible career goals"],
  "career_stage_preference": "early-career | mid-career | senior | any",
  "industry_overlap": ["list of 2-4 industries for cross-pollination"],
  "personality_compatibility": {{
    "hexaco_preferences": {{"trait": "high|medium|low preference for each HEXACO trait"}},
    "collaboration_style": "independent | collaborative | leadership | supportive"
  }},
  "mentorship_direction": "seeking_mentor | peer_level | willing_to_mentor | bidirectional",
  "interaction_preferences": ["networking", "project_collaboration", "knowledge_sharing", "career_advice"]
}}
"""
        return prompt
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API with compatibility analysis prompt."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career counselor and personality psychologist. Extract peer compatibility preferences from user profiles. Return only valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _parse_compatibility_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate LLM response."""
        try:
            # Extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.rfind("```")
                response = response[json_start:json_end].strip()
            
            compatibility_vector = json.loads(response)
            
            # Validate required keys
            required_keys = [
                "desired_riasec_codes", "target_skill_deltas", "goal_overlap_keywords",
                "career_stage_preference", "industry_overlap", "personality_compatibility",
                "mentorship_direction", "interaction_preferences"
            ]
            
            for key in required_keys:
                if key not in compatibility_vector:
                    logger.warning(f"Missing key in compatibility vector: {key}")
                    compatibility_vector[key] = self._get_default_value(key)
            
            # Add metadata
            compatibility_vector["generated_at"] = datetime.now(timezone.utc).isoformat()
            compatibility_vector["version"] = "1.0"
            
            return compatibility_vector
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response content: {response}")
            return self._get_fallback_compatibility_vector()
    
    def _get_default_value(self, key: str) -> Any:
        """Get default value for missing compatibility vector key."""
        defaults = {
            "desired_riasec_codes": ["S", "E"],
            "target_skill_deltas": ["communication", "leadership"],
            "goal_overlap_keywords": ["career_growth", "professional_development"],
            "career_stage_preference": "any",
            "industry_overlap": ["technology", "business"],
            "personality_compatibility": {
                "hexaco_preferences": {},
                "collaboration_style": "collaborative"
            },
            "mentorship_direction": "peer_level",
            "interaction_preferences": ["networking", "knowledge_sharing"]
        }
        return defaults.get(key, [])
    
    def _get_fallback_compatibility_vector(self) -> Dict[str, Any]:
        """Return fallback compatibility vector on failure."""
        return {
            "desired_riasec_codes": ["S", "E"],
            "target_skill_deltas": ["communication", "leadership", "problem_solving"],
            "goal_overlap_keywords": ["career_growth", "professional_development", "networking"],
            "career_stage_preference": "any",
            "industry_overlap": ["technology", "business"],
            "personality_compatibility": {
                "hexaco_preferences": {
                    "honesty_humility": "medium",
                    "emotionality": "medium",
                    "extraversion": "medium",
                    "agreeableness": "high",
                    "conscientiousness": "high",
                    "openness": "high"
                },
                "collaboration_style": "collaborative"
            },
            "mentorship_direction": "peer_level",
            "interaction_preferences": ["networking", "knowledge_sharing"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "fallback": True
        }
    
    async def bulk_extract_compatibility_vectors(
        self, 
        user_ids: List[int], 
        db: Session
    ) -> Dict[int, Dict[str, Any]]:
        """Extract compatibility vectors for multiple users concurrently."""
        
        # Fetch user profiles
        profiles_stmt = select(UserProfile).where(UserProfile.user_id.in_(user_ids))
        profiles_result = db.execute(profiles_stmt).all()
        profiles = [row[0] for row in profiles_result]
        
        # Process concurrently with semaphore to limit API calls
        semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent API calls
        
        async def extract_with_semaphore(profile):
            async with semaphore:
                vector = await self.extract_compatibility_vector(profile, db)
                return profile.user_id, vector
        
        tasks = [extract_with_semaphore(profile) for profile in profiles]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        compatibility_vectors = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Bulk extraction failed for a user: {result}")
                continue
            user_id, vector = result
            compatibility_vectors[user_id] = vector
        
        logger.info(f"Bulk extracted {len(compatibility_vectors)} compatibility vectors")
        return compatibility_vectors

# Service instance
compatibility_service = LLMCompatibilityService()