"""
Pydantic schemas for Orientator AI feature
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class MessageComponentType(str, Enum):
    """Types of message components"""
    TEXT = "text"
    SKILL_TREE = "skill_tree"
    CAREER_PATH = "career_path"
    JOB_CARD = "job_card"
    PEER_CARD = "peer_card"
    TEST_RESULT = "test_result"
    CHALLENGE_CARD = "challenge_card"
    SAVE_CONFIRMATION = "save_confirmation"


class ComponentActionType(str, Enum):
    """Types of component actions"""
    SAVE = "save"
    EXPAND = "expand"
    EXPLORE = "explore"
    SHARE = "share"
    START = "start"


class ComponentAction(BaseModel):
    """Action available on a message component"""
    type: ComponentActionType
    label: str = Field(..., min_length=1, max_length=50)
    endpoint: Optional[str] = Field(None, pattern="^/api/.*")
    params: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "type": "save",
                "label": "Save to My Space",
                "endpoint": "/api/orientator/save-component",
                "params": {"component_id": "comp_123"}
            }
        }


class MessageComponent(BaseModel):
    """Rich component within a message"""
    id: str = Field(..., min_length=1, max_length=100)
    type: MessageComponentType
    data: Dict[str, Any]
    actions: List[ComponentAction] = Field(default_factory=list, max_items=10)
    saved: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('data')
    def validate_data(cls, v, values):
        """Validate data based on component type"""
        if 'type' in values:
            component_type = values['type']
            
            # Add type-specific validations
            if component_type == MessageComponentType.SKILL_TREE and 'skills' not in v:
                raise ValueError("skill_tree component must contain 'skills' field")
            elif component_type == MessageComponentType.CAREER_PATH and 'path' not in v:
                raise ValueError("career_path component must contain 'path' field")
            elif component_type == MessageComponentType.JOB_CARD and 'job_title' not in v:
                raise ValueError("job_card component must contain 'job_title' field")
                
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "comp_123",
                "type": "skill_tree",
                "data": {
                    "skills": [
                        {"name": "Python", "level": "advanced", "importance": "high"},
                        {"name": "Machine Learning", "level": "intermediate", "importance": "high"}
                    ],
                    "role": "Data Scientist"
                },
                "actions": [
                    {
                        "type": "save",
                        "label": "Save Skills",
                        "endpoint": "/api/orientator/save-component"
                    }
                ],
                "saved": False,
                "metadata": {
                    "tool_source": "esco_skills",
                    "generated_at": "2024-01-20T10:30:00Z"
                }
            }
        }


class OrientatorResponse(BaseModel):
    """Response from Orientator AI"""
    content: str = Field(..., min_length=1, max_length=5000)
    components: List[MessageComponent] = Field(default_factory=list, max_items=20)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "content": "I'll help you explore the path to becoming a data scientist. Let me analyze the typical journey and required skills.",
                "components": [
                    {
                        "id": "comp_123",
                        "type": "career_path",
                        "data": {
                            "milestones": [
                                {"title": "Learn Programming", "duration": "3-6 months"},
                                {"title": "Master Statistics", "duration": "2-3 months"}
                            ]
                        },
                        "actions": [{"type": "save", "label": "Save Path"}]
                    }
                ],
                "metadata": {
                    "tools_invoked": ["career_tree", "esco_skills"],
                    "intent": "career_exploration",
                    "confidence": 0.95
                }
            }
        }


class OrientatorMessageRequest(BaseModel):
    """Request to send message to Orientator"""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: int = Field(..., gt=0)
    
    class Config:
        schema_extra = {
            "example": {
                "message": "I want to become a data scientist",
                "conversation_id": 123
            }
        }


class OrientatorMessageResponse(BaseModel):
    """Response containing Orientator message"""
    message_id: int
    role: str = Field(default="assistant", pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)
    components: List[MessageComponent] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "message_id": 456,
                "role": "assistant",
                "content": "I'll help you explore data science careers...",
                "components": [],
                "metadata": {"tools_invoked": ["career_tree"]},
                "created_at": "2024-01-20T10:30:00Z"
            }
        }


class SaveComponentRequest(BaseModel):
    """Request to save a component"""
    component_id: str = Field(..., min_length=1, max_length=100)
    component_type: MessageComponentType
    component_data: Dict[str, Any]
    source_tool: str = Field(..., min_length=1, max_length=50)
    conversation_id: int = Field(..., gt=0)
    note: Optional[str] = Field(None, max_length=500)
    
    class Config:
        schema_extra = {
            "example": {
                "component_id": "comp_123",
                "component_type": "skill_tree",
                "component_data": {"skills": ["Python", "ML", "Statistics"]},
                "source_tool": "esco_skills",
                "conversation_id": 123,
                "note": "Key skills for my target role"
            }
        }


class SaveComponentResponse(BaseModel):
    """Response after saving component"""
    success: bool
    saved_item_id: int
    message: str = Field(default="Component saved successfully", max_length=200)
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "saved_item_id": 789,
                "message": "Component saved successfully to My Space"
            }
        }


class UserJourneyResponse(BaseModel):
    """Aggregated user journey data"""
    user_id: int
    journey_stages: List[Dict[str, Any]] = Field(default_factory=list)
    saved_items_count: int = Field(ge=0)
    tools_used: List[str] = Field(default_factory=list)
    career_goals: List[str] = Field(default_factory=list)
    skill_progression: Dict[str, Any] = Field(default_factory=dict)
    personality_insights: Optional[Dict[str, Any]] = None
    peer_connections: List[Dict[str, Any]] = Field(default_factory=list)
    challenges_completed: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 123,
                "journey_stages": [
                    {
                        "type": "career_exploration",
                        "data": {"career": "Data Scientist"},
                        "achieved_at": "2024-01-15T10:00:00Z"
                    }
                ],
                "saved_items_count": 15,
                "tools_used": ["esco_skills", "career_tree", "peer_matching"],
                "career_goals": ["Data Scientist", "ML Engineer"],
                "skill_progression": {
                    "Python": {"level": "advanced", "saved_at": "2024-01-10T10:00:00Z"}
                },
                "personality_insights": {
                    "hexaco_scores": {"openness": 0.8, "conscientiousness": 0.75}
                },
                "peer_connections": [
                    {"peer_id": 456, "name": "John Doe", "match_score": 0.85}
                ],
                "challenges_completed": [
                    {"challenge_id": 789, "title": "Python Basics", "xp_earned": 100}
                ]
            }
        }


class ToolInvocationResult(BaseModel):
    """Result from tool invocation tracking"""
    tool_name: str = Field(..., min_length=1, max_length=50)
    success: bool
    execution_time_ms: int = Field(ge=0)
    input_params: Dict[str, Any] = Field(default_factory=dict)
    output_summary: Optional[str] = Field(None, max_length=500)
    error: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        schema_extra = {
            "example": {
                "tool_name": "esco_skills",
                "success": True,
                "execution_time_ms": 250,
                "input_params": {"role": "Data Scientist"},
                "output_summary": "Retrieved 15 skills for Data Scientist role"
            }
        }


# Additional request/response models for specific endpoints

class FeedbackRequest(BaseModel):
    """Request to submit feedback on AI response"""
    message_id: int = Field(..., gt=0)
    feedback: str = Field(..., min_length=1, max_length=1000)
    rating: Optional[int] = Field(None, ge=1, le=5)
    
    class Config:
        schema_extra = {
            "example": {
                "message_id": 456,
                "feedback": "Very helpful response with clear next steps",
                "rating": 5
            }
        }


class ConversationSummary(BaseModel):
    """Summary of an Orientator conversation"""
    id: int
    title: str
    created_at: datetime
    last_message_at: Optional[datetime]
    message_count: int = Field(ge=0)
    tools_used: List[str] = Field(default_factory=list)
    is_favorite: bool = False
    is_archived: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "title": "Exploring Data Science Careers",
                "created_at": "2024-01-20T10:00:00Z",
                "last_message_at": "2024-01-20T11:30:00Z",
                "message_count": 15,
                "tools_used": ["career_tree", "esco_skills"],
                "is_favorite": True,
                "is_archived": False
            }
        }


class ToolAnalytics(BaseModel):
    """Analytics data for tool usage"""
    total_invocations: int = Field(ge=0)
    tool_usage: Dict[str, Dict[str, Union[int, float]]]
    success_rate: float = Field(ge=0, le=1)
    most_used_tools: List[Dict[str, Union[str, int]]] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "total_invocations": 150,
                "tool_usage": {
                    "esco_skills": {
                        "count": 45,
                        "success": 43,
                        "success_rate": 0.956,
                        "avg_execution_time": 245.5
                    }
                },
                "success_rate": 0.94,
                "most_used_tools": [
                    {"tool": "esco_skills", "count": 45},
                    {"tool": "career_tree", "count": 38}
                ]
            }
        }


# Type aliases for clarity
ComponentData = Dict[str, Any]
MetaData = Dict[str, Any]
ToolParams = Dict[str, Any]