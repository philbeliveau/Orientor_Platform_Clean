"""
Enhanced Chat Schemas

Pydantic schemas for GraphSage-enhanced chat functionality.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class SkillRelevanceInfo(BaseModel):
    """Schema for skill relevance information."""
    name: str = Field(..., description="Skill name")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="GraphSage relevance score (0-1)")
    description: str = Field("", description="Skill description")

class ConversationContext(BaseModel):
    """Schema for conversation context from GraphSage analysis."""
    user_strengths: List[str] = Field(default_factory=list, description="User's current strengths")
    career_keywords_detected: List[str] = Field(default_factory=list, description="Career keywords detected in conversation")
    top_skill_matches: List[str] = Field(default_factory=list, description="Top skill matches for current context")

class GraphSageInsights(BaseModel):
    """Schema for GraphSage insights in conversations."""
    relevant_skills: List[SkillRelevanceInfo] = Field(default_factory=list, description="Skills relevant to current conversation")
    skill_gaps: List[SkillRelevanceInfo] = Field(default_factory=list, description="Identified skill gaps")
    conversation_context: ConversationContext = ConversationContext()
    learning_suggestions: List[str] = Field(default_factory=list, description="AI-generated learning suggestions")

class EnhancedFeatures(BaseModel):
    """Schema for enhanced chat features status."""
    skill_relevance_analysis: bool = Field(True, description="Whether skill relevance analysis is enabled")
    personalized_learning_suggestions: bool = Field(True, description="Whether personalized learning suggestions are enabled")
    career_path_insights: bool = Field(True, description="Whether career path insights are enabled")

class EnhancedMessageResponse(BaseModel):
    """Schema for enhanced chat message response."""
    response: str = Field(..., description="AI assistant response")
    conversation_id: int = Field(..., description="Conversation ID")
    message_id: int = Field(..., description="Message ID")
    graphsage_insights: Dict[str, Any] = Field(default_factory=dict, description="GraphSage analysis insights")
    enhanced_features: EnhancedFeatures = EnhancedFeatures()

class SkillExplanation(BaseModel):
    """Schema for detailed skill explanation."""
    skill_id: str = Field(..., description="Skill node ID in GraphSage")
    name: str = Field(..., description="Skill name")
    description: str = Field("", description="Skill description")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score for user")
    explanation: str = Field(..., description="Personalized explanation of skill relevance")

class LearningPhase(BaseModel):
    """Schema for learning path phase."""
    phase_name: str = Field(..., description="Name of the learning phase")
    duration: str = Field(..., description="Duration of the phase")
    skills_focus: List[str] = Field(default_factory=list, description="Skills to focus on in this phase")
    learning_objectives: List[str] = Field(default_factory=list, description="Learning objectives for this phase")
    recommended_resources: List[str] = Field(default_factory=list, description="Recommended learning resources")
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics for this phase")

class LearningRecommendations(BaseModel):
    """Schema for personalized learning recommendations."""
    high_impact_skills: List[SkillExplanation] = Field(default_factory=list, description="High-impact skills (score > 0.8)")
    foundational_skills: List[SkillExplanation] = Field(default_factory=list, description="Foundational skills (score > 0.6)")
    complementary_skills: List[SkillExplanation] = Field(default_factory=list, description="Complementary skills")
    learning_path: List[LearningPhase] = Field(default_factory=list, description="Structured learning path")

class SkillAnalysis(BaseModel):
    """Schema for individual skill analysis."""
    skill_name: str = Field(..., description="Name of the skill")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="GraphSage relevance score")
    description: str = Field("", description="Skill description")
    user_proficiency: float = Field(..., ge=0.0, le=1.0, description="User's current proficiency level")

class CareerPathAnalysis(BaseModel):
    """Schema for career path compatibility analysis."""
    career_path: str = Field(..., description="Career path being analyzed")
    compatibility_score: float = Field(..., ge=0.0, le=1.0, description="Overall compatibility score")
    matching_skills: List[SkillAnalysis] = Field(default_factory=list, description="Skills that match well")
    skill_gaps: List[SkillAnalysis] = Field(default_factory=list, description="Identified skill gaps")
    recommendations: str = Field(..., description="Personalized recommendations for career preparation")

class GraphSageModelStatus(BaseModel):
    """Schema for GraphSage model status."""
    model_loaded: bool = Field(..., description="Whether the GraphSage model is loaded")
    nodes_available: int = Field(..., description="Number of nodes in the graph")
    edges_available: int = Field(..., description="Number of edges in the graph")

class UserProfileSummary(BaseModel):
    """Schema for user profile summary."""
    career_goals: Optional[str] = Field(None, description="User's career goals")
    interests: Optional[str] = Field(None, description="User's interests")
    current_skills: Dict[str, float] = Field(default_factory=dict, description="User's current skill levels")

class GraphSageInsightsResponse(BaseModel):
    """Schema for general GraphSage insights response."""
    user_profile_summary: UserProfileSummary = UserProfileSummary()
    top_relevant_skills: List[SkillRelevanceInfo] = Field(default_factory=list, description="Top relevant skills for user")
    graphsage_model_status: GraphSageModelStatus = Field(..., description="Status of GraphSage model")

class EnhancedChatStatus(BaseModel):
    """Schema for enhanced chat system status."""
    enhanced_chat_available: bool = Field(..., description="Whether enhanced chat is available")
    graphsage_model_loaded: bool = Field(..., description="Whether GraphSage model is loaded")
    node_metadata_count: int = Field(..., description="Number of nodes with metadata")
    edge_count: int = Field(..., description="Number of edges in graph")
    features: EnhancedFeatures = EnhancedFeatures()
    error: Optional[str] = Field(None, description="Error message if system is not available")

# Request schemas
class EnhancedMessageRequest(BaseModel):
    """Schema for enhanced chat message request."""
    text: str = Field(..., min_length=1, max_length=2000, description="Message text")
    conversation_id: Optional[int] = Field(None, description="Optional conversation ID")

class SkillExplanationRequest(BaseModel):
    """Schema for skill explanation request."""
    skill_name: str = Field(..., min_length=1, max_length=200, description="Name of skill to explain")

class CareerPathAnalysisRequest(BaseModel):
    """Schema for career path analysis request."""
    career_path: str = Field(..., min_length=1, max_length=200, description="Career path to analyze")

# Response wrapper schemas
class SkillExplanationResponse(BaseModel):
    """Schema for skill explanation response."""
    skill_name: str = Field(..., description="Name of the skill")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    explanation: str = Field(..., description="Detailed explanation")
    skill_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional skill metadata")
    graphsage_analysis: bool = Field(..., description="Whether GraphSage analysis was used")

class LearningRecommendationsResponse(BaseModel):
    """Schema for learning recommendations response."""
    high_impact_skills: List[Dict[str, Any]] = Field(default_factory=list, description="High-impact skills")
    foundational_skills: List[Dict[str, Any]] = Field(default_factory=list, description="Foundational skills")
    complementary_skills: List[Dict[str, Any]] = Field(default_factory=list, description="Complementary skills")
    learning_path: List[Dict[str, Any]] = Field(default_factory=list, description="Learning path phases")

class CareerPathAnalysisResponse(BaseModel):
    """Schema for career path analysis response."""
    career_path: str = Field(..., description="Career path analyzed")
    compatibility_score: float = Field(..., ge=0.0, le=1.0, description="Compatibility score")
    matching_skills: List[Dict[str, Any]] = Field(default_factory=list, description="Matching skills")
    skill_gaps: List[Dict[str, Any]] = Field(default_factory=list, description="Skill gaps")
    recommendations: str = Field(..., description="Recommendations")