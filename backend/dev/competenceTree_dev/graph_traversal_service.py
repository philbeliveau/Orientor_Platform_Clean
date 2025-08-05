"""
Service de traversée du graphe ESCO en utilisant GraphSAGE.

Ce service permet de traverser le graphe ESCO à partir de nœuds d'ancrage
en utilisant le modèle GraphSAGE pour calculer les similarités entre les nœuds.
"""

import os
import logging
import torch
import numpy as np
import networkx as nx
from typing import List, Dict, Any, Optional, Tuple, Set
from pathlib import Path
import json
import pickle
from collections import defaultdict, deque
import sys

# Configuration du logger early
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Production-grade path resolution for Railway deployment compatibility
def get_production_paths():
    """Get correct paths for both local development and Railway deployment."""
    current_file = os.path.abspath(__file__)
    
    # Try Railway deployment paths first
    railway_paths = {
        'backend': '/app',
        'services': '/app/app/services', 
        'gnn': '/app/app/services/GNN',
        'model': '/app/app/services/GNN/best_model_20250520_022237.pt',
        'data_dir': '/app/app/data'  # Moved from /app/dev which might not deploy
    }
    
    # Check if we're in Railway environment
    if os.path.exists('/app/main_deploy.py'):
        return railway_paths
    
    # Local development paths
    local_backend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_paths = {
        'backend': local_backend,
        'services': os.path.join(local_backend, "app", "services"),
        'gnn': os.path.join(local_backend, "app", "services", "GNN"),
        'model': os.path.join(local_backend, "app", "services", "GNN", "best_model_20250520_022237.pt")
    }
    
    return local_paths

# Get production paths
PATHS = get_production_paths()

# Import GraphSAGE model safely with multiple fallback paths
graphsage_model = None
CareerTreeModel = None

try:
    # Try importing from services/GNN first
    sys.path.insert(0, PATHS['services'])
    from GNN.GraphSage import GraphSAGE, CareerTreeModel
    graphsage_model = GraphSAGE
    logger.info("✅ GraphSAGE importé depuis app/services/GNN")
except ImportError as e:
    logger.warning(f"❌ Impossible d'importer GraphSAGE depuis services/GNN: {e}")
    
    try:
        # Fallback: Try importing from local GNN path
        sys.path.insert(0, PATHS['gnn'])
        from GraphSage import GraphSAGE, CareerTreeModel
        graphsage_model = GraphSAGE
        logger.info("✅ GraphSAGE importé depuis chemin GNN local")
    except ImportError as e2:
        logger.error(f"❌ Impossible d'importer GraphSAGE depuis tous les chemins: {e2}")
        logger.info("Le service fonctionnera en mode fallback sans GraphSAGE")

