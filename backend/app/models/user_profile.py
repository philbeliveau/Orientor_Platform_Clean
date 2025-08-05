from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Float, ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    name = Column(String, nullable=True)
    age = Column(Integer)
    sex = Column(String(50))
    major = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    gpa = Column(Float)
    hobbies = Column(Text, nullable=True)
    country = Column(String(255))
    state_province = Column(String(255))
    unique_quality = Column(Text)
    story = Column(Text)
    favorite_movie = Column(String(255))
    favorite_book = Column(String(255))
    favorite_celebrities = Column(Text)  # Stored as comma-separated values
    learning_style = Column(String(50))  # Visual, Auditory, Reading/Writing, Kinesthetic
    interests = Column(Text, nullable=True)
    
    # Career-related fields
    job_title = Column(String)
    industry = Column(String)
    years_experience = Column(Integer)
    education_level = Column(String)
    career_goals = Column(String)
    skills = Column(ARRAY(String))
    
    # RIASEC analysis field (already exists in database)
    personal_analysis = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="profile") 