"""
Pydantic schemas for School Programs API

This module contains the request/response models for the school programs functionality.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

# Handle different Pydantic versions
try:
    from pydantic import validator  # Pydantic v1
except ImportError:
    from pydantic import field_validator as validator  # Pydantic v2


class ProgramSearchQuery(BaseModel):
    """Program search query parameters"""
    text: Optional[str] = Field(None, description="Search text for program titles and descriptions")
    program_types: Optional[List[str]] = Field(default=[], description="Filter by program types")
    levels: Optional[List[str]] = Field(default=[], description="Filter by program levels")
    location: Optional[Dict[str, str]] = Field(default={}, description="Location filters")
    languages: Optional[List[str]] = Field(default=[], description="Language preferences")
    duration: Optional[Dict[str, int]] = Field(default={}, description="Duration constraints")
    budget: Optional[Dict[str, float]] = Field(default={}, description="Budget constraints")
    sort: Optional[Dict[str, str]] = Field(default={"field": "relevance", "direction": "desc"})
    pagination: Optional[Dict[str, int]] = Field(default={"page": 1, "limit": 20})
    
    @validator('pagination')
    def validate_pagination(cls, v):
        if v.get('limit', 20) > 100:
            v['limit'] = 100
        if v.get('page', 1) < 1:
            v['page'] = 1
        return v


class ProgramResponse(BaseModel):
    """Program data response model"""
    id: UUID
    title: str
    title_fr: Optional[str]
    description: Optional[str]
    description_fr: Optional[str]
    institution: Dict[str, Any]
    program_details: Dict[str, Any]
    classification: Dict[str, Any]
    admission: Dict[str, Any]
    academic_info: Dict[str, Any]
    career_outcomes: Dict[str, Any]
    costs: Dict[str, Any]
    metadata: Dict[str, Any]


class SearchResultsResponse(BaseModel):
    """Search results response model"""
    results: List[ProgramResponse]
    pagination: Dict[str, Any]
    facets: Dict[str, Any]
    metadata: Dict[str, Any]


class UserProgramInteraction(BaseModel):
    """User program interaction model"""
    program_id: UUID
    interaction_type: str = Field(..., pattern="^(viewed|saved|applied|dismissed|shared|compared)$")
    metadata: Optional[Dict[str, Any]] = Field(default={})


class SaveProgramRequest(BaseModel):
    """Save program request model"""
    program_id: UUID
    notes: Optional[str] = None
    priority_level: Optional[int] = Field(1, ge=1, le=5)
    tags: Optional[List[str]] = Field(default=[])


class ProgramComparison(BaseModel):
    """Program comparison request"""
    program_ids: List[UUID] = Field(..., min_items=2, max_items=5)