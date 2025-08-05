import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text

# Configuration du logging
logger = logging.getLogger(__name__)

class HexacoScoringService:
    """
    Service de calcul des scores HEXACO-PI-R.
    Gère le calcul des scores des facettes et des domaines avec gestion des reverse_keyed items.
    """
    
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "hexaco_facet_mapping.json"
        self._config_cache = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration HEXACO depuis le fichier JSON."""
        if self._config_cache is None:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
                logger.info("Configuration de scoring HEXACO chargée avec succès")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de la configuration de scoring: {e}")
                raise
        return self._config_cache
    
    def _get_facet_items_mapping(self, questions: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[int]]]:
        """
        Crée un mapping des facettes vers leurs items et items inversés.
        
        Args:
            questions: Liste des questions avec leurs métadonnées
            
        Returns:
            Dict avec structure: {facet_name: {"items": [1,2,3], "reverse_items": [4,5]}}
        """
        facet_mapping = {}
        
        for question in questions:
            facet = question["facet"]
            item_id = question["item_id"]
            is_reverse = question["reverse_keyed"]
            
            if facet not in facet_mapping:
                facet_mapping[facet] = {"items": [], "reverse_items": []}
            
            if is_reverse:
                facet_mapping[facet]["reverse_items"].append(item_id)
            else:
                facet_mapping[facet]["items"].append(item_id)
        
        return facet_mapping
    
    def calculate_facet_score(self, responses: Dict[int, int], items: List[int], 
                            reverse_items: List[int]) -> float:
        """
        Calcule le score d'une facette HEXACO.
        
        Args:
            responses: Dictionnaire des réponses {item_id: response_value}
            items: Liste des IDs d'items normaux pour cette facette
            reverse_items: Liste des IDs d'items à inverser
            
        Returns:
            Score moyen de la facette (1.0-5.0)
        """
        total = 0
        count = 0
        
        # Traiter les items normaux
        for item_id in items:
            if item_id in responses:
                total += responses[item_id]
                count += 1
        
        # Traiter les items inversés (score = 6 - response pour échelle 1-5)
        for item_id in reverse_items:
            if item_id in responses:
                inverted_score = 6 - responses[item_id]
                total += inverted_score
                count += 1
        
        return total / count if count > 0 else 0.0
    
    def calculate_domain_score(self, facet_scores: Dict[str, float], domain_facets: List[str]) -> float:
        """
        Calcule le score d'un domaine HEXACO à partir des scores de facettes.
        
        Args:
            facet_scores: Dictionnaire des scores de facettes
            domain_facets: Liste des facettes composant le domaine
            
        Returns:
            Score moyen du domaine (1.0-5.0)
        """
        total = sum(facet_scores.get(facet, 0.0) for facet in domain_facets)
        return total / len(domain_facets) if domain_facets else 0.0
    
    def calculate_hexaco_scores(self, responses: Dict[int, int], 
                              questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcule tous les scores HEXACO (facettes et domaines).
        
        Args:
            responses: Dictionnaire des réponses {item_id: response_value}
            questions: Liste des questions avec leurs métadonnées
            
        Returns:
            Dictionnaire avec les scores des domaines et facettes
        """
        try:
            config = self._load_config()
            domains_config = config["domains"]
            
            # Créer le mapping facettes -> items
            facet_mapping = self._get_facet_items_mapping(questions)
            
            # Calculer les scores des facettes
            facet_scores = {}
            for facet_name, item_mapping in facet_mapping.items():
                score = self.calculate_facet_score(
                    responses, 
                    item_mapping["items"], 
                    item_mapping["reverse_items"]
                )
                facet_scores[facet_name] = round(score, 2)
            
            # Calculer les scores des domaines
            domain_scores = {}
            for domain_name, domain_config in domains_config.items():
                domain_facets = domain_config["facets"]
                score = self.calculate_domain_score(facet_scores, domain_facets)
                domain_scores[domain_name] = round(score, 2)
            
            # Calculer les percentiles (simulation - dans un vrai système, 
            # cela serait basé sur des données normatives)
            percentiles = self._calculate_percentiles(domain_scores, facet_scores)
            
            # Calculer les indices de fiabilité (simulation)
            reliability = self._calculate_reliability(domain_scores, facet_scores)
            
            result = {
                "domains": domain_scores,
                "facets": facet_scores,
                "percentiles": percentiles,
                "reliability": reliability,
                "total_responses": len(responses),
                "completion_rate": len(responses) / len(questions) if questions else 0
            }
            
            logger.info(f"Scores HEXACO calculés: {len(domain_scores)} domaines, {len(facet_scores)} facettes")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des scores HEXACO: {e}")
            raise
    
    def _calculate_percentiles(self, domain_scores: Dict[str, float], 
                             facet_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Calcule les percentiles approximatifs (simulation basée sur distribution normale).
        Dans un système de production, cela devrait être basé sur des données normatives réelles.
        """
        percentiles = {}
        
        # Simulation simple: convertir les scores 1-5 en percentiles approximatifs
        for name, score in {**domain_scores, **facet_scores}.items():
            # Conversion approximative: score de 1-5 vers percentile 5-95
            percentile = ((score - 1) / 4) * 90 + 5
            percentiles[name] = round(min(95, max(5, percentile)), 1)
        
        return percentiles
    
    def _calculate_reliability(self, domain_scores: Dict[str, float], 
                             facet_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Calcule les indices de fiabilité approximatifs.
        Dans un système de production, cela devrait être basé sur des analyses psychométriques réelles.
        """
        reliability = {}
        
        # Simulation: fiabilité basée sur la cohérence des scores
        for name, score in {**domain_scores, **facet_scores}.items():
            # Simulation simple: fiabilité plus élevée pour les scores modérés
            distance_from_center = abs(score - 3.0)
            reliability_score = 0.95 - (distance_from_center * 0.1)
            reliability[name] = round(max(0.7, min(0.95, reliability_score)), 2)
        
        return reliability
    
    def save_hexaco_profile(self, db: Session, user_id: int, session_id: str,
                           scores: Dict[str, Any], assessment_version: str,
                           language: str = "fr", narrative_description: str = None) -> bool:
        """
        Sauvegarde le profil HEXACO calculé dans la base de données.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            session_id: ID de la session d'évaluation
            scores: Scores calculés
            assessment_version: Version de l'évaluation
            language: Langue de l'évaluation
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            # Récupérer l'assessment_id
            assessment_query = text("""
                SELECT id FROM personality_assessments 
                WHERE session_id = :session_id
            """)
            
            assessment_result = db.execute(assessment_query, {"session_id": session_id}).fetchone()
            if not assessment_result:
                logger.error(f"Assessment non trouvé pour session_id: {session_id}")
                return False
            
            assessment_id = assessment_result[0]
            
            # Vérifier si un profil existe déjà
            check_query = text("""
                SELECT id FROM personality_profiles 
                WHERE user_id = :user_id AND profile_type = 'hexaco' 
                AND assessment_version = :assessment_version
            """)
            
            existing_profile = db.execute(check_query, {
                "user_id": user_id,
                "assessment_version": assessment_version
            }).fetchone()
            
            if existing_profile:
                # Mettre à jour le profil existant
                update_query = text("""
                    UPDATE personality_profiles
                    SET assessment_id = :assessment_id,
                        scores = :scores,
                        percentile_ranks = :percentiles,
                        reliability_estimates = :reliability,
                        language = :language,
                        narrative_description = :narrative_description,
                        computed_at = NOW(),
                        updated_at = NOW()
                    WHERE id = :profile_id
                """)
                
                db.execute(update_query, {
                    "profile_id": existing_profile[0],
                    "assessment_id": assessment_id,
                    "scores": json.dumps(scores),
                    "percentiles": json.dumps(scores.get("percentiles", {})),
                    "reliability": json.dumps(scores.get("reliability", {})),
                    "language": language,
                    "narrative_description": narrative_description
                })
            else:
                # Créer un nouveau profil
                insert_query = text("""
                    INSERT INTO personality_profiles (
                        user_id, assessment_id, profile_type, language,
                        scores, percentile_ranks, reliability_estimates,
                        assessment_version, narrative_description
                    ) VALUES (
                        :user_id, :assessment_id, 'hexaco', :language,
                        :scores, :percentiles, :reliability,
                        :assessment_version, :narrative_description
                    )
                """)
                
                db.execute(insert_query, {
                    "user_id": user_id,
                    "assessment_id": assessment_id,
                    "language": language,
                    "scores": json.dumps(scores),
                    "percentiles": json.dumps(scores.get("percentiles", {})),
                    "reliability": json.dumps(scores.get("reliability", {})),
                    "assessment_version": assessment_version,
                    "narrative_description": narrative_description
                })
            
            db.commit()
            logger.info(f"Profil HEXACO sauvegardé pour utilisateur {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur lors de la sauvegarde du profil HEXACO: {e}")
            return False
    
    def get_user_hexaco_profile(self, db: Session, user_id: int, 
                               assessment_version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Récupère le profil HEXACO d'un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            assessment_version: Version spécifique (optionnel)
            
        Returns:
            Profil HEXACO ou None si non trouvé
        """
        try:
            if assessment_version:
                query = text("""
                    SELECT scores, percentile_ranks, reliability_estimates, 
                           narrative_description, assessment_version, language,
                           computed_at
                    FROM personality_profiles 
                    WHERE user_id = :user_id AND profile_type = 'hexaco'
                    AND assessment_version = :assessment_version
                    ORDER BY computed_at DESC
                    LIMIT 1
                """)
                params = {"user_id": user_id, "assessment_version": assessment_version}
            else:
                query = text("""
                    SELECT scores, percentile_ranks, reliability_estimates, 
                           narrative_description, assessment_version, language,
                           computed_at
                    FROM personality_profiles 
                    WHERE user_id = :user_id AND profile_type = 'hexaco'
                    ORDER BY computed_at DESC
                    LIMIT 1
                """)
                params = {"user_id": user_id}
            
            result = db.execute(query, params).fetchone()
            if not result:
                return None
            
            # Gérer le cas où les données sont déjà des dict (JSONB) ou des chaînes JSON
            def safe_json_loads(data):
                if isinstance(data, dict):
                    return data
                elif data:
                    return json.loads(data)
                else:
                    return {}
            
            profile = {
                "scores": safe_json_loads(result.scores),
                "percentiles": safe_json_loads(result.percentile_ranks),
                "reliability": safe_json_loads(result.reliability_estimates),
                "narrative_description": result.narrative_description,
                "assessment_version": result.assessment_version,
                "language": result.language,
                "computed_at": result.computed_at.isoformat() if result.computed_at else None
            }
            
            logger.info(f"Profil HEXACO récupéré pour utilisateur {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du profil HEXACO: {e}")
            return None