"""
Enhanced Chat Service with GraphSage Integration

This service enhances the existing chat functionality with GraphSage-based
skill relevance insights and personalized learning recommendations.
"""

import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
import os

from .graphsage_llm_integration import graphsage_llm
from ..models import User, UserProfile, UserSkill, Conversation, ChatMessage
from .conversation_service import ConversationService
from .chat_message_service import ChatMessageService

logger = logging.getLogger(__name__)

class EnhancedChatService:
    """
    Enhanced chat service that integrates GraphSage insights into conversations.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    async def send_enhanced_message(self, user_id: int, message_text: str, 
                                  conversation_id: Optional[int], db: Session) -> Dict[str, Any]:
        """
        Send a message with GraphSage enhancement and get intelligent response.
        
        Args:
            user_id: User ID
            message_text: User's message
            conversation_id: Optional conversation ID
            db: Database session
            
        Returns:
            Enhanced response with GraphSage insights
        """
        try:
            # Get or create conversation
            if conversation_id:
                conversation = await ConversationService.get_conversation_by_id(
                    db, conversation_id, user_id
                )
                if not conversation:
                    raise ValueError("Conversation not found")
            else:
                conversation = await ConversationService.create_conversation(
                    db, user_id, message_text
                )
                
            # Get GraphSage insights for the message
            graphsage_insights = await graphsage_llm.enhance_conversation_with_graphsage(
                message_text, user_id, db
            )
            
            # Add user message to conversation
            user_message = await ChatMessageService.add_message(
                db, conversation.id, "user", message_text
            )
            
            # Get recent conversation history
            recent_messages = await ChatMessageService.get_conversation_messages(
                db, conversation.id, limit=20
            )
            
            # Build enhanced system prompt with GraphSage insights
            enhanced_system_prompt = await self._build_enhanced_system_prompt(
                user_id, graphsage_insights, db
            )
            
            # Prepare messages for OpenAI
            messages_for_openai = [
                {"role": "system", "content": enhanced_system_prompt}
            ]
            
            # Add conversation history (excluding system messages)
            for msg in reversed(recent_messages):
                if msg.role != "system":
                    messages_for_openai.append({
                        "role": msg.role,
                        "content": msg.content
                    })
                    
            # Generate enhanced response
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages_for_openai,
                temperature=0.8,
                max_tokens=400,
                presence_penalty=0.6,
                frequency_penalty=0.3
            )
            
            assistant_response = response.choices[0].message.content
            
            # Add assistant response to conversation
            assistant_message = await ChatMessageService.add_message(
                db, conversation.id, "assistant", assistant_response,
                tokens_used=response.usage.total_tokens if hasattr(response, 'usage') else None,
                model_used="gpt-4"
            )
            
            return {
                "response": assistant_response,
                "conversation_id": conversation.id,
                "message_id": assistant_message.id,
                "graphsage_insights": graphsage_insights,
                "enhanced_features": {
                    "skill_relevance_analysis": True,
                    "personalized_learning_suggestions": True,
                    "career_path_insights": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced chat service: {str(e)}")
            raise
            
    async def _build_enhanced_system_prompt(self, user_id: int, 
                                          graphsage_insights: Dict[str, Any], 
                                          db: Session) -> str:
        """Build enhanced system prompt with GraphSage insights."""
        try:
            # Get user profile
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).first()
            
            base_prompt = """
You are an AI career mentor with advanced knowledge of skill relationships and career pathways. 
Your responses are enhanced with GraphSage neural network insights that analyze skill relevance 
and career path connections.

Your role:
- Provide personalized career guidance based on skill relevance analysis
- Explain why certain skills are important for the user's career path
- Suggest learning priorities based on GraphSage relevance scores
- Help users understand skill connections and career progression paths
- Keep responses conversational, insightful, and actionable

Guidelines:
- Use GraphSage insights to explain skill relevance when appropriate
- Reference relevance scores (0-1 scale) to prioritize recommendations
- Connect skills to specific career outcomes
- Provide concrete next steps for skill development
- Ask thoughtful follow-up questions to guide exploration
"""

            # Add user profile context
            if user_profile:
                profile_context = f"""
                
