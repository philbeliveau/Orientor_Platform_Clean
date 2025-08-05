"""
LLM Competence Service for extracting personalized skills from user profiles.

This service combines user narrative, skills ratings, and psychometric scores
to infer 5 anchor skills using OpenAI's GPT models.
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from openai import OpenAI
import traceback

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMCompetenceService:
    """
    Service for inferring anchor skills from user profiles using LLM.
    
    Combines narrative text, skill ratings, and psychometric assessments
    to generate 5 personalized anchor skills for skill tree generation.
    """
    
    def __init__(self):
        """Initialize the LLM service with OpenAI client."""
        self.client = None
        self._initialize_openai()
    
    def _initialize_openai(self) -> bool:
        """
        Initialize OpenAI client.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OpenAI API key not found in environment variables")
                return False
            
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            return False
    
    def get_user_profile_data(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Gather comprehensive user profile data for skill inference.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dict containing user profile data
        """
        try:
            # Get user profile information
            profile_query = text("""
                SELECT 
                    story, interests, career_goals, hobbies, unique_quality,
                    major, industry, education_level, years_experience,
                    name, age, job_title
                FROM user_profiles 
                WHERE user_id = :user_id
            """)
            profile_result = db.execute(profile_query, {"user_id": user_id}).fetchone()
            
            # Get user skills ratings
            skills_query = text("""
                SELECT 
                    creativity, leadership, digital_literacy, critical_thinking,
                    problem_solving, analytical_thinking, attention_to_detail,
                    collaboration, adaptability, independence, evaluation,
                    decision_making, stress_tolerance
                FROM user_skills 
                WHERE user_id = :user_id
            """)
            skills_result = db.execute(skills_query, {"user_id": user_id}).fetchone()
            
            # Get HEXACO personality scores
            hexaco_query = text("""
                SELECT scores, narrative_description
                FROM personality_profiles 
                WHERE user_id = :user_id AND profile_type = 'hexaco'
                ORDER BY created_at DESC LIMIT 1
            """)
            hexaco_result = db.execute(hexaco_query, {"user_id": user_id}).fetchone()
            
            # Get Holland RIASEC scores
            holland_query = text("""
                SELECT r_score, i_score, a_score, s_score, e_score, c_score, top_3_code
                FROM gca_results 
                WHERE user_id = :user_id
                ORDER BY created_at DESC LIMIT 1
            """)
            holland_result = db.execute(holland_query, {"user_id": user_id}).fetchone()
            
            # Get strengths reflection responses
            reflection_query = text("""
                SELECT prompt_text, response
                FROM strengths_reflection_responses 
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """)
            reflection_results = db.execute(reflection_query, {"user_id": user_id}).fetchall()
            
            # Compile profile data
            profile_data = {
                "narrative": {
                    "story": profile_result[0] if profile_result and profile_result[0] else "",
                    "interests": profile_result[1] if profile_result and profile_result[1] else "",
                    "career_goals": profile_result[2] if profile_result and profile_result[2] else "",
                    "hobbies": profile_result[3] if profile_result and profile_result[3] else "",
                    "unique_quality": profile_result[4] if profile_result and profile_result[4] else "",
                },
                "demographics": {
                    "age": profile_result[9] if profile_result and profile_result[9] else 25,
                    "major": profile_result[5] if profile_result and profile_result[5] else "",
                    "industry": profile_result[6] if profile_result and profile_result[6] else "",
                    "education_level": profile_result[7] if profile_result and profile_result[7] else "",
                    "years_experience": profile_result[8] if profile_result and profile_result[8] else 0,
                    "job_title": profile_result[10] if profile_result and profile_result[10] else "",
                },
                "skills_ratings": {},
                "hexaco_scores": {},
                "holland_scores": {},
                "reflections": []
            }
            
            # Add skills ratings if available
            if skills_result:
                skills_fields = [
                    "creativity", "leadership", "digital_literacy", "critical_thinking",
                    "problem_solving", "analytical_thinking", "attention_to_detail",
                    "collaboration", "adaptability", "independence", "evaluation",
                    "decision_making", "stress_tolerance"
                ]
                for i, field in enumerate(skills_fields):
                    if skills_result[i] is not None:
                        profile_data["skills_ratings"][field] = float(skills_result[i])
            
            # Add HEXACO scores if available
            if hexaco_result and hexaco_result[0]:
                try:
                    profile_data["hexaco_scores"] = json.loads(hexaco_result[0]) if isinstance(hexaco_result[0], str) else hexaco_result[0]
                    profile_data["hexaco_narrative"] = hexaco_result[1] if hexaco_result[1] else ""
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"Invalid HEXACO scores format for user {user_id}")
            
            # Add Holland scores if available
            if holland_result:
                profile_data["holland_scores"] = {
                    "realistic": float(holland_result[0]) if holland_result[0] else 0,
                    "investigative": float(holland_result[1]) if holland_result[1] else 0,
                    "artistic": float(holland_result[2]) if holland_result[2] else 0,
                    "social": float(holland_result[3]) if holland_result[3] else 0,
                    "enterprising": float(holland_result[4]) if holland_result[4] else 0,
                    "conventional": float(holland_result[5]) if holland_result[5] else 0,
                    "top_3_code": holland_result[6] if holland_result[6] else ""
                }
            
            # Add reflection responses if available
            if reflection_results:
                profile_data["reflections"] = [
                    {"prompt": row[0], "response": row[1]}
                    for row in reflection_results
                    if row[1] and row[1].strip()
                ]
            
            logger.info(f"Successfully gathered profile data for user {user_id}")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error gathering user profile data for user {user_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return {}
    
    def infer_anchor_skills(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        Infer 5 anchor skills from user profile using LLM.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of 5 inferred skills with labels and justifications
        """
        try:
            if not self.client:
                logger.error("OpenAI client not initialized")
                return []
            
            # Gather user profile data
            profile_data = self.get_user_profile_data(db, user_id)
            if not profile_data:
                logger.error(f"No profile data found for user {user_id}")
                return []
            
            # Build comprehensive prompt
            prompt = self._build_skill_inference_prompt(profile_data)
            
            # Call OpenAI API with fallback for model compatibility
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",  # This model supports JSON mode
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an expert career counselor and skills assessment specialist. Your task is to analyze user profiles and identify their top 5 anchor skills that should form the foundation of their personalized skill development tree. Respond ONLY with valid JSON."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                    response_format={"type": "json_object"}
                )
            except Exception as e:
                if "response_format" in str(e):
                    logger.warning(f"JSON format not supported, trying without response_format: {str(e)}")
                    # Fallback without response_format
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are an expert career counselor and skills assessment specialist. Your task is to analyze user profiles and identify their top 5 anchor skills that should form the foundation of their personalized skill development tree. Respond ONLY with valid JSON in this exact format: {\"skills\": [{\"label\": \"skill name\", \"justification\": \"reason\", \"confidence\": 0.8, \"category\": \"technical\"}]}"
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=1000
                    )
                else:
                    raise e
            
            if not response.choices:
                logger.error("No response from OpenAI")
                return []
            
            # Parse the response
            response_content = response.choices[0].message.content
            try:
                skills_data = json.loads(response_content)
                
                # Validate response structure
                if "skills" not in skills_data or not isinstance(skills_data["skills"], list):
                    logger.error("Invalid response structure from LLM")
                    return []
                
                # Ensure we have exactly 5 skills
                skills = skills_data["skills"][:5]
                
                # Validate each skill has required fields
                validated_skills = []
                for skill in skills:
                    if all(field in skill for field in ["label", "justification", "confidence"]):
                        validated_skills.append({
                            "label": skill["label"],
                            "justification": skill["justification"],
                            "confidence": float(skill.get("confidence", 0.5)),
                            "category": skill.get("category", "general")
                        })
                
                if len(validated_skills) < 3:
                    logger.error(f"Not enough valid skills returned for user {user_id}")
                    return []
                
                logger.info(f"Successfully inferred {len(validated_skills)} skills for user {user_id}")
                return validated_skills
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response from LLM: {str(e)}")
                logger.error(f"Raw response: {response_content}")
                return []
                
        except Exception as e:
            logger.error(f"Error inferring anchor skills for user {user_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
    
    def _build_skill_inference_prompt(self, profile_data: Dict[str, Any]) -> str:
        """
        Build comprehensive prompt for skill inference.
        
        Args:
            profile_data: User profile data
            
        Returns:
            Formatted prompt string
        """
        prompt = """
        Analyze the following user profile and identify their TOP 5 ANCHOR SKILLS that should form the foundation of their personalized skill development tree.

        USER PROFILE:
        
        **Personal Story & Goals:**
        {narrative_text}
        
        **Demographics:**
        - Age: {age}
        - Education: {education}
        - Industry: {industry}
        - Experience: {experience} years
        - Job Title: {job_title}
        
        **Current Skill Ratings (0-5 scale):**
        {skills_ratings}
        
        **Personality Profile (HEXACO):**
        {hexaco_summary}
        
        **Career Interests (Holland RIASEC):**
        {holland_summary}
        
        **Personal Reflections:**
        {reflections}
        
        **TASK:** Identify exactly 5 anchor skills that:
        1. Align with their personality, interests, and goals
        2. Build on their existing strengths
        3. Support their career trajectory
        4. Represent diverse skill categories (technical, interpersonal, cognitive, creative, leadership)
        5. Are specific enough to be actionable but broad enough to anchor a skill tree
        
        **OUTPUT FORMAT:** Return ONLY a JSON object with this exact structure:
        {{
            "skills": [
                {{
                    "label": "Specific skill name (e.g., 'Data Analysis', 'Creative Problem Solving', 'Team Leadership')",
                    "justification": "2-3 sentence explanation based on profile analysis",
                    "confidence": 0.85,
                    "category": "technical/interpersonal/cognitive/creative/leadership"
                }}
            ]
        }}
        """.format(
            narrative_text=self._format_narrative(profile_data.get("narrative", {})),
            age=profile_data.get("demographics", {}).get("age", "Unknown"),
            education=profile_data.get("demographics", {}).get("education_level", "Unknown"),
            industry=profile_data.get("demographics", {}).get("industry", "Unknown"),
            experience=profile_data.get("demographics", {}).get("years_experience", 0),
            job_title=profile_data.get("demographics", {}).get("job_title", "Unknown"),
            skills_ratings=self._format_skills_ratings(profile_data.get("skills_ratings", {})),
            hexaco_summary=self._format_hexaco(profile_data.get("hexaco_scores", {})),
            holland_summary=self._format_holland(profile_data.get("holland_scores", {})),
            reflections=self._format_reflections(profile_data.get("reflections", []))
        )
        
        return prompt
    
    def _format_narrative(self, narrative: Dict[str, str]) -> str:
        """Format narrative text from profile."""
        parts = []
        if narrative.get("story"):
            parts.append(f"Story: {narrative['story']}")
        if narrative.get("career_goals"):
            parts.append(f"Career Goals: {narrative['career_goals']}")
        if narrative.get("interests"):
            parts.append(f"Interests: {narrative['interests']}")
        if narrative.get("unique_quality"):
            parts.append(f"Unique Quality: {narrative['unique_quality']}")
        return "\n".join(parts) if parts else "No narrative provided"
    
    def _format_skills_ratings(self, skills: Dict[str, float]) -> str:
        """Format skills ratings for prompt."""
        if not skills:
            return "No skill ratings available"
        
        formatted = []
        for skill, rating in skills.items():
            formatted.append(f"- {skill.replace('_', ' ').title()}: {rating}/5")
        return "\n".join(formatted)
    
    def _format_hexaco(self, hexaco: Dict[str, Any]) -> str:
        """Format HEXACO scores for prompt."""
        if not hexaco:
            return "No HEXACO assessment available"
        
        # Extract main dimensions if available
        dimensions = ["honesty_humility", "emotionality", "extraversion", "agreeableness", "conscientiousness", "openness"]
        formatted = []
        
        for dim in dimensions:
            if dim in hexaco:
                formatted.append(f"- {dim.replace('_', ' ').title()}: {hexaco[dim]}")
        
        return "\n".join(formatted) if formatted else "HEXACO data available but format unclear"
    
    def _format_holland(self, holland: Dict[str, Any]) -> str:
        """Format Holland RIASEC scores for prompt."""
        if not holland:
            return "No Holland assessment available"
        
        riasec_map = {
            "realistic": "Realistic (R) - Hands-on, practical",
            "investigative": "Investigative (I) - Analytical, scientific", 
            "artistic": "Artistic (A) - Creative, expressive",
            "social": "Social (S) - Helping, interpersonal",
            "enterprising": "Enterprising (E) - Leadership, business",
            "conventional": "Conventional (C) - Organized, detail-oriented"
        }
        
        formatted = []
        for key, description in riasec_map.items():
            if key in holland:
                formatted.append(f"- {description}: {holland[key]}")
        
        if holland.get("top_3_code"):
            formatted.append(f"- Top 3 Code: {holland['top_3_code']}")
        
        return "\n".join(formatted) if formatted else "Holland data available but format unclear"
    
    def _format_reflections(self, reflections: List[Dict[str, str]]) -> str:
        """Format reflection responses for prompt."""
        if not reflections:
            return "No reflection responses available"
        
        formatted = []
        for i, reflection in enumerate(reflections[:3], 1):  # Limit to top 3 reflections
            formatted.append(f"{i}. {reflection.get('prompt', 'Question')}: {reflection.get('response', 'No response')}")
        
        return "\n".join(formatted)