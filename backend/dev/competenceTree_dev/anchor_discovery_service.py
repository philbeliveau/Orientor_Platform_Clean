"""
Service de découverte des nœuds d'ancrage via recherche sémantique dans Pinecone.

Ce service permet de trouver les nœuds d'ancrage dans le graphe ESCO en utilisant
une recherche sémantique dans Pinecone. Les nœuds d'ancrage sont les points de départ
pour la traversée du graphe.
"""

import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pinecone import Pinecone

# Configuration du logger
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnchorDiscoveryService:
    """
    Service pour découvrir les nœuds d'ancrage dans le graphe ESCO.
    
    Ce service utilise Pinecone pour effectuer une recherche sémantique
    et trouver les nœuds d'ancrage les plus pertinents pour un embedding donné.
    """
    
    def __init__(self, api_key: Optional[str] = None, index_name: str = "esco-368"):
        """
        Initialise le service de découverte des nœuds d'ancrage.
        
        Args:
            api_key: Clé API Pinecone (si None, utilise la variable d'environnement PINECONE_API_KEY)
            index_name: Nom de l'index Pinecone à utiliser
        """
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("La clé API Pinecone n'est pas définie. Utilisez le paramètre api_key ou définissez la variable d'environnement PINECONE_API_KEY.")
        
        self.index_name = index_name
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(self.index_name)
        logger.info(f"Service de découverte des nœuds d'ancrage initialisé avec l'index {index_name}")
    
    def find_anchors(self, 
                    embedding: np.ndarray, 
                    top_k: int = 5, 
                    threshold: float = 0.1,
                    filter_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Trouve les nœuds d'ancrage les plus pertinents pour un embedding donné.
        
        Args:
            embedding: Embedding vectoriel de dimension 384
            top_k: Nombre maximum de nœuds d'ancrage à retourner
            threshold: Seuil de similarité minimum (entre 0 et 1)
            filter_types: Liste des types de nœuds à inclure (occupation, skill, skillgroup)
                          Si None, tous les types sont inclus
        
        Returns:
            Liste des nœuds d'ancrage trouvés, avec leurs métadonnées et scores
        """
        if embedding.shape[0] != 384:
            raise ValueError(f"L'embedding doit être de dimension 384, mais a une dimension de {embedding.shape[0]}")
        
        # Convertir l'embedding en liste pour Pinecone
        vector = embedding.astype(np.float32).tolist()
        
        # Préparer le filtre si nécessaire
        filter_dict = None
        if filter_types:
            filter_dict = {"type": {"$in": filter_types}}
        # # Préparer le filtre - par défaut, ne chercher que les occupations
        # filter_dict = {"type": {"$in": filter_types if filter_types else ["occupation"]}}
        
        # Effectuer la recherche dans Pinecone
        try:
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=True,
                include_values=True
            )
            
            # Filtrer les résultats par seuil de similarité
            filtered_matches = []
            for match in results.matches:
                # Pinecone retourne une distance, nous la convertissons en similarité (1 - distance)
                similarity = 1 - match.score
                if similarity >= threshold:
                    filtered_matches.append({
                        "id": match.id,
                        "score": similarity,
                        "metadata": match.metadata,
                        "vector": match.values
                    })
            
            logger.info(f"Trouvé {len(filtered_matches)} nœuds d'ancrage avec un seuil de similarité de {threshold}")
            return filtered_matches
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche dans Pinecone: {str(e)}")
            return []
    
    def find_diverse_anchors(self, 
                           embedding: np.ndarray, 
                           top_k_per_type: int = 3,
                           threshold: float = 0.3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Trouve des nœuds d'ancrage diversifiés par type (occupation, skill, skillgroup).
        
        Args:
            embedding: Embedding vectoriel de dimension 384
            top_k_per_type: Nombre maximum de nœuds d'ancrage à retourner par type
            threshold: Seuil de similarité minimum (entre 0 et 1)
        
        Returns:
            Dictionnaire des nœuds d'ancrage par type
        """
        types = ["occupation", "skill", "skillgroup"]
        results = {}
        
        for node_type in types:
            anchors = self.find_anchors(
                embedding=embedding,
                top_k=top_k_per_type,
                threshold=threshold,
                filter_types=[node_type]
            )
            results[node_type] = anchors
            
        return results
    
    def get_anchor_node_ids(self, 
                          embedding: np.ndarray, 
                          top_k: int = 5,
                          threshold: float = 0.3,
                          filter_types: Optional[List[str]] = None) -> List[str]:
        """
        Récupère uniquement les IDs des nœuds d'ancrage.
        
        Args:
            embedding: Embedding vectoriel de dimension 384
            top_k: Nombre maximum de nœuds d'ancrage à retourner
            threshold: Seuil de similarité minimum (entre 0 et 1)
            filter_types: Liste des types de nœuds à inclure
        
        Returns:
            Liste des IDs des nœuds d'ancrage
        """
        anchors = self.find_anchors(embedding, top_k, threshold, filter_types)
        return [anchor["id"] for anchor in anchors]