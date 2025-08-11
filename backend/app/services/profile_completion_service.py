"""
Profile Completion Service

This service calculates user profile completion percentage across all data sources
and provides recommendations for improving profile completeness.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, select

from ..models.user_profile import UserProfile
from ..models.personality_profiles import PersonalityProfile
from ..models.user import User
from ..utils.clerk_auth import get_database_user_id_sync

logger = logging.getLogger(__name__)


class CompletionAction:
    """Represents a profile completion action."""
    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        url: str,
        category: str,
        weight: float,
        estimated_time: str
    ):
        self.id = id
        self.title = title
        self.description = description
        self.url = url
        self.category = category
        self.weight = weight
        self.estimated_time = estimated_time


class ProfileCompletionResult:
    """Profile completion analysis result."""
    def __init__(
        self,
        overall_percentage: float,
        category_scores: Dict[str, float],
        next_actions: List[CompletionAction],
        recommendation_eligible: bool,
        missing_critical_data: List[str]
    ):
        self.overall_percentage = overall_percentage
        self.category_scores = category_scores
        self.next_actions = next_actions
        self.recommendation_eligible = recommendation_eligible
        self.missing_critical_data = missing_critical_data


class ProfileCompletionCalculator:
    """Calculates profile completion across all data sources."""

    # Define completion categories and their weights
    COMPLETION_CATEGORIES = {
        "basic_info": {
            "weight": 0.25,
            "required_for_recommendations": True,
            "fields": ["name", "age", "major", "year", "country"]
        },
        "career_info": {
            "weight": 0.20,
            "required_for_recommendations": True,
            "fields": ["job_title", "industry", "education_level", "career_goals"]
        },
        "personality_assessments": {
            "weight": 0.20,
            "required_for_recommendations": True,
            "assessments": ["hexaco", "holland"]
        },
        "personal_details": {
            "weight": 0.15,
            "required_for_recommendations": False,
            "fields": ["hobbies", "interests", "learning_style", "story", "unique_quality"]
        },
        "preferences": {
            "weight": 0.10,
            "required_for_recommendations": False,
            "fields": ["favorite_movie", "favorite_book", "favorite_celebrities"]
        },
        "skills_goals": {
            "weight": 0.10,
            "required_for_recommendations": False,
            "fields": ["skills", "years_experience", "gpa"]
        }
    }

    # Minimum completion percentage for recommendations
    MIN_COMPLETION_FOR_RECOMMENDATIONS = 0.60

    @classmethod
    def calculate_completion(cls, db: Session, user_id: str) -> ProfileCompletionResult:
        """
        Calculate profile completion percentage for a user.
        
        Args:
            db: Database session
            user_id: Clerk user ID
            
        Returns:
            ProfileCompletionResult with completion analysis
        """
        try:
            # Convert Clerk user ID to database user ID
            db_user_id = get_database_user_id_sync(user_id, db)
            if not db_user_id:
                logger.error(f"User not found for Clerk ID: {user_id}")
                return cls._get_empty_result()

            # Get user profile
            profile = db.query(UserProfile).filter(UserProfile.user_id == db_user_id).first()
            if not profile:
                logger.info(f"No profile found for user {user_id}")
                return cls._get_empty_result()

            # Calculate completion for each category
            category_scores = {}
            
            # Basic info completion
            category_scores["basic_info"] = cls._calculate_basic_info_completion(profile)
            
            # Career info completion
            category_scores["career_info"] = cls._calculate_career_info_completion(profile)
            
            # Personality assessments completion
            category_scores["personality_assessments"] = cls._calculate_assessments_completion(db, db_user_id)
            
            # Personal details completion
            category_scores["personal_details"] = cls._calculate_personal_details_completion(profile)
            
            # Preferences completion
            category_scores["preferences"] = cls._calculate_preferences_completion(profile)
            
            # Skills and goals completion
            category_scores["skills_goals"] = cls._calculate_skills_goals_completion(profile)

            # Calculate overall completion percentage
            overall_percentage = cls._calculate_overall_percentage(category_scores)
            
            # Determine recommendation eligibility
            recommendation_eligible = cls._is_recommendation_eligible(category_scores, overall_percentage)
            
            # Get next recommended actions
            next_actions = cls._get_next_actions(category_scores, profile, db, db_user_id)
            
            # Get missing critical data
            missing_critical_data = cls._get_missing_critical_data(category_scores, profile)

            logger.info(f"Profile completion calculated for user {user_id}: {overall_percentage:.1%}")
            
            return ProfileCompletionResult(
                overall_percentage=overall_percentage,
                category_scores=category_scores,
                next_actions=next_actions,
                recommendation_eligible=recommendation_eligible,
                missing_critical_data=missing_critical_data
            )

        except Exception as e:
            logger.error(f"Error calculating profile completion for user {user_id}: {e}")
            return cls._get_empty_result()

    @classmethod
    def _calculate_basic_info_completion(cls, profile: UserProfile) -> float:
        """Calculate completion for basic info fields."""
        fields = cls.COMPLETION_CATEGORIES["basic_info"]["fields"]
        completed_fields = 0
        
        for field in fields:
            value = getattr(profile, field, None)
            if value is not None and str(value).strip():
                completed_fields += 1
                
        return completed_fields / len(fields)

    @classmethod
    def _calculate_career_info_completion(cls, profile: UserProfile) -> float:
        """Calculate completion for career info fields."""
        fields = cls.COMPLETION_CATEGORIES["career_info"]["fields"]
        completed_fields = 0
        
        for field in fields:
            value = getattr(profile, field, None)
            if value is not None and str(value).strip():
                completed_fields += 1
                
        return completed_fields / len(fields)

    @classmethod
    def _calculate_assessments_completion(cls, db: Session, db_user_id: int) -> float:
        """Calculate completion for personality assessments."""
        # Check for recent personality assessments
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=365)  # Consider assessments valid for 1 year
        
        recent_assessments = db.query(PersonalityProfile).filter(
            PersonalityProfile.user_id == db_user_id,
            PersonalityProfile.computed_at >= cutoff_date
        ).all()
        
        if not recent_assessments:
            return 0.0
        
        # Check for specific assessment types
        assessment_types = set()
        for assessment in recent_assessments:
            profile_type = assessment.profile_type.lower()
            if "hexaco" in profile_type:
                assessment_types.add("hexaco")
            elif "holland" in profile_type or "riasec" in profile_type:
                assessment_types.add("holland")
        
        required_assessments = cls.COMPLETION_CATEGORIES["personality_assessments"]["assessments"]
        completed_assessments = len(assessment_types.intersection(set(required_assessments)))
        
        return completed_assessments / len(required_assessments)

    @classmethod
    def _calculate_personal_details_completion(cls, profile: UserProfile) -> float:
        """Calculate completion for personal details fields."""
        fields = cls.COMPLETION_CATEGORIES["personal_details"]["fields"]
        completed_fields = 0
        
        for field in fields:
            value = getattr(profile, field, None)
            if value is not None and str(value).strip():
                completed_fields += 1
                
        return completed_fields / len(fields)

    @classmethod
    def _calculate_preferences_completion(cls, profile: UserProfile) -> float:
        """Calculate completion for preferences fields."""
        fields = cls.COMPLETION_CATEGORIES["preferences"]["fields"]
        completed_fields = 0
        
        for field in fields:
            value = getattr(profile, field, None)
            if value is not None and str(value).strip():
                completed_fields += 1
                
        return completed_fields / len(fields)

    @classmethod
    def _calculate_skills_goals_completion(cls, profile: UserProfile) -> float:
        """Calculate completion for skills and goals fields."""
        fields = cls.COMPLETION_CATEGORIES["skills_goals"]["fields"]
        completed_fields = 0
        
        for field in fields:
            value = getattr(profile, field, None)
            if field == "skills":
                # Skills is an array - check if it has elements
                if value is not None and len(value) > 0:
                    completed_fields += 1
            else:
                if value is not None and str(value).strip():
                    completed_fields += 1
                    
        return completed_fields / len(fields)

    @classmethod
    def _calculate_overall_percentage(cls, category_scores: Dict[str, float]) -> float:
        """Calculate weighted overall completion percentage."""
        total_weight = 0
        weighted_sum = 0
        
        for category, score in category_scores.items():
            if category in cls.COMPLETION_CATEGORIES:
                weight = cls.COMPLETION_CATEGORIES[category]["weight"]
                total_weight += weight
                weighted_sum += score * weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    @classmethod
    def _is_recommendation_eligible(cls, category_scores: Dict[str, float], overall_percentage: float) -> bool:
        """Determine if user is eligible for personalized recommendations."""
        # Check overall completion threshold
        if overall_percentage < cls.MIN_COMPLETION_FOR_RECOMMENDATIONS:
            return False
        
        # Check critical categories
        for category, config in cls.COMPLETION_CATEGORIES.items():
            if config.get("required_for_recommendations", False):
                if category_scores.get(category, 0) < 0.5:  # At least 50% completion in critical categories
                    return False
        
        return True

    @classmethod
    def _get_next_actions(
        cls, 
        category_scores: Dict[str, float], 
        profile: UserProfile,
        db: Session,
        db_user_id: int
    ) -> List[CompletionAction]:
        """Get next recommended actions for profile completion."""
        actions = []
        
        # Prioritize critical categories first
        sorted_categories = sorted(
            cls.COMPLETION_CATEGORIES.items(),
            key=lambda x: (not x[1].get("required_for_recommendations", False), category_scores.get(x[0], 0))
        )
        
        for category, config in sorted_categories:
            score = category_scores.get(category, 0)
            if score < 1.0:  # Not fully complete
                action = cls._get_action_for_category(category, config, score, profile, db, db_user_id)
                if action:
                    actions.append(action)
        
        return actions[:5]  # Return top 5 actions

    @classmethod
    def _get_action_for_category(
        cls,
        category: str,
        config: Dict[str, Any],
        score: float,
        profile: UserProfile,
        db: Session,
        db_user_id: int
    ) -> Optional[CompletionAction]:
        """Get specific action for a category."""
        if category == "basic_info":
            return CompletionAction(
                id="complete_basic_info",
                title="Complete Basic Information",
                description="Add your name, age, major, and location details",
                url="/profile",
                category="Essential",
                weight=config["weight"],
                estimated_time="2 minutes"
            )
        elif category == "career_info":
            return CompletionAction(
                id="complete_career_info",
                title="Complete Career Information",
                description="Add your job title, industry, and career goals",
                url="/profile",
                category="Essential",
                weight=config["weight"],
                estimated_time="3 minutes"
            )
        elif category == "personality_assessments":
            # Check which specific assessments are missing
            recent_assessments = db.query(PersonalityProfile).filter(
                PersonalityProfile.user_id == db_user_id,
                PersonalityProfile.computed_at >= datetime.now(timezone.utc) - timedelta(days=365)
            ).all()
            
            assessment_types = set()
            for assessment in recent_assessments:
                profile_type = assessment.profile_type.lower()
                if "hexaco" in profile_type:
                    assessment_types.add("hexaco")
                elif "holland" in profile_type or "riasec" in profile_type:
                    assessment_types.add("holland")
            
            if "hexaco" not in assessment_types:
                return CompletionAction(
                    id="take_hexaco_test",
                    title="Take Personality Assessment",
                    description="Complete the HEXACO personality test to understand your traits",
                    url="/hexaco-test",
                    category="Essential",
                    weight=config["weight"],
                    estimated_time="10 minutes"
                )
            elif "holland" not in assessment_types:
                return CompletionAction(
                    id="take_holland_test",
                    title="Take Career Interest Assessment",
                    description="Complete the Holland Code test to discover your career interests",
                    url="/holland-test",
                    category="Essential",
                    weight=config["weight"],
                    estimated_time="8 minutes"
                )
        elif category == "personal_details":
            return CompletionAction(
                id="complete_personal_details",
                title="Share Your Personal Story",
                description="Add hobbies, interests, and your unique story",
                url="/profile",
                category="Personal",
                weight=config["weight"],
                estimated_time="5 minutes"
            )
        elif category == "preferences":
            return CompletionAction(
                id="add_preferences",
                title="Add Your Preferences",
                description="Share your favorite movies, books, and celebrities",
                url="/profile",
                category="Personal",
                weight=config["weight"],
                estimated_time="2 minutes"
            )
        elif category == "skills_goals":
            return CompletionAction(
                id="define_skills_goals",
                title="Define Skills & Experience",
                description="Add your skills, experience level, and academic performance",
                url="/profile",
                category="Professional",
                weight=config["weight"],
                estimated_time="4 minutes"
            )
        
        return None

    @classmethod
    def _get_missing_critical_data(cls, category_scores: Dict[str, float], profile: UserProfile) -> List[str]:
        """Get list of missing critical data for recommendations."""
        missing = []
        
        for category, config in cls.COMPLETION_CATEGORIES.items():
            if config.get("required_for_recommendations", False):
                score = category_scores.get(category, 0)
                if score < 0.5:  # Less than 50% complete
                    missing.append(category.replace("_", " ").title())
        
        return missing

    @classmethod
    def _get_empty_result(cls) -> ProfileCompletionResult:
        """Return empty result for error cases."""
        return ProfileCompletionResult(
            overall_percentage=0.0,
            category_scores={},
            next_actions=[],
            recommendation_eligible=False,
            missing_critical_data=["All categories need completion"]
        )