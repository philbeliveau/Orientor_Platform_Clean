from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator

class CareerTreeNode(BaseModel):
    """Schema for nodes in the career tree structure."""
    id: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    type: Literal["root", "domain", "family", "skill"] = Field(...)
    level: int = Field(..., ge=0, le=3)
    actions: Optional[List[str]] = None
    children: Optional[List["CareerTreeNode"]] = None
    
    @model_validator(mode="after")
    def validate_node_consistency(self) -> "CareerTreeNode":
        """
        Validates that the node structure is consistent:
        - Root nodes must be at level 0
        - Domain nodes must be at level 1
        - Family nodes must be at level 2
        - Skill nodes must be at level 3
        - Only skill nodes should have actions
        """
        # Validate type and level consistency
        if self.type == "root" and self.level != 0:
            raise ValueError(f"Root node must be at level 0, not {self.level}")
        
        elif self.type == "domain" and self.level != 1:
            raise ValueError(f"Domain node must be at level 1, not {self.level}")
        
        elif self.type == "family" and self.level != 2:
            raise ValueError(f"Family node must be at level 2, not {self.level}")
        
        elif self.type == "skill" and self.level != 3:
            raise ValueError(f"Skill node must be at level 3, not {self.level}")
        
        # Validate that only skill nodes have actions
        if self.type != "skill" and self.actions:
            raise ValueError(f"Only skill nodes should have actions, not {self.type} nodes")
        
        # Validate that skill nodes must have actions
        if self.type == "skill" and (not self.actions or len(self.actions) == 0):
            raise ValueError("Skill nodes must have at least one action")
        
        # Validate that non-skill nodes have children
        if self.type != "skill" and (not self.children or len(self.children) == 0):
            raise ValueError(f"{self.type.capitalize()} nodes must have at least one child")
        
        return self 