class GraphTraversalService:
    """
    Service de traversée du graphe ESCO utilisant GraphSAGE pour les calculs de similarité.
    
    Ce service :
    1. Charge un graphe ESCO prétraité
    2. Utilise un modèle GraphSAGE entraîné pour calculer les similarités
    3. Permet la traversée intelligente du graphe basée sur les embeddings
    4. Supporte les requêtes de similarité entre nœuds
    """
    
    def __init__(self):
        """Initialise le service de traversée du graphe."""
        self.graph = None
        self.node_metadata = {}
        self.graphsage_model = None
        self.model_loaded = False
        self.graph_loaded = False
        
        # Tenter de charger le graphe et le modèle
        self._load_graph()
        self._load_graphsage_model()
    
    def _load_graph(self):
        """Charge le graphe ESCO depuis les fichiers de données."""
        try:
            # Chercher les fichiers de graphe dans différents emplacements
            possible_graph_files = [
                os.path.join(PATHS.get('data_dir', PATHS['backend']), 'esco_graph.pkl'),
                os.path.join(PATHS['backend'], 'data', 'esco_graph.pkl'),
                os.path.join(PATHS['backend'], 'app', 'data', 'esco_graph.pkl'),
                os.path.join(PATHS['backend'], 'dev', 'competenceTree_dev', 'esco_graph.pkl')
            ]
            
            graph_file = None
            for file_path in possible_graph_files:
                if os.path.exists(file_path):
                    graph_file = file_path
                    break
            
            if graph_file:
                with open(graph_file, 'rb') as f:
                    graph_data = pickle.load(f)
                    self.graph = graph_data.get('graph', nx.Graph())
                    self.node_metadata = graph_data.get('metadata', {})
                
                logger.info(f"✅ Graphe ESCO chargé depuis {graph_file}")
                logger.info(f"📊 Graphe: {self.graph.number_of_nodes()} nœuds, {self.graph.number_of_edges()} arêtes")
                self.graph_loaded = True
            else:
                logger.warning("❌ Aucun fichier de graphe ESCO trouvé, création d'un graphe vide")
                self._create_fallback_graph()
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du graphe: {e}")
            self._create_fallback_graph()
    
    def _create_fallback_graph(self):
        """Crée un graphe de fallback minimal pour les tests."""
        self.graph = nx.Graph()
        self.node_metadata = {}
        
        # Ajouter quelques nœuds d'exemple pour éviter les erreurs
        sample_nodes = [
            ("occupation_1", {"type": "occupation", "preferredLabel": "Software Developer"}),
            ("skill_1", {"type": "skill", "preferredLabel": "Programming"}),
            ("skill_2", {"type": "skill", "preferredLabel": "Problem Solving"}),
            ("skill_3", {"type": "skill", "preferredLabel": "Critical Thinking"})
        ]
        
        for node_id, metadata in sample_nodes:
            self.graph.add_node(node_id)
            self.node_metadata[node_id] = metadata
        
        # Ajouter quelques arêtes d'exemple
        self.graph.add_edge("occupation_1", "skill_1")
        self.graph.add_edge("occupation_1", "skill_2")
        self.graph.add_edge("skill_1", "skill_3")
        
        logger.info("✅ Graphe de fallback créé avec des données d'exemple")
        self.graph_loaded = True
    
    def _load_graphsage_model(self):
        """Charge le modèle GraphSAGE pré-entraîné."""
        if not graphsage_model or not CareerTreeModel:
            logger.warning("❌ Classes GraphSAGE non disponibles, mode fallback activé")
            return
        
        try:
            model_path = PATHS['model']
            
            if not os.path.exists(model_path):
                logger.warning(f"❌ Modèle GraphSAGE non trouvé: {model_path}")
                logger.info("Le service fonctionnera avec des similarités basiques")
                return
            
            # Créer une instance du modèle complet
            full_model = CareerTreeModel(
                input_dim=1024,
                hidden_dim=128,
                output_dim=128,
                dropout=0.2
            )
            
            # Charger le checkpoint
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
            
            if 'model_state_dict' not in checkpoint:
                logger.error("❌ Checkpoint invalide: 'model_state_dict' manquant")
                return
            
            # Charger les poids
            full_model.load_state_dict(checkpoint['model_state_dict'])
            full_model.eval()
            
            # Extraire seulement l'encodeur (GraphSAGE)
            self.graphsage_model = full_model.encoder
            self.graphsage_model.eval()
            
            logger.info("✅ Modèle GraphSAGE chargé avec succès")
            self.model_loaded = True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle GraphSAGE: {e}")
            logger.info("Le service fonctionnera avec des similarités basiques")
    
    def get_node_neighbors(self, node_id: str, max_neighbors: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les voisins directs d'un nœud.
        
        Args:
            node_id: ID du nœud source
            max_neighbors: Nombre maximum de voisins à retourner
            
        Returns:
            Liste des voisins avec leurs métadonnées
        """
        if not self.graph_loaded or node_id not in self.graph:
            return []
        
        neighbors = []
        for neighbor_id in list(self.graph.neighbors(node_id))[:max_neighbors]:
            neighbor_data = {
                'id': neighbor_id,
                'metadata': self.node_metadata.get(neighbor_id, {}),
                'similarity': 1.0  # Similarité maximale pour les voisins directs
            }
            neighbors.append(neighbor_data)
        
        return neighbors
    
    def compute_node_similarity(self, node_id1: str, node_id2: str) -> float:
        """
        Calcule la similarité entre deux nœuds.
        
        Args:
            node_id1: Premier nœud
            node_id2: Deuxième nœud
            
        Returns:
            Score de similarité entre 0 et 1
        """
        if not self.graph_loaded:
            return 0.0
        
        if node_id1 not in self.graph or node_id2 not in self.graph:
            return 0.0
        
        if node_id1 == node_id2:
            return 1.0
        
        # Si le modèle GraphSAGE est disponible, l'utiliser
        if self.model_loaded and self.graphsage_model:
            try:
                return self._compute_graphsage_similarity(node_id1, node_id2)
            except Exception as e:
                logger.warning(f"❌ Erreur GraphSAGE, fallback vers similarité basique: {e}")
        
        # Fallback: utiliser la similarité basée sur les voisins communs
        return self._compute_basic_similarity(node_id1, node_id2)
    
    def _compute_graphsage_similarity(self, node_id1: str, node_id2: str) -> float:
        """
        Calcule la similarité en utilisant les embeddings GraphSAGE.
        
        Args:
            node_id1: Premier nœud
            node_id2: Deuxième nœud
            
        Returns:
            Score de similarité GraphSAGE
        """
        # TODO: Implémenter le calcul réel avec GraphSAGE
        # Pour l'instant, retourner une similarité basique
        return self._compute_basic_similarity(node_id1, node_id2)
    
    def _compute_basic_similarity(self, node_id1: str, node_id2: str) -> float:
        """
        Calcule une similarité basique basée sur les voisins communs.
        
        Args:
            node_id1: Premier nœud
            node_id2: Deuxième nœud
            
        Returns:
            Score de similarité basique
        """
        try:
            # Voisins directs
            neighbors1 = set(self.graph.neighbors(node_id1))
            neighbors2 = set(self.graph.neighbors(node_id2))
            
            # Calcul de l'indice de Jaccard
            intersection = len(neighbors1.intersection(neighbors2))
            union = len(neighbors1.union(neighbors2))
            
            if union == 0:
                return 0.0
            
            jaccard_similarity = intersection / union
            
            # Vérifier s'ils sont directement connectés (bonus)
            if self.graph.has_edge(node_id1, node_id2):
                jaccard_similarity = min(1.0, jaccard_similarity + 0.3)
            
            # Vérifier le même type (bonus léger)
            type1 = self.node_metadata.get(node_id1, {}).get('type', '')
            type2 = self.node_metadata.get(node_id2, {}).get('type', '')
            if type1 == type2 and type1:
                jaccard_similarity = min(1.0, jaccard_similarity + 0.1)
            
            return jaccard_similarity
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul similarité basique: {e}")
            return 0.0
    
    def find_similar_nodes(self, 
                          node_id: str, 
                          node_type: Optional[str] = None,
                          max_results: int = 10,
                          min_similarity: float = 0.1) -> List[Dict[str, Any]]:
        """
        Trouve les nœuds similaires à un nœud donné.
        
        Args:
            node_id: ID du nœud de référence
            node_type: Type de nœuds à chercher (optionnel)
            max_results: Nombre maximum de résultats
            min_similarity: Seuil minimum de similarité
            
        Returns:
            Liste des nœuds similaires triés par similarité décroissante
        """
        if not self.graph_loaded or node_id not in self.graph:
            return []
        
        similar_nodes = []
        
        # Parcourir tous les nœuds du graphe
        for candidate_id in self.graph.nodes():
            if candidate_id == node_id:
                continue
            
            # Filtrer par type si spécifié
            if node_type:
                candidate_type = self.node_metadata.get(candidate_id, {}).get('type', '')
                if candidate_type != node_type:
                    continue
            
            # Calculer la similarité
            similarity = self.compute_node_similarity(node_id, candidate_id)
            
            if similarity >= min_similarity:
                similar_nodes.append({
                    'id': candidate_id,
                    'similarity': similarity,
                    'metadata': self.node_metadata.get(candidate_id, {}),
                    'type': self.node_metadata.get(candidate_id, {}).get('type', 'unknown')
                })
        
        # Trier par similarité décroissante et limiter les résultats
        similar_nodes.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_nodes[:max_results]
    
    def traverse_graph(self, 
                      start_node: str,
                      max_depth: int = 3,
                      max_nodes_per_level: int = 5,
                      node_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Traverse le graphe à partir d'un nœud de départ.
        
        Args:
            start_node: Nœud de départ
            max_depth: Profondeur maximale de traversée
            max_nodes_per_level: Nombre maximum de nœuds par niveau
            node_types: Types de nœuds à inclure (optionnel)
            
        Returns:
            Structure hiérarchique de la traversée
        """
        if not self.graph_loaded or start_node not in self.graph:
            return {"error": "Nœud de départ invalide ou graphe non chargé"}
        
        visited = set()
        result = {
            "start_node": start_node,
            "levels": [],
            "total_nodes": 0
        }
        
        current_level = [start_node]
        visited.add(start_node)
        
        for depth in range(max_depth):
            level_nodes = []
            next_level = []
            
            for node_id in current_level:
                # Ajouter le nœud actuel au niveau
                node_data = {
                    "id": node_id,
                    "metadata": self.node_metadata.get(node_id, {}),
                    "depth": depth
                }
                level_nodes.append(node_data)
                
                # Trouver les voisins pour le niveau suivant
                neighbors = self.get_node_neighbors(node_id, max_nodes_per_level * 2)
                neighbor_scores = []
                
                for neighbor in neighbors:
                    neighbor_id = neighbor['id']
                    
                    if neighbor_id in visited:
                        continue
                    
                    # Filtrer par type si spécifié
                    if node_types:
                        neighbor_type = neighbor['metadata'].get('type', '')
                        if neighbor_type not in node_types:
                            continue
                    
                    # Calculer la similarité pour le tri
                    similarity = self.compute_node_similarity(node_id, neighbor_id)
                    neighbor_scores.append((neighbor_id, similarity))
                
                # Trier les voisins par similarité et prendre les meilleurs
                neighbor_scores.sort(key=lambda x: x[1], reverse=True)
                for neighbor_id, _ in neighbor_scores[:max_nodes_per_level]:
                    if neighbor_id not in visited:
                        next_level.append(neighbor_id)
                        visited.add(neighbor_id)
                        
                        if len(next_level) >= max_nodes_per_level:
                            break
                
                if len(next_level) >= max_nodes_per_level:
                    break
            
            result["levels"].append(level_nodes)
            result["total_nodes"] += len(level_nodes)
            
            if not next_level:
                break
                
            current_level = next_level[:max_nodes_per_level]
        
        return result
    
    def get_node_info(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations détaillées d'un nœud.
        
        Args:
            node_id: ID du nœud
            
        Returns:
            Informations du nœud ou None si non trouvé
        """
        if not self.graph_loaded or node_id not in self.graph:
            return None
        
        neighbors = list(self.graph.neighbors(node_id))
        metadata = self.node_metadata.get(node_id, {})
        
        return {
            "id": node_id,
            "metadata": metadata,
            "type": metadata.get("type", "unknown"),
            "label": metadata.get("preferredLabel", metadata.get("label", node_id)),
            "neighbor_count": len(neighbors),
            "neighbors": neighbors[:10],  # Limiter à 10 pour l'affichage
            "degree": self.graph.degree(node_id)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du graphe et du service.
        
        Returns:
            Dictionnaire des statistiques
        """
        stats = {
            "graph_loaded": self.graph_loaded,
            "model_loaded": self.model_loaded,
            "nodes_count": 0,
            "edges_count": 0,
            "node_types": {},
            "graphsage_available": self.graphsage_model is not None
        }
        
        if self.graph_loaded and self.graph:
            stats["nodes_count"] = self.graph.number_of_nodes()
            stats["edges_count"] = self.graph.number_of_edges()
            
            # Compter les types de nœuds
            type_counts = {}
            for node_id in self.graph.nodes():
                node_type = self.node_metadata.get(node_id, {}).get('type', 'unknown')
                type_counts[node_type] = type_counts.get(node_type, 0) + 1
            
            stats["node_types"] = type_counts
        
        return stats

# Fonction utilitaire pour créer une instance globale
_graph_service_instance = None

def get_graph_service() -> GraphTraversalService:
    """
    Récupère l'instance globale du service de traversée du graphe.
    
    Returns:
        Instance du GraphTraversalService
    """
    global _graph_service_instance
    if _graph_service_instance is None:
        _graph_service_instance = GraphTraversalService()
    return _graph_service_instance

# Test des fonctionnalités si exécuté directement
if __name__ == "__main__":
    print("🧪 Test du service de traversée du graphe ESCO")
    print("=" * 60)
    
    # Créer une instance du service
    service = GraphTraversalService()
    
    # Afficher les statistiques
    stats = service.get_statistics()
    print(f"📊 Statistiques du service:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()
    
    # Tester avec les nœuds d'exemple
    if service.graph_loaded:
        # Lister quelques nœuds
        sample_nodes = list(service.graph.nodes())[:3]
        print(f"🔍 Nœuds d'exemple: {sample_nodes}")
        
        if sample_nodes:
            test_node = sample_nodes[0]
            print(f"\n🧪 Test avec le nœud: {test_node}")
            
            # Informations du nœud
            node_info = service.get_node_info(test_node)
            print(f"ℹ️  Informations: {node_info}")
            
            # Voisins
            neighbors = service.get_node_neighbors(test_node, max_neighbors=3)
            print(f"👥 Voisins: {[n['id'] for n in neighbors]}")
            
            # Nœuds similaires
            similar = service.find_similar_nodes(test_node, max_results=3)
            print(f"🔄 Similaires: {[(s['id'], f\"{s['similarity']:.2f}\") for s in similar]}")
            
            # Traversée
            traversal = service.traverse_graph(test_node, max_depth=2, max_nodes_per_level=2)
            if "error" not in traversal:
                print(f"🌐 Traversée: {traversal['total_nodes']} nœuds sur {len(traversal['levels'])} niveaux")
            else:
                print(f"❌ Erreur traversée: {traversal['error']}")
    
    print("\n✅ Test terminé")