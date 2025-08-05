from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_name = Column(String(255), nullable=False)
    course_code = Column(String(50), nullable=True)
    semester = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    professor = Column(String(255), nullable=True)
    subject_category = Column(String(50), nullable=True)  # STEM/humanities/business/arts
    grade = Column(String(10), nullable=True)
    credits = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    learning_outcomes = Column(JSON, nullable=True)  # Store as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="courses")
    psychological_insights = relationship("PsychologicalInsight", back_populates="course", cascade="all, delete-orphan")
    career_signals = relationship("CareerSignal", back_populates="course")
    conversation_logs = relationship("ConversationLog", back_populates="course", cascade="all, delete-orphan")

class PsychologicalInsight(Base):
    __tablename__ = "psychological_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    insight_type = Column(String(100), nullable=False)  # cognitive_preference/work_style/subject_affinity
    insight_value = Column(JSON, nullable=False)  # Store complex insight data as JSON
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    evidence_source = Column(Text, nullable=True)  # What led to this insight
    esco_mapping = Column(JSON, nullable=True)  # Links to ESCO categories
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="psychological_insights")
    course = relationship("Course", back_populates="psychological_insights")

class CareerSignal(Base):
    __tablename__ = "career_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, index=True)  # Can be null for cross-course signals
    signal_type = Column(String(100), nullable=False)  # analytical_thinking/creative_problem_solving/interpersonal_skills
    strength_score = Column(Float, nullable=False)  # 0.0 to 1.0
    evidence_source = Column(Text, nullable=False)  # course_id + specific_interaction
    pattern_metadata = Column(JSON, nullable=True)  # Store patterns across courses/semesters
    esco_skill_mapping = Column(JSON, nullable=True)  # Link to ESCO skill categories
    trend_analysis = Column(JSON, nullable=True)  # Track evolution over time
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="career_signals")
    course = relationship("Course", back_populates="career_signals")

class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)  # Group related conversations
    question_intent = Column(String(100), nullable=False)  # explore_frustration/identify_strengths/clarify_preferences
    question_text = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    extracted_insights = Column(JSON, nullable=True)  # Insights extracted from this conversation
    sentiment_analysis = Column(JSON, nullable=True)  # Emotional indicators
    career_implications = Column(JSON, nullable=True)  # Direct career guidance insights
    llm_metadata = Column(JSON, nullable=True)  # Model version, tokens used, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversation_logs")
    course = relationship("Course", back_populates="conversation_logs")

class CareerProfileAggregate(Base):
    __tablename__ = "career_profile_aggregates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    aggregate_type = Column(String(50), nullable=False)  # semester/yearly/overall
    time_period = Column(String(50), nullable=True)  # "2024-fall", "2024", etc.
    cognitive_preferences = Column(JSON, nullable=True)  # Aggregated cognitive style insights
    work_style_preferences = Column(JSON, nullable=True)  # Collaboration vs individual work
    subject_affinities = Column(JSON, nullable=True)  # Authentic interests vs forced choices
    career_readiness_signals = Column(JSON, nullable=True)  # Combined career signals
    esco_path_suggestions = Column(JSON, nullable=True)  # Personalized ESCO tree starting points
    contradiction_flags = Column(JSON, nullable=True)  # Self-perception vs performance mismatches
    confidence_metrics = Column(JSON, nullable=True)  # Overall confidence in profile accuracy
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="career_profile_aggregates")