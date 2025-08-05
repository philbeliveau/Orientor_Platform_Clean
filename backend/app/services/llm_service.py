import os
import logging
from typing import Dict, Any, Optional
import openai
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_career_advice(
    system_prompt: str,
    user_query: str,
    context: Dict[str, Any],
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> str:
    """
    Generate career advice using OpenAI's GPT model with appropriate formatting.
    
    Args:
        system_prompt: System instructions for the AI
        user_query: The user's question
        context: Full context including user profile, job details, and analysis
        model: OpenAI model to use
        temperature: Response creativity (0-1)
        max_tokens: Maximum response length
        
    Returns:
        Generated career advice response
    """
    try:
        # Build the messages for the chat completion
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"""
                Context:
                {json.dumps(context, indent=2)}
                
                Question: {user_query}
                
                Please provide a helpful, honest, and specific response.
                """
            }
        ]
        
        # Call OpenAI API
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error generating career advice: {str(e)}")
        
        # Fallback response if API fails
        return f"""I apologize, but I'm having trouble generating a detailed response right now. 
        
Based on your question about {context.get('job_details', {}).get('title', 'this career')}, 
I can suggest looking at:
- Required education and skills
- Typical career timeline
- Industry growth and opportunities
- Your current qualifications vs requirements

Please try again or rephrase your question."""

async def generate_esco_analysis(
    job_data: Dict[str, Any],
    user_profile: Dict[str, Any],
    analysis_type: str = "comprehensive"
) -> Dict[str, str]:
    """
    Generate ESCO-specific career analysis using the ESCO-OccupationFormatter.
    
    Args:
        job_data: ESCO job information
        user_profile: User's profile and skills
        analysis_type: Type of analysis to perform
        
    Returns:
        Dictionary with analysis results
    """
    try:
        system_prompt = """
        You are an expert career counselor specializing in ESCO occupational analysis.
        Provide structured, actionable insights using the ESCO taxonomy.
        Focus on competencies, qualifications, and career pathways.
        """
        
        prompts = {
            "personal_fit": f"""
                Analyze how well this ESCO occupation matches the user's profile:
                - Skill alignment (rate each essential skill)
                - Interest compatibility
                - Values alignment
                - Personality fit
                Be specific about strengths and gaps.
            """,
            "entry_requirements": f"""
                Detail the entry requirements for this ESCO occupation:
                - Minimum education level
                - Required certifications/licenses
                - Essential skills and competencies
                - Typical experience requirements
                - Alternative entry paths
            """,
            "development_plan": f"""
                Create a development plan for this ESCO occupation:
                - Skill gaps to address (prioritized)
                - Recommended courses/training
                - Experience-building opportunities
                - Timeline with milestones
                - Cost estimates
            """
        }
        
        results = {}
        
        for key, prompt in prompts.items():
            if analysis_type == "comprehensive" or analysis_type == key:
                response = await generate_career_advice(
                    system_prompt=system_prompt,
                    user_query=prompt,
                    context={
                        "job_data": job_data,
                        "user_profile": user_profile,
                        "formatter": "ESCO-OccupationFormatter"
                    }
                )
                results[key] = response
        
        return results
        
    except Exception as e:
        logger.error(f"Error generating ESCO analysis: {str(e)}")
        return {
            "error": "Unable to generate analysis at this time."
        }

async def generate_oasis_analysis(
    job_data: Dict[str, Any],
    user_profile: Dict[str, Any],
    graphsage_skills: list = None
) -> Dict[str, str]:
    """
    Generate OaSIS-specific career analysis using the OaSIS-RoleFormatter.
    
    Args:
        job_data: OaSIS job information
        user_profile: User's profile and skills
        graphsage_skills: Top skills from GraphSAGE analysis
        
    Returns:
        Dictionary with analysis results
    """
    try:
        system_prompt = """
        You are a career advisor specializing in skills-based career matching.
        Use the OaSIS-RoleFormatter to analyze careers based on skills and competencies.
        Focus on practical skill development and career transitions.
        """
        
        context = {
            "job_data": job_data,
            "user_profile": user_profile,
            "graphsage_skills": graphsage_skills or [],
            "formatter": "OaSIS-RoleFormatter"
        }
        
        response = await generate_career_advice(
            system_prompt=system_prompt,
            user_query="""
                Provide a skills-based analysis of this career opportunity:
                1. Top 5 critical skills and user's current level
                2. Transferable skills from user's background
                3. Quick wins vs long-term development areas
                4. Practical next steps to build readiness
            """,
            context=context
        )
        
        return {
            "skills_analysis": response
        }
        
    except Exception as e:
        logger.error(f"Error generating OaSIS analysis: {str(e)}")
        return {
            "error": "Unable to generate analysis at this time."
        }