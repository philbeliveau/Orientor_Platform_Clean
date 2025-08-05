import os
import json
import csv
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import uuid4
import uuid

# Configuration du logging
logger = logging.getLogger(__name__)

class HexacoService:
    """
    Service principal pour la gestion des tests HEXACO-PI-R.
    Gère le chargement des données CSV, les métadonnées et l'orchestration des tests.
    """
    
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "hexaco_facet_mapping.json"
        self.data_path = Path(__file__).parent.parent.parent.parent / "data_n_notebook" / "data"
        self._config_cache = None
        self._questions_cache = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration HEXACO depuis le fichier JSON."""
        if self._config_cache is None:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
                logger.info("Configuration HEXACO chargée avec succès")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de la configuration HEXACO: {e}")
                raise
        return self._config_cache
    
    def get_available_versions(self) -> Dict[str, Any]:
        """Retourne les versions disponibles du test HEXACO."""
        config = self._load_config()
        return config.get("versions", {})
    
    def get_available_languages(self) -> Dict[str, Any]:
        """Retourne les langues disponibles pour le test HEXACO."""
        config = self._load_config()
        return config.get("languages", {})
    
    def get_domains_config(self) -> Dict[str, Any]:
        """Retourne la configuration des domaines HEXACO."""
        config = self._load_config()
        return config.get("domains", {})
    
    def get_version_metadata(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Retourne les métadonnées pour une version spécifique."""
        versions = self.get_available_versions()
        return versions.get(version_id)
    
    def _load_questions_from_csv(self, csv_filename: str) -> List[Dict[str, Any]]:
        """Charge les questions depuis un fichier CSV."""
        if csv_filename in self._questions_cache:
            return self._questions_cache[csv_filename]
        
        csv_path = self.data_path / csv_filename
        questions = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    question = {
                        "item_id": int(row["item_id"]),
                        "item_text": row["item_text"],
                        "response_min": int(row["response_min"]),
                        "response_max": int(row["response_max"]),
                        "version": row["version"],
                        "language": row["language"],
                        "reverse_keyed": row["reverse_keyed"].lower() == "true",
                        "facet": row["facet"]
                    }
                    questions.append(question)
            
            self._questions_cache[csv_filename] = questions
            logger.info(f"Questions chargées depuis {csv_filename}: {len(questions)} items")
            return questions
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier CSV {csv_filename}: {e}")
            raise
    
    def get_questions_for_version(self, version_id: str) -> List[Dict[str, Any]]:
        """Retourne les questions pour une version spécifique du test."""
        version_metadata = self.get_version_metadata(version_id)
        if not version_metadata:
            raise ValueError(f"Version non trouvée: {version_id}")
        
        csv_filename = version_metadata["csv_file"]
        return self._load_questions_from_csv(csv_filename)
    
    def create_assessment_session(self, db: Session, user_id: int, version_id: str) -> str:
        """Crée une nouvelle session d'évaluation HEXACO."""
        try:
            version_metadata = self.get_version_metadata(version_id)
            if not version_metadata:
                raise ValueError(f"Version non trouvée: {version_id}")
            
            session_id = str(uuid4())
            
            # Insérer dans personality_assessments
            insert_query = text("""
                INSERT INTO personality_assessments (
                    user_id, assessment_type, assessment_version, session_id,
                    status, total_items, completed_items, metadata
                ) VALUES (
                    :user_id, 'hexaco', :assessment_version, :session_id,
                    'in_progress', :total_items, 0, :metadata
                ) RETURNING id
            """)
            
            metadata = {
                "language": version_metadata["language"],
                "estimated_duration": version_metadata["estimated_duration"],
                "title": version_metadata["title"]
            }
            
            result = db.execute(insert_query, {
                "user_id": user_id,
                "assessment_version": version_id,
                "session_id": session_id,
                "total_items": version_metadata["item_count"],
                "metadata": json.dumps(metadata)
            })
            
            assessment_id = result.fetchone()[0]
            db.commit()
            
            logger.info(f"Session d'évaluation HEXACO créée: {session_id} pour l'utilisateur {user_id}")
            return session_id
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur lors de la création de la session d'évaluation: {e}")
            raise
    
    def save_response(self, db: Session, session_id: str, item_id: int, response_value: int, 
                     response_time_ms: Optional[int] = None) -> bool:
        """Sauvegarde une réponse individuelle."""
        try:
            # Récupérer l'assessment_id depuis session_id
            assessment_query = text("""
                SELECT id, status FROM personality_assessments
                WHERE session_id = :session_id
            """)
            
            assessment_result = db.execute(assessment_query, {"session_id": session_id}).fetchone()
            if not assessment_result:
                logger.warning(f"Session non trouvée: {session_id}")
                return False
            
            # Si la session est déjà complétée, ignorer silencieusement la réponse
            if assessment_result.status == 'completed':
                logger.info(f"Session déjà complétée, réponse ignorée: {session_id}")
                return True  # Retourner True pour éviter les erreurs côté frontend
            
            assessment_id = assessment_result.id
            
            # Vérifier si une réponse existe déjà pour cet item
            check_query = text("""
                SELECT id FROM personality_responses 
                WHERE assessment_id = :assessment_id AND item_id = :item_id
            """)
            
            existing_response = db.execute(check_query, {
                "assessment_id": assessment_id,
                "item_id": str(item_id)
            }).fetchone()
            
            if existing_response:
                # Mettre à jour la réponse existante
                update_query = text("""
                    UPDATE personality_responses 
                    SET response_value = :response_value, response_time_ms = :response_time_ms,
                        revision_count = revision_count + 1, updated_at = NOW()
                    WHERE id = :response_id
                """)
                
                db.execute(update_query, {
                    "response_id": existing_response[0],
                    "response_value": json.dumps({"value": response_value}),
                    "response_time_ms": response_time_ms
                })
            else:
                # Insérer une nouvelle réponse
                insert_query = text("""
                    INSERT INTO personality_responses (
                        assessment_id, item_id, item_type, response_value, response_time_ms
                    ) VALUES (
                        :assessment_id, :item_id, 'likert', :response_value, :response_time_ms
                    )
                """)
                
                db.execute(insert_query, {
                    "assessment_id": assessment_id,
                    "item_id": str(item_id),
                    "response_value": json.dumps({"value": response_value}),
                    "response_time_ms": response_time_ms
                })
            
            # Mettre à jour le compteur de questions complétées
            update_progress_query = text("""
                UPDATE personality_assessments 
                SET completed_items = (
                    SELECT COUNT(DISTINCT item_id) 
                    FROM personality_responses 
                    WHERE assessment_id = :assessment_id
                ), updated_at = NOW()
                WHERE id = :assessment_id
            """)
            
            db.execute(update_progress_query, {"assessment_id": assessment_id})
            db.commit()
            
            logger.info(f"Réponse sauvegardée: session={session_id}, item={item_id}, value={response_value}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur lors de la sauvegarde de la réponse: {e}")
            return False
    
    def get_assessment_progress(self, db: Session, session_id: str) -> Optional[Dict[str, Any]]:
        """Retourne le progrès d'une évaluation."""
        try:
            query = text("""
                SELECT total_items, completed_items, status, assessment_version
                FROM personality_assessments 
                WHERE session_id = :session_id
            """)
            
            result = db.execute(query, {"session_id": session_id}).fetchone()
            if not result:
                return None
            
            return {
                "total_items": result.total_items,
                "completed_items": result.completed_items,
                "progress_percentage": (result.completed_items / result.total_items * 100) if result.total_items > 0 else 0,
                "status": result.status,
                "assessment_version": result.assessment_version
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du progrès: {e}")
            return None
    
    def complete_assessment(self, db: Session, session_id: str) -> bool:
        """Marque une évaluation comme complétée."""
        try:
            update_query = text("""
                UPDATE personality_assessments 
                SET status = 'completed', completed_at = NOW(), updated_at = NOW()
                WHERE session_id = :session_id AND status = 'in_progress'
            """)
            
            result = db.execute(update_query, {"session_id": session_id})
            db.commit()
            
            if result.rowcount > 0:
                logger.info(f"Évaluation complétée: {session_id}")
                return True
            else:
                logger.warning(f"Aucune évaluation en cours trouvée pour: {session_id}")
                return False
                
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur lors de la finalisation de l'évaluation: {e}")
            return False
    
    def get_user_responses(self, db: Session, session_id: str) -> Dict[int, int]:
        """Récupère toutes les réponses d'un utilisateur pour une session."""
        try:
            query = text("""
                SELECT pr.item_id, pr.response_value
                FROM personality_responses pr
                JOIN personality_assessments pa ON pr.assessment_id = pa.id
                WHERE pa.session_id = :session_id
            """)
            
            results = db.execute(query, {"session_id": session_id}).fetchall()
            
            responses = {}
            for row in results:
                item_id = int(row.item_id)
                # Gérer le cas où response_value est déjà un dict (JSONB) ou une chaîne JSON
                if isinstance(row.response_value, dict):
                    response_data = row.response_value
                else:
                    response_data = json.loads(row.response_value)
                responses[item_id] = response_data["value"]
            
            logger.info(f"Réponses récupérées pour {session_id}: {len(responses)} items")
            return responses
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des réponses: {e}")
            return {}