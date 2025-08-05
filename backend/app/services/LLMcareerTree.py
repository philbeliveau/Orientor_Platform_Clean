import os
import json
import logging
import time
import traceback
from typing import Dict, Any
import openai
from pydantic import ValidationError
from app.schemas.career_tree import CareerTreeNode
from ..core.cache import cache

# Configure logging
logger = logging.getLogger(__name__)

# In-memory cache to store generated career trees (kept for backward compatibility)
career_tree_cache = {}

class CareerTreeService:
    def __init__(self):
        # Initialize OpenAI client
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY is not set in the environment variables")
            raise ValueError("OPENAI_API_KEY is not set in the environment variables")
            
        logger.info(f"CareerTreeService initialized with OpenAI API key: {self.api_key[:5]}...{self.api_key[-5:] if len(self.api_key) > 10 else ''}")
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def _build_prompt(self, profile: str) -> str:
        """
        Builds the GPT-4o prompt for generating the career tree based on the student profile.
        """
        logger.debug(f"Building prompt with profile (first 50 chars): {profile[:50]}...")
         
        prompt = (
    "You are CAREER-ENGINE, a structured LLM trained to output strict JSON trees representing Career Exploration Maps.\n\n"
    "Your task is to design a career growth tree that inspires students to explore broad career paths based on their interests, "
    "without locking them into specific jobs yet.\n\n"
    "---\n\n"
    "# INPUT\n"
    "Start from this user profile:\n"
    f'"{profile}"\n\n'
    "---\n\n"
    "# TREE STRUCTURE\n"
    "1. Root Node (\"root\" type)\n"
    "- Describes the student's self-assessment or broad interest\n\n"
    "2. Domain Nodes (\"domain\" type)\n"
    "- Represent wide career fields (Tech, Arts, Healthcare, Environment, Business, etc.)\n"
    "- Should feel aspirational but grounded\n\n"
    "3. Family Nodes (\"family\" type)\n"
    "- Represent career families inside each domain (e.g., Tech ➝ Programming, Cybersecurity, AI Research)\n\n"
    "4. (Optional) Bridge Nodes (\"domain\" type)\n"
    "- Show intersections (e.g., \"Tech for Healthcare\" ➝ Health Informatics)\n\n"
    "No specific job titles are needed. No skills. No technical stacks.\n\n"
    "---\n\n"
    "# PRINCIPLES\n"
    "✅ Emotional pull first\n"
    "✅ Breadth > Depth\n"
    "✅ Exploration\n"
    "✅ Keep simple: Max 2 layers deep\n\n"
    "---\n\n"
    "# OUTPUT FORMAT (Strict JSON)\n"
    "{\n"
    '  "id": "root",\n'
    '  "label": "Curious about technology and solving problems",\n'
    '  "type": "root",\n'
    '  "level": 0,\n'
    '  "children": [\n'
    '    {\n'
    '      "id": "domain-tech",\n'
    '      "label": "Technology",\n'
    '      "type": "domain",\n'
    '      "level": 1,\n'
    '      "children": [\n'
    '        {\n'
    '          "id": "family-programming",\n'
    '          "label": "Programming & Software Development",\n'
    '          "type": "family",\n'
    '          "level": 2\n'
    '        }\n'
    '      ]\n'
    '    }\n'
    '  ]\n'
    "}\n\n"
    "---\n\n"
    "# SPECIAL NOTES\n"
    "- Minimum: 4–5 Domains\n"
    "- Each Domain: 2–3 Families\n"
    "- Allow interdisciplinary families if natural\n"
    "- Max total nodes: ~15–20\n\n"
    "Return only valid JSON. No explanations or extra text."
)

        logger.debug(f"Prompt built, length: {len(prompt)} characters")
        return prompt
    
    def _validate_tree(self, tree_data: Dict[str, Any]) -> CareerTreeNode:
        """
        Validates the tree structure against the CareerTreeNode schema.
        """
        try:
            logger.debug(f"Validating tree data: {str(tree_data)[:100]}...")
            return CareerTreeNode(**tree_data)
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            
            # Enhance error message with more information
            validation_errors = e.errors()
            error_type_counts = {}
            
            invalid_types = []
            for error in validation_errors:
                if error["type"] == "literal_error" and "type" in error["loc"][-1]:
                    invalid_type = error.get("input")
                    if invalid_type and invalid_type not in invalid_types:
                        invalid_types.append(invalid_type)
                
                error_type = error["type"]
                error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
            
            enhanced_message = str(e)
            if invalid_types:
                enhanced_message += f"\n\nInvalid node types found: {', '.join(invalid_types)}"
                enhanced_message += "\nAllowed types are: 'root', 'domain', 'family', 'skill'"
                
            # Log a sample of the tree data for debugging
            try:
                tree_sample = json.dumps(tree_data)[:500] + "..." if len(json.dumps(tree_data)) > 500 else json.dumps(tree_data)
                logger.error(f"Invalid tree data sample: {tree_sample}")
            except Exception as json_err:
                logger.error(f"Error while trying to log tree data: {str(json_err)}")
                
            raise ValueError(f"Generated career tree does not match expected schema: {enhanced_message}")
    
    def _preprocess_tree(self, tree_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocesses the tree data to fix common issues before validation.
        """
        if not isinstance(tree_data, dict):
            logger.error(f"Tree data is not a dictionary: {type(tree_data)}")
            return tree_data
            
        # Fix root node type if needed
        if tree_data.get('type') != 'root' and tree_data.get('level') == 0:
            logger.warning(f"Fixing root node type from '{tree_data.get('type')}' to 'root'")
            tree_data['type'] = 'root'
            
        # Process children recursively
        if 'children' in tree_data and isinstance(tree_data['children'], list):
            for i, child in enumerate(tree_data['children']):
                if not isinstance(child, dict):
                    continue
                    
                # Level 1 should be domains
                if tree_data.get('type') == 'root' and child.get('type') not in ['domain']:
                    logger.warning(f"Fixing level 1 node type from '{child.get('type')}' to 'domain'")
                    child['type'] = 'domain'
                    child['level'] = 1
                
                # Level 2 should be families
                if tree_data.get('type') == 'domain' and child.get('type') not in ['family']:
                    logger.warning(f"Fixing level 2 node type from '{child.get('type')}' to 'family'")
                    child['type'] = 'family'
                    child['level'] = 2
                
                # Level 3 should be skills with actions
                if tree_data.get('type') == 'family' and child.get('type') not in ['skill']:
                    logger.warning(f"Fixing level 3 node type from '{child.get('type')}' to 'skill'")
                    child['type'] = 'skill'
                    child['level'] = 3
                    # Make sure it has actions
                    if 'actions' not in child or not child['actions']:
                        child['actions'] = ["Learn fundamentals", "Practice regularly"]
                
                # Recursively process this child's children
                tree_data['children'][i] = self._preprocess_tree(child)
                
        return tree_data

    async def generate_career_tree(self, profile: str, user_id: str = None) -> CareerTreeNode:
        """
        Generates a career tree based on the student profile.
        Caches the tree by user_id if provided.
        """
        start_time = time.time()
        logger.info(f"Starting career tree generation for {'user ' + user_id if user_id else 'anonymous user'}")
        
        # Check Redis cache first (if user_id is provided)
        if user_id:
            # Try Redis cache
            cached_tree = await cache.get(user_id, namespace="career_trees")
            if cached_tree:
                logger.info(f"Using Redis cached career tree for user {user_id}")
                try:
                    # Reconstruct the CareerTreeNode from cached data
                    return CareerTreeNode(**cached_tree)
                except Exception as e:
                    logger.warning(f"Failed to reconstruct tree from cache: {str(e)}")
            
            # Fallback to in-memory cache
            if user_id in career_tree_cache:
                logger.info(f"Using in-memory cached career tree for user {user_id}")
                return career_tree_cache[user_id]
        
        # Build prompt
        logger.info("Building prompt")
        prompt = self._build_prompt(profile)
        
        # Call OpenAI API
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt+1}/{max_retries}: Calling OpenAI API")
                
                # Log if API key looks invalid
                if not self.api_key or len(self.api_key) < 10:
                    logger.error(f"API key appears invalid: {self.api_key}")
                
                api_call_start = time.time()
                response = self.client.chat.completions.create(
                    model="gpt-4o", #gpt-3.5-turbo", #gpt-4o
                    messages=[
                        {"role": "system", "content": "You are TREE-ENGINE-Career, generating structured career trees in strict JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2500,
                    response_format={"type": "json_object"}
                )
                api_call_duration = time.time() - api_call_start
                logger.info(f"OpenAI API call completed in {api_call_duration:.2f} seconds")
                
                # Parse and validate response
                logger.info("Parsing OpenAI response")
                content = response.choices[0].message.content
                logger.debug(f"API response content: {content[:100]}...")
                
                logger.info("Parsing JSON from response")
                try:
                    tree_data = json.loads(content)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {str(e)}")
                    logger.error(f"Response content sample: {content[:200]}...")
                    raise
                
                # Preprocess the tree to fix common issues
                logger.info("Preprocessing tree to fix common issues")
                tree_data = self._preprocess_tree(tree_data)
                
                # Validate against schema
                logger.info("Validating tree structure")
                tree = self._validate_tree(tree_data)
                
                # Cache the result if user_id is provided
                if user_id:
                    logger.info(f"Caching career tree for user {user_id}")
                    # Cache to Redis (24 hour TTL)
                    try:
                        await cache.set(
                            user_id, 
                            tree.dict(), 
                            ttl=86400,  # 24 hours
                            namespace="career_trees"
                        )
                        logger.info(f"Successfully cached to Redis for user {user_id}")
                    except Exception as e:
                        logger.warning(f"Failed to cache to Redis: {str(e)}")
                    
                    # Also cache in memory as fallback
                    career_tree_cache[user_id] = tree
                
                total_duration = time.time() - start_time
                logger.info(f"Career tree generation completed successfully in {total_duration:.2f} seconds")
                return tree
                
            except openai.APIError as e:
                logger.error(f"OpenAI API error on attempt {attempt+1}/{max_retries}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} attempts due to OpenAI API error")
                    raise ValueError(f"OpenAI API error: {str(e)}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error on attempt {attempt+1}/{max_retries}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} attempts due to JSON parsing error")
                    raise ValueError(f"Failed to parse JSON response: {str(e)}")
            except ValidationError as e:
                logger.error(f"Schema validation error on attempt {attempt+1}/{max_retries}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} attempts due to validation error")
                    raise ValueError(f"Generated career tree has invalid structure: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt+1}/{max_retries}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} attempts due to unexpected error")
                    raise ValueError(f"Unexpected error during career tree generation: {str(e)}")
        
        # This should not be reached, but added for safety
        logger.error("Career tree generation failed: unexpected exit from retry loop")
        raise ValueError("Failed to generate career tree: unexpected error") 