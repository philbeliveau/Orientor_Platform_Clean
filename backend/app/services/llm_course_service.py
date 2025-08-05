import os
import logging
from openai import OpenAI
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import json
import asyncio
from ..models.course import Course, ConversationLog

logger = logging.getLogger(__name__)

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found. LLM course service will not function properly.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

class LLMCourseService:
    """
    Service for LLM-powered course analysis and career profiling conversations.
    """
    
    @staticmethod
    async def generate_targeted_questions(
        course: Course,
        context: Dict[str, Any],
        focus_areas: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Generate career-focused questions based on course and user context.
        """
        if not client:
            logger.error("OpenAI client not initialized")
            return LLMCourseService._get_fallback_questions(course, focus_areas)
        
        try:
            # Build prompt for question generation
            prompt = LLMCourseService._build_question_generation_prompt(
                course, context, focus_areas
            )
            
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a career counselor and educational psychologist specializing in extracting career insights from academic experiences. Generate thoughtful, specific questions that help students discover their authentic career preferences through reflection on their coursework."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse the response to extract questions
            content = response.choices[0].message.content
            questions = LLMCourseService._parse_questions_from_response(content)
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating targeted questions: {str(e)}")
            return LLMCourseService._get_fallback_questions(course, focus_areas)
    
    @staticmethod
    def _build_question_generation_prompt(
        course: Course,
        context: Dict[str, Any],
        focus_areas: Optional[List[str]]
    ) -> str:
        """
        Build a detailed prompt for question generation.
        """
        prompt = f"""
        Generate 3-5 targeted questions for career profiling based on this course experience:

        **Course Information:**
        - Name: {course.course_name}
        - Subject: {course.subject_category}
        - Grade: {course.grade or 'Not specified'}
        - Semester: {course.semester or 'Not specified'}
        - Professor: {course.professor or 'Not specified'}

        **Student Context:**
        - Previous courses taken: {context.get('user_history', {}).get('total_courses', 0)}
        - Subject distribution: {context.get('user_history', {}).get('subject_distribution', {})}
        - Previous insights discovered: {len(context.get('previous_insights', []))}

        **Focus Areas (if specified):** {focus_areas or 'General career exploration'}

        **Question Guidelines:**
        1. Focus on psychological constructs that inform career choices:
           - Cognitive style (analytical vs. creative, concrete vs. abstract thinking)
           - Work environment preferences (collaborative vs. independent, structured vs. flexible)
           - Interest authenticity (genuine engagement vs. external pressure)
           - Motivation patterns (what energizes vs. drains them)

        2. Use specific course experiences as anchors:
           - Reference actual assignments, projects, or concepts from this type of course
           - Ask about comparisons with other courses or experiences
           - Explore emotional reactions to different learning activities

        3. Make questions actionable for career guidance:
           - Connect responses to potential career paths
           - Identify transferable skills and preferences
           - Reveal patterns that inform ESCO skill categories

        **Example Question Frameworks:**
        - Cognitive Style: "You [struggled/excelled] with [specific concept] in {course.course_name} - what felt different about solving those problems compared to other courses?"
        - Work Preferences: "Your [group project/individual work] grade was [higher/lower] than usual - do you prefer [collaborative/independent] work environments?"
        - Interest Authenticity: "Your grade in {course.course_name} is [high/low] but how do you actually feel about the subject matter - what specifically engages or disengages you?"

        Return the questions in this JSON format:
        [
            {{
                "id": "q1",
                "question": "Your specific question here",
                "intent": "cognitive_preference|work_style|subject_affinity|motivation_pattern",
                "follow_up_triggers": ["keyword1", "keyword2"]
            }}
        ]
        """
        return prompt
    
    @staticmethod
    def _parse_questions_from_response(content: str) -> List[Dict[str, str]]:
        """
        Parse questions from LLM response.
        """
        try:
            # Try to extract JSON from the response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                questions = json.loads(json_str)
                return questions
            else:
                # Fallback: parse questions manually
                lines = content.split('\n')
                questions = []
                question_id = 1
                
                for line in lines:
                    line = line.strip()
                    if line and ('?' in line or line.startswith('-')):
                        # Clean up the question
                        question_text = line.lstrip('- ').strip()
                        if question_text:
                            questions.append({
                                "id": f"q{question_id}",
                                "question": question_text,
                                "intent": "general_exploration",
                                "follow_up_triggers": []
                            })
                            question_id += 1
                
                return questions[:5]  # Limit to 5 questions
                
        except Exception as e:
            logger.error(f"Error parsing questions: {str(e)}")
            return []
    
    @staticmethod
    def _get_fallback_questions(course: Course, focus_areas: Optional[List[str]]) -> List[Dict[str, str]]:
        """
        Generate fallback questions when LLM is unavailable.
        """
        course_name = course.course_name
        subject = course.subject_category or "this subject"
        
        fallback_questions = [
            {
                "id": "q1",
                "question": f"What aspects of {course_name} did you find most engaging or interesting?",
                "intent": "subject_affinity",
                "follow_up_triggers": ["enjoyed", "interesting", "engaging"]
            },
            {
                "id": "q2", 
                "question": f"When working on assignments for {course_name}, did you prefer working alone or collaborating with others? Why?",
                "intent": "work_style",
                "follow_up_triggers": ["alone", "group", "team", "collaboration"]
            },
            {
                "id": "q3",
                "question": f"What was the most challenging part of {course_name}, and how did you approach solving those challenges?",
                "intent": "cognitive_preference", 
                "follow_up_triggers": ["challenging", "difficult", "problem", "approach"]
            }
        ]
        
        # Add subject-specific questions
        if course.subject_category == "STEM":
            fallback_questions.append({
                "id": "q4",
                "question": f"In {course_name}, did you prefer theoretical concepts or hands-on practical applications? What made one more appealing?",
                "intent": "cognitive_preference",
                "follow_up_triggers": ["theoretical", "practical", "hands-on", "applied"]
            })
        elif course.subject_category == "business":
            fallback_questions.append({
                "id": "q4", 
                "question": f"When analyzing business cases or scenarios in {course_name}, what kind of solutions did you gravitate toward - analytical/data-driven or creative/innovative approaches?",
                "intent": "cognitive_preference",
                "follow_up_triggers": ["analytical", "creative", "data", "innovative"]
            })
        
        return fallback_questions
    
    @staticmethod
    async def analyze_response(
        response: str,
        question_id: str,
        session_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Analyze user response and extract psychological insights.
        """
        if not client:
            logger.error("OpenAI client not initialized")
            return LLMCourseService._get_fallback_analysis(response, question_id)
        
        try:
            # Get conversation context
            context = await LLMCourseService._get_conversation_context(session_id, db)
            
            # Build analysis prompt
            prompt = LLMCourseService._build_analysis_prompt(
                response, question_id, context
            )
            
            llm_response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational psychologist and career counselor. Analyze student responses to extract specific psychological insights that inform career guidance. Focus on:

1. Cognitive Preferences: How they think and process information
2. Work Style Preferences: How they prefer to work and collaborate
3. Authentic Interests: What genuinely engages vs. what feels forced
4. Career Signals: Indicators of skills and aptitudes for specific career paths

Provide specific, actionable insights with confidence scores."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            content = llm_response.choices[0].message.content
            analysis = LLMCourseService._parse_analysis_response(content)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing response: {str(e)}")
            return LLMCourseService._get_fallback_analysis(response, question_id)
    
    @staticmethod
    async def _get_conversation_context(session_id: str, db: Session) -> Dict[str, Any]:
        """
        Get context from previous conversation in this session.
        """
        logs = db.query(ConversationLog).filter(
            ConversationLog.session_id == session_id
        ).order_by(ConversationLog.created_at.asc()).all()
        
        context = {
            "session_id": session_id,
            "previous_responses": [],
            "extracted_insights": [],
            "question_count": len(logs)
        }
        
        for log in logs:
            if log.response:
                context["previous_responses"].append({
                    "question": log.question_text,
                    "response": log.response,
                    "intent": log.question_intent
                })
            
            if log.extracted_insights:
                context["extracted_insights"].extend(log.extracted_insights)
        
        return context
    
    @staticmethod
    def _build_analysis_prompt(
        response: str,
        question_id: str, 
        context: Dict[str, Any]
    ) -> str:
        """
        Build prompt for response analysis.
        """
        prompt = f"""
        Analyze this student response for psychological insights that inform career guidance:

        **Current Response:**
        Question ID: {question_id}
        Student Response: "{response}"

        **Conversation Context:**
        - Total questions answered: {context.get('question_count', 0)}
        - Previous insights discovered: {len(context.get('extracted_insights', []))}

        **Previous Responses in Session:**
        {json.dumps(context.get('previous_responses', []), indent=2)}

        **Analysis Framework:**

        1. **Cognitive Preferences** - Extract indicators of:
           - Analytical vs. creative thinking patterns
           - Concrete vs. abstract processing preferences  
           - Detail-oriented vs. big-picture thinking
           - Problem-solving approaches

        2. **Work Style Preferences** - Identify preferences for:
           - Individual vs. collaborative work
           - Structured vs. flexible environments
           - Autonomous vs. guided work
           - Fast-paced vs. methodical approaches

        3. **Authentic Interests** - Distinguish between:
           - Genuine engagement and curiosity
           - External pressure or expectations
           - Intrinsic vs. extrinsic motivation
           - Natural aptitudes vs. learned skills

        4. **Career Signals** - Map to specific skills/traits:
           - Analytical thinking
           - Creative problem solving
           - Interpersonal skills
           - Leadership potential
           - Attention to detail
           - Stress tolerance

        **Output Format (JSON):**
        {{
            "insights": [
                {{
                    "type": "cognitive_preference|work_style|subject_affinity",
                    "value": {{"specific_insight": "detailed description", "indicators": ["evidence1", "evidence2"]}},
                    "confidence": 0.8,
                    "evidence": "specific phrases or patterns from response"
                }}
            ],
            "career_signals": [
                {{
                    "type": "analytical_thinking|creative_problem_solving|interpersonal_skills|leadership_potential|attention_to_detail|stress_tolerance",
                    "strength": 0.7,
                    "evidence": "specific evidence from response",
                    "metadata": {{"context": "additional context"}}
                }}
            ],
            "sentiment": {{
                "engagement_level": 0.8,
                "authenticity": 0.9,
                "emotional_indicators": ["enthusiasm", "frustration", "confidence"]
            }},
            "next_questions": [
                {{
                    "question": "Follow-up question based on this response",
                    "intent": "explore_deeper|clarify_contradiction|validate_insight",
                    "priority": "high|medium|low"
                }}
            ],
            "session_complete": false,
            "career_implications": {{
                "immediate_insights": ["insight1", "insight2"],
                "esco_connections": ["skill_category1", "skill_category2"],
                "recommended_exploration": ["career_path1", "career_path2"]
            }}
        }}
        """
        return prompt
    
    @staticmethod
    def _parse_analysis_response(content: str) -> Dict[str, Any]:
        """
        Parse analysis response from LLM.
        """
        try:
            # Try to extract JSON
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                analysis = json.loads(json_str)
                
                # Transform next_questions to match our schema
                if "next_questions" in analysis:
                    analysis["next_questions"] = LLMCourseService._transform_questions(
                        analysis["next_questions"]
                    )
                
                return analysis
            else:
                # Fallback parsing
                return {
                    "insights": [],
                    "career_signals": [],
                    "sentiment": {"engagement_level": 0.5},
                    "next_questions": [],
                    "session_complete": False,
                    "career_implications": {}
                }
                
        except Exception as e:
            logger.error(f"Error parsing analysis response: {str(e)}")
            return LLMCourseService._get_fallback_analysis("", "")
    
    @staticmethod
    def _transform_questions(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform questions to match QuestionSchema format.
        """
        transformed = []
        for i, question in enumerate(questions):
            # Ensure required fields exist
            transformed_question = {
                "id": question.get("id", f"question_{i+1}"),
                "question": question.get("question", ""),
                "intent": question.get("intent", "general"),
                "follow_up_triggers": question.get("follow_up_triggers", [])
            }
            
            # If follow_up_triggers is missing, try to extract from other fields
            if not transformed_question["follow_up_triggers"]:
                # Generate some basic triggers based on intent
                intent = transformed_question["intent"]
                if intent == "explore_deeper":
                    transformed_question["follow_up_triggers"] = ["more", "example", "specifically"]
                elif intent == "clarify_contradiction":
                    transformed_question["follow_up_triggers"] = ["prefer", "compare", "difference"]
                else:
                    transformed_question["follow_up_triggers"] = ["experience", "feeling"]
            
            transformed.append(transformed_question)
        
        return transformed
    
    @staticmethod
    def _get_fallback_analysis(response: str, question_id: str) -> Dict[str, Any]:
        """
        Provide fallback analysis when LLM is unavailable.
        """
        # Simple keyword-based analysis
        response_lower = response.lower()
        
        insights = []
        career_signals = []
        
        # Basic sentiment analysis
        positive_words = ["enjoy", "love", "interesting", "engaging", "exciting", "fun"]
        negative_words = ["boring", "difficult", "frustrating", "hate", "dislike"]
        
        positive_count = sum(1 for word in positive_words if word in response_lower)
        negative_count = sum(1 for word in negative_words if word in response_lower)
        
        engagement_level = max(0.1, min(0.9, 0.5 + (positive_count - negative_count) * 0.2))
        
        # Basic insight extraction
        if "team" in response_lower or "group" in response_lower:
            insights.append({
                "type": "work_style",
                "value": {"collaboration_preference": "collaborative"},
                "confidence": 0.6,
                "evidence": "Mentioned team or group work"
            })
            
            career_signals.append({
                "type": "interpersonal_skills",
                "strength": 0.7,
                "evidence": "Positive mention of team work",
                "metadata": {"source": "fallback_analysis"}
            })
        
        if "alone" in response_lower or "independent" in response_lower:
            insights.append({
                "type": "work_style", 
                "value": {"collaboration_preference": "individual"},
                "confidence": 0.6,
                "evidence": "Mentioned independent work preference"
            })
        
        if "analyze" in response_lower or "data" in response_lower or "logic" in response_lower:
            career_signals.append({
                "type": "analytical_thinking",
                "strength": 0.6,
                "evidence": "Mentioned analytical concepts",
                "metadata": {"source": "fallback_analysis"}
            })
        
        return {
            "insights": insights,
            "career_signals": career_signals,
            "sentiment": {
                "engagement_level": engagement_level,
                "authenticity": 0.5,
                "emotional_indicators": ["neutral"]
            },
            "next_questions": [
                {
                    "id": "follow_up_1",
                    "question": "Can you tell me more about what specifically interests you about this subject?",
                    "intent": "explore_deeper",
                    "follow_up_triggers": ["interest", "subject"]
                }
            ],
            "session_complete": False,
            "career_implications": {
                "immediate_insights": ["Basic preferences identified"],
                "esco_connections": [],
                "recommended_exploration": []
            }
        }
    
    @staticmethod
    async def generate_session_summary(logs: List[ConversationLog]) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of a conversation session.
        """
        if not client or not logs:
            return LLMCourseService._get_fallback_summary(logs)
        
        try:
            # Prepare conversation data
            conversation_data = []
            for log in logs:
                if log.response:
                    conversation_data.append({
                        "question": log.question_text,
                        "response": log.response,
                        "intent": log.question_intent,
                        "insights": log.extracted_insights
                    })
            
            prompt = f"""
            Create a comprehensive summary of this career counseling conversation session:

            **Conversation Data:**
            {json.dumps(conversation_data, indent=2)}

            **Generate Summary Including:**

            1. **Key Discoveries** - Most important insights about the student's:
               - Cognitive preferences and learning style
               - Work environment preferences 
               - Authentic interests vs external pressures
               - Natural strengths and aptitudes

            2. **Career Implications** - Based on the insights:
               - Specific career paths that align well
               - Industries or roles to explore
               - Skills to develop further
               - Potential mismatches to be aware of

            3. **Next Steps** - Actionable recommendations:
               - Immediate actions the student can take
               - Additional courses or experiences to consider
               - Skills to develop or strengthen
               - People to connect with or resources to explore

            4. **Confidence Assessment** - How reliable are these insights based on:
               - Depth and consistency of responses
               - Amount of evidence gathered
               - Clarity of preferences expressed

            **Return JSON format:**
            {{
                "session_overview": {{
                    "total_insights": 0,
                    "primary_focus_areas": [],
                    "confidence_score": 0.0
                }},
                "key_discoveries": [
                    {{
                        "category": "cognitive_style|work_preferences|interests|aptitudes",
                        "insight": "Detailed insight description",
                        "evidence": "Supporting evidence",
                        "confidence": 0.8
                    }}
                ],
                "career_recommendations": [
                    {{
                        "career_path": "Specific career or role",
                        "alignment_score": 0.8,
                        "reasoning": "Why this matches their profile",
                        "next_steps": ["action1", "action2"]
                    }}
                ],
                "development_areas": [
                    {{
                        "skill_area": "Specific skill or competency",
                        "current_level": "developing|intermediate|strong",
                        "importance": "high|medium|low",
                        "development_suggestions": ["suggestion1", "suggestion2"]
                    }}
                ],
                "next_steps": [
                    {{
                        "action": "Specific action to take",
                        "timeline": "immediate|short_term|long_term",
                        "priority": "high|medium|low",
                        "resources": ["resource1", "resource2"]
                    }}
                ]
            }}
            """
            
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career counselor creating comprehensive session summaries that provide actionable insights and recommendations for students' career development."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            summary = LLMCourseService._parse_summary_response(content)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating session summary: {str(e)}")
            return LLMCourseService._get_fallback_summary(logs)
    
    @staticmethod
    def _parse_summary_response(content: str) -> Dict[str, Any]:
        """
        Parse summary response from LLM.
        """
        try:
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                summary = json.loads(json_str)
                return summary
            else:
                return LLMCourseService._get_basic_summary_structure()
                
        except Exception as e:
            logger.error(f"Error parsing summary response: {str(e)}")
            return LLMCourseService._get_basic_summary_structure()
    
    @staticmethod
    def _get_fallback_summary(logs: List[ConversationLog]) -> Dict[str, Any]:
        """
        Generate fallback summary when LLM is unavailable.
        """
        summary = LLMCourseService._get_basic_summary_structure()
        
        # Basic analysis of conversation logs
        total_responses = len([log for log in logs if log.response])
        total_insights = sum(len(log.extracted_insights or []) for log in logs)
        
        summary["session_overview"] = {
            "total_insights": total_insights,
            "primary_focus_areas": ["general_exploration"],
            "confidence_score": min(0.8, total_responses * 0.2)
        }
        
        summary["key_discoveries"] = [
            {
                "category": "general",
                "insight": f"Completed {total_responses} conversation exchanges",
                "evidence": "Session participation",
                "confidence": 0.5
            }
        ]
        
        return summary
    
    @staticmethod
    def _get_basic_summary_structure() -> Dict[str, Any]:
        """
        Get basic summary structure.
        """
        return {
            "session_overview": {
                "total_insights": 0,
                "primary_focus_areas": [],
                "confidence_score": 0.0
            },
            "key_discoveries": [],
            "career_recommendations": [],
            "development_areas": [],
            "next_steps": []
        }