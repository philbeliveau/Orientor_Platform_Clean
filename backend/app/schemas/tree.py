from typing import List, Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

class TreeNode(BaseModel):
    id: str = Field(..., description="Unique lowercase-dash-separated ID")
    label: str = Field(..., description="Short human-readable label")
    type: Literal["root", "skill", "outcome", "career"] = Field(..., description="Node type")
    level: int = Field(..., description="Tree level (0=root, 1=skill, 2=outcome, 3=skill, 4=career)")
    actions: Optional[List[str]] = Field(None, description="List of actions (required for skill nodes)")
    children: Optional[List["TreeNode"]] = Field(None, description="List of child nodes")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "root",
                "label": "Student Profile",
                "type": "root",
                "level": 0,
                "children": [
                    {
                        "id": "skill-1",
                        "label": "Communication",
                        "type": "skill",
                        "level": 1,
                        "actions": ["Join debate club", "Practice public speaking", "Write blog posts"],
                        "children": []
                    }
                ]
            }
        }


class ProfileInput(BaseModel):
    profile: str = Field(..., description="User profile text for tree generation")


class SkillsTreeInput(BaseModel):
    profile: str = Field(..., description="Technical profile for skills tree generation")
    custom_prompt: str = Field("", description="Custom prompt for generating a technical skills tree")


class TreeResponse(BaseModel):
    tree: TreeNode = Field(..., description="Generated skill tree")


# Update forward reference for TreeNode.children
TreeNode.model_rebuild()

# TreePath schemas
class TreePathBase(BaseModel):
    tree_type: str
    tree_json: Dict[str, Any]

class TreePathCreate(TreePathBase):
    pass

class TreePath(TreePathBase):
    id: UUID 
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# NodeNote schemas
class NodeNoteBase(BaseModel):
    node_id: str
    action_index: int
    note_text: str

class NodeNoteCreate(NodeNoteBase):
    pass

class NodeNote(NodeNoteBase):
    id: int
    user_id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

# UserProgress schemas
class UserProgressBase(BaseModel):
    total_xp: int
    level: int
    last_completed_node: Optional[str] = None
    completed_actions: Optional[Dict[str, List[bool]]] = None

class UserProgressCreate(UserProgressBase):
    pass

class UserProgressUpdate(BaseModel):
    xp_gained: int
    node_id: str
    completed_actions: Optional[Dict[str, List[bool]]] = None

class UserProgress(UserProgressBase):
    id: str
    user_id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True