from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SavedJobBase(BaseModel):
    esco_id: str
    job_title: str
    skills_required: List[str] = []
    discovery_source: str = "tree"
    tree_graph_id: Optional[str] = None
    relevance_score: Optional[float] = None
    metadata: Dict[str, Any] = {}

class SavedJobCreate(SavedJobBase):
    pass

class SavedJob(SavedJobBase):
    id: int
    user_id: int
    saved_at: datetime
    
    class Config:
        from_attributes = True

class SavedJobResponse(SavedJob):
    already_saved: bool = False