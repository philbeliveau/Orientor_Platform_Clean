"""
ESCO Formatting Service for converting user skills to ESCO-compliant format.

This service takes user-inferred skills and formats them according to ESCO standards
before matching them in Pinecone.
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
import traceback

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ESCOFormattingService:
    """
    Service for formatting user skills into ESCO-compliant descriptions.
    
    Takes LLM-inferred skills and converts them to standardized ESCO format
    suitable for semantic matching in the skill graph.
    """
    
    def __init__(self):
        """Initialize the ESCO formatting service."""
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
            logger.info("OpenAI client initialized successfully for ESCO formatting")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            return False
    
    def format_esco_skill(self, skill_label: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a single skill according to ESCO standards.
        
        Args:
            skill_label: The skill label to format
            user_context: User context for personalization
            
        Returns:
            Dict containing ESCO-formatted skill information
        """
        try:
            if not self.client:
                logger.error("OpenAI client not initialized")
                return self._create_fallback_skill(skill_label)
            
            # Build ESCO formatting prompt
            prompt = self._build_esco_skill_prompt(skill_label, user_context)
            
            # Call OpenAI API with fallback
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",  # This model supports JSON mode
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert in ESCO (European Skills, Competences, Qualifications and Occupations) classification standards. Format user skills according to ESCO guidelines with professional, action-oriented descriptions. Respond ONLY with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=400,
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
                                "content": "You are an expert in ESCO classification standards. Format user skills according to ESCO guidelines. Respond ONLY with valid JSON in this exact format: {\"preferredLabel\": \"skill name\", \"description\": \"description\", \"applications\": [\"app1\", \"app2\"], \"skill_level\": \"intermediate\", \"skill_type\": \"technical\"}"
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.3,
                        max_tokens=400
                    )
                else:
                    raise e
            
            if not response.choices:
                logger.error("No response from OpenAI for ESCO formatting")
                return self._create_fallback_skill(skill_label)
            
            # Parse the response
            response_content = response.choices[0].message.content
            try:
                skill_data = json.loads(response_content)
                
                # Validate response structure
                required_fields = ["preferredLabel", "description", "applications"]
                if not all(field in skill_data for field in required_fields):
                    logger.error(f"Invalid ESCO formatting response structure for skill: {skill_label}")
                    return self._create_fallback_skill(skill_label)
                
                return {
                    "original_label": skill_label,
                    "esco_label": skill_data["preferredLabel"],
                    "esco_description": skill_data["description"],
                    "applications": skill_data.get("applications", []),
                    "skill_level": skill_data.get("skill_level", "intermediate"),
                    "formatted": True
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response for ESCO formatting: {str(e)}")
                return self._create_fallback_skill(skill_label)
                
        except Exception as e:
            logger.error(f"Error formatting ESCO skill {skill_label}: {str(e)}")
            logger.error(traceback.format_exc())
            return self._create_fallback_skill(skill_label)
    
    def format_multiple_skills(self, skills: List[Dict[str, Any]], user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format multiple skills according to ESCO standards.
        
        Args:
            skills: List of skill dictionaries with 'label' field
            user_context: User context for personalization
            
        Returns:
            List of ESCO-formatted skill dictionaries
        """
        formatted_skills = []
        
        for skill in skills:
            skill_label = skill.get("label", "")
            if not skill_label:
                continue
            
            # Format the skill
            formatted_skill = self.format_esco_skill(skill_label, user_context)
            
            # Add original metadata
            formatted_skill.update({
                "original_justification": skill.get("justification", ""),
                "confidence": skill.get("confidence", 0.5),
                "category": skill.get("category", "general")
            })
            
            formatted_skills.append(formatted_skill)
        
        logger.info(f"Successfully formatted {len(formatted_skills)} skills to ESCO standard")
        return formatted_skills
    
    def _build_esco_skill_prompt(self, skill_label: str, user_context: Dict[str, Any]) -> str:
        """
        Build ESCO skill formatting prompt.
        
        Args:
            skill_label: The skill to format
            user_context: User context information
            
        Returns:
            Formatted prompt string
        """
        prompt = """
        Convert the following user skill into ESCO (European Skills, Competences, Qualifications and Occupations) standard format.

        SKILL TO FORMAT: "{skill_label}"

        USER CONTEXT:
        - Age: {age}
        - Education: {education}
        - Industry: {industry}
        - Experience: {experience} years
        - Career Goals: {career_goals}

        ESCO FORMATTING REQUIREMENTS:
        1. Use professional, objective language (no first person)
        2. Focus on actionable capabilities, not personal traits
        3. Use active voice and specific verbs
        4. Align with workplace contexts and professional applications
        5. Be concise but comprehensive

        OUTPUT FORMAT (JSON):
        {{
            "preferredLabel": "ESCO-compliant skill name (2-4 words)",
            "description": "Professional description of what this skill enables (2-3 sentences, active voice)",
            "applications": [
                "Specific application 1",
                "Specific application 2", 
                "Specific application 3"
            ],
            "skill_level": "beginner/intermediate/advanced",
            "skill_type": "technical/cognitive/interpersonal/leadership"
        }}
        """.format(
            skill_label=skill_label,
            age=user_context.get("age", "Unknown"),
            education=user_context.get("education_level", "Unknown"),
            industry=user_context.get("industry", "Unknown"),
            experience=user_context.get("years_experience", 0),
            career_goals=user_context.get("career_goals", "Unknown")
        )
        
        return prompt
    
    def _create_fallback_skill(self, skill_label: str) -> Dict[str, Any]:
        """
        Create a fallback skill format when ESCO formatting fails.
        
        Args:
            skill_label: Original skill label
            
        Returns:
            Basic skill dictionary
        """
        return {
            "original_label": skill_label,
            "esco_label": skill_label,
            "esco_description": f"Competency in {skill_label.lower()} applications and methodologies.",
            "applications": [
                f"Apply {skill_label.lower()} in professional contexts",
                f"Develop solutions using {skill_label.lower()}",
                f"Collaborate on {skill_label.lower()}-related projects"
            ],
            "skill_level": "intermediate",
            "formatted": False
        }
    
    def create_searchable_text(self, formatted_skill: Dict[str, Any]) -> str:
        """
        Create searchable text for embedding generation.
        
        Args:
            formatted_skill: ESCO-formatted skill dictionary
            
        Returns:
            Concatenated text for embedding
        """
        try:
            text_parts = [
                formatted_skill.get("esco_label", ""),
                formatted_skill.get("esco_description", "")
            ]
            
            # Add applications
            applications = formatted_skill.get("applications", [])
            if applications:
                text_parts.append(" ".join(applications))
            
            return " ".join(text_parts).strip()
            
        except Exception as e:
            logger.error(f"Error creating searchable text: {str(e)}")
            return formatted_skill.get("esco_label", formatted_skill.get("original_label", ""))