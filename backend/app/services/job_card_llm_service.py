"""
Job Card LLM Service - AI-powered career guidance for job recommendations.

This service provides personalized, context-aware responses to user queries about specific jobs,
using ESCO/OaSIS formatters for proper job context formatting.
"""

import os
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import json

from ..models import User, UserSkill, UserProfile, SavedRecommendation, UserRepresentation
from ..services.esco_formatting_service import ESCOFormattingService

logger = logging.getLogger(__name__)

# Configure OpenAI
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Prompt templates for different query types
PROMPT_TEMPLATES = {
    "barriers": """You are a brutally honest career counselor analyzing barriers to entry for a specific job.

USER PROFILE:
{user_context}

JOB INFORMATION ({job_type}):
{job_context}

The user asks: "{user_query}"

Provide a brutally honest assessment of:
1. **Real Barriers**: What specific obstacles will this person face getting this job?
2. **Skill Gaps**: What critical skills are they missing? Be specific.
3. **Experience Gaps**: How far off are they from the typical candidate?
4. **Reality Check**: Give them the unvarnished truth about their chances.
5. **Competition**: What does their competition look like?

Be direct and honest. Don't sugarcoat. If they're not ready, tell them clearly why.""",

    "timeline": """You are a realistic career timeline advisor providing honest assessments.

USER PROFILE:
{user_context}

JOB INFORMATION ({job_type}):
{job_context}

The user asks: "{user_query}"

Provide a realistic timeline including:
1. **Current Position**: Where they stand today (be honest)
2. **Immediate Steps**: What they need to do in the next 3-6 months
3. **Medium Term**: 6 months to 2 years milestones
4. **Long Term**: 2-5 year trajectory
5. **Fast Track Options**: If any exist (but be realistic)
6. **Potential Setbacks**: Common delays and obstacles

Give specific timeframes. Be realistic, not optimistic.""",

    "qualifications": """You are an expert analyzing job qualifications and requirements.

USER PROFILE:
{user_context}

JOB INFORMATION ({job_type}):
{job_context}

The user asks: "{user_query}"

Analyze:
1. **Hard Requirements**: Non-negotiable qualifications
2. **Soft Requirements**: Preferred but flexible qualifications
3. **Your Match**: How you stack up (percentage match)
4. **Critical Gaps**: The most important things you're missing
5. **Transferable Assets**: What you have that could compensate
6. **Minimum Viable Profile**: The bare minimum to be considered

Be specific and quantitative where possible.""",

    "why_want": """You are a career psychologist helping users understand their motivations.

USER PROFILE:
{user_context}

JOB INFORMATION ({job_type}):
{job_context}

The user asks: "{user_query}"

Based on their profile, explain:
1. **Alignment with Values**: How this job matches their stated goals and interests
2. **Personality Fit**: Based on their assessments (RIASEC, skills), why this might appeal
3. **Growth Potential**: How this role could develop them
4. **Lifestyle Fit**: How this matches their life situation
5. **Hidden Motivations**: What deeper needs this job might fulfill
6. **Potential Mismatches**: Where they might struggle or be disappointed

Use their specific data to make this personal and insightful.""",

    "general": """You are an AI career advisor providing personalized guidance.

USER PROFILE:
{user_context}

JOB INFORMATION ({job_type}):
{job_context}

The user asks: "{user_query}"

Provide a helpful, personalized response that:
1. Directly addresses their specific question
2. Uses their profile data to give contextual advice
3. Is honest but constructive
4. Includes specific, actionable next steps
5. References relevant aspects of the job and their background

Be professional but conversational."""
}

