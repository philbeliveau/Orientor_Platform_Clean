import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from ..models.course import Course, PsychologicalInsight, CareerSignal, ConversationLog
from ..models.user import User
from ..schemas.course import SubjectCategory
import asyncio

logger = logging.getLogger(__name__)

class CourseAnalysisService:
    """
    Service for analyzing courses and extracting psychological insights.
    """
    
    @staticmethod
    async def categorize_course(course_name: str, description: Optional[str] = None) -> SubjectCategory:
        """
        Automatically categorize a course based on name and description.
        """
        course_text = f"{course_name} {description or ''}".lower()
        
        # STEM indicators
        stem_keywords = [
            'math', 'calculus', 'algebra', 'statistics', 'data', 'science', 'computer',
            'programming', 'software', 'engineering', 'physics', 'chemistry', 'biology',
            'technology', 'machine learning', 'artificial intelligence', 'algorithm'
        ]
        
        # Business indicators
        business_keywords = [
            'business', 'management', 'marketing', 'finance', 'accounting', 'economics',
            'strategy', 'operations', 'leadership', 'entrepreneurship', 'sales'
        ]
        
        # Arts indicators
        arts_keywords = [
            'art', 'design', 'creative', 'music', 'theater', 'visual', 'fine arts',
            'drawing', 'painting', 'sculpture', 'photography', 'film', 'media'
        ]
        
        # Humanities indicators
        humanities_keywords = [
            'history', 'literature', 'philosophy', 'language', 'english', 'writing',
            'cultural', 'social', 'anthropology', 'sociology', 'political', 'law'
        ]
        
        # Count matches for each category
        stem_score = sum(1 for keyword in stem_keywords if keyword in course_text)
        business_score = sum(1 for keyword in business_keywords if keyword in course_text)
        arts_score = sum(1 for keyword in arts_keywords if keyword in course_text)
        humanities_score = sum(1 for keyword in humanities_keywords if keyword in course_text)
        
        # Determine category based on highest score
        scores = {
            SubjectCategory.STEM: stem_score,
            SubjectCategory.BUSINESS: business_score,
            SubjectCategory.ARTS: arts_score,
            SubjectCategory.HUMANITIES: humanities_score
        }
        
        best_category = max(scores, key=scores.get)
        
        # If no clear category or tie, default to OTHER
        if scores[best_category] == 0 or list(scores.values()).count(scores[best_category]) > 1:
            return SubjectCategory.OTHER
        
        return best_category
    
    @staticmethod
    async def build_analysis_context(
        course: Course, 
        user: User, 
        db: Session, 
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Build context for course analysis including user history and course details.
        """
        context = {
            "course": {
                "name": course.course_name,
                "category": course.subject_category,
                "grade": course.grade,
                "semester": course.semester,
                "year": course.year,
                "professor": course.professor
            },
            "user_history": {},
            "previous_insights": [],
            "career_signals": [],
            "focus_areas": focus_areas or []
        }
        
        # Get user's other courses for pattern analysis
        other_courses = db.query(Course).filter(
            Course.user_id == user.id,
            Course.id != course.id
        ).all()
        
        if other_courses:
            context["user_history"]["total_courses"] = len(other_courses)
            context["user_history"]["subject_distribution"] = {}
            
            for other_course in other_courses:
                category = other_course.subject_category
                if category:
                    context["user_history"]["subject_distribution"][category] = \
                        context["user_history"]["subject_distribution"].get(category, 0) + 1
        
        # Get previous insights for this course
        insights = db.query(PsychologicalInsight).filter(
            PsychologicalInsight.course_id == course.id
        ).all()
        
        context["previous_insights"] = [
            {
                "type": insight.insight_type,
                "value": insight.insight_value,
                "confidence": insight.confidence_score,
                "date": insight.extracted_at.isoformat()
            }
            for insight in insights
        ]
        
        # Get career signals for the user
        signals = db.query(CareerSignal).filter(
            CareerSignal.user_id == user.id
        ).limit(10).all()
        
        context["career_signals"] = [
            {
                "type": signal.signal_type,
                "strength": signal.strength_score,
                "evidence": signal.evidence_source
            }
            for signal in signals
        ]
        
        # Generate initial insights based on context
        if not insights:
            context["initial_insights"] = await CourseAnalysisService._generate_initial_insights(
                course, context
            )
        
        return context
    
    @staticmethod
    async def _generate_initial_insights(course: Course, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate initial insights based on course and user context.
        """
        insights = []
        
        # Performance pattern insights
        if course.grade:
            grade_quality = CourseAnalysisService._assess_grade_quality(course.grade)
            if grade_quality:
                insights.append({
                    "type": "performance_indicator",
                    "insight": f"Grade of {course.grade} suggests {grade_quality} performance in {course.subject_category}",
                    "questions_to_explore": [
                        "What aspects of this course did you find most engaging?",
                        "Were there specific challenges that stood out to you?"
                    ]
                })
        
        # Subject pattern insights
        subject_history = context.get("user_history", {}).get("subject_distribution", {})
        if course.subject_category in subject_history:
            insights.append({
                "type": "subject_pattern",
                "insight": f"This is your {subject_history[course.subject_category] + 1} course in {course.subject_category}",
                "questions_to_explore": [
                    "How does this course compare to your other courses in this subject?",
                    "What draws you to this field of study?"
                ]
            })
        
        return insights
    
    @staticmethod
    def _assess_grade_quality(grade: str) -> Optional[str]:
        """
        Assess the quality of a grade for insight generation.
        """
        grade_upper = grade.upper()
        
        if grade_upper in ['A+', 'A', 'A-']:
            return "excellent"
        elif grade_upper in ['B+', 'B', 'B-']:
            return "good"
        elif grade_upper in ['C+', 'C', 'C-']:
            return "satisfactory"
        elif grade_upper in ['D+', 'D', 'D-', 'F']:
            return "challenging"
        
        return None
    
    @staticmethod
    async def generate_profile_summary(
        insights: List[PsychologicalInsight], 
        signals: List[CareerSignal]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive psychological profile summary.
        """
        summary = {
            "cognitive_preferences": {},
            "work_style_indicators": {},
            "subject_affinities": {},
            "career_readiness": {},
            "confidence_score": 0.0
        }
        
        # Group insights by type
        insight_groups = {}
        for insight in insights:
            insight_type = insight.insight_type
            if insight_type not in insight_groups:
                insight_groups[insight_type] = []
            insight_groups[insight_type].append(insight)
        
        # Analyze cognitive preferences
        if "cognitive_preference" in insight_groups:
            cognitive_insights = insight_groups["cognitive_preference"]
            summary["cognitive_preferences"] = CourseAnalysisService._analyze_cognitive_patterns(
                cognitive_insights
            )
        
        # Analyze work style preferences
        if "work_style" in insight_groups:
            work_style_insights = insight_groups["work_style"]
            summary["work_style_indicators"] = CourseAnalysisService._analyze_work_style_patterns(
                work_style_insights
            )
        
        # Analyze subject affinities
        if "subject_affinity" in insight_groups:
            affinity_insights = insight_groups["subject_affinity"]
            summary["subject_affinities"] = CourseAnalysisService._analyze_subject_patterns(
                affinity_insights
            )
        
        # Analyze career signals
        summary["career_readiness"] = CourseAnalysisService._analyze_career_signals(signals)
        
        # Calculate overall confidence score
        total_insights = len(insights)
        if total_insights > 0:
            avg_confidence = sum(i.confidence_score or 0.5 for i in insights) / total_insights
            summary["confidence_score"] = min(0.9, avg_confidence + (total_insights * 0.05))
        
        return summary
    
    @staticmethod
    def _analyze_cognitive_patterns(insights: List[PsychologicalInsight]) -> Dict[str, Any]:
        """
        Analyze cognitive preference patterns from insights.
        """
        patterns = {
            "analytical_thinking": 0.0,
            "creative_thinking": 0.0,
            "concrete_vs_abstract": 0.0,  # -1 = concrete, +1 = abstract
            "detail_vs_big_picture": 0.0  # -1 = detail, +1 = big picture
        }
        
        for insight in insights:
            value = insight.insight_value
            confidence = insight.confidence_score or 0.5
            
            # Extract patterns based on insight value structure
            if "analytical" in str(value).lower():
                patterns["analytical_thinking"] += confidence
            if "creative" in str(value).lower():
                patterns["creative_thinking"] += confidence
                
        # Normalize scores
        count = len(insights)
        if count > 0:
            for key in patterns:
                patterns[key] = patterns[key] / count
        
        return patterns
    
    @staticmethod
    def _analyze_work_style_patterns(insights: List[PsychologicalInsight]) -> Dict[str, Any]:
        """
        Analyze work style patterns from insights.
        """
        patterns = {
            "collaboration_preference": 0.0,  # 0 = individual, 1 = collaborative
            "structure_preference": 0.0,      # 0 = flexible, 1 = structured
            "autonomy_preference": 0.0,       # 0 = guided, 1 = autonomous
            "pace_preference": 0.0            # 0 = steady, 1 = fast-paced
        }
        
        for insight in insights:
            value = insight.insight_value
            confidence = insight.confidence_score or 0.5
            
            # Extract work style indicators
            if "collaboration" in str(value).lower() or "team" in str(value).lower():
                patterns["collaboration_preference"] += confidence
            if "independent" in str(value).lower() or "solo" in str(value).lower():
                patterns["collaboration_preference"] -= confidence
                
        # Normalize and adjust scores
        count = len(insights) if insights else 1
        for key in patterns:
            patterns[key] = max(0, min(1, (patterns[key] / count + 1) / 2))
        
        return patterns
    
    @staticmethod
    def _analyze_subject_patterns(insights: List[PsychologicalInsight]) -> Dict[str, Any]:
        """
        Analyze subject affinity patterns from insights.
        """
        affinities = {
            "authentic_interests": [],
            "forced_choices": [],
            "engagement_patterns": {},
            "difficulty_tolerance": 0.0
        }
        
        for insight in insights:
            value = insight.insight_value
            confidence = insight.confidence_score or 0.5
            
            # Extract authentic interests vs forced choices
            if isinstance(value, dict):
                if value.get("authentic", False):
                    affinities["authentic_interests"].append({
                        "subject": value.get("subject"),
                        "reason": value.get("reason"),
                        "confidence": confidence
                    })
                elif value.get("forced", False):
                    affinities["forced_choices"].append({
                        "subject": value.get("subject"),
                        "reason": value.get("reason"),
                        "confidence": confidence
                    })
        
        return affinities
    
    @staticmethod
    def _analyze_career_signals(signals: List[CareerSignal]) -> Dict[str, Any]:
        """
        Analyze career readiness from signals.
        """
        readiness = {
            "strongest_signals": [],
            "developing_areas": [],
            "overall_readiness": 0.0,
            "esco_alignment": {}
        }
        
        # Group signals by type and calculate averages
        signal_groups = {}
        for signal in signals:
            signal_type = signal.signal_type
            if signal_type not in signal_groups:
                signal_groups[signal_type] = []
            signal_groups[signal_type].append(signal.strength_score)
        
        # Calculate average strength for each signal type
        signal_averages = {}
        for signal_type, scores in signal_groups.items():
            signal_averages[signal_type] = sum(scores) / len(scores)
        
        # Sort by strength
        sorted_signals = sorted(signal_averages.items(), key=lambda x: x[1], reverse=True)
        
        # Identify strongest and developing areas
        if sorted_signals:
            top_half = len(sorted_signals) // 2
            readiness["strongest_signals"] = [
                {"type": sig_type, "strength": strength}
                for sig_type, strength in sorted_signals[:max(1, top_half)]
                if strength >= 0.6
            ]
            
            readiness["developing_areas"] = [
                {"type": sig_type, "strength": strength}
                for sig_type, strength in sorted_signals[top_half:]
                if strength < 0.6
            ]
            
            # Overall readiness score
            readiness["overall_readiness"] = sum(signal_averages.values()) / len(signal_averages)
        
        return readiness
    
    @staticmethod
    async def analyze_signal_patterns(signals: List[CareerSignal]) -> Dict[str, Any]:
        """
        Analyze patterns across career signals for trend identification.
        """
        if not signals:
            return {"patterns": [], "trends": [], "consistency": 0.0}
        
        patterns = {
            "signal_distribution": {},
            "strength_trends": {},
            "cross_course_patterns": [],
            "consistency_score": 0.0
        }
        
        # Analyze signal distribution
        for signal in signals:
            signal_type = signal.signal_type
            patterns["signal_distribution"][signal_type] = \
                patterns["signal_distribution"].get(signal_type, 0) + 1
        
        # Analyze strength trends over time
        signals_by_type = {}
        for signal in signals:
            if signal.signal_type not in signals_by_type:
                signals_by_type[signal.signal_type] = []
            signals_by_type[signal.signal_type].append({
                "strength": signal.strength_score,
                "date": signal.created_at,
                "course_id": signal.course_id
            })
        
        # Calculate trends for each signal type
        for signal_type, signal_data in signals_by_type.items():
            if len(signal_data) >= 3:
                # Sort by date
                sorted_data = sorted(signal_data, key=lambda x: x["date"])
                
                # Calculate trend (simple linear regression approximation)
                x_values = list(range(len(sorted_data)))
                y_values = [d["strength"] for d in sorted_data]
                
                if len(x_values) > 1:
                    # Simple trend calculation
                    n = len(x_values)
                    sum_x = sum(x_values)
                    sum_y = sum(y_values)
                    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
                    sum_x2 = sum(x * x for x in x_values)
                    
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    patterns["strength_trends"][signal_type] = {
                        "trend": "increasing" if slope > 0.1 else "decreasing" if slope < -0.1 else "stable",
                        "slope": slope,
                        "data_points": len(sorted_data)
                    }
        
        return patterns
    
    @staticmethod
    async def identify_trends(signals: List[CareerSignal]) -> Dict[str, Any]:
        """
        Identify career development trends from signal history.
        """
        trends = {
            "emerging_strengths": [],
            "declining_areas": [],
            "stable_competencies": [],
            "recommendation_priority": []
        }
        
        # This would typically involve more sophisticated trend analysis
        # For now, we'll provide a simplified version
        
        signal_groups = {}
        for signal in signals:
            if signal.signal_type not in signal_groups:
                signal_groups[signal.signal_type] = []
            signal_groups[signal.signal_type].append(signal)
        
        for signal_type, signal_list in signal_groups.items():
            if len(signal_list) >= 2:
                # Sort by creation date
                sorted_signals = sorted(signal_list, key=lambda x: x.created_at)
                recent_strength = sorted_signals[-1].strength_score
                earlier_strength = sorted_signals[0].strength_score
                
                change = recent_strength - earlier_strength
                
                if change > 0.2:
                    trends["emerging_strengths"].append({
                        "signal_type": signal_type,
                        "improvement": change,
                        "current_strength": recent_strength
                    })
                elif change < -0.2:
                    trends["declining_areas"].append({
                        "signal_type": signal_type,
                        "decline": abs(change),
                        "current_strength": recent_strength
                    })
                else:
                    trends["stable_competencies"].append({
                        "signal_type": signal_type,
                        "stability": 1 - abs(change),
                        "current_strength": recent_strength
                    })
        
        return trends
    
    @staticmethod
    async def generate_recommendations(
        signals: List[CareerSignal],
        pattern_analysis: Dict[str, Any],
        esco_paths: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations based on analysis.
        """
        recommendations = []
        
        # Skill development recommendations based on signal patterns
        if pattern_analysis.get("strength_trends"):
            for signal_type, trend_data in pattern_analysis["strength_trends"].items():
                if trend_data["trend"] == "declining":
                    recommendations.append({
                        "type": "skill_development",
                        "priority": "high",
                        "title": f"Strengthen {signal_type.replace('_', ' ').title()}",
                        "description": f"Recent data shows a decline in {signal_type}. Consider focused practice or courses.",
                        "action_items": [
                            f"Identify specific areas within {signal_type} that need improvement",
                            "Seek mentorship or additional training",
                            "Practice through relevant projects or coursework"
                        ]
                    })
                elif trend_data["trend"] == "increasing":
                    recommendations.append({
                        "type": "leverage_strength",
                        "priority": "medium",
                        "title": f"Leverage Growing {signal_type.replace('_', ' ').title()}",
                        "description": f"Your {signal_type} is improving. Consider roles that utilize this strength.",
                        "action_items": [
                            f"Explore career paths that emphasize {signal_type}",
                            "Seek leadership opportunities in this area",
                            "Consider specialization or advanced study"
                        ]
                    })
        
        # ESCO-based career recommendations
        for esco_path in esco_paths[:3]:  # Top 3 paths
            recommendations.append({
                "type": "career_exploration",
                "priority": "medium",
                "title": f"Explore {esco_path.get('occupation_title', 'Career Path')}",
                "description": f"Based on your profile, this career path shows strong alignment.",
                "action_items": [
                    "Research job market and requirements",
                    "Connect with professionals in this field",
                    "Identify skill gaps and development opportunities"
                ],
                "esco_data": esco_path
            })
        
        return recommendations