## User Profile Context:
- Name: {user_profile.name or 'Not specified'}
- Career Goals: {user_profile.career_goals or 'Not specified'}
- Interests: {user_profile.interests or 'Not specified'}
- Major: {user_profile.major or 'Not specified'}
- Experience Level: {user_profile.years_experience or 'Not specified'} years
"""
                base_prompt += profile_context
                
            # Add GraphSage insights
            insights = graphsage_insights.get("graphsage_insights", {})
            if isinstance(insights, dict) and insights.get("relevant_skills"):
                graphsage_context = f"""

## GraphSage Skill Relevance Analysis:
Current conversation shows relevance to these skills:
"""
                for skill in insights["relevant_skills"][:3]:  # Top 3 most relevant
                    graphsage_context += f"- {skill['name']}: {skill['relevance_score']:.3f} relevance score\n"
                    
                if insights.get("conversation_context", {}).get("user_strengths"):
                    graphsage_context += f"\nUser's current strengths: {', '.join(insights['conversation_context']['user_strengths'])}\n"
                    
                base_prompt += graphsage_context
                
            # Add behavioral instructions
            base_prompt += """

## Response Style:
- Be encouraging and supportive
- Use specific examples when explaining skill importance
- Reference relevance scores when discussing skill priorities
- Ask one thoughtful question to continue the conversation
- Keep responses focused and actionable (2-3 paragraphs max)
"""

            return base_prompt
            
        except Exception as e:
            logger.error(f"Error building enhanced system prompt: {str(e)}")
            return "You are a helpful career mentor providing personalized guidance."
            
    async def get_skill_explanation(self, user_id: int, skill_name: str, 
                                  db: Session) -> Dict[str, Any]:
        """
        Get detailed explanation for why a specific skill is relevant for the user.
        
        Args:
            user_id: User ID
            skill_name: Name of the skill to explain
            db: Database session
            
        Returns:
            Detailed skill explanation with relevance analysis
        """
        try:
            # Get user profile
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).first()
            
            if not user_profile:
                return {"error": "User profile not found"}
                
            # Find skill in GraphSage metadata
            skill_id = None
            relevance_score = 0.0
            
            for node_id, metadata in graphsage_llm.node_metadata.items():
                if (metadata.get("type") == "skill" and 
                    skill_name.lower() in metadata.get("label", "").lower()):
                    skill_id = node_id
                    break
                    
            if skill_id:
                # Compute relevance score for this specific skill
                user_skill_dict = {}
                career_goals = []
                
                if user_skills:
                    skill_mapping = {
                        "creativity": "Creativity",
                        "leadership": "Leadership",
                        "digital_literacy": "Digital Literacy",
                        "critical_thinking": "Critical Thinking",
                        "problem_solving": "Problem Solving"
                    }
                    
                    for skill_key, skill_display_name in skill_mapping.items():
                        value = getattr(user_skills, skill_key)
                        if value is not None:
                            user_skill_dict[skill_display_name] = value
                            
                if user_profile.career_goals:
                    career_goals = [user_profile.career_goals]
                    
                relevance_scores = graphsage_llm.compute_skill_relevance_scores(
                    user_skill_dict, career_goals
                )
                relevance_score = relevance_scores.get(skill_id, 0.0)
                
                # Generate detailed explanation
                explanation = await graphsage_llm.generate_skill_explanation(
                    skill_id, relevance_score, 
                    graphsage_llm._build_user_profile_dict(user_profile, user_skills)
                )
                
                return {
                    "skill_name": skill_name,
                    "relevance_score": relevance_score,
                    "explanation": explanation,
                    "skill_metadata": graphsage_llm.node_metadata.get(skill_id, {}),
                    "graphsage_analysis": True
                }
            else:
                return {
                    "skill_name": skill_name,
                    "relevance_score": 0.0,
                    "explanation": f"Skill '{skill_name}' not found in GraphSage knowledge base.",
                    "graphsage_analysis": False
                }
                
        except Exception as e:
            logger.error(f"Error getting skill explanation: {str(e)}")
            return {"error": f"Failed to get skill explanation: {str(e)}"}
            
    async def generate_learning_recommendations(self, user_id: int, 
                                              db: Session) -> Dict[str, Any]:
        """
        Generate personalized learning recommendations based on GraphSage analysis.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Personalized learning recommendations
        """
        try:
            return await graphsage_llm.generate_personalized_learning_priorities(user_id, db)
            
        except Exception as e:
            logger.error(f"Error generating learning recommendations: {str(e)}")
            return {"error": f"Failed to generate learning recommendations: {str(e)}"}
            
    async def analyze_career_path_compatibility(self, user_id: int, career_path: str,
                                              db: Session) -> Dict[str, Any]:
        """
        Analyze how well a career path matches the user's skills using GraphSage.
        
        Args:
            user_id: User ID
            career_path: Career path to analyze
            db: Database session
            
        Returns:
            Career path compatibility analysis
        """
        try:
            # Get user profile
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).first()
            
            if not user_profile:
                return {"error": "User profile not found"}
                
            # Build user skills dictionary
            user_skill_dict = {}
            if user_skills:
                skill_mapping = {
                    "creativity": "Creativity",
                    "leadership": "Leadership",
                    "digital_literacy": "Digital Literacy",
                    "critical_thinking": "Critical Thinking",
                    "problem_solving": "Problem Solving",
                    "analytical_thinking": "Analytical Thinking",
                    "attention_to_detail": "Attention to Detail",
                    "collaboration": "Collaboration",
                    "adaptability": "Adaptability"
                }
                
                for skill_key, skill_name in skill_mapping.items():
                    value = getattr(user_skills, skill_key)
                    if value is not None:
                        user_skill_dict[skill_name] = value
                        
            # Compute relevance scores for the career path
            relevance_scores = graphsage_llm.compute_skill_relevance_scores(
                user_skill_dict, [career_path]
            )
            
            # Get top relevant skills for this career path
            top_skills = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Calculate overall compatibility score
            compatibility_score = sum(score for _, score in top_skills[:5]) / 5 if top_skills else 0.0
            
            # Generate analysis
            analysis = {
                "career_path": career_path,
                "compatibility_score": compatibility_score,
                "matching_skills": [],
                "skill_gaps": [],
                "recommendations": []
            }
            
            # Analyze skill matches and gaps
            for skill_id, score in top_skills:
                skill_metadata = graphsage_llm.node_metadata.get(skill_id, {})
                skill_name = skill_metadata.get("label", "Unknown Skill")
                
                skill_analysis = {
                    "skill_name": skill_name,
                    "relevance_score": score,
                    "description": skill_metadata.get("description", ""),
                    "user_proficiency": user_skill_dict.get(skill_name, 0) / 5.0 if skill_name in user_skill_dict else 0.0
                }
                
                if score > 0.7:
                    analysis["matching_skills"].append(skill_analysis)
                elif score > 0.5:
                    analysis["skill_gaps"].append(skill_analysis)
                    
            # Generate recommendations using LLM
            recommendations_prompt = f"""
Based on GraphSage analysis, provide 3-4 specific recommendations for someone pursuing {career_path}.

## Compatibility Analysis:
- Overall compatibility: {compatibility_score:.2f}/1.0
- Strong skill matches: {len(analysis['matching_skills'])}
- Skill gaps identified: {len(analysis['skill_gaps'])}

## User's Current Skills:
{', '.join([f"{skill}: {score}/5" for skill, score in user_skill_dict.items()])}

## Top Relevant Skills for {career_path}:
{', '.join([skill['skill_name'] for skill in analysis['matching_skills'][:3]])}

Provide actionable recommendations for skill development and career preparation.
"""

            recommendations_response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a career counselor providing specific, actionable recommendations."},
                    {"role": "user", "content": recommendations_prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            analysis["recommendations"] = recommendations_response.choices[0].message.content
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing career path compatibility: {str(e)}")
            return {"error": f"Failed to analyze career path compatibility: {str(e)}"}


# Global instance
enhanced_chat_service = EnhancedChatService()