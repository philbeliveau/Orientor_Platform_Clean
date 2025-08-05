"""
Tool Registry for Orientator AI - Manages and invokes platform tools
"""

import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session
from app.services.esco_integration_service import ESCOIntegrationService
from app.services.career_progression_service import CareerProgressionService
import app.services.Oasisembedding_service as oasis_service
import app.services.peer_matching_service as peer_service
from app.services.hexaco_service import HexacoService
from app.services.LLMholland_service import LLMService as LLMHollandService

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any], user_id: int, db: Session) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get information about the tool"""
        pass


class ESCOSkillsTool(BaseTool):
    """Tool for ESCO skills analysis and exploration"""
    
    def __init__(self):
        self.esco_service = ESCOIntegrationService()
    
    async def execute(self, params: Dict[str, Any], user_id: int, db: Session) -> ToolResult:
        """
        Execute ESCO skills analysis.
        
        Args:
            params: Parameters including 'role' or 'skills'
            user_id: User ID
            db: Database session
            
        Returns:
            ToolResult with skills data
        """
        try:
            if "role" in params:
                # Mock result for skills required for a role
                # In production, this would integrate with actual ESCO service
                result = {
                    "role": params["role"],
                    "skills": [
                        {
                            "uri": "http://data.europa.eu/esco/skill/1",
                            "name": "Python programming",
                            "skill_type": "skill/competence",
                            "reuse_level": "cross-sectoral",
                            "proficiency_level": "advanced"
                        },
                        {
                            "uri": "http://data.europa.eu/esco/skill/2", 
                            "name": "Machine learning",
                            "skill_type": "skill/competence",
                            "reuse_level": "occupation-specific",
                            "proficiency_level": "advanced"
                        }
                    ],
                    "skill_hierarchy": {
                        "technical": ["Python programming", "Machine learning"],
                        "analytical": [],
                        "soft": []
                    }
                }
                return ToolResult(
                    success=True,
                    data=result,
                    metadata={"source": "esco", "operation": "role_skills"}
                )
            elif "skills" in params:
                # Mock result for skill analysis
                result = {
                    "analyzed_skills": [
                        {
                            "input_skill": skill,
                            "matched_skill": {
                                "name": skill.title(),
                                "uri": f"http://data.europa.eu/esco/skill/{i}",
                                "broader_skills": ["Programming languages"],
                                "narrower_skills": []
                            }
                        }
                        for i, skill in enumerate(params["skills"])
                    ]
                }
                return ToolResult(
                    success=True,
                    data=result,
                    metadata={"source": "esco", "operation": "skill_analysis"}
                )
            else:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: 'role' or 'skills'"
                )
        except Exception as e:
            logger.error(f"ESCO tool error: {str(e)}")
            return ToolResult(success=False, error=str(e))
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "esco_skills",
            "description": "Analyze skills and competencies using ESCO framework",
            "category": "skills",
            "required_params": ["role OR skills"],
            "optional_params": ["level", "include_hierarchy"]
        }


class CareerTreeTool(BaseTool):
    """Tool for career progression path generation"""
    
    def __init__(self):
        self.career_service = CareerProgressionService()
    
    async def execute(self, params: Dict[str, Any], user_id: int, db: Session) -> ToolResult:
        """
        Generate career progression path.
        
        Args:
            params: Parameters including 'career_goal'
            user_id: User ID
            db: Database session
            
        Returns:
            ToolResult with career path data
        """
        try:
            career_goal = params.get("career_goal")
            if not career_goal:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: 'career_goal'"
                )
            
            # Get user profile for personalized path
            from app.models.user import User
            user = db.query(User).filter(User.id == user_id).first()
            
            # Mock result for career path
            # In production, this would use actual career service
            result = {
                "career_goal": career_goal,
                "current_position": "Entry Level",
                "path": [
                    {
                        "step": 1,
                        "position": "Junior Developer",
                        "duration": "Current",
                        "skills_needed": ["Python", "SQL"],
                        "description": "Build foundation in programming"
                    },
                    {
                        "step": 2,
                        "position": "Data Analyst",
                        "duration": "1-2 years",
                        "skills_needed": ["Statistics", "Data Visualization"],
                        "description": "Transition to data-focused role"
                    },
                    {
                        "step": 3,
                        "position": career_goal,
                        "duration": "2-3 years",
                        "skills_needed": ["Machine Learning", "Deep Learning"],
                        "description": "Achieve target role"
                    }
                ],
                "total_duration": "3-5 years",
                "key_transitions": [
                    "Developer to Analyst: Focus on data skills",
                    "Analyst to Target: Add specialized expertise"
                ]
            }
            
            return ToolResult(
                success=True,
                data=result,
                metadata={"tool": "career_tree", "personalized": bool(user)}
            )
        except Exception as e:
            logger.error(f"Career tree tool error: {str(e)}")
            return ToolResult(success=False, error=str(e))
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "career_tree",
            "description": "Generate personalized career progression paths",
            "category": "career",
            "required_params": ["career_goal"],
            "optional_params": ["current_position", "timeline"]
        }


class OASISExplorerTool(BaseTool):
    """Tool for job exploration using OASIS embeddings"""
    
    def __init__(self):
        # OASIS service is a module, not a class
        pass
    
    async def execute(self, params: Dict[str, Any], user_id: int, db: Session) -> ToolResult:
        """
        Search for similar jobs and careers.
        
        Args:
            params: Parameters including 'query'
            user_id: User ID
            db: Database session
            
        Returns:
            ToolResult with job matches
        """
        try:
            query = params.get("query")
            if not query:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: 'query'"
                )
            
            limit = params.get("limit", 10)
            min_score = params.get("min_match_score", 0.7)
            
            # For now, return a mock result since OASIS service doesn't have search functionality
            # In production, this would integrate with actual OASIS search
            result = {
                "query": query,
                "results": [
                    {
                        "occupation_code": "2152",
                        "occupation_title": "Data Scientists",
                        "description": "Analyze complex data to help companies make decisions",
                        "match_score": 0.95,
                        "required_skills": ["Statistics", "Machine Learning", "Python"]
                    }
                ],
                "filters_applied": {
                    "min_match_score": min_score,
                    "limit": limit
                }
            }
            
            return ToolResult(
                success=True,
                data=result,
                metadata={"tool": "oasis_explorer", "query": query}
            )
        except Exception as e:
            logger.error(f"OASIS explorer tool error: {str(e)}")
            return ToolResult(success=False, error=str(e))
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "oasis_explorer",
            "description": "Explore similar jobs and career opportunities",
            "category": "exploration",
            "required_params": ["query"],
            "optional_params": ["limit", "min_match_score"]
        }


class PeerMatchingTool(BaseTool):
    """Tool for finding compatible peers"""
    
    def __init__(self):
        # Peer service is a module, not a class
        pass
    
    async def execute(self, params: Dict[str, Any], user_id: int, db: Session) -> ToolResult:
        """
        Find compatible peers based on profile.
        
        Args:
            params: Parameters for peer matching
            user_id: User ID
            db: Database session
            
        Returns:
            ToolResult with matched peers
        """
        try:
            limit = params.get("limit", 5)
            min_score = params.get("min_match_score", 0.7)
            focus_area = params.get("focus_area")
            
            # Use the module function
            result = await peer_service.find_compatible_peers(
                user_id=user_id,
                db=db,
                limit=limit,
                min_score=min_score,
                focus_area=focus_area
            )
            
            return ToolResult(
                success=True,
                data=result,
                metadata={"tool": "peer_matching", "matches_found": len(result.get("matched_peers", []))}
            )
        except Exception as e:
            logger.error(f"Peer matching tool error: {str(e)}")
            return ToolResult(success=False, error=str(e))
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "peer_matching",
            "description": "Find compatible peers for networking and collaboration",
            "category": "social",
            "required_params": [],
            "optional_params": ["limit", "min_match_score", "focus_area"]
        }


class HEXACOTestTool(BaseTool):
    """Tool for HEXACO personality assessment"""
    
    def __init__(self):
        self.hexaco_service = HexacoService()
    
    async def execute(self, params: Dict[str, Any], user_id: int, db: Session) -> ToolResult:
        """
        Handle HEXACO test operations.
        
        Args:
            params: Parameters including 'action'
            user_id: User ID
            db: Database session
            
        Returns:
            ToolResult with test data
        """
        try:
            action = params.get("action", "start")
            
            if action == "start":
                # Mock initiate test result
                result = {
                    "test_id": f"hexaco_{user_id}_{datetime.now().timestamp()}",
                    "test_type": "HEXACO-60",
                    "questions": [
                        {
                            "id": 1,
                            "text": "I would be quite bored by a visit to an art gallery",
                            "dimension": "Openness",
                            "reversed": True
                        }
                    ],
                    "total_questions": 60,
                    "estimated_time": "10-15 minutes"
                }
                return ToolResult(
                    success=True,
                    data=result,
                    metadata={"tool": "hexaco_test", "action": "initiated"}
                )
            elif action == "submit":
                test_id = params.get("test_id")
                answers = params.get("answers", {})
                # Mock process results
                result = {
                    "test_id": test_id,
                    "scores": {
                        "Honesty-Humility": 3.8,
                        "Emotionality": 3.2,
                        "Extraversion": 4.1,
                        "Agreeableness": 3.5,
                        "Conscientiousness": 4.3,
                        "Openness": 4.5
                    },
                    "career_implications": {
                        "strengths": ["analytical thinking", "innovation", "leadership"],
                        "suitable_environments": ["research", "startups", "tech companies"],
                        "recommended_roles": ["Data Scientist", "Product Manager", "Research Analyst"]
                    },
                    "detailed_analysis": "High openness and conscientiousness suggest..."
                }
                return ToolResult(
                    success=True,
                    data=result,
                    metadata={"tool": "hexaco_test", "action": "completed"}
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown action: {action}"
                )
        except Exception as e:
            logger.error(f"HEXACO test tool error: {str(e)}")
            return ToolResult(success=False, error=str(e))
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "hexaco_test",
            "description": "HEXACO personality assessment for career insights",
            "category": "assessment",
            "required_params": ["action"],
            "optional_params": ["test_id", "answers"]
        }


class HollandTestTool(BaseTool):
    """Tool for Holland/RIASEC career interest assessment"""
    
    def __init__(self):
        self.holland_service = LLMHollandService()
    
    async def execute(self, params: Dict[str, Any], user_id: int, db: Session) -> ToolResult:
        """
        Process Holland interest assessment.
        
        Args:
            params: Parameters including interests
            user_id: User ID
            db: Database session
            
        Returns:
            ToolResult with Holland code and matches
        """
        try:
            interests = params.get("interests", [])
            if not interests:
                # Mock initiate test
                result = {
                    "test_id": f"holland_{user_id}_{datetime.now().timestamp()}",
                    "instructions": "Please indicate your interests in various activities",
                    "categories": ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"],
                    "sample_questions": [
                        "Working with tools and machinery",
                        "Solving complex problems",
                        "Creating art or music"
                    ]
                }
                return ToolResult(
                    success=True,
                    data=result,
                    metadata={"tool": "holland_test", "action": "initiated"}
                )
            else:
                # Mock process interests
                result = {
                    "holland_code": "IAS",
                    "scores": {
                        "Realistic": 2.1,
                        "Investigative": 4.5,
                        "Artistic": 3.8,
                        "Social": 3.2,
                        "Enterprising": 2.8,
                        "Conventional": 2.3
                    },
                    "primary_type": "Investigative",
                    "secondary_type": "Artistic",
                    "tertiary_type": "Social",
                    "career_matches": [
                        {
                            "occupation": "Data Scientist",
                            "match_score": 0.92,
                            "description": "Perfect blend of investigation and creativity"
                        },
                        {
                            "occupation": "UX Researcher",
                            "match_score": 0.85,
                            "description": "Combines research with design thinking"
                        }
                    ]
                }
                return ToolResult(
                    success=True,
                    data=result,
                    metadata={"tool": "holland_test", "action": "completed"}
                )
        except Exception as e:
            logger.error(f"Holland test tool error: {str(e)}")
            return ToolResult(success=False, error=str(e))
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "holland_test",
            "description": "Holland/RIASEC career interest assessment",
            "category": "assessment",
            "required_params": [],
            "optional_params": ["interests"]
        }


class XPChallengesTool(BaseTool):
    """Tool for skill development challenges"""
    
    def __init__(self):
        # Would initialize challenges service here
        pass
    
    async def execute(self, params: Dict[str, Any], user_id: int, db: Session) -> ToolResult:
        """
        Get challenges for skill development.
        
        Args:
            params: Parameters including 'skill' or 'career_goal'
            user_id: User ID
            db: Database session
            
        Returns:
            ToolResult with challenges
        """
        try:
            if "skill" in params:
                # Get challenges for specific skill
                # In production, would call challenges service
                result = {
                    "skill": params["skill"],
                    "user_level": "intermediate",
                    "challenges": [
                        {
                            "id": "ch_001",
                            "title": f"Master {params['skill']} Fundamentals",
                            "description": f"Complete exercises to strengthen your {params['skill']} skills",
                            "difficulty": "intermediate",
                            "xp_reward": 150,
                            "estimated_time": "2-3 hours"
                        }
                    ],
                    "progression_path": {
                        "current_level": "intermediate",
                        "next_level": "advanced",
                        "xp_to_next_level": 500
                    }
                }
            elif "career_goal" in params:
                # Get challenges for career goal
                result = {
                    "career_goal": params["career_goal"],
                    "challenge_tracks": [
                        {
                            "track_name": "Foundation Track",
                            "challenges": [{"id": "track_001", "title": "Build Core Skills"}]
                        }
                    ],
                    "total_xp_available": 1500
                }
            else:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: 'skill' or 'career_goal'"
                )
            
            return ToolResult(
                success=True,
                data=result,
                metadata={"tool": "xp_challenges"}
            )
        except Exception as e:
            logger.error(f"XP challenges tool error: {str(e)}")
            return ToolResult(success=False, error=str(e))
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "xp_challenges",
            "description": "Get skill development challenges with XP rewards",
            "category": "development",
            "required_params": ["skill OR career_goal"],
            "optional_params": ["difficulty", "time_commitment"]
        }


class ToolRegistry:
    """Registry for managing and invoking tools"""
    
    def __init__(self):
        """Initialize tool registry with default tools"""
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools"""
        self.register("esco_skills", ESCOSkillsTool())
        self.register("career_tree", CareerTreeTool())
        self.register("oasis_explorer", OASISExplorerTool())
        self.register("peer_matching", PeerMatchingTool())
        self.register("hexaco_test", HEXACOTestTool())
        self.register("holland_test", HollandTestTool())
        self.register("xp_challenges", XPChallengesTool())
    
    def register(self, name: str, tool: BaseTool):
        """
        Register a new tool.
        
        Args:
            name: Tool name
            tool: Tool instance
            
        Raises:
            ValueError: If tool already registered
        """
        if name in self.tools:
            raise ValueError(f"Tool '{name}' already registered")
        self.tools[name] = tool
        logger.info(f"Registered tool: {name}")
    
    async def invoke(
        self, 
        tool_name: str, 
        params: Dict[str, Any],
        user_id: int,
        db: Session
    ) -> ToolResult:
        """
        Invoke a tool by name.
        
        Args:
            tool_name: Name of the tool
            params: Parameters for the tool
            user_id: User ID
            db: Database session
            
        Returns:
            ToolResult from tool execution
            
        Raises:
            ValueError: If tool not found
        """
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool = self.tools[tool_name]
        
        try:
            logger.info(f"Invoking tool: {tool_name} with params: {params}")
            result = await tool.execute(params, user_id, db)
            logger.info(f"Tool {tool_name} completed: success={result.success}")
            return result
        except Exception as e:
            logger.error(f"Error invoking tool {tool_name}: {str(e)}")
            return ToolResult(success=False, error=str(e))
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools with their info.
        
        Returns:
            List of tool information dictionaries
        """
        return [tool.get_info() for tool in self.tools.values()]
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool information dictionary
            
        Raises:
            ValueError: If tool not found
        """
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return self.tools[tool_name].get_info()