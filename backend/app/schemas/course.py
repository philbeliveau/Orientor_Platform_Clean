from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class SubjectCategory(str, Enum):
    STEM = "STEM"
    HUMANITIES = "humanities"
    BUSINESS = "business"
    ARTS = "arts"
    SOCIAL_SCIENCES = "social_sciences"
    OTHER = "other"

class InsightType(str, Enum):
    COGNITIVE_PREFERENCE = "cognitive_preference"
    WORK_STYLE = "work_style"
    SUBJECT_AFFINITY = "subject_affinity"
    LEARNING_PREFERENCE = "learning_preference"

class SignalType(str, Enum):
    ANALYTICAL_THINKING = "analytical_thinking"
    CREATIVE_PROBLEM_SOLVING = "creative_problem_solving"
    INTERPERSONAL_SKILLS = "interpersonal_skills"
    LEADERSHIP_POTENTIAL = "leadership_potential"
    ATTENTION_TO_DETAIL = "attention_to_detail"
    STRESS_TOLERANCE = "stress_tolerance"

class QuestionIntent(str, Enum):
    EXPLORE_FRUSTRATION = "explore_frustration"
    IDENTIFY_STRENGTHS = "identify_strengths"
    CLARIFY_PREFERENCES = "clarify_preferences"
    ASSESS_ENGAGEMENT = "assess_engagement"
    DISCOVER_MOTIVATIONS = "discover_motivations"

# Course Schemas
class CourseBase(BaseModel):
    course_name: str = Field(..., min_length=1, max_length=255)
    course_code: Optional[str] = Field(None, max_length=50)
    semester: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    professor: Optional[str] = Field(None, max_length=255)
    subject_category: Optional[SubjectCategory] = None
    grade: Optional[str] = Field(None, max_length=10)
    credits: Optional[int] = Field(None, ge=0, le=20)
    description: Optional[str] = None
    learning_outcomes: Optional[List[str]] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    course_name: Optional[str] = Field(None, min_length=1, max_length=255)
    course_code: Optional[str] = Field(None, max_length=50)
    semester: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    professor: Optional[str] = Field(None, max_length=255)
    subject_category: Optional[SubjectCategory] = None
    grade: Optional[str] = Field(None, max_length=10)
    credits: Optional[int] = Field(None, ge=0, le=20)
    description: Optional[str] = None
    learning_outcomes: Optional[List[str]] = None

class Course(CourseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Psychological Insight Schemas
class PsychologicalInsightBase(BaseModel):
    insight_type: InsightType
    insight_value: Dict[str, Any]
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    evidence_source: Optional[str] = None
    esco_mapping: Optional[Dict[str, Any]] = None

class PsychologicalInsightCreate(PsychologicalInsightBase):
    course_id: int

class PsychologicalInsight(PsychologicalInsightBase):
    id: int
    user_id: int
    course_id: int
    extracted_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Career Signal Schemas
class CareerSignalBase(BaseModel):
    signal_type: SignalType
    strength_score: float = Field(..., ge=0.0, le=1.0)
    evidence_source: str
    pattern_metadata: Optional[Dict[str, Any]] = None
    esco_skill_mapping: Optional[Dict[str, Any]] = None
    trend_analysis: Optional[Dict[str, Any]] = None

class CareerSignalCreate(CareerSignalBase):
    course_id: Optional[int] = None

class CareerSignal(CareerSignalBase):
    id: int
    user_id: int
    course_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Conversation Log Schemas
class ConversationLogBase(BaseModel):
    question_intent: QuestionIntent
    question_text: str = Field(..., min_length=1)
    response: Optional[str] = None
    extracted_insights: Optional[Dict[str, Any]] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None
    career_implications: Optional[Dict[str, Any]] = None
    llm_metadata: Optional[Dict[str, Any]] = None

class ConversationLogCreate(ConversationLogBase):
    course_id: int
    session_id: Optional[str] = None

class ConversationLog(ConversationLogBase):
    id: int
    user_id: int
    course_id: int
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Career Profile Aggregate Schemas
class CareerProfileAggregateBase(BaseModel):
    aggregate_type: str = Field(..., pattern="^(semester|yearly|overall)$")
    time_period: Optional[str] = None
    cognitive_preferences: Optional[Dict[str, Any]] = None
    work_style_preferences: Optional[Dict[str, Any]] = None
    subject_affinities: Optional[Dict[str, Any]] = None
    career_readiness_signals: Optional[Dict[str, Any]] = None
    esco_path_suggestions: Optional[Dict[str, Any]] = None
    contradiction_flags: Optional[Dict[str, Any]] = None
    confidence_metrics: Optional[Dict[str, Any]] = None

class CareerProfileAggregate(CareerProfileAggregateBase):
    id: int
    user_id: int
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Request/Response Schemas for API endpoints
class CourseAnalysisRequest(BaseModel):
    course_id: int
    analysis_type: str = Field(..., pattern="^(strengths|frustrations|preferences|engagement|career_implications)$")
    context: Optional[Dict[str, Any]] = None

class CourseAnalysisResponse(BaseModel):
    conversation_id: int
    session_id: str
    questions: List[Dict[str, str]]
    initial_insights: Optional[List[Dict[str, Any]]] = None

class PsychologicalProfileResponse(BaseModel):
    user_id: int
    profile_summary: Dict[str, Any]
    insights_by_course: Dict[int, List[PsychologicalInsight]]
    career_signals: List[CareerSignal]
    esco_recommendations: Dict[str, Any]
    confidence_score: float
    last_updated: datetime

class CareerSignalsResponse(BaseModel):
    user_id: int
    signals: List[CareerSignal]
    pattern_analysis: Dict[str, Any]
    esco_tree_paths: List[Dict[str, Any]]
    trend_indicators: Dict[str, Any]
    recommendations: List[Dict[str, Any]]

# Targeted Analysis Schemas
class TargetedAnalysisRequest(BaseModel):
    focus_areas: Optional[List[str]] = None
    previous_session_id: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None

class QuestionSchema(BaseModel):
    id: str
    question: str
    intent: str
    follow_up_triggers: List[str]

class TargetedAnalysisResponse(BaseModel):
    session_id: str
    conversation_started: bool
    next_questions: List[QuestionSchema]
    context_insights: Optional[List[Dict[str, Any]]] = None

class ConversationResponseRequest(BaseModel):
    question_id: str
    response: str

class ConversationAnalysisResponse(BaseModel):
    next_questions: List[QuestionSchema]
    insights_discovered: List[Dict[str, Any]]
    session_complete: bool
    career_recommendations: List[Dict[str, Any]]