"""
Program Matching Service

This service handles matching career goals with educational programs,
specifically focusing on CEGEP and university programs in Quebec.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..models import User

logger = logging.getLogger(__name__)

class ProgramMatchingService:
    """Service for matching career goals with educational programs"""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def find_programs_for_career_goal(
        self, 
        goal_id: int, 
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find educational programs that align with a career goal.
        
        Args:
            goal_id: Career goal ID
            user_id: User ID for personalization
            limit: Maximum number of programs to return
            
        Returns:
            List of matching programs with relevance scores
        """
        try:
            # Get career goal details with job information
            goal_query = text("""
                SELECT cg.id, cg.user_id, cg.notes, cg.target_date,
                       sj.job_title, sj.esco_id, sj.skills_required, sj.metadata
                FROM career_goals cg
                JOIN saved_jobs sj ON cg.job_id = sj.id
                WHERE cg.id = :goal_id AND cg.user_id = :user_id AND cg.status = 'active'
            """)
            
            goal_result = self.db.execute(goal_query, {"goal_id": goal_id, "user_id": user_id}).fetchone()
            
            if not goal_result:
                logger.warning(f"No active career goal found for goal_id={goal_id}, user_id={user_id}")
                return []
            
            job_title = goal_result[4]
            esco_id = goal_result[5]
            skills_required = goal_result[6] or []
            
            logger.info(f"Finding programs for career goal: {job_title} (ESCO: {esco_id})")
            
            # Get user profile for personalization
            user_profile = await self._get_user_profile(user_id)
            
            # Generate program recommendations based on job requirements
            programs = await self._search_matching_programs(
                job_title=job_title,
                esco_id=esco_id,
                skills_required=skills_required,
                user_profile=user_profile,
                limit=limit
            )
            
            # Calculate match scores and prepare response
            scored_programs = []
            for program in programs:
                match_score = self._calculate_match_score(
                    program=program,
                    job_title=job_title,
                    skills_required=skills_required,
                    user_profile=user_profile
                )
                
                program_recommendation = {
                    "id": program.get("id"),
                    "program_name": program.get("name"),
                    "institution": program.get("institution"),
                    "institution_type": program.get("type", "cegep"),
                    "program_code": program.get("code"),
                    "duration": program.get("duration"),
                    "admission_requirements": program.get("requirements", []),
                    "match_score": match_score,
                    "cost_estimate": program.get("cost"),
                    "location": {
                        "city": program.get("city"),
                        "province": "Quebec",
                        "campus_type": program.get("delivery_mode", "on_campus")
                    },
                    "intake_dates": program.get("intake_dates", []),
                    "relevance_explanation": self._generate_relevance_explanation(
                        program, job_title, match_score
                    ),
                    "career_outcomes": program.get("career_outcomes", []),
                    "website_url": program.get("website"),
                    "contact_info": program.get("contact")
                }
                scored_programs.append(program_recommendation)
            
            # Sort by match score and return top results
            scored_programs.sort(key=lambda x: x["match_score"], reverse=True)
            return scored_programs[:limit]
            
        except Exception as e:
            logger.error(f"Error finding programs for career goal {goal_id}: {str(e)}")
            raise
    
    async def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user profile data for personalization"""
        try:
            profile_query = text("""
                SELECT up.name, up.major, up.year, up.interests, up.hobbies,
                       up.education_level, up.country, up.state_province
                FROM user_profiles up
                WHERE up.user_id = :user_id
            """)
            
            result = self.db.execute(profile_query, {"user_id": user_id}).fetchone()
            
            if result:
                return {
                    "name": result[0],
                    "major": result[1], 
                    "year": result[2],
                    "interests": result[3],
                    "hobbies": result[4],
                    "education_level": result[5],
                    "location": {
                        "country": result[6],
                        "province": result[7]
                    }
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting user profile for user {user_id}: {str(e)}")
            return {}
    
    async def _search_matching_programs(
        self,
        job_title: str,
        esco_id: str,
        skills_required: List[str],
        user_profile: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search for programs matching the job requirements"""
        
        # For now, return mock data until we integrate with real CEGEP data
        # This would be replaced with actual database queries or API calls
        mock_programs = [
            {
                "id": "cegep-software-dev-1",
                "name": "Computer Science Technology - Software Development",
                "institution": "Dawson College",
                "type": "cegep",
                "code": "420.B0",
                "duration": "3 years",
                "requirements": [
                    "High school diploma or equivalent",
                    "Mathematics: TS 4 or SN 4 or 436",
                    "Physics: STE 4 or SE 4 or 534"
                ],
                "cost": 195.0,  # Per semester for Quebec residents
                "city": "Montreal",
                "delivery_mode": "on_campus",
                "intake_dates": ["September 2025", "January 2026"],
                "career_outcomes": [
                    "Software Developer",
                    "Web Developer", 
                    "Systems Analyst",
                    "Database Administrator"
                ],
                "website": "https://www.dawsoncollege.qc.ca/computer-science-technology/",
                "contact": {
                    "email": "admissions@dawsoncollege.qc.ca",
                    "phone": "(514) 931-8731"
                }
            },
            {
                "id": "university-computer-science-1",
                "name": "Bachelor of Computer Science",
                "institution": "McGill University",
                "type": "university",
                "code": "COMP",
                "duration": "4 years",
                "requirements": [
                    "CEGEP diploma or equivalent",
                    "Mathematics: Calculus 1 and 2",
                    "Strong performance in sciences",
                    "Minimum R-Score: 28"
                ],
                "cost": 3000.0,  # Per year for Quebec residents
                "city": "Montreal",
                "delivery_mode": "on_campus",
                "intake_dates": ["September 2025"],
                "career_outcomes": [
                    "Software Engineer",
                    "Research Scientist",
                    "Data Scientist",
                    "Technical Lead"
                ],
                "website": "https://www.mcgill.ca/study/2024-2025/faculties/science/undergraduate/programs/bachelor-science-bsc-major-computer-science",
                "contact": {
                    "email": "admissions@mcgill.ca",
                    "phone": "(514) 398-3910"
                }
            },
            {
                "id": "cegep-web-dev-1",
                "name": "Web Programming and Design",
                "institution": "Collège de Maisonneuve",
                "type": "cegep",
                "code": "582.A1",
                "duration": "3 years",
                "requirements": [
                    "High school diploma",
                    "Mathematics: CST 4 or 514"
                ],
                "cost": 195.0,
                "city": "Montreal", 
                "delivery_mode": "hybrid",
                "intake_dates": ["September 2025"],
                "career_outcomes": [
                    "Web Developer",
                    "Front-end Developer",
                    "UI/UX Designer",
                    "Digital Media Specialist"
                ],
                "website": "https://www.cmaisonneuve.qc.ca/programme/techniques-de-linformatique-programmation-web-et-conception/",
                "contact": {
                    "email": "admission@cmaisonneuve.qc.ca",
                    "phone": "(514) 254-7131"
                }
            }
        ]
        
        # Filter programs based on job title keywords
        job_keywords = job_title.lower().split()
        relevant_programs = []
        
        for program in mock_programs:
            program_text = f"{program['name']} {' '.join(program['career_outcomes'])}".lower()
            
            # Check if job keywords match program content
            match_count = sum(1 for keyword in job_keywords if keyword in program_text)
            if match_count > 0:
                relevant_programs.append(program)
        
        # If no keyword matches, return all programs (broad search)
        if not relevant_programs:
            relevant_programs = mock_programs
            
        return relevant_programs[:limit]
    
    def _calculate_match_score(
        self,
        program: Dict[str, Any],
        job_title: str,
        skills_required: List[str],
        user_profile: Dict[str, Any]
    ) -> float:
        """Calculate a match score between 0.0 and 1.0 for a program"""
        
        score = 0.0
        
        # Job title relevance (40% weight)
        job_keywords = set(job_title.lower().split())
        program_text = f"{program.get('name', '')} {' '.join(program.get('career_outcomes', []))}".lower()
        program_words = set(program_text.split())
        
        keyword_matches = len(job_keywords.intersection(program_words))
        job_relevance = min(1.0, keyword_matches / max(len(job_keywords), 1)) * 0.4
        score += job_relevance
        
        # Skills alignment (30% weight)
        if skills_required:
            program_outcomes = program.get('career_outcomes', [])
            skills_text = ' '.join(skills_required).lower()
            outcomes_text = ' '.join(program_outcomes).lower()
            
            # Simple keyword matching for skills
            skill_words = set(skills_text.split())
            outcome_words = set(outcomes_text.split())
            skill_matches = len(skill_words.intersection(outcome_words))
            skills_relevance = min(1.0, skill_matches / max(len(skill_words), 1)) * 0.3
            score += skills_relevance
        
        # User profile alignment (20% weight)
        profile_score = 0.0
        
        # Education level compatibility
        current_education = user_profile.get('education_level', '').lower()
        program_type = program.get('type', 'cegep').lower()
        
        if program_type == 'cegep' and 'high school' in current_education:
            profile_score += 0.1
        elif program_type == 'university' and ('cegep' in current_education or 'college' in current_education):
            profile_score += 0.1
        
        # Location preference (Quebec residents)
        user_location = user_profile.get('location', {})
        if user_location.get('province', '').lower() in ['quebec', 'qc']:
            profile_score += 0.1
        
        score += profile_score
        
        # Institution reputation bonus (10% weight)
        prestigious_institutions = ['mcgill', 'concordia', 'uqam', 'université', 'dawson']
        institution_name = program.get('institution', '').lower()
        
        if any(prestige in institution_name for prestige in prestigious_institutions):
            score += 0.1
        
        return min(1.0, max(0.1, score))  # Ensure score is between 0.1 and 1.0
    
    def _generate_relevance_explanation(
        self,
        program: Dict[str, Any],
        job_title: str,
        match_score: float
    ) -> str:
        """Generate a human-readable explanation of why this program matches"""
        
        program_name = program.get('name', 'Unknown Program')
        institution = program.get('institution', 'Unknown Institution')
        career_outcomes = program.get('career_outcomes', [])
        
        explanations = []
        
        # Match score interpretation
        if match_score >= 0.8:
            explanations.append(f"This program is an excellent match for {job_title}.")
        elif match_score >= 0.6:
            explanations.append(f"This program aligns well with {job_title}.")
        else:
            explanations.append(f"This program provides relevant foundation for {job_title}.")
        
        # Career outcomes
        if career_outcomes:
            matching_outcomes = [outcome for outcome in career_outcomes 
                               if any(word in outcome.lower() for word in job_title.lower().split())]
            if matching_outcomes:
                explanations.append(f"Graduates often work as {', '.join(matching_outcomes[:2])}.")
        
        # Institution credibility
        explanations.append(f"Offered by {institution}, a recognized educational institution.")
        
        return ' '.join(explanations)
    
    async def save_program_recommendation(
        self,
        goal_id: int,
        program_data: Dict[str, Any]
    ) -> int:
        """Save a program recommendation to the database"""
        try:
            insert_query = text("""
                INSERT INTO program_recommendations (
                    goal_id, program_name, institution, institution_type,
                    program_code, duration, admission_requirements, match_score,
                    cost_estimate, location, intake_dates, created_at
                ) VALUES (
                    :goal_id, :program_name, :institution, :institution_type,
                    :program_code, :duration, :admission_requirements::jsonb, :match_score,
                    :cost_estimate, :location::jsonb, :intake_dates::jsonb, NOW()
                ) RETURNING id
            """)
            
            result = self.db.execute(insert_query, {
                "goal_id": goal_id,
                "program_name": program_data.get("program_name"),
                "institution": program_data.get("institution"),
                "institution_type": program_data.get("institution_type"),
                "program_code": program_data.get("program_code"),
                "duration": program_data.get("duration"),
                "admission_requirements": json.dumps(program_data.get("admission_requirements", [])),
                "match_score": program_data.get("match_score"),
                "cost_estimate": program_data.get("cost_estimate"),
                "location": json.dumps(program_data.get("location", {})),
                "intake_dates": json.dumps(program_data.get("intake_dates", []))
            }).fetchone()
            
            self.db.commit()
            
            recommendation_id = result[0]
            logger.info(f"Saved program recommendation {recommendation_id} for goal {goal_id}")
            return recommendation_id
            
        except Exception as e:
            logger.error(f"Error saving program recommendation: {str(e)}")
            self.db.rollback()
            raise
    
    async def get_saved_recommendations(self, goal_id: int) -> List[Dict[str, Any]]:
        """Get previously saved program recommendations for a career goal"""
        try:
            query = text("""
                SELECT id, program_name, institution, institution_type,
                       program_code, duration, admission_requirements, match_score,
                       cost_estimate, location, intake_dates, created_at
                FROM program_recommendations
                WHERE goal_id = :goal_id
                ORDER BY match_score DESC, created_at DESC
            """)
            
            results = self.db.execute(query, {"goal_id": goal_id}).fetchall()
            
            recommendations = []
            for row in results:
                recommendations.append({
                    "id": row[0],
                    "program_name": row[1],
                    "institution": row[2],
                    "institution_type": row[3],
                    "program_code": row[4],
                    "duration": row[5],
                    "admission_requirements": json.loads(row[6]) if row[6] else [],
                    "match_score": float(row[7]) if row[7] else 0.0,
                    "cost_estimate": float(row[8]) if row[8] else None,
                    "location": json.loads(row[9]) if row[9] else {},
                    "intake_dates": json.loads(row[10]) if row[10] else [],
                    "created_at": row[11]
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting saved recommendations for goal {goal_id}: {str(e)}")
            return []