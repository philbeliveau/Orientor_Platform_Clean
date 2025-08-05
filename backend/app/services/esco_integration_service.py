import logging
from typing import Dict, List, Any, Optional
import asyncio
from ..models.course import CareerSignal

logger = logging.getLogger(__name__)

class ESCOIntegrationService:
    """
    Service for integrating course analysis insights with ESCO skill categories and career paths.
    """
    
    # ESCO skill category mappings for career signals
    SIGNAL_TO_ESCO_MAPPING = {
        "analytical_thinking": {
            "esco_categories": ["S1.1.1", "S1.2.1", "S1.3.1"],  # Thinking skills, analytical competencies
            "skill_groups": ["analytical skills", "critical thinking", "problem analysis"],
            "related_occupations": ["data analyst", "research scientist", "financial analyst"]
        },
        "creative_problem_solving": {
            "esco_categories": ["S1.1.2", "S1.4.1", "S3.1.1"],  # Creative thinking, innovation
            "skill_groups": ["creativity", "innovation", "design thinking"],
            "related_occupations": ["product designer", "marketing specialist", "architect"]
        },
        "interpersonal_skills": {
            "esco_categories": ["S2.1.1", "S2.2.1", "S2.3.1"],  # Social skills, communication
            "skill_groups": ["communication", "teamwork", "relationship building"],
            "related_occupations": ["human resources specialist", "teacher", "sales representative"]
        },
        "leadership_potential": {
            "esco_categories": ["S2.4.1", "S2.5.1", "S3.2.1"],  # Leadership, management
            "skill_groups": ["leadership", "team management", "strategic planning"],
            "related_occupations": ["project manager", "team leader", "executive"]
        },
        "attention_to_detail": {
            "esco_categories": ["S1.5.1", "S3.3.1", "S4.1.1"],  # Precision, quality control
            "skill_groups": ["quality assurance", "precision work", "documentation"],
            "related_occupations": ["quality controller", "accountant", "laboratory technician"]
        },
        "stress_tolerance": {
            "esco_categories": ["S2.6.1", "S3.4.1"],  # Resilience, adaptability
            "skill_groups": ["stress management", "adaptability", "resilience"],
            "related_occupations": ["emergency responder", "healthcare worker", "consultant"]
        }
    }
    
    # Subject category to ESCO occupation group mappings
    SUBJECT_TO_OCCUPATION_MAPPING = {
        "STEM": {
            "occupation_groups": ["21", "31", "35"],  # Science/engineering professionals, technicians
            "primary_skills": ["S1.1.1", "S1.2.1", "S4.2.1"],  # Analytical, technical skills
            "career_clusters": ["Information Technology", "Engineering", "Scientific Research"]
        },
        "business": {
            "occupation_groups": ["12", "24", "33"],  # Business managers, business professionals
            "primary_skills": ["S2.4.1", "S3.2.1", "S1.3.1"],  # Leadership, strategic thinking
            "career_clusters": ["Business Operations", "Finance", "Management"]
        },
        "humanities": {
            "occupation_groups": ["23", "26", "34"],  # Teaching, legal, cultural professionals
            "primary_skills": ["S2.1.1", "S1.1.2", "S2.3.1"],  # Communication, critical thinking
            "career_clusters": ["Education", "Legal Services", "Arts and Culture"]
        },
        "arts": {
            "occupation_groups": ["26", "34"],  # Arts, cultural professionals
            "primary_skills": ["S1.4.1", "S3.1.1", "S2.1.1"],  # Creativity, artistic skills
            "career_clusters": ["Arts and Entertainment", "Design", "Media"]
        }
    }
    
    @staticmethod
    async def generate_career_paths(
        profile_summary: Dict[str, Any], 
        signals: List[CareerSignal]
    ) -> Dict[str, Any]:
        """
        Generate personalized ESCO career paths based on psychological profile and signals.
        """
        try:
            career_paths = {
                "recommended_paths": [],
                "skill_development_areas": [],
                "occupation_clusters": [],
                "esco_tree_entry_points": []
            }
            
            # Analyze career signals for ESCO mapping
            signal_analysis = ESCOIntegrationService._analyze_signals_for_esco(signals)
            
            # Generate recommended career paths
            recommended_paths = await ESCOIntegrationService._generate_recommended_paths(
                profile_summary, signal_analysis
            )
            career_paths["recommended_paths"] = recommended_paths
            
            # Identify skill development areas
            skill_areas = ESCOIntegrationService._identify_skill_development_areas(
                profile_summary, signals
            )
            career_paths["skill_development_areas"] = skill_areas
            
            # Map to ESCO occupation clusters
            occupation_clusters = ESCOIntegrationService._map_to_occupation_clusters(
                signal_analysis
            )
            career_paths["occupation_clusters"] = occupation_clusters
            
            # Generate ESCO tree entry points
            entry_points = ESCOIntegrationService._generate_tree_entry_points(
                signal_analysis, profile_summary
            )
            career_paths["esco_tree_entry_points"] = entry_points
            
            return career_paths
            
        except Exception as e:
            logger.error(f"Error generating career paths: {str(e)}")
            return ESCOIntegrationService._get_fallback_career_paths()
    
    @staticmethod
    def _analyze_signals_for_esco(signals: List[CareerSignal]) -> Dict[str, Any]:
        """
        Analyze career signals and map to ESCO categories.
        """
        signal_analysis = {
            "primary_signals": [],
            "esco_categories": set(),
            "skill_groups": set(),
            "occupation_hints": set(),
            "strength_distribution": {}
        }
        
        # Group signals by type and calculate average strengths
        signal_groups = {}
        for signal in signals:
            signal_type = signal.signal_type
            if signal_type not in signal_groups:
                signal_groups[signal_type] = []
            signal_groups[signal_type].append(signal.strength_score)
        
        # Calculate averages and map to ESCO
        for signal_type, strengths in signal_groups.items():
            avg_strength = sum(strengths) / len(strengths)
            signal_analysis["strength_distribution"][signal_type] = avg_strength
            
            # Map to ESCO if strength is significant
            if avg_strength >= 0.6 and signal_type in ESCOIntegrationService.SIGNAL_TO_ESCO_MAPPING:
                esco_mapping = ESCOIntegrationService.SIGNAL_TO_ESCO_MAPPING[signal_type]
                
                signal_analysis["primary_signals"].append({
                    "type": signal_type,
                    "strength": avg_strength,
                    "esco_mapping": esco_mapping
                })
                
                signal_analysis["esco_categories"].update(esco_mapping["esco_categories"])
                signal_analysis["skill_groups"].update(esco_mapping["skill_groups"])
                signal_analysis["occupation_hints"].update(esco_mapping["related_occupations"])
        
        # Convert sets to lists for JSON serialization
        signal_analysis["esco_categories"] = list(signal_analysis["esco_categories"])
        signal_analysis["skill_groups"] = list(signal_analysis["skill_groups"])
        signal_analysis["occupation_hints"] = list(signal_analysis["occupation_hints"])
        
        return signal_analysis
    
    @staticmethod
    async def _generate_recommended_paths(
        profile_summary: Dict[str, Any],
        signal_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate specific career path recommendations.
        """
        recommended_paths = []
        
        # Get primary signals (strongest career indicators)
        primary_signals = signal_analysis.get("primary_signals", [])
        primary_signals.sort(key=lambda x: x["strength"], reverse=True)
        
        # Generate paths based on top signals
        for i, signal in enumerate(primary_signals[:3]):  # Top 3 signals
            signal_type = signal["type"]
            strength = signal["strength"]
            esco_mapping = signal["esco_mapping"]
            
            # Create career path recommendation
            path = {
                "path_id": f"path_{i+1}",
                "primary_signal": signal_type,
                "alignment_score": strength,
                "occupation_examples": esco_mapping["related_occupations"][:3],
                "skill_requirements": esco_mapping["skill_groups"],
                "esco_categories": esco_mapping["esco_categories"],
                "development_priority": ESCOIntegrationService._calculate_development_priority(
                    signal, profile_summary
                ),
                "career_cluster": ESCOIntegrationService._determine_career_cluster(signal_type),
                "next_steps": ESCOIntegrationService._generate_next_steps(signal_type, strength)
            }
            
            recommended_paths.append(path)
        
        # Add interdisciplinary paths if multiple strong signals
        if len(primary_signals) >= 2:
            interdisciplinary_path = ESCOIntegrationService._create_interdisciplinary_path(
                primary_signals[:2]
            )
            recommended_paths.append(interdisciplinary_path)
        
        return recommended_paths
    
    @staticmethod
    def _identify_skill_development_areas(
        profile_summary: Dict[str, Any],
        signals: List[CareerSignal]
    ) -> List[Dict[str, Any]]:
        """
        Identify areas for skill development based on gaps and growth opportunities.
        """
        development_areas = []
        
        # Analyze signal strengths to identify gaps
        signal_strengths = {}
        for signal in signals:
            signal_type = signal.signal_type
            if signal_type not in signal_strengths:
                signal_strengths[signal_type] = []
            signal_strengths[signal_type].append(signal.strength_score)
        
        # Calculate averages
        avg_strengths = {}
        for signal_type, strengths in signal_strengths.items():
            avg_strengths[signal_type] = sum(strengths) / len(strengths)
        
        # Identify development opportunities
        all_signal_types = list(ESCOIntegrationService.SIGNAL_TO_ESCO_MAPPING.keys())
        
        for signal_type in all_signal_types:
            current_strength = avg_strengths.get(signal_type, 0.0)
            
            # Areas with room for improvement (< 0.7) but some foundation (> 0.3)
            if 0.3 <= current_strength < 0.7:
                esco_mapping = ESCOIntegrationService.SIGNAL_TO_ESCO_MAPPING[signal_type]
                
                development_areas.append({
                    "skill_area": signal_type,
                    "current_level": current_strength,
                    "potential_impact": ESCOIntegrationService._calculate_impact_potential(
                        signal_type, profile_summary
                    ),
                    "esco_categories": esco_mapping["esco_categories"],
                    "development_methods": ESCOIntegrationService._suggest_development_methods(
                        signal_type
                    ),
                    "related_occupations": esco_mapping["related_occupations"],
                    "priority": "high" if current_strength > 0.5 else "medium"
                })
        
        # Sort by potential impact and current level
        development_areas.sort(
            key=lambda x: (x["potential_impact"], x["current_level"]), 
            reverse=True
        )
        
        return development_areas[:5]  # Return top 5 development areas
    
    @staticmethod
    def _map_to_occupation_clusters(signal_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Map signals to ESCO occupation clusters.
        """
        clusters = []
        
        # Analyze signal patterns to determine occupation clusters
        primary_signals = signal_analysis.get("primary_signals", [])
        
        # Group signals by related occupation clusters
        cluster_scores = {}
        
        for signal in primary_signals:
            signal_type = signal["type"]
            strength = signal["strength"]
            
            # Determine which clusters this signal supports
            related_clusters = ESCOIntegrationService._get_related_clusters(signal_type)
            
            for cluster in related_clusters:
                if cluster not in cluster_scores:
                    cluster_scores[cluster] = []
                cluster_scores[cluster].append(strength)
        
        # Calculate cluster alignment scores
        for cluster, scores in cluster_scores.items():
            avg_score = sum(scores) / len(scores)
            
            clusters.append({
                "cluster_name": cluster,
                "alignment_score": avg_score,
                "supporting_signals": len(scores),
                "esco_occupation_group": ESCOIntegrationService._get_esco_group_for_cluster(cluster),
                "sample_occupations": ESCOIntegrationService._get_sample_occupations(cluster),
                "entry_requirements": ESCOIntegrationService._get_entry_requirements(cluster)
            })
        
        # Sort by alignment score
        clusters.sort(key=lambda x: x["alignment_score"], reverse=True)
        
        return clusters[:5]  # Return top 5 clusters
    
    @staticmethod
    def _generate_tree_entry_points(
        signal_analysis: Dict[str, Any],
        profile_summary: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized ESCO tree entry points for exploration.
        """
        entry_points = []
        
        primary_signals = signal_analysis.get("primary_signals", [])
        
        for signal in primary_signals[:3]:  # Top 3 signals
            signal_type = signal["type"]
            strength = signal["strength"]
            esco_mapping = signal["esco_mapping"]
            
            # Create entry point for each ESCO category
            for category in esco_mapping["esco_categories"][:2]:  # Top 2 categories per signal
                entry_point = {
                    "entry_point_id": f"{signal_type}_{category}",
                    "esco_category": category,
                    "signal_type": signal_type,
                    "alignment_strength": strength,
                    "exploration_path": ESCOIntegrationService._create_exploration_path(
                        category, signal_type
                    ),
                    "skill_assessment_areas": esco_mapping["skill_groups"][:3],
                    "recommended_first_steps": ESCOIntegrationService._get_first_steps(
                        category, signal_type
                    ),
                    "depth_level": "beginner" if strength < 0.7 else "intermediate"
                }
                
                entry_points.append(entry_point)
        
        return entry_points
    
    @staticmethod
    async def generate_tree_paths(signals: List[CareerSignal]) -> List[Dict[str, Any]]:
        """
        Generate specific ESCO tree traversal paths based on career signals.
        """
        try:
            signal_analysis = ESCOIntegrationService._analyze_signals_for_esco(signals)
            
            tree_paths = []
            
            # Generate paths for each primary signal
            for signal in signal_analysis.get("primary_signals", []):
                signal_type = signal["type"]
                strength = signal["strength"]
                esco_mapping = signal["esco_mapping"]
                
                # Create traversal path
                path = {
                    "path_name": f"{signal_type.replace('_', ' ').title()} Career Path",
                    "starting_signal": signal_type,
                    "confidence_score": strength,
                    "traversal_steps": [
                        {
                            "step": 1,
                            "node_type": "skill_group",
                            "nodes": esco_mapping["skill_groups"][:3],
                            "description": f"Core skills for {signal_type}"
                        },
                        {
                            "step": 2,
                            "node_type": "occupation_examples",
                            "nodes": esco_mapping["related_occupations"][:3],
                            "description": "Related career opportunities"
                        },
                        {
                            "step": 3,
                            "node_type": "esco_categories",
                            "nodes": esco_mapping["esco_categories"],
                            "description": "ESCO skill categories to explore"
                        }
                    ],
                    "alternative_branches": ESCOIntegrationService._generate_alternative_branches(
                        signal_type, esco_mapping
                    ),
                    "personalization_factors": {
                        "signal_strength": strength,
                        "development_potential": ESCOIntegrationService._assess_development_potential(signal_type),
                        "market_demand": ESCOIntegrationService._assess_market_demand(signal_type)
                    }
                }
                
                tree_paths.append(path)
            
            return tree_paths
            
        except Exception as e:
            logger.error(f"Error generating tree paths: {str(e)}")
            return []
    
    @staticmethod
    def _calculate_development_priority(
        signal: Dict[str, Any], 
        profile_summary: Dict[str, Any]
    ) -> str:
        """
        Calculate development priority for a career signal.
        """
        strength = signal["strength"]
        signal_type = signal["type"]
        
        # High priority if strength is good but can be improved
        if 0.6 <= strength < 0.8:
            return "high"
        # Medium priority if strength is developing
        elif 0.4 <= strength < 0.6:
            return "medium"
        # Low priority if very strong or very weak
        else:
            return "low"
    
    @staticmethod
    def _determine_career_cluster(signal_type: str) -> str:
        """
        Determine career cluster for a signal type.
        """
        cluster_mapping = {
            "analytical_thinking": "Data & Analysis",
            "creative_problem_solving": "Innovation & Design",
            "interpersonal_skills": "Communication & Relations",
            "leadership_potential": "Management & Leadership",
            "attention_to_detail": "Quality & Precision",
            "stress_tolerance": "High-Pressure Environments"
        }
        
        return cluster_mapping.get(signal_type, "General")
    
    @staticmethod
    def _generate_next_steps(signal_type: str, strength: float) -> List[str]:
        """
        Generate next steps for developing a specific signal.
        """
        base_steps = {
            "analytical_thinking": [
                "Practice data analysis with real datasets",
                "Take courses in statistics or research methods",
                "Work on logic puzzles and analytical challenges"
            ],
            "creative_problem_solving": [
                "Engage in design thinking workshops",
                "Practice brainstorming techniques",
                "Work on creative projects outside your comfort zone"
            ],
            "interpersonal_skills": [
                "Join group projects or team activities",
                "Practice active listening techniques",
                "Develop presentation and communication skills"
            ],
            "leadership_potential": [
                "Take on leadership roles in projects",
                "Study leadership theories and practices",
                "Seek mentorship opportunities"
            ],
            "attention_to_detail": [
                "Practice quality control exercises",
                "Develop systematic checking procedures",
                "Work on projects requiring precision"
            ],
            "stress_tolerance": [
                "Practice stress management techniques",
                "Take on challenging but manageable projects",
                "Develop resilience through difficult situations"
            ]
        }
        
        steps = base_steps.get(signal_type, ["Seek relevant learning opportunities"])
        
        # Modify based on current strength
        if strength < 0.5:
            steps = [f"Start with basics: {step.lower()}" for step in steps]
        elif strength > 0.7:
            steps = [f"Advanced development: {step}" for step in steps]
        
        return steps[:3]  # Return top 3 steps
    
    @staticmethod
    def _create_interdisciplinary_path(primary_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create an interdisciplinary career path combining multiple signals.
        """
        signal1, signal2 = primary_signals[0], primary_signals[1]
        
        combined_path = {
            "path_id": "interdisciplinary",
            "primary_signals": [signal1["type"], signal2["type"]],
            "alignment_score": (signal1["strength"] + signal2["strength"]) / 2,
            "occupation_examples": ESCOIntegrationService._find_interdisciplinary_occupations(
                signal1["type"], signal2["type"]
            ),
            "skill_requirements": list(set(
                signal1["esco_mapping"]["skill_groups"] + 
                signal2["esco_mapping"]["skill_groups"]
            ))[:5],
            "esco_categories": list(set(
                signal1["esco_mapping"]["esco_categories"] + 
                signal2["esco_mapping"]["esco_categories"]
            )),
            "development_priority": "high",
            "career_cluster": "Interdisciplinary",
            "next_steps": [
                "Explore roles that combine both skill areas",
                "Develop expertise in connecting different domains",
                "Look for interdisciplinary programs or projects"
            ]
        }
        
        return combined_path
    
    @staticmethod
    def _find_interdisciplinary_occupations(signal1: str, signal2: str) -> List[str]:
        """
        Find occupations that combine two different signals.
        """
        combinations = {
            ("analytical_thinking", "creative_problem_solving"): [
                "UX researcher", "product manager", "innovation consultant"
            ],
            ("analytical_thinking", "interpersonal_skills"): [
                "business analyst", "consultant", "project coordinator"
            ],
            ("creative_problem_solving", "leadership_potential"): [
                "creative director", "innovation manager", "startup founder"
            ],
            ("interpersonal_skills", "attention_to_detail"): [
                "project manager", "quality assurance manager", "client success manager"
            ]
        }
        
        # Try both orderings
        key1 = (signal1, signal2)
        key2 = (signal2, signal1)
        
        return combinations.get(key1, combinations.get(key2, ["interdisciplinary specialist"]))
    
    @staticmethod
    def _calculate_impact_potential(signal_type: str, profile_summary: Dict[str, Any]) -> float:
        """
        Calculate the potential impact of developing a specific signal.
        """
        # This would typically involve market analysis and personal fit assessment
        # For now, return a simplified calculation
        
        base_impact = {
            "analytical_thinking": 0.9,      # High demand skill
            "creative_problem_solving": 0.8, # Growing importance
            "interpersonal_skills": 0.85,   # Always valuable
            "leadership_potential": 0.9,     # High career impact
            "attention_to_detail": 0.7,     # Specialized value
            "stress_tolerance": 0.75        # Situational value
        }
        
        return base_impact.get(signal_type, 0.6)
    
    @staticmethod
    def _suggest_development_methods(signal_type: str) -> List[str]:
        """
        Suggest methods for developing a specific signal.
        """
        methods = {
            "analytical_thinking": [
                "Online courses in data analysis",
                "Practice with analytical software",
                "Join research projects"
            ],
            "creative_problem_solving": [
                "Design thinking workshops",
                "Creative writing or art classes",
                "Innovation challenges"
            ],
            "interpersonal_skills": [
                "Communication workshops",
                "Team sports or group activities",
                "Volunteer in community organizations"
            ],
            "leadership_potential": [
                "Leadership development programs",
                "Mentoring others",
                "Take on project leadership roles"
            ],
            "attention_to_detail": [
                "Quality control training",
                "Precision-based hobbies",
                "Documentation and process improvement"
            ],
            "stress_tolerance": [
                "Stress management courses",
                "Mindfulness and meditation",
                "Gradual exposure to challenging situations"
            ]
        }
        
        return methods.get(signal_type, ["Seek relevant training opportunities"])
    
    @staticmethod
    def _get_fallback_career_paths() -> Dict[str, Any]:
        """
        Get fallback career paths when ESCO integration fails.
        """
        return {
            "recommended_paths": [
                {
                    "path_id": "general_exploration",
                    "primary_signal": "general",
                    "alignment_score": 0.5,
                    "occupation_examples": ["generalist", "coordinator", "analyst"],
                    "skill_requirements": ["communication", "problem solving", "adaptability"],
                    "development_priority": "medium",
                    "career_cluster": "General",
                    "next_steps": ["Explore various career options", "Take career assessments", "Gain diverse experiences"]
                }
            ],
            "skill_development_areas": [],
            "occupation_clusters": [],
            "esco_tree_entry_points": []
        }
    
    # Helper methods for internal calculations
    @staticmethod
    def _get_related_clusters(signal_type: str) -> List[str]:
        """Get career clusters related to a signal type."""
        return [ESCOIntegrationService._determine_career_cluster(signal_type)]
    
    @staticmethod
    def _get_esco_group_for_cluster(cluster: str) -> str:
        """Get ESCO occupation group for a cluster."""
        return f"Group_{cluster.replace(' ', '_')}"
    
    @staticmethod
    def _get_sample_occupations(cluster: str) -> List[str]:
        """Get sample occupations for a cluster."""
        return [f"{cluster} specialist", f"{cluster} coordinator", f"{cluster} manager"]
    
    @staticmethod
    def _get_entry_requirements(cluster: str) -> List[str]:
        """Get entry requirements for a cluster."""
        return ["Relevant education", "Basic skills", "Entry-level experience"]
    
    @staticmethod
    def _create_exploration_path(category: str, signal_type: str) -> List[str]:
        """Create exploration path for ESCO category."""
        return [f"Explore {category}", f"Assess {signal_type} skills", "Identify opportunities"]
    
    @staticmethod
    def _get_first_steps(category: str, signal_type: str) -> List[str]:
        """Get first steps for exploring a category."""
        return [f"Research {category}", f"Practice {signal_type}", "Connect with professionals"]
    
    @staticmethod
    def _generate_alternative_branches(signal_type: str, esco_mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alternative exploration branches."""
        return [
            {
                "branch_name": f"Alternative {signal_type} path",
                "focus_area": "specialized application",
                "occupations": esco_mapping["related_occupations"][1:3]
            }
        ]
    
    @staticmethod
    def _assess_development_potential(signal_type: str) -> float:
        """Assess development potential for a signal."""
        return 0.7  # Default moderate potential
    
    @staticmethod
    def _assess_market_demand(signal_type: str) -> float:
        """Assess market demand for a signal."""
        demand_scores = {
            "analytical_thinking": 0.9,
            "creative_problem_solving": 0.8,
            "interpersonal_skills": 0.85,
            "leadership_potential": 0.8,
            "attention_to_detail": 0.7,
            "stress_tolerance": 0.6
        }
        return demand_scores.get(signal_type, 0.6)