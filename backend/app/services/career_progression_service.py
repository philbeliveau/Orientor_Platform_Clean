"""
Career Progression Service - GraphSage Implementation

Implements recursive skill extraction using GraphSage for career progression trees.
Provides tier-based traversal with configurable depth and intelligent filtering.

Phases implemented:
- PHASE 1: GraphSage Progression Extraction with recursive traversal
- PHASE 2: Intelligent Skill Filtering with score-based ranking and deduplication
"""

import os
import logging
import torch
import numpy as np
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict, deque
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import traceback
from datetime import datetime

# Import existing services
from .competenceTree import CompetenceTreeService
from ..models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CareerProgressionService:
    """
    Career Progression Service using GraphSage for intelligent skill extraction.
    
    This service implements:
    1. Recursive skill extraction from occupation nodes
    2. Tier-based traversal with configurable depth
    3. GraphSage score-based ranking and filtering
    4. User profile personalization
    5. Cross-tier deduplication
    """
    
    def __init__(self):
        """Initialize the career progression service."""
        self.competence_service = CompetenceTreeService()
        self.graph_service = None
        self._initialize_graph_service()
        
    def _initialize_graph_service(self):
        """Initialize the graph traversal service for GraphSage operations."""
        try:
            import sys
            backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            competence_tree_dev_path = os.path.join(backend_path, "dev", "competenceTree_dev")
            
            if competence_tree_dev_path not in sys.path:
                sys.path.insert(0, competence_tree_dev_path)
                
            from graph_traversal_service import GraphTraversalService
            self.graph_service = GraphTraversalService()
            logger.info("GraphTraversalService initialized successfully for career progression")
            
        except Exception as e:
            logger.warning(f"Failed to initialize GraphTraversalService: {str(e)}")
            self.graph_service = None
    
    def extract_career_progression(self, 
                                 occupation_id: str, 
                                 depth: int = 3,
                                 max_skills_per_tier: int = 5,
                                 min_similarity: float = 0.4,
                                 user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        PHASE 1: Extract career progression skills using recursive GraphSage traversal.
        
        Args:
            occupation_id: ESCO occupation ID to start from
            depth: Maximum traversal depth (X parameter)
            max_skills_per_tier: Maximum skills per tier (default 5)
            min_similarity: Minimum GraphSage similarity threshold
            user_id: Optional user ID for personalization
            
        Returns:
            Dict containing tiered skill progression with GraphSage scores
        """
        try:
            logger.info(f"Starting career progression extraction for occupation {occupation_id}")
            logger.info(f"Parameters: depth={depth}, max_per_tier={max_skills_per_tier}, min_sim={min_similarity}")
            
            # PHASE 1: Recursive skill extraction with tier-based traversal
            progression_data = self._extract_tiered_skills(
                occupation_id=occupation_id,
                max_depth=depth,
                max_skills_per_tier=max_skills_per_tier,
                min_similarity=min_similarity
            )
            
            if not progression_data.get("tiers"):
                logger.warning(f"No progression data found for occupation {occupation_id}")
                return {
                    "occupation_id": occupation_id,
                    "tiers": [],
                    "total_skills": 0,
                    "depth_achieved": 0,
                    "metadata": {"error": "No skills found"}
                }
            
            # PHASE 2: Apply intelligent filtering and deduplication
            filtered_progression = self._apply_intelligent_filtering(
                progression_data=progression_data,
                user_id=user_id
            )
            
            # Add progression metadata
            filtered_progression.update({
                "occupation_id": occupation_id,
                "extraction_params": {
                    "depth": depth,
                    "max_skills_per_tier": max_skills_per_tier,
                    "min_similarity": min_similarity
                },
                "generated_at": datetime.now().isoformat(),
                "personalized": user_id is not None
            })
            
            logger.info(f"Career progression extracted: {len(filtered_progression.get('tiers', []))} tiers, "
                       f"{filtered_progression.get('total_skills', 0)} total skills")
            
            return filtered_progression
            
        except Exception as e:
            logger.error(f"Error extracting career progression: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "occupation_id": occupation_id,
                "tiers": [],
                "total_skills": 0,
                "error": str(e)
            }
    
    def _extract_tiered_skills(self, 
                              occupation_id: str, 
                              max_depth: int,
                              max_skills_per_tier: int,
                              min_similarity: float) -> Dict[str, Any]:
        """
        PHASE 1 Implementation: Extract skills in tiers using GraphSage recursive traversal.
        
        Each tier represents a level of career progression:
        - Tier 1: Core foundational skills
        - Tier 2: Intermediate development skills
        - Tier 3+: Advanced specialization skills
        
        Args:
            occupation_id: Starting occupation
            max_depth: Maximum traversal depth
            max_skills_per_tier: Skills per tier limit
            min_similarity: GraphSage similarity threshold
            
        Returns:
            Dict with tiered skill structure
        """
        try:
            # Initialize progression structure
            tiers = []
            all_extracted_skills = set()
            current_nodes = [occupation_id]
            
            # Check if graph service is available
            if not self.graph_service:
                logger.warning("Graph service not available, using fallback method")
                return self._fallback_skill_extraction(occupation_id, max_depth)
            
            # Tier-based recursive extraction
            for tier_level in range(max_depth):
                logger.info(f"Extracting tier {tier_level + 1} from {len(current_nodes)} nodes")
                
                tier_skills = []
                next_tier_nodes = []
                
                # Process each node in current tier
                for node_id in current_nodes:
                    # Get related skills using GraphSage traversal
                    related_skills = self._get_graphsage_related_skills(
                        node_id=node_id,
                        max_results=max_skills_per_tier * 2,  # Get more for filtering
                        min_similarity=min_similarity,
                        exclude_skills=all_extracted_skills
                    )
                    
                    # Add to tier with GraphSage scores
                    for skill_data in related_skills:
                        if len(tier_skills) < max_skills_per_tier:
                            if skill_data["id"] not in all_extracted_skills:
                                tier_skills.append({
                                    "id": skill_data["id"],
                                    "label": skill_data["label"],
                                    "graphsage_score": skill_data["similarity"],
                                    "source_node": node_id,
                                    "tier": tier_level + 1,
                                    "skill_type": skill_data.get("type", "technical"),
                                    "metadata": skill_data.get("metadata", {})
                                })
                                all_extracted_skills.add(skill_data["id"])
                                next_tier_nodes.append(skill_data["id"])
                
                # Sort tier by GraphSage score (descending)
                tier_skills.sort(key=lambda x: x["graphsage_score"], reverse=True)
                
                if tier_skills:
                    tiers.append({
                        "tier_number": tier_level + 1,
                        "skills": tier_skills[:max_skills_per_tier],
                        "average_score": np.mean([s["graphsage_score"] for s in tier_skills]),
                        "skill_count": len(tier_skills)
                    })
                    
                    # Prepare nodes for next tier (limit to prevent explosion)
                    current_nodes = next_tier_nodes[:max_skills_per_tier]
                else:
                    # No more skills found, stop traversal
                    break
            
            return {
                "tiers": tiers,
                "total_skills": len(all_extracted_skills),
                "depth_achieved": len(tiers),
                "extraction_method": "graphsage_recursive"
            }
            
        except Exception as e:
            logger.error(f"Error in tiered skill extraction: {str(e)}")
            return {"tiers": [], "total_skills": 0, "error": str(e)}
    
    def _get_graphsage_related_skills(self, 
                                     node_id: str, 
                                     max_results: int,
                                     min_similarity: float,
                                     exclude_skills: Set[str]) -> List[Dict[str, Any]]:
        """
        Get related skills using GraphSage similarity computation.
        
        Args:
            node_id: Source node ID
            max_results: Maximum results to return
            min_similarity: Minimum similarity threshold
            exclude_skills: Skills to exclude from results
            
        Returns:
            List of skill dictionaries with GraphSage scores
        """
        try:
            related_skills = []
            
            # Use graph service to find neighbors
            if self.graph_service and hasattr(self.graph_service, 'graph'):
                neighbors = list(self.graph_service.graph.neighbors(node_id))
                
                # Filter for skill nodes only
                skill_neighbors = []
                for neighbor_id in neighbors:
                    neighbor_metadata = self.graph_service.node_metadata.get(neighbor_id, {})
                    if (neighbor_metadata.get("type") == "skill" and 
                        neighbor_id not in exclude_skills):
                        skill_neighbors.append(neighbor_id)
                
                # Compute GraphSage similarities
                for skill_id in skill_neighbors[:max_results * 2]:  # Get more for filtering
                    similarity = self.graph_service.compute_node_similarity(node_id, skill_id)
                    
                    if similarity >= min_similarity:
                        skill_metadata = self.graph_service.node_metadata.get(skill_id, {})
                        skill_label = skill_metadata.get("preferredLabel", 
                                                        skill_metadata.get("label", skill_id))
                        
                        related_skills.append({
                            "id": skill_id,
                            "label": skill_label,
                            "similarity": similarity,
                            "type": self._classify_skill_type(skill_label, skill_metadata),
                            "metadata": skill_metadata
                        })
                
                # Sort by similarity and return top results
                related_skills.sort(key=lambda x: x["similarity"], reverse=True)
                return related_skills[:max_results]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting GraphSage related skills: {str(e)}")
            return []
    
    def _classify_skill_type(self, skill_label: str, metadata: Dict[str, Any]) -> str:
        """
        Classify skill type for PHASE 2 filtering.
        
        Args:
            skill_label: Skill label text
            metadata: Skill metadata
            
        Returns:
            Skill type classification
        """
        skill_lower = skill_label.lower()
        
        # Technical skills indicators
        technical_keywords = [
            'programming', 'software', 'database', 'algorithm', 'coding',
            'python', 'java', 'sql', 'api', 'framework', 'technology',
            'system', 'network', 'cloud', 'ai', 'machine learning'
        ]
        
        # Soft skills indicators
        soft_keywords = [
            'communication', 'leadership', 'teamwork', 'collaboration',
            'management', 'presentation', 'negotiation', 'creativity',
            'problem solving', 'critical thinking', 'adaptability'
        ]
        
        # Certification indicators
        cert_keywords = [
            'certification', 'license', 'accreditation', 'qualification',
            'certificate', 'diploma', 'degree', 'training'
        ]
        
        # Check skill type based on keywords
        for keyword in technical_keywords:
            if keyword in skill_lower:
                return "technical"
        
        for keyword in soft_keywords:
            if keyword in skill_lower:
                return "soft"
        
        for keyword in cert_keywords:
            if keyword in skill_lower:
                return "certification"
        
        # Default classification
        return "general"
    
    def _apply_intelligent_filtering(self, 
                                   progression_data: Dict[str, Any],
                                   user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        PHASE 2 Implementation: Apply intelligent filtering and deduplication.
        
        Features:
        1. GraphSage score-based ranking within tiers
        2. Cross-tier deduplication logic
        3. Skill type filtering (technical/soft/certifications)
        4. User profile personalization
        
        Args:
            progression_data: Raw progression data from Phase 1
            user_id: Optional user ID for personalization
            
        Returns:
            Filtered and personalized progression data
        """
        try:
            tiers = progression_data.get("tiers", [])
            if not tiers:
                return progression_data
            
            # Step 1: Cross-tier deduplication
            deduplicated_tiers = self._deduplicate_across_tiers(tiers)
            
            # Step 2: Skill type balancing
            balanced_tiers = self._balance_skill_types(deduplicated_tiers)
            
            # Step 3: User personalization (if user_id provided)
            if user_id:
                personalized_tiers = self._personalize_for_user(balanced_tiers, user_id)
            else:
                personalized_tiers = balanced_tiers
            
            # Step 4: Final GraphSage score optimization
            optimized_tiers = self._optimize_graphsage_scores(personalized_tiers)
            
            # Calculate final statistics
            total_skills = sum(len(tier.get("skills", [])) for tier in optimized_tiers)
            
            return {
                "tiers": optimized_tiers,
                "total_skills": total_skills,
                "depth_achieved": len(optimized_tiers),
                "filtering_applied": {
                    "deduplication": True,
                    "skill_type_balancing": True,
                    "user_personalization": user_id is not None,
                    "graphsage_optimization": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in intelligent filtering: {str(e)}")
            return progression_data
    
    def _deduplicate_across_tiers(self, tiers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate skills across tiers, keeping highest-scoring instance.
        
        Args:
            tiers: List of tier dictionaries
            
        Returns:
            Deduplicated tiers
        """
        seen_skills = {}
        deduplicated_tiers = []
        
        for tier in tiers:
            tier_skills = tier.get("skills", [])
            filtered_skills = []
            
            for skill in tier_skills:
                skill_id = skill["id"]
                current_score = skill["graphsage_score"]
                
                if skill_id not in seen_skills:
                    # First occurrence - add to seen and include
                    seen_skills[skill_id] = {
                        "tier": tier["tier_number"],
                        "score": current_score
                    }
                    filtered_skills.append(skill)
                else:
                    # Duplicate found - keep higher scoring version
                    if current_score > seen_skills[skill_id]["score"]:
                        # Remove from previous tier and add to current
                        prev_tier_num = seen_skills[skill_id]["tier"]
                        self._remove_skill_from_tier(deduplicated_tiers, skill_id, prev_tier_num)
                        
                        seen_skills[skill_id] = {
                            "tier": tier["tier_number"],
                            "score": current_score
                        }
                        filtered_skills.append(skill)
            
            # Update tier with filtered skills
            updated_tier = tier.copy()
            updated_tier["skills"] = filtered_skills
            updated_tier["skill_count"] = len(filtered_skills)
            if filtered_skills:
                updated_tier["average_score"] = np.mean([s["graphsage_score"] for s in filtered_skills])
            
            deduplicated_tiers.append(updated_tier)
        
        return deduplicated_tiers
    
    def _remove_skill_from_tier(self, tiers: List[Dict], skill_id: str, tier_number: int):
        """Remove a skill from a specific tier."""
        for tier in tiers:
            if tier["tier_number"] == tier_number:
                tier["skills"] = [s for s in tier["skills"] if s["id"] != skill_id]
                break
    
    def _balance_skill_types(self, tiers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Balance skill types within each tier for diverse progression.
        
        Args:
            tiers: Deduplicated tiers
            
        Returns:
            Balanced tiers with diverse skill types
        """
        balanced_tiers = []
        
        for tier in tiers:
            skills = tier.get("skills", [])
            
            # Group skills by type
            skill_groups = defaultdict(list)
            for skill in skills:
                skill_type = skill.get("skill_type", "general")
                skill_groups[skill_type].append(skill)
            
            # Sort each group by GraphSage score
            for skill_type in skill_groups:
                skill_groups[skill_type].sort(key=lambda x: x["graphsage_score"], reverse=True)
            
            # Select balanced representation
            balanced_skills = []
            target_per_type = max(1, len(skills) // len(skill_groups)) if skill_groups else 0
            
            # Ensure at least one skill of each type if available
            for skill_type, type_skills in skill_groups.items():
                balanced_skills.extend(type_skills[:target_per_type])
            
            # Fill remaining slots with highest-scoring skills
            remaining_slots = len(skills) - len(balanced_skills)
            if remaining_slots > 0:
                all_remaining = [s for s in skills if s not in balanced_skills]
                all_remaining.sort(key=lambda x: x["graphsage_score"], reverse=True)
                balanced_skills.extend(all_remaining[:remaining_slots])
            
            # Sort final skills by GraphSage score
            balanced_skills.sort(key=lambda x: x["graphsage_score"], reverse=True)
            
            # Update tier
            balanced_tier = tier.copy()
            balanced_tier["skills"] = balanced_skills
            balanced_tier["skill_type_distribution"] = {
                skill_type: len([s for s in balanced_skills if s.get("skill_type") == skill_type])
                for skill_type in skill_groups.keys()
            }
            
            balanced_tiers.append(balanced_tier)
        
        return balanced_tiers
    
    def _personalize_for_user(self, tiers: List[Dict[str, Any]], user_id: int) -> List[Dict[str, Any]]:
        """
        Personalize progression based on user profile and existing skills.
        
        Args:
            tiers: Balanced tiers
            user_id: User ID for personalization
            
        Returns:
            Personalized tiers
        """
        try:
            # This would integrate with user profile data
            # For now, implement basic personalization logic
            
            personalized_tiers = []
            
            for tier in tiers:
                skills = tier.get("skills", [])
                
                # Apply personalization scoring boost
                for skill in skills:
                    # Boost technical skills for technical users, etc.
                    # This is a placeholder for more sophisticated personalization
                    skill_type = skill.get("skill_type", "general")
                    
                    if skill_type == "technical":
                        skill["personalization_boost"] = 0.1
                    elif skill_type == "soft":
                        skill["personalization_boost"] = 0.05
                    else:
                        skill["personalization_boost"] = 0.0
                    
                    # Apply boost to GraphSage score
                    skill["personalized_score"] = (
                        skill["graphsage_score"] + skill["personalization_boost"]
                    )
                
                # Re-sort by personalized score
                skills.sort(key=lambda x: x.get("personalized_score", x["graphsage_score"]), 
                           reverse=True)
                
                personalized_tier = tier.copy()
                personalized_tier["skills"] = skills
                personalized_tier["personalized"] = True
                
                personalized_tiers.append(personalized_tier)
            
            return personalized_tiers
            
        except Exception as e:
            logger.error(f"Error in user personalization: {str(e)}")
            return tiers
    
    def _optimize_graphsage_scores(self, tiers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Final optimization of GraphSage scores within each tier.
        
        Args:
            tiers: Personalized tiers
            
        Returns:
            Optimized tiers
        """
        optimized_tiers = []
        
        for tier in tiers:
            skills = tier.get("skills", [])
            
            if skills:
                # Normalize scores within tier
                scores = [s.get("personalized_score", s["graphsage_score"]) for s in skills]
                if scores:
                    max_score = max(scores)
                    min_score = min(scores)
                    score_range = max_score - min_score if max_score > min_score else 1
                    
                    for skill in skills:
                        raw_score = skill.get("personalized_score", skill["graphsage_score"])
                        skill["normalized_score"] = (raw_score - min_score) / score_range
                        skill["final_score"] = raw_score
                
                # Final sort by optimized scores
                skills.sort(key=lambda x: x.get("final_score", x["graphsage_score"]), 
                           reverse=True)
            
            optimized_tier = tier.copy()
            optimized_tier["skills"] = skills
            optimized_tier["optimization_applied"] = True
            
            optimized_tiers.append(optimized_tier)
        
        return optimized_tiers
    
    def _fallback_skill_extraction(self, occupation_id: str, max_depth: int) -> Dict[str, Any]:
        """
        Fallback method when GraphSage service is not available.
        
        Args:
            occupation_id: Starting occupation
            max_depth: Maximum depth
            
        Returns:
            Basic skill extraction result
        """
        logger.warning("Using fallback skill extraction method")
        
        # Use Pinecone to find related skills
        try:
            if self.competence_service.index:
                results = self.competence_service.index.query(
                    id=occupation_id,
                    top_k=15,
                    filter={"type": {"$eq": "skill"}},
                    include_metadata=True
                )
                
                skills = []
                for i, match in enumerate(results.matches):
                    skill_label = match.metadata.get("preferredLabel", match.id)
                    skills.append({
                        "id": match.id,
                        "label": skill_label,
                        "graphsage_score": 1.0 - match.score,  # Convert distance to similarity
                        "source_node": occupation_id,
                        "tier": 1,
                        "skill_type": "general",
                        "metadata": match.metadata
                    })
                
                return {
                    "tiers": [{
                        "tier_number": 1,
                        "skills": skills[:5],
                        "skill_count": len(skills[:5]),
                        "average_score": np.mean([s["graphsage_score"] for s in skills[:5]]) if skills else 0
                    }],
                    "total_skills": len(skills[:5]),
                    "depth_achieved": 1,
                    "extraction_method": "fallback_pinecone"
                }
        
        except Exception as e:
            logger.error(f"Fallback extraction failed: {str(e)}")
        
        return {"tiers": [], "total_skills": 0, "extraction_method": "failed"}