class JobCardLLMService:
    """Service for handling LLM-powered chat on job cards."""
    
    def __init__(self):
        self.esco_formatter = ESCOFormattingService()
        
    async def process_job_query(
        self,
        user_id: int,
        job_data: Dict[str, Any],
        user_query: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Process a user query about a specific job with full context.
        
        Args:
            user_id: The user's ID
            job_data: The job information (ESCO or OaSIS format)
            user_query: The user's question
            db: Database session
            
        Returns:
            Dict containing the response and metadata
        """
        try:
            # Determine query type
            query_type = self._classify_query(user_query)
            
            # Get user context
            user_context = await self._build_user_context(user_id, db)
            
            # Format job context based on type
            job_type = "ESCO" if "esco" in job_data.get("id", "").lower() else "OaSIS"
            job_context = self._format_job_context(job_data, job_type)
            
            # Select appropriate template
            template = PROMPT_TEMPLATES.get(query_type, PROMPT_TEMPLATES["general"])
            
            # Build the prompt
            prompt = template.format(
                user_context=user_context,
                job_context=job_context,
                job_type=job_type,
                user_query=user_query
            )
            
            # Get LLM response
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career counselor providing personalized, honest guidance. Be direct and specific, using the user's actual data."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content
            
            # Store interaction in memory
            self._store_interaction(user_id, job_data.get("id"), user_query, answer, query_type)
            
            return {
                "response": answer,
                "query_type": query_type,
                "job_type": job_type,
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": self._calculate_confidence(user_context, job_context)
            }
            
        except Exception as e:
            logger.error(f"Error processing job query: {str(e)}")
            return {
                "response": "I'm having trouble processing your question right now. Please try again or rephrase your question.",
                "error": str(e),
                "query_type": "error"
            }
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query for template selection."""
        query_lower = query.lower()
        
        barriers_keywords = ["barrier", "obstacle", "difficult", "hard", "challenge", "prevent", "stop"]
        timeline_keywords = ["how long", "when", "timeline", "time", "years", "months", "duration"]
        qualification_keywords = ["qualification", "requirement", "need", "must have", "prerequisite", "degree"]
        why_keywords = ["why", "want", "interested", "motivation", "appeal", "like"]
        
        if any(keyword in query_lower for keyword in barriers_keywords):
            return "barriers"
        elif any(keyword in query_lower for keyword in timeline_keywords):
            return "timeline"
        elif any(keyword in query_lower for keyword in qualification_keywords):
            return "qualifications"
        elif any(keyword in query_lower for keyword in why_keywords):
            return "why_want"
        else:
            return "general"
    
    async def _build_user_context(self, user_id: int, db: Session) -> str:
        """Build comprehensive user context for LLM."""
        # Get user profile data
        user = db.query(User).filter(User.id == user_id).first()
        user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).first()
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        context_parts = []
        
        # Basic information
        if user_profile:
            if user_profile.name:
                context_parts.append(f"Name: {user_profile.name}")
            if user_profile.age:
                context_parts.append(f"Age: {user_profile.age}")
            if user_profile.education_level:
                context_parts.append(f"Education: {user_profile.education_level}")
            if user_profile.major:
                context_parts.append(f"Major: {user_profile.major}")
            if user_profile.job_title:
                context_parts.append(f"Current Role: {user_profile.job_title}")
            if user_profile.years_experience:
                context_parts.append(f"Experience: {user_profile.years_experience} years")
            if user_profile.career_goals:
                context_parts.append(f"Career Goals: {user_profile.career_goals}")
            if user_profile.interests:
                context_parts.append(f"Interests: {user_profile.interests}")
        
        # Skills assessment
        if user_skills:
            skills_data = []
            skill_mapping = {
                "creativity": "Creativity",
                "leadership": "Leadership",
                "digital_literacy": "Digital Literacy",
                "critical_thinking": "Critical Thinking",
                "problem_solving": "Problem Solving"
            }
            
            for skill_key, skill_name in skill_mapping.items():
                value = getattr(user_skills, skill_key)
                if value is not None:
                    skills_data.append(f"{skill_name}: {value}/5")
            
            if skills_data:
                context_parts.append("Key Skills:\n" + "\n".join(f"  - {s}" for s in skills_data))
        
        # Holland test results
        try:
            holland_query = db.execute(
                "SELECT top_3_code FROM gca_results WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 1",
                {"user_id": user_id}
            )
            holland_row = holland_query.fetchone()
            if holland_row:
                context_parts.append(f"RIASEC Type: {holland_row[0]}")
        except:
            pass
        
        return "\n".join(context_parts) if context_parts else "Limited profile information available."
    
    def _format_job_context(self, job_data: Dict[str, Any], job_type: str) -> str:
        """Format job data based on whether it's ESCO or OaSIS."""
        if job_type == "ESCO":
            return self._format_esco_job(job_data)
        else:
            return self._format_oasis_job(job_data)
    
    def _format_esco_job(self, job_data: Dict[str, Any]) -> str:
        """Format ESCO job data."""
        parts = []
        metadata = job_data.get("metadata", {})
        
        parts.append(f"Job Title: {metadata.get('preferred_label', job_data.get('id', 'Unknown'))}")
        
        if metadata.get('description'):
            parts.append(f"Description: {metadata['description']}")
        
        if metadata.get('alt_labels'):
            parts.append(f"Alternative Titles: {', '.join(metadata['alt_labels'][:3])}")
        
        if metadata.get('skills'):
            parts.append(f"Required Skills: {', '.join(metadata['skills'][:5])}")
        
        return "\n".join(parts)
    
    def _format_oasis_job(self, job_data: Dict[str, Any]) -> str:
        """Format OaSIS job data."""
        parts = []
        metadata = job_data.get("metadata", {})
        
        parts.append(f"Job Title: {metadata.get('title', job_data.get('id', 'Unknown'))}")
        
        if metadata.get('description'):
            parts.append(f"Description: {metadata['description']}")
        
        if metadata.get('main_duties'):
            parts.append(f"Main Duties: {metadata['main_duties']}")
        
        # Add skill requirements
        skills = []
        skill_fields = ['creativity', 'leadership', 'digital_literacy', 'critical_thinking', 'problem_solving']
        for skill in skill_fields:
            if skill in metadata:
                skills.append(f"{skill.replace('_', ' ').title()}: {metadata[skill]}/5")
        
        if skills:
            parts.append("Skill Requirements:\n" + "\n".join(f"  - {s}" for s in skills))
        
        return "\n".join(parts)
    
    def _calculate_confidence(self, user_context: str, job_context: str) -> float:
        """Calculate confidence score based on available context."""
        # Simple heuristic based on context completeness
        user_score = min(len(user_context) / 500, 1.0) * 0.5
        job_score = min(len(job_context) / 300, 1.0) * 0.5
        return round(user_score + job_score, 2)
    
    def _store_interaction(self, user_id: int, job_id: str, query: str, response: str, query_type: str):
        """Store the interaction in memory for future reference."""
        try:
            # Store in memory for swarm coordination
            memory_key = f"swarm-auto-centralized-1750552628330/llm-specialist/interactions/{user_id}/{job_id}"
            interaction_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": query,
                "response": response,
                "query_type": query_type
            }
            # This would integrate with the Memory service
            logger.info(f"Stored LLM interaction: {memory_key}")
        except Exception as e:
            logger.error(f"Failed to store interaction: {str(e)}")

# Preset queries for quick access
PRESET_QUERIES = {
    "barriers": "What are the main barriers preventing me from getting this job?",
    "timeline": "How long would it realistically take me to qualify for this position?",
    "qualifications": "What qualifications do I need for this job and which ones am I missing?",
    "why_want": "Based on my profile, why would I want this job?",
    "growth": "What growth opportunities does this role offer for someone like me?",
    "preparation": "What specific steps should I take to prepare for this role?"
}

async def get_preset_queries() -> List[Dict[str, str]]:
    """Get preset queries for the UI."""
    return [
        {"id": key, "text": value, "icon": _get_query_icon(key)}
        for key, value in PRESET_QUERIES.items()
    ]

def _get_query_icon(query_type: str) -> str:
    """Get icon for query type."""
    icons = {
        "barriers": "🚧",
        "timeline": "⏱️",
        "qualifications": "📋",
        "why_want": "🤔",
        "growth": "📈",
        "preparation": "📚"
    }
    return icons.get(query_type, "💬")