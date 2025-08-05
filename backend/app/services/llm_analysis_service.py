"""
LLM Analysis Service for generating personalized job recommendation analyses.
"""

import os
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
import logging

from ..models import User, UserSkill, UserProfile, SavedRecommendation, UserRepresentation

logger = logging.getLogger(__name__)

# Configure OpenAI
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


async def generate_personalized_analysis(
    user_id: int,
    recommendation: SavedRecommendation,
    db: Session
) -> Dict[str, str]:
    """
    Generate personalized LLM analysis for a job recommendation based on user profile.
    
    Args:
        user_id: The user's ID
        recommendation: The saved recommendation to analyze
        db: Database session
        
    Returns:
        Dict containing personal_analysis, entry_qualifications, and suggested_improvements
    """
    try:
        # Get user profile data
        user = db.query(User).filter(User.id == user_id).first()
        user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).first()
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        user_representation = db.query(UserRepresentation).filter(UserRepresentation.user_id == user_id).first()
        
        # Get Holland test results if available
        holland_results = None
        try:
            holland_query = db.execute(
                "SELECT r_score, i_score, a_score, s_score, e_score, c_score, top_3_code "
                "FROM gca_results WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 1",
                {"user_id": user_id}
            )
            holland_row = holland_query.fetchone()
            if holland_row:
                holland_results = {
                    'realistic': holland_row[0],
                    'investigative': holland_row[1], 
                    'artistic': holland_row[2],
                    'social': holland_row[3],
                    'enterprising': holland_row[4],
                    'conventional': holland_row[5],
                    'top_3_code': holland_row[6]
                }
        except Exception as e:
            logger.debug(f"Could not fetch Holland results: {e}")
            holland_results = None
        
        # Build user profile text
        profile_sections = []
        
        # Add skills if available
        if user_skills:
            skills_text = []
            skill_mapping = {
                "creativity": "Creativity",
                "leadership": "Leadership",
                "digital_literacy": "Digital Literacy",
                "critical_thinking": "Critical Thinking",
                "problem_solving": "Problem Solving",
                "analytical_thinking": "Analytical Thinking",
                "attention_to_detail": "Attention to Detail",
                "collaboration": "Collaboration",
                "adaptability": "Adaptability",
                "independence": "Independence",
                "evaluation": "Evaluation",
                "decision_making": "Decision Making",
                "stress_tolerance": "Stress Tolerance"
            }
            
            for skill_key, skill_name in skill_mapping.items():
                value = getattr(user_skills, skill_key)
                if value is not None:
                    skills_text.append(f"- {skill_name}: {value}/5")
            
            if skills_text:
                profile_sections.append(f"Skills:\n" + "\n".join(skills_text))
        
        # Add user profile information if available
        if user_profile:
            if user_profile.interests:
                profile_sections.append(f"Interests:\n{user_profile.interests}")
            
            if user_profile.hobbies:
                profile_sections.append(f"Hobbies:\n{user_profile.hobbies}")
            
            if user_profile.career_goals:
                profile_sections.append(f"Career Goals:\n{user_profile.career_goals}")
            
            # Experience information
            experience_info = []
            if user_profile.job_title:
                experience_info.append(f"Current Job: {user_profile.job_title}")
            if user_profile.industry:
                experience_info.append(f"Industry: {user_profile.industry}")
            if user_profile.years_experience:
                experience_info.append(f"Years of Experience: {user_profile.years_experience}")
            
            if experience_info:
                profile_sections.append("Experience:\n" + "\n".join(experience_info))
            
            # Education information
            education_info = []
            if user_profile.education_level:
                education_info.append(f"Education Level: {user_profile.education_level}")
            if user_profile.major:
                education_info.append(f"Major: {user_profile.major}")
            if user_profile.gpa:
                education_info.append(f"GPA: {user_profile.gpa}")
            
            if education_info:
                profile_sections.append("Education:\n" + "\n".join(education_info))
            
            # Skills array
            if user_profile.skills:
                profile_sections.append(f"Additional Skills:\n{', '.join(user_profile.skills)}")
            
            # Personal information
            personal_info = []
            if user_profile.name:
                personal_info.append(f"Name: {user_profile.name}")
            if user_profile.age:
                personal_info.append(f"Age: {user_profile.age}")
            if user_profile.learning_style:
                personal_info.append(f"Learning Style: {user_profile.learning_style}")
            
            if personal_info:
                profile_sections.append("Personal Information:\n" + "\n".join(personal_info))
            
            # Add personality analysis if available
            if user_profile.personal_analysis:
                profile_sections.append(f"Personality Analysis:\n{user_profile.personal_analysis}")
        
        # Add Holland test results if available
        if holland_results:
            holland_text = f"""Holland Career Assessment (RIASEC):
- Realistic: {holland_results['realistic']:.2f}
- Investigative: {holland_results['investigative']:.2f}
- Artistic: {holland_results['artistic']:.2f}
- Social: {holland_results['social']:.2f}
- Enterprising: {holland_results['enterprising']:.2f}
- Conventional: {holland_results['conventional']:.2f}
- Top 3 Career Types: {holland_results['top_3_code']}"""
            profile_sections.append(holland_text)
        
        # Add user representation summary if available
        if user_representation and user_representation.summary:
            profile_sections.append(f"AI-Generated User Summary:\n{user_representation.summary}")
        
        # Build the complete user profile
        user_profile_text = "\n\n".join(profile_sections) if profile_sections else "Limited profile information available."
        
        # Build job information
        job_info = f"""
Job Title: {recommendation.label}
OASIS Code: {recommendation.oasis_code}

Description:
{recommendation.description or 'No description available.'}

Main Duties:
{recommendation.main_duties or 'No main duties specified.'}

Required Skills (Role Requirements):
- Creativity: {recommendation.role_creativity}/5
- Leadership: {recommendation.role_leadership}/5
- Digital Literacy: {recommendation.role_digital_literacy}/5
- Critical Thinking: {recommendation.role_critical_thinking}/5
- Problem Solving: {recommendation.role_problem_solving}/5

Cognitive Traits Required:
- Analytical Thinking: {recommendation.analytical_thinking}/5
- Attention to Detail: {recommendation.attention_to_detail}/5
- Collaboration: {recommendation.collaboration}/5
- Adaptability: {recommendation.adaptability}/5
- Independence: {recommendation.independence}/5
- Evaluation: {recommendation.evaluation}/5
- Decision Making: {recommendation.decision_making}/5
- Stress Tolerance: {recommendation.stress_tolerance}/5
"""

        # Create the prompt
        prompt = f"""
You are an expert career counselor analyzing job-candidate fit. Please provide a personalized analysis for this specific user and job combination.

## User Profile:
{user_profile_text}

## Job Information:
{job_info}

Please provide:

1. **Personal Analysis**: A detailed, personalized analysis of how well this specific user matches this job. Consider their unique skills, personality, interests, and experience. Be specific about strengths and potential challenges based on their profile.

2. **Entry Qualifications**: List the key qualifications and requirements for entering this role, considering both technical skills and soft skills.

3. **Suggested Improvements**: Provide concrete, actionable steps this specific user can take to improve their fit for this role. Base these suggestions on their current profile and the gaps identified.

Format your response with clear sections for each of the three areas. Make the analysis highly personalized and specific to this user's profile, not generic.
"""

        # Call OpenAI API
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert career counselor providing personalized job fit analysis. Focus on being specific and actionable based on the user's unique profile."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse the response
        full_response = response.choices[0].message.content
        
        # Extract sections from the response
        sections = {
            "personal_analysis": "",
            "entry_qualifications": "",
            "suggested_improvements": ""
        }
        
        # Split response into sections
        current_section = None
        lines = full_response.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # Identify section headers
            if 'personal analysis' in line_lower:
                current_section = 'personal_analysis'
                continue
            elif 'entry qualification' in line_lower or 'key qualification' in line_lower:
                current_section = 'entry_qualifications'
                continue
            elif 'suggested improvement' in line_lower or 'improvement' in line_lower or 'suggestion' in line_lower:
                current_section = 'suggested_improvements'
                continue
            
            # Add content to current section
            if current_section and line.strip():
                if not line.startswith('**') and not line.startswith('##'):  # Skip headers
                    sections[current_section] += line + '\n'
        
        # Clean up sections
        for key in sections:
            sections[key] = sections[key].strip()
            
        # Fallback if parsing didn't work well
        if not all(sections.values()):
            # Try a simpler split approach
            parts = full_response.split('\n\n')
            if len(parts) >= 3:
                sections['personal_analysis'] = parts[0]
                sections['entry_qualifications'] = parts[1] 
                sections['suggested_improvements'] = '\n\n'.join(parts[2:])
        
        return sections
        
    except Exception as e:
        logger.error(f"Error generating LLM analysis: {str(e)}")
        # Return default values on error
        return {
            "personal_analysis": "Unable to generate personalized analysis at this time. Please try again later.",
            "entry_qualifications": "Unable to load entry qualifications. Please try again later.",
            "suggested_improvements": "Unable to generate improvement suggestions. Please try again later."
        }


async def update_recommendation_analysis(
    recommendation_id: int,
    user_id: int,
    db: Session
) -> SavedRecommendation:
    """
    Update a saved recommendation with LLM analysis.
    
    Args:
        recommendation_id: The recommendation ID
        user_id: The user's ID
        db: Database session
        
    Returns:
        Updated SavedRecommendation object
    """
    # Get the recommendation
    recommendation = db.query(SavedRecommendation).filter(
        SavedRecommendation.id == recommendation_id,
        SavedRecommendation.user_id == user_id
    ).first()
    
    if not recommendation:
        raise ValueError("Recommendation not found")
    
    # Generate analysis
    analysis = await generate_personalized_analysis(user_id, recommendation, db)
    
    # Update recommendation with analysis
    recommendation.personal_analysis = analysis['personal_analysis']
    recommendation.entry_qualifications = analysis['entry_qualifications']
    recommendation.suggested_improvements = analysis['suggested_improvements']
    
    db.commit()
    db.refresh(recommendation)
    
    return recommendation