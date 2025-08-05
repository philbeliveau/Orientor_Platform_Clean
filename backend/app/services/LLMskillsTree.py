import os
import json
import logging
import time
import traceback
from typing import Dict, Any
import openai
from pydantic import ValidationError
from app.schemas.tree import TreeNode

# Configure logging
logger = logging.getLogger(__name__)

# In-memory cache to store generated trees
tree_cache = {}

class TreeService:
    def __init__(self):
        # Initialize OpenAI client
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY is not set in the environment variables")
            raise ValueError("OPENAI_API_KEY is not set in the environment variables")
            
        logger.info(f"TreeService initialized with OpenAI API key: {self.api_key[:5]}...{self.api_key[-5:] if len(self.api_key) > 10 else ''}")
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def _build_prompt(self, profile: str) -> str:
        """
        Builds the GPT-4o prompt for generating the skill tree based on the student profile.
        """
        logger.debug(f"Building prompt with profile (first 50 chars): {profile[:50]}...")
        
        prompt = f"""You are TREE-ENGINE, an LLM that outputs ONLY valid JSON representing a structured skill-to-career exploration map.  

Start from the student's initial profile:
{profile}

Structure:
1. Root Node: Initial Profile (type: "root", level: 0)
2. Level 1: 3 broad skill areas to develop (type: "skill", level: 1)
3. Level 2: 3 first outcomes (type: "outcome", level: 2)
4. Level 3: 6 refined skills (type: "skill", level: 3)
5. Level 4: 12 careers (type: "career", level: 4)

IMPORTANT: You MUST use EXACTLY these node types:
- "root" for the root node
- "skill" for all skill nodes (both level 1 and level 3)
- "outcome" for all outcome nodes (level 2)
- "career" for all career nodes (level 4)

DO NOT use types like "field" or "refined-skill" - they will cause validation errors!

Rules:
- **Temporal Coherence**: skills must precede fields, fields precede deeper skills, skills precede careers.
- **Spatial Coherence**: structure the tree top-down, no missing layers.
- **Actions**: every skill node must have 2–3 recommended actions to develop the skill.
- **Strict JSON only**. No explanation, no markdown, no commentary.
- Use "id", "label", "type", "level", "actions" (for skills), and "children" fields exactly.

Example format (partial):
{{
  "id": "root",
  "label": "Initial Profile",
  "type": "root",
  "level": 0,
  "children": [
    {{
      "id": "skill-1",
      "label": "First Skill",
      "type": "skill",
      "level": 1,
      "actions": ["Action 1", "Action 2", "Action 3"],
      "children": [
        {{
          "id": "outcome-1",
          "label": "First Outcome",
          "type": "outcome",
          "level": 2,
          "children": [
            {{
              "id": "skill-detail-1",
              "label": "Refined Skill 1",
              "type": "skill",
              "level": 3,
              "actions": ["Action 1", "Action 2"],
              "children": [
                {{
                  "id": "career-1",
                  "label": "Career 1",
                  "type": "career",
                  "level": 4
                }},
                {{
                  "id": "career-2",
                  "label": "Career 2",
                  "type": "career",
                  "level": 4
                }}
              ]
            }}
          ]
        }}
      ]
    }}
  ]
}}
"""
        logger.debug(f"Prompt built, length: {len(prompt)} characters")
        return prompt
    
    def _validate_tree(self, tree_data: Dict[str, Any]) -> TreeNode:
        """
        Validates the tree structure against the TreeNode schema.
        """
        try:
            logger.debug(f"Validating tree data: {str(tree_data)[:100]}...")
            return TreeNode(**tree_data)
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
                enhanced_message += "\nAllowed types are: 'root', 'skill', 'outcome', 'career'"
                
            # Log a sample of the tree data for debugging
            try:
                tree_sample = json.dumps(tree_data)[:500] + "..." if len(json.dumps(tree_data)) > 500 else json.dumps(tree_data)
                logger.error(f"Invalid tree data sample: {tree_sample}")
            except Exception as json_err:
                logger.error(f"Error while trying to log tree data: {str(json_err)}")
                
            raise ValueError(f"Generated tree does not match expected schema: {enhanced_message}")
    
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
                    
                # First level (level 1) should be skills
                if tree_data.get('type') == 'root' and child.get('type') not in ['skill']:
                    logger.warning(f"Fixing level 1 node type from '{child.get('type')}' to 'skill'")
                    child['type'] = 'skill'
                    child['level'] = 1
                    # Make sure it has actions
                    if 'actions' not in child or not child['actions']:
                        child['actions'] = ["Develop this skill", "Practice regularly"]
                
                # Fix known incorrect types
                if child.get('type') == 'field':
                    logger.warning(f"Fixing node type from 'field' to 'outcome'")
                    child['type'] = 'outcome'
                    child['level'] = 2
                elif child.get('type') == 'refined-skill':
                    logger.warning(f"Fixing node type from 'refined-skill' to 'skill'")
                    child['type'] = 'skill'
                    child['level'] = 3
                    # Make sure it has actions
                    if 'actions' not in child or not child['actions']:
                        child['actions'] = ["Develop this skill", "Practice regularly"]
                
                # Recursively process this child's children
                tree_data['children'][i] = self._preprocess_tree(child)
                
        return tree_data

    async def generate_tree(self, profile: str, user_id: str = None) -> TreeNode:
        """
        Generates a skill tree based on the student profile.
        Caches the tree by user_id if provided.
        """
        start_time = time.time()
        logger.info(f"Starting tree generation for {'user ' + user_id if user_id else 'anonymous user'}")
        
        # Check cache first (if user_id is provided)
        if user_id and user_id in tree_cache:
            logger.info(f"Using cached tree for user {user_id}")
            return tree_cache[user_id]
        
        # Build prompt
        logger.info("Building prompt")
        prompt = self._build_prompt(profile)
        
        # Generate the tree with the built prompt
        return await self._generate_tree_with_prompt(prompt, user_id)

    async def generate_custom_tree(self, profile: str, custom_prompt: str, user_id: str = None) -> TreeNode:
        """
        Generates a skill tree using a custom prompt.
        Caches the tree by user_id if provided.
        """
        start_time = time.time()
        logger.info(f"Starting custom tree generation for {'user ' + user_id if user_id else 'anonymous user'}")
        
        # Create a unique cache key for this custom prompt + profile combination
        cache_key = f"{user_id}_{hash(custom_prompt)}" if user_id else None
        
        # Check cache first (if cache_key is provided)
        if cache_key and cache_key in tree_cache:
            logger.info(f"Using cached custom tree for key {cache_key}")
            return tree_cache[cache_key]
        
        # Use the custom prompt with the profile
        logger.info("Using custom prompt for tree generation")
        final_prompt = custom_prompt.replace("{user_profile_input}", profile)
        
        # Generate the tree with the custom prompt
        tree = await self._generate_tree_with_prompt(final_prompt, cache_key)
        
        # If it's a skills tree, ensure the node types are valid
        tree_data = tree.dict()
        tree_data = self._preprocess_tree(tree_data)
        tree = self._validate_tree(tree_data)
        
        return tree
        
    async def _generate_tree_with_prompt(self, prompt: str, cache_key: str = None) -> TreeNode:
        """
        internal method to generate a tree using a given prompt.
        Abstracts the API call and validation logic for reuse.
        """
        start_time = time.time()
        
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
                        {"role": "system", "content": "You are TREE-ENGINE, generating structured skill trees in strict JSON format."},
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
                
                # Cache the result if cache_key is provided
                if cache_key:
                    logger.info(f"Caching tree with key {cache_key}")
                    tree_cache[cache_key] = tree
                
                total_duration = time.time() - start_time
                logger.info(f"Tree generation completed successfully in {total_duration:.2f} seconds")
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
                    raise ValueError(f"Generated tree has invalid structure: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt+1}/{max_retries}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} attempts due to unexpected error")
                    raise ValueError(f"Unexpected error during tree generation: {str(e)}")
        
        # This should not be reached, but added for safety
        logger.error("Tree generation failed: unexpected exit from retry loop")
        raise ValueError("Failed to generate tree: unexpected error") 