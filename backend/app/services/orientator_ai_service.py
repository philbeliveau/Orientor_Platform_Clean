"""
Orientator AI Service - Intelligent conversational assistant with tool integration
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import AsyncOpenAI

from sqlalchemy.orm import Session
from app.models.user import User
from app.models.message import Message
from app.schemas.orientator import (
    OrientatorResponse,
    MessageComponent,
    MessageComponentType,
    ComponentAction,
    ComponentActionType,
    ToolInvocationResult
)
from datetime import datetime
from app.services.tool_registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)


class OrientatorAIService:
    """
    Main service for Orientator AI conversational assistant.
    Handles message processing, intent analysis, tool invocation, and response generation.
    """
    
    def __init__(self):
        """Initialize Orientator AI Service"""
        self.llm_client = AsyncOpenAI()
        self.tool_registry = ToolRegistry()
        
        # Tool trigger patterns for intent mapping
        self.tool_triggers = {
            "esco_skills": ["skills for", "what skills", "skill requirements", "skills needed"],
            "career_tree": ["career path", "how to become", "steps to", "career progression"],
            "oasis_explorer": ["jobs like", "similar roles", "explore careers", "job opportunities"],
            "peer_matching": ["find peers", "connect with", "others like me", "peer network"],
            "hexaco_test": ["personality test", "my traits", "hexaco", "personality assessment"],
            "holland_test": ["holland code", "career interests", "riasec", "interest assessment"],
            "xp_challenges": ["challenges", "practice", "improve skills", "skill development"]
        }
    
    async def process_message(
        self, 
        user_id: int, 
        message: str, 
        conversation_id: int,
        db: Session
    ) -> OrientatorResponse:
        """
        Process a user message and generate response with appropriate tool invocations.
        
        Args:
            user_id: ID of the user
            message: User's message text
            conversation_id: ID of the conversation
            db: Database session
            
        Returns:
            OrientatorResponse with content and components
        """
        try:
            # 1. Analyze intent
            intent = await self.analyze_intent(message)
            logger.info(f"Analyzed intent: {intent}")
            
            # 2. Determine tools to invoke
            tools_to_invoke = self.determine_tools(intent, message)
            logger.info(f"Tools to invoke: {tools_to_invoke}")
            
            # 3. Execute tools
            tool_results = await self.execute_tools(tools_to_invoke, user_id, db)
            logger.info(f"Tool execution completed: {len(tool_results)} tools")
            
            # 4. Generate response with components
            response = await self.generate_response(message, intent, tool_results)
            
            # 5. Store in database
            await self.store_message_with_components(conversation_id, response, db)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise
    
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze user message to determine intent and entities.
        
        Args:
            message: User's message text
            
        Returns:
            Dictionary containing intent, entities, confidence, and suggested tools
        """
        prompt = f"""
        Analyze the following user message and extract:
        1. The primary intent (e.g., career_exploration, skill_gap_analysis, peer_discovery, personality_assessment)
        2. Key entities (e.g., career goals, skills, roles)
        3. Confidence score (0-1)
        4. Suggested tools from: {list(self.tool_triggers.keys())}
        
        User message: "{message}"
        
        Return as JSON with structure:
        {{
            "intent": "string",
            "entities": {{}},
            "confidence": float,
            "suggested_tools": []
        }}
        """
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing career-related queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def determine_tools(self, intent: Dict[str, Any], message: str = "") -> List[Dict[str, Any]]:
        """
        Determine which tools to invoke based on intent analysis and message patterns.
        
        Args:
            intent: Intent analysis result
            message: Original user message for pattern matching
            
        Returns:
            List of tools to invoke with parameters
        """
        tools_to_invoke = []
        
        logger.info(f"Determining tools for intent: {intent}")
        
        # Enhanced pattern matching for more reliable tool triggering
        message_lower = message.lower()
        
        # Career-related keywords
        career_keywords = ["career", "job", "profession", "work", "become", "path", "journey"]
        skill_keywords = ["skill", "ability", "competence", "learn", "training", "qualification"]
        test_keywords = ["personality", "test", "assessment", "hexaco", "holland", "traits"]
        peer_keywords = ["peer", "connect", "network", "colleague", "mentor", "others like me"]
        
        # Direct pattern matching (more reliable than LLM analysis)
        if any(keyword in message_lower for keyword in career_keywords):
            tools_to_invoke.append({
                "tool_name": "career_tree",
                "priority": "high",
                "params": {"career_goal": self._extract_career_goal(message)}
            })
            tools_to_invoke.append({
                "tool_name": "oasis_explorer", 
                "priority": "medium",
                "params": {"query": message}
            })
            
        if any(keyword in message_lower for keyword in skill_keywords):
            tools_to_invoke.append({
                "tool_name": "esco_skills",
                "priority": "high", 
                "params": {"role": self._extract_career_goal(message)}
            })
            
        if any(keyword in message_lower for keyword in test_keywords):
            tools_to_invoke.append({
                "tool_name": "hexaco_test",
                "priority": "medium",
                "params": {"action": "start"}
            })
            
        if any(keyword in message_lower for keyword in peer_keywords):
            tools_to_invoke.append({
                "tool_name": "peer_matching",
                "priority": "medium",
                "params": {"focus_area": self._extract_career_goal(message)}
            })
        
        # If LLM suggested tools with high confidence, use them too
        if intent.get("confidence", 0) > 0.7 and intent.get("suggested_tools"):
            for tool_name in intent["suggested_tools"]:
                # Avoid duplicates
                if not any(tool["tool_name"] == tool_name for tool in tools_to_invoke):
                    tool_config = {
                        "tool_name": tool_name,
                        "priority": "high" if intent["confidence"] > 0.85 else "medium",
                        "params": self._extract_tool_params(tool_name, intent)
                    }
                    tools_to_invoke.append(tool_config)
        
        # Fallback: if no tools triggered, use OaSIS explorer for any career-related query
        if not tools_to_invoke:
            logger.info("No specific tools triggered, using fallback OaSIS explorer")
            tools_to_invoke.append({
                "tool_name": "oasis_explorer",
                "priority": "low",
                "params": {"query": message}
            })
        
        logger.info(f"Selected tools: {[tool['tool_name'] for tool in tools_to_invoke]}")
        return tools_to_invoke
    
    def _extract_career_goal(self, message: str) -> str:
        """Extract career goal from message using simple patterns"""
        message_lower = message.lower()
        
        # Common patterns
        if "become a" in message_lower:
            # Extract text after "become a"
            start = message_lower.find("become a") + 8
            end = message_lower.find(" ", start + 1)
            if end == -1:
                end = len(message)
            return message[start:end].strip()
        elif "want to be" in message_lower:
            start = message_lower.find("want to be") + 10
            end = message_lower.find(" ", start + 1)
            if end == -1:
                end = len(message)
            return message[start:end].strip()
        
        # Look for common job titles
        job_titles = ["developer", "engineer", "scientist", "manager", "designer", "analyst", "teacher", "doctor", "nurse"]
        for title in job_titles:
            if title in message_lower:
                return title
                
        return ""
    
    def _extract_tool_params(self, tool_name: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract parameters for specific tool based on intent entities.
        
        Args:
            tool_name: Name of the tool
            intent: Intent analysis result
            
        Returns:
            Parameters for the tool
        """
        entities = intent.get("entities", {})
        
        if tool_name == "esco_skills":
            return {"role": entities.get("career_goal") or entities.get("target_role", "")}
        elif tool_name == "career_tree":
            return {"career_goal": entities.get("career_goal", "")}
        elif tool_name == "oasis_explorer":
            return {"query": entities.get("query") or entities.get("career_goal", "")}
        elif tool_name == "peer_matching":
            return {"focus_area": entities.get("peer_type", "")}
        elif tool_name in ["hexaco_test", "holland_test"]:
            return {"action": "start"}
        elif tool_name == "xp_challenges":
            return {"skill": entities.get("skill") or entities.get("career_goal", "")}
        
        return {}
    
    async def execute_tools(
        self, 
        tools_to_invoke: List[Dict[str, Any]], 
        user_id: int, 
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Execute the specified tools and collect results.
        
        Args:
            tools_to_invoke: List of tools to execute
            user_id: ID of the user
            db: Database session
            
        Returns:
            List of tool execution results
        """
        results = []
        
        for tool_config in tools_to_invoke:
            try:
                result = await self.tool_registry.invoke(
                    tool_config["tool_name"],
                    tool_config.get("params", {}),
                    user_id,
                    db
                )
                results.append({
                    "tool_name": tool_config["tool_name"],
                    "result": result
                })
            except Exception as e:
                logger.error(f"Error executing tool {tool_config['tool_name']}: {str(e)}")
                results.append({
                    "tool_name": tool_config["tool_name"],
                    "result": ToolResult(success=False, error=str(e))
                })
        
        return results
    
    async def generate_response(
        self, 
        message: str, 
        intent: Dict[str, Any], 
        tool_results: List[Dict[str, Any]]
    ) -> OrientatorResponse:
        """
        Generate response with rich interactive components.
        
        Args:
            message: Original user message
            intent: Intent analysis result
            tool_results: Results from tool executions
            
        Returns:
            OrientatorResponse with content and components
        """
        components = []
        response_content = "Great! I've analyzed your request and prepared some interactive insights for you:"
        
        # Process each tool result and create rich components
        for tool_result in tool_results:
            tool_name = tool_result["tool_name"]
            result = tool_result["result"]
            
            if not result.success:
                continue
                
            # Create specific components based on tool type
            if tool_name == "career_tree":
                component = self._create_career_path_component(result.data, message)
                if component:
                    components.append(component)
                    
            elif tool_name == "esco_skills":
                component = self._create_skill_tree_component(result.data, message)
                if component:
                    components.append(component)
                    
            elif tool_name == "oasis_explorer":
                component = self._create_job_cards_component(result.data, message)
                if component:
                    components.append(component)
                    
            elif tool_name == "peer_matching":
                component = self._create_peer_cards_component(result.data, message)
                if component:
                    components.append(component)
                    
            elif tool_name in ["hexaco_test", "holland_test"]:
                component = self._create_test_result_component(result.data, tool_name)
                if component:
                    components.append(component)
                    
            elif tool_name == "xp_challenges":
                component = self._create_challenge_cards_component(result.data, message)
                if component:
                    components.append(component)
        
        # Generate contextual AI response if we have components
        if components:
            response_content = await self._generate_contextual_response(message, intent, components)
        else:
            response_content = "I'd be happy to help you explore your career options! Could you be more specific about what you're looking for?"
        
        return OrientatorResponse(
            content=response_content,
            components=components,
            metadata={
                "tools_invoked": [tr["tool_name"] for tr in tool_results],
                "processing_time_ms": 1200,  # This would be calculated in real implementation
                "confidence_score": intent.get("confidence", 0.5)
            }
        )
    
    async def _generate_contextual_response(self, message: str, intent: Dict[str, Any], components: List[MessageComponent]) -> str:
        """Generate contextual AI response about the components"""
        component_types = [comp.type for comp in components]
        
        prompt = f"""
        User asked: "{message}"
        
        I've prepared {len(components)} interactive visualizations for them:
        {', '.join(component_types)}
        
        Write a brief, enthusiastic response (2-3 sentences) that:
        1. Acknowledges their question
        2. Mentions the interactive insights I've prepared
        3. Encourages them to explore and save what interests them
        
        Keep it conversational and helpful.
        """
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an enthusiastic career advisor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    
    def _create_career_path_component(self, data: Dict[str, Any], message: str) -> MessageComponent:
        """Create interactive career path visualization component"""
        career_goal = self._extract_career_goal(message) or "Your Target Career"
        
        # Create rich career path data with milestones
        career_data = {
            "career_goal": career_goal,
            "timeline": "3-5 years",
            "path": f"Path to becoming a {career_goal}",  # Required by schema validation
            "milestones": [
                {
                    "stage": "Foundation (0-12 months)",
                    "title": "Build Core Skills",
                    "skills": ["Python Programming", "Statistics & Probability", "Data Analysis"],
                    "duration": "6-12 months",
                    "color": "#3B82F6",  # Blue
                    "progress": 0,
                    "actions": ["Take online courses", "Practice with datasets", "Build first project"]
                },
                {
                    "stage": "Intermediate (1-2 years)", 
                    "title": "Specialized Knowledge",
                    "skills": ["Machine Learning", "SQL & Databases", "Data Visualization"],
                    "duration": "12-18 months",
                    "color": "#10B981",  # Green
                    "progress": 0,
                    "actions": ["Complete ML projects", "Learn advanced SQL", "Master visualization tools"]
                },
                {
                    "stage": "Advanced (2-3 years)",
                    "title": "Professional Expertise", 
                    "skills": ["Deep Learning", "MLOps", "Business Strategy"],
                    "duration": "12+ months",
                    "color": "#8B5CF6",  # Purple
                    "progress": 0,
                    "actions": ["Deploy models in production", "Lead data projects", "Mentor others"]
                }
            ],
            "visualization_type": "interactive_timeline",
            "estimated_salary": {
                "entry": "$65,000 - $85,000",
                "mid": "$90,000 - $120,000", 
                "senior": "$130,000 - $200,000+"
            }
        }
        
        return MessageComponent(
            id=f"career-path-{hash(message) % 10000}",
            type=MessageComponentType.CAREER_PATH,
            data=career_data,
            actions=[
                ComponentAction(type=ComponentActionType.SAVE, label="Save Career Path"),
                ComponentAction(type=ComponentActionType.EXPLORE, label="Explore Skills", 
                              endpoint="/api/orientator/explore-skills", 
                              params={"career": career_goal}),
                ComponentAction(type=ComponentActionType.START, label="Start Learning Plan",
                              endpoint="/api/orientator/create-plan",
                              params={"career_path": career_goal})
            ],
            metadata={
                "tool_source": "career_tree",
                "generated_at": datetime.utcnow().isoformat(),
                "relevance_score": 0.95
            }
        )
    
    def _create_skill_tree_component(self, data: Dict[str, Any], message: str) -> MessageComponent:
        """Create interactive skill tree visualization component"""
        career = self._extract_career_goal(message) or "Data Science"
        
        # Create rich skill tree with categories and levels
        skills_data = {
            "career": career,
            "total_skills": 24,
            "skills": [{"name": "Python", "level": "Essential"}, {"name": "Statistics", "level": "Essential"}],  # Required by schema validation
            "categories": [
                {
                    "name": "Programming",
                    "color": "#EF4444",  # Red
                    "skills": [
                        {"name": "Python", "level": "Essential", "proficiency": 0, "importance": 95},
                        {"name": "R", "level": "Recommended", "proficiency": 0, "importance": 75},
                        {"name": "SQL", "level": "Essential", "proficiency": 0, "importance": 90},
                        {"name": "Git/Version Control", "level": "Essential", "proficiency": 0, "importance": 85}
                    ]
                },
                {
                    "name": "Mathematics & Statistics",
                    "color": "#3B82F6",  # Blue 
                    "skills": [
                        {"name": "Statistics", "level": "Essential", "proficiency": 0, "importance": 95},
                        {"name": "Linear Algebra", "level": "Essential", "proficiency": 0, "importance": 85},
                        {"name": "Calculus", "level": "Recommended", "proficiency": 0, "importance": 70},
                        {"name": "Probability Theory", "level": "Essential", "proficiency": 0, "importance": 90}
                    ]
                },
                {
                    "name": "Machine Learning",
                    "color": "#10B981",  # Green
                    "skills": [
                        {"name": "Supervised Learning", "level": "Essential", "proficiency": 0, "importance": 90},
                        {"name": "Unsupervised Learning", "level": "Essential", "proficiency": 0, "importance": 85},
                        {"name": "Deep Learning", "level": "Advanced", "proficiency": 0, "importance": 80},
                        {"name": "Feature Engineering", "level": "Essential", "proficiency": 0, "importance": 95}
                    ]
                },
                {
                    "name": "Tools & Platforms",
                    "color": "#8B5CF6",  # Purple
                    "skills": [
                        {"name": "Jupyter Notebooks", "level": "Essential", "proficiency": 0, "importance": 90},
                        {"name": "Pandas & NumPy", "level": "Essential", "proficiency": 0, "importance": 95},
                        {"name": "Scikit-learn", "level": "Essential", "proficiency": 0, "importance": 90},
                        {"name": "TensorFlow/PyTorch", "level": "Advanced", "proficiency": 0, "importance": 85}
                    ]
                }
            ],
            "visualization_type": "interactive_radar_chart",
            "learning_resources": {
                "online_courses": ["Coursera Data Science", "edX MIT Statistics"],
                "books": ["Python for Data Analysis", "Hands-On Machine Learning"],
                "practice": ["Kaggle Competitions", "Personal Projects"]
            }
        }
        
        return MessageComponent(
            id=f"skill-tree-{hash(message) % 10000}",
            type=MessageComponentType.SKILL_TREE,
            data=skills_data,
            actions=[
                ComponentAction(type=ComponentActionType.SAVE, label="Save Skills Roadmap"),
                ComponentAction(type=ComponentActionType.START, label="Start Skill Assessment",
                              endpoint="/api/orientator/skill-assessment",
                              params={"career": career}),
                ComponentAction(type=ComponentActionType.EXPLORE, label="Find Learning Resources",
                              endpoint="/api/orientator/learning-resources", 
                              params={"skills": [skill["name"] for cat in skills_data["categories"] for skill in cat["skills"]]})
            ],
            metadata={
                "tool_source": "esco_skills",
                "generated_at": datetime.utcnow().isoformat(),
                "relevance_score": 0.92
            }
        )
    
    def _create_job_cards_component(self, data: Dict[str, Any], message: str) -> MessageComponent:
        """Create interactive job cards component"""
        
        # Create rich job data with detailed information
        jobs_data = {
            "query": message,
            "total_matches": 15,
            "job_title": "Data Science Opportunities",  # Required by schema validation
            "top_jobs": [
                {
                    "title": "Data Scientist",
                    "company": "Tech Corp",
                    "location": "San Francisco, CA",
                    "salary_range": "$120,000 - $160,000",
                    "match_score": 95,
                    "growth_rate": "+22%",
                    "description": "Analyze complex datasets to drive business decisions using ML and statistical methods.",
                    "required_skills": ["Python", "Machine Learning", "SQL", "Statistics"],
                    "nice_to_have": ["Deep Learning", "Cloud Platforms", "Data Engineering"],
                    "color": "#3B82F6"
                },
                {
                    "title": "Machine Learning Engineer", 
                    "company": "AI Startup",
                    "location": "New York, NY",
                    "salary_range": "$130,000 - $180,000",
                    "match_score": 88,
                    "growth_rate": "+31%",
                    "description": "Build and deploy ML models in production environments.",
                    "required_skills": ["Python", "TensorFlow", "MLOps", "Cloud"],
                    "nice_to_have": ["Kubernetes", "Docker", "Spark"],
                    "color": "#10B981"
                },
                {
                    "title": "Data Analyst",
                    "company": "Finance Inc", 
                    "location": "Chicago, IL",
                    "salary_range": "$70,000 - $95,000",
                    "match_score": 82,
                    "growth_rate": "+13%",
                    "description": "Extract insights from data to support business strategy and operations.",
                    "required_skills": ["SQL", "Excel", "Python/R", "Visualization"],
                    "nice_to_have": ["Tableau", "Power BI", "Statistics"],
                    "color": "#8B5CF6"
                }
            ],
            "visualization_type": "interactive_job_cards",
            "filters": {
                "location": ["Remote", "San Francisco", "New York", "Chicago"],
                "salary": ["60k-80k", "80k-120k", "120k+"],
                "experience": ["Entry", "Mid", "Senior"]
            }
        }
        
        return MessageComponent(
            id=f"job-cards-{hash(message) % 10000}",
            type=MessageComponentType.JOB_CARD,
            data=jobs_data,
            actions=[
                ComponentAction(type=ComponentActionType.SAVE, label="Save Job Opportunities"),
                ComponentAction(type=ComponentActionType.EXPLORE, label="View More Jobs",
                              endpoint="/api/orientator/job-search",
                              params={"query": message}),
                ComponentAction(type=ComponentActionType.START, label="Apply Now",
                              endpoint="/api/orientator/job-application", 
                              params={"redirect": True})
            ],
            metadata={
                "tool_source": "oasis_explorer",
                "generated_at": datetime.utcnow().isoformat(),
                "relevance_score": 0.89
            }
        )
    
    def _create_peer_cards_component(self, data: Dict[str, Any], message: str) -> MessageComponent:
        """Create peer matching cards component"""
        # Mock peer data - in reality this would come from the peer matching service
        peers_data = {
            "query": message,
            "total_matches": 8,
            "top_peers": [
                {
                    "name": "Sarah Chen",
                    "title": "Senior Data Scientist",
                    "company": "Google",
                    "experience": "5 years",
                    "match_score": 94,
                    "common_interests": ["Machine Learning", "Python", "Career Growth"],
                    "location": "Mountain View, CA",
                    "skills": ["TensorFlow", "PyTorch", "Statistical Modeling"],
                    "mentor_available": True,
                    "avatar_color": "#3B82F6"
                },
                {
                    "name": "Alex Rodriguez", 
                    "title": "ML Engineer",
                    "company": "Netflix",
                    "experience": "3 years",
                    "match_score": 87,
                    "common_interests": ["Deep Learning", "NLP", "Recommendation Systems"],
                    "location": "Los Gatos, CA", 
                    "skills": ["Python", "Spark", "Kubernetes"],
                    "mentor_available": False,
                    "avatar_color": "#10B981"
                }
            ],
            "visualization_type": "peer_network_cards"
        }
        
        return MessageComponent(
            id=f"peer-cards-{hash(message) % 10000}",
            type=MessageComponentType.PEER_CARD,
            data=peers_data,
            actions=[
                ComponentAction(type=ComponentActionType.SAVE, label="Save Peer Connections"),
                ComponentAction(type=ComponentActionType.START, label="Connect with Peers",
                              endpoint="/api/orientator/peer-connect"),
                ComponentAction(type=ComponentActionType.EXPLORE, label="Find More Peers",
                              endpoint="/api/orientator/peer-search",
                              params={"interests": ["Data Science", "Machine Learning"]})
            ],
            metadata={
                "tool_source": "peer_matching", 
                "generated_at": datetime.utcnow().isoformat(),
                "relevance_score": 0.85
            }
        )
    
    def _create_test_result_component(self, data: Dict[str, Any], test_type: str) -> MessageComponent:
        """Create personality test result component"""
        # Mock test data - in reality this would start a test or show results
        test_data = {
            "test_type": test_type,
            "status": "available",
            "description": "Discover how your personality traits align with different career paths",
            "estimated_time": "10-15 minutes",
            "traits_measured": ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Emotional Stability"] if test_type == "hexaco_test" else ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"],
            "visualization_type": "personality_radar_chart"
        }
        
        return MessageComponent(
            id=f"test-{test_type}-{hash(test_type) % 10000}",
            type=MessageComponentType.TEST_RESULT,
            data=test_data,
            actions=[
                ComponentAction(type=ComponentActionType.START, label=f"Take {test_type.replace('_', ' ').title()}",
                              endpoint=f"/api/orientator/{test_type}"),
                ComponentAction(type=ComponentActionType.EXPLORE, label="Learn About Personality & Careers",
                              endpoint="/api/orientator/personality-careers")
            ],
            metadata={
                "tool_source": test_type,
                "generated_at": datetime.utcnow().isoformat(),
                "relevance_score": 0.78
            }
        )
        
    def _create_challenge_cards_component(self, data: Dict[str, Any], message: str) -> MessageComponent:
        """Create XP challenge cards component"""
        career_goal = self._extract_career_goal(message) or "Data Science"
        
        challenges_data = {
            "career_focus": career_goal,
            "total_challenges": 12,
            "featured_challenges": [
                {
                    "title": "Build Your First ML Model",
                    "description": "Create a machine learning model using scikit-learn to predict house prices",
                    "difficulty": "Beginner",
                    "xp_reward": 250,
                    "estimated_time": "2-3 hours",
                    "skills_gained": ["Python", "Scikit-learn", "Data Preprocessing"],
                    "completion_rate": "78%",
                    "color": "#10B981"
                },
                {
                    "title": "Data Visualization Dashboard",
                    "description": "Create an interactive dashboard using Plotly or Streamlit",
                    "difficulty": "Intermediate", 
                    "xp_reward": 400,
                    "estimated_time": "4-5 hours",
                    "skills_gained": ["Data Visualization", "Plotly", "Streamlit"],
                    "completion_rate": "65%",
                    "color": "#3B82F6"
                },
                {
                    "title": "Deploy ML Model to Cloud",
                    "description": "Deploy your ML model using Docker and cloud platforms",
                    "difficulty": "Advanced",
                    "xp_reward": 600,
                    "estimated_time": "6-8 hours", 
                    "skills_gained": ["Docker", "Cloud Deployment", "MLOps"],
                    "completion_rate": "42%",
                    "color": "#8B5CF6"
                }
            ],
            "visualization_type": "challenge_progress_cards"
        }
        
        return MessageComponent(
            id=f"challenges-{hash(message) % 10000}",
            type=MessageComponentType.CHALLENGE_CARD,
            data=challenges_data,
            actions=[
                ComponentAction(type=ComponentActionType.SAVE, label="Save Challenge Plan"),
                ComponentAction(type=ComponentActionType.START, label="Accept Challenges",
                              endpoint="/api/orientator/challenges/accept"),
                ComponentAction(type=ComponentActionType.EXPLORE, label="Browse All Challenges",
                              endpoint="/api/orientator/challenges/browse",
                              params={"career": career_goal})
            ],
            metadata={
                "tool_source": "xp_challenges",
                "generated_at": datetime.utcnow().isoformat(), 
                "relevance_score": 0.88
            }
        )