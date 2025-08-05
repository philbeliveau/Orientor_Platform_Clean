# import os
# import logging
# import numpy as np
# import random
# import networkx as nx
# from typing import List, Dict, Any, Optional
# from sqlalchemy.orm import Session
# from sqlalchemy import text
# import pinecone
# from pinecone import Pinecone
# from ..models import UserSkillTree
# from uuid import uuid4
# import torch
# import sys

# # Add the path to import the GNN model
# sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))
# from GNN.GraphSage import GraphSAGE, CareerTreeModel

# # Configuration du logger
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Configuration Pinecone
# PINECONE_INDEX = "esco-368"

# class CompetenceTreeService:
#     """
#     Service pour générer des arbres de compétences personnalisés avec des défis dynamiques.
#     """
    
#     def __init__(self, index_name: str = "esco-368"):
#         """
#         Initialise le service d'arbre de compétences.
#         """
#         self.api_key = os.getenv("PINECONE_API_KEY")
#         if not self.api_key:
#             raise ValueError("La clé API Pinecone n'est pas définie. Utilisez le paramètre api_key ou définissez la variable d'environnement PINECONE_API_KEY.")
        
#         self.index_name = index_name
#         self.pc = Pinecone(api_key=self.api_key)
#         self.index = self.pc.Index(self.index_name)
#         self.embedding_model = None
#         self._initialize_pinecone()
#         self._initialize_embedding_model()
#         self._initialize_gnn_model()
        
#     def _initialize_embedding_model(self):
#         """
#         Initialise le modèle d'embedding pour la recherche vectorielle.
        
#         Returns:
#             bool: True si l'initialisation a réussi, False sinon
#         """
#         try:
#             from sentence_transformers import SentenceTransformer
#             self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
#             logger.info("Modèle d'embedding initialisé avec succès")
#             return True
#         except Exception as e:
#             logger.error(f"Erreur lors de l'initialisation du modèle d'embedding: {str(e)}")
#             return False
    
#     def _initialize_pinecone(self) -> bool:
#         """
#         Initialise la connexion à Pinecone.
        
#         Returns:
#             bool: True si l'initialisation a réussi, False sinon
#         """
#         try:
#             api_key = os.getenv("PINECONE_API_KEY")
#             if not api_key:
#                 logger.error("Clé API Pinecone non définie dans les variables d'environnement")
#                 return False
            
#             self.pinecone_client = Pinecone(api_key=api_key)
#             self.index = self.pinecone_client.Index(PINECONE_INDEX)
#             logger.info(f"Connexion à l'index Pinecone '{PINECONE_INDEX}' établie avec succès")
#             return True
#         except Exception as e:
#             logger.error(f"Erreur lors de l'initialisation de Pinecone: {str(e)}")
#             return False
    
#     def _initialize_gnn_model(self):
#         """Initialize the GNN model for graph traversal."""
#         try:
#             model_path = os.path.join(
#                 os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
#                 "services", "GNN", "best_model_20250520_022237.pt"
#             )
            
#             if not os.path.exists(model_path):
#                 logger.error(f"Le fichier du modèle n'existe pas: {model_path}")
#                 return
            
#             # Load the checkpoint
#             checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
            
#             # Initialize the model
#             self.gnn_model = CareerTreeModel(
#                 input_dim=384,  # Embedding dimension
#                 hidden_dim=128,
#                 output_dim=128,
#                 dropout=0.2
#             )
            
#             # Load model weights
#             if "model_state_dict" not in checkpoint:
#                 logger.error("Le checkpoint ne contient pas 'model_state_dict'")
#                 return
            
#             self.gnn_model.load_state_dict(checkpoint["model_state_dict"])
#             self.gnn_model.eval()  # Set to evaluation mode
            
#             logger.info("Modèle GraphSAGE chargé avec succès")
            
#         except Exception as e:
#             logger.error(f"Erreur lors de l'initialisation du modèle GNN: {str(e)}")
#             self.gnn_model = None
    
#     # Fonction supprimée car non nécessaire pour extraire les top 5
    
#     def get_user_embedding(self, db: Session, user_id: int, embedding_type: str = "esco_embedding_skill") -> Optional[np.ndarray]:
#         """
#         Récupère l'embedding de compétences d'un utilisateur depuis la base de données.
        
#         Args:
#             db: Session de base de données
#             user_id: ID de l'utilisateur
#             embedding_type: Type d'embedding à récupérer (par défaut: esco_embedding_skill)
            
#         Returns:
#             np.ndarray: Embedding de l'utilisateur ou None en cas d'échec
#         """
#         try:
#             # Vérifier que le type d'embedding est valide
#             valid_types = ["esco_embedding", "esco_embedding_occupation", "esco_embedding_skill", "esco_embedding_skillsgroup"]
#             if embedding_type not in valid_types:
#                 logger.error(f"Type d'embedding invalide: {embedding_type}")
#                 return None
            
#             # Récupérer l'embedding depuis la base de données
#             query = text(f"SELECT {embedding_type} FROM user_profiles WHERE user_id = :user_id")
#             result = db.execute(query, {"user_id": user_id}).fetchone()
            
#             if not result or not result[0]:
#                 logger.error(f"Aucun embedding {embedding_type} trouvé pour l'utilisateur {user_id}")
#                 return None
            
#             # Convertir la chaîne en tableau numpy
#             import ast
#             embedding = np.array(ast.literal_eval(result[0]), dtype=np.float32)
#             logger.info(f"Embedding {embedding_type} récupéré avec succès pour l'utilisateur {user_id}: {embedding.shape}")
#             return embedding
#         except Exception as e:
#             logger.error(f"Erreur lors de la récupération de l'embedding: {str(e)}")
#             return None
    
#     def extract_anchor_skills(self, db: Session, user_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
#         """
#         Extrait les compétences dominantes d'un utilisateur en utilisant son embedding vectoriel.
#         Retourne une liste de dicts contenant l'ID, score, metadata et vecteur de chaque compétence.
#         """
#         try:
#             user_embedding = self.get_user_embedding(db, user_id, "esco_embedding_skill")
#             if user_embedding is None:
#                 logger.error(f"Aucun embedding trouvé pour l'utilisateur {user_id}")
#                 return []

#             if self.index is None and not self._initialize_pinecone():
#                 logger.error("Impossible d'initialiser Pinecone")
#                 return []

#             vector = user_embedding.astype(np.float32).tolist()

#             logger.info(f"Recherche des compétences similaires dans Pinecone pour l'utilisateur {user_id}")
#             results = self.index.query(
#                 vector=vector,
#                 top_k=top_k,
#                 filter=None, # {"type": {"$eq": "skill"}},
#                 include_metadata=True,
#                 include_values=True
#             )

#             matches = []
#             for match in results.matches:
#                 similarity = 1 - match.score
#                 if similarity >= 0.1:
#                     matches.append({
#                         "id": match.id,
#                         "score": similarity,
#                         "metadata": match.metadata,
#                         "vector": match.values
#                     })

#             logger.info(f"Trouvé {len(matches)} nœuds d'ancrage avec un seuil de similarité ≥ 0.1")
#             return matches

#         except Exception as e:
#             logger.error(f"Erreur lors de l'extraction des compétences dominantes: {str(e)}")
#             return []

#     def traverse_skill_graph(self, anchor_skills: List[Dict[str, Any]], max_depth: int = 3, max_nodes_per_level: int = 5) -> Dict[str, Any]:
#         """
#         Traverse le graphe de compétences à partir de compétences d'ancrage en utilisant le modèle GNN.
#         """
#         try:
#             graph = nx.DiGraph()
#             metadata_lookup = {}
#             current_level_nodes = []

#             # Initialisation des nœuds d'ancrage
#             for skill in anchor_skills:
#                 skill_id = skill["id"]
#                 metadata = skill["metadata"]
#                 vector = skill["vector"]
#                 label = metadata.get("preferredLabel", skill_id)

#                 graph.add_node(skill_id, label=label, type="skill", level=0, metadata=metadata)
#                 metadata_lookup[skill_id] = metadata
#                 current_level_nodes.append((skill_id, vector))

#             # Traversée niveau par niveau
#             for level in range(1, max_depth + 1):
#                 next_level_nodes = []

#                 for node_id, node_vector in current_level_nodes:
#                     try:
#                         # Rechercher des nœuds similaires dans Pinecone
#                         results = self.index.query(
#                             vector=node_vector,
#                             top_k=max_nodes_per_level * 2,  # Get more candidates for filtering
#                             include_metadata=True,
#                             filter={"type": {"$eq": "skill"}}
#                         )

#                         # Filtrer et trier les résultats en utilisant GraphSAGE
#                         filtered_matches = []
#                         for match in results.matches:
#                             if match.id not in graph:
#                                 # Convertir les vecteurs en tensors
#                                 node_tensor = torch.tensor(node_vector, dtype=torch.float32).unsqueeze(0)
#                                 match_tensor = torch.tensor(match.values, dtype=torch.float32).unsqueeze(0)
                                
#                                 # Créer un mini-graphe pour les deux nœuds
#                                 x = torch.cat([node_tensor, match_tensor], dim=0)
#                                 edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)
                                
#                                 # Calculer la similarité avec GraphSAGE
#                                 with torch.no_grad():
#                                     node_embeddings = self.gnn_model.encoder(x, edge_index)
#                                     similarity = torch.cosine_similarity(
#                                         node_embeddings[0], 
#                                         node_embeddings[1], 
#                                         dim=0
#                                     ).item()
                                
#                                 # Normaliser la similarité entre 0 et 1
#                                 similarity = (similarity + 1) / 2
                                
#                                 if similarity >= 0.3:  # Seuil de similarité minimal
#                                     filtered_matches.append((match, similarity))

#                         # Trier par similarité décroissante et prendre les meilleurs
#                         filtered_matches.sort(key=lambda x: x[1], reverse=True)
#                         filtered_matches = filtered_matches[:max_nodes_per_level]

#                         # Ajouter les nœuds filtrés au graphe
#                         for match, similarity in filtered_matches:
#                             match_label = match.metadata.get("preferredLabel", match.id)
#                             graph.add_node(match.id, label=match_label, type="skill", level=level, metadata=match.metadata)
#                             graph.add_edge(node_id, match.id, weight=similarity)
#                             next_level_nodes.append((match.id, match.values))

#                     except Exception as e:
#                         logger.error(f"Erreur lors de la recherche de voisins pour {node_id}: {str(e)}")

#                 current_level_nodes = next_level_nodes[:max_nodes_per_level]
#                 if not current_level_nodes:
#                     break

#             # Construction du résultat final
#             nodes = [{
#                 "id": n,
#                 "label": d.get("label", n),
#                 "type": d.get("type", "skill"),
#                 "level": d.get("level", 0),
#                 "metadata": d.get("metadata", {})
#             } for n, d in graph.nodes(data=True)]

#             edges = [{
#                 "source": u,
#                 "target": v,
#                 "weight": d.get("weight", 1.0)
#             } for u, v, d in graph.edges(data=True)]

#             return {
#                 "nodes": {node["id"]: node for node in nodes},
#                 "edges": edges,
#                 "anchor_nodes": [s["id"] for s in anchor_skills]
#             }

#         except Exception as e:
#             logger.error(f"Erreur lors de la traversée du graphe de compétences: {str(e)}")
#             return {}

#     def mark_visibility(self, graph: nx.DiGraph, reveal_ratio: float = 0.60) -> Dict[str, bool]:
#         """
#         Marque la visibilité des nœuds dans le graphe.
        
#         Args:
#             graph: Graphe de compétences
#             reveal_ratio: Ratio de nœuds à révéler
            
#         Returns:
#             Dict[str, bool]: Dictionnaire {skill_id: is_revealed}
#         """
#         try:
#             # Calculer le nombre de nœuds à révéler
#             total_nodes = len(graph.nodes())
#             nodes_to_reveal = int(total_nodes * reveal_ratio)
            
#             # Récupérer les nœuds de niveau 0 (nœuds d'ancrage)
#             anchor_nodes = [node for node, data in graph.nodes(data=True) if data.get("level", 0) == 0]
            
#             # Tous les nœuds d'ancrage sont toujours révélés
#             visibility = {node: (node in anchor_nodes) for node in graph.nodes()}
            
#             # Calculer combien de nœuds supplémentaires doivent être révélés
#             already_revealed = len(anchor_nodes)
#             additional_reveals = max(0, nodes_to_reveal - already_revealed)
            
#             # Sélectionner des nœuds supplémentaires à révéler
#             non_anchor_nodes = [node for node in graph.nodes() if node not in anchor_nodes]
            
#             # Prioriser les nœuds connectés aux nœuds d'ancrage
#             connected_to_anchor = []
#             for node in non_anchor_nodes:
#                 for anchor in anchor_nodes:
#                     if graph.has_edge(anchor, node):
#                         connected_to_anchor.append(node)
#                         break
            
#             # Autres nœuds non connectés directement
#             other_nodes = [node for node in non_anchor_nodes if node not in connected_to_anchor]
            
#             # Mélanger les listes pour une sélection aléatoire
#             random.shuffle(connected_to_anchor)
#             random.shuffle(other_nodes)
            
#             # Révéler d'abord les nœuds connectés aux ancres, puis les autres si nécessaire
#             nodes_to_reveal_list = connected_to_anchor + other_nodes
#             for node in nodes_to_reveal_list[:additional_reveals]:
#                 visibility[node] = True
            
#             logger.info(f"Visibilité des nœuds marquée: {sum(visibility.values())}/{total_nodes} nœuds révélés")
#             return visibility
#         except Exception as e:
#             logger.error(f"Erreur lors du marquage de la visibilité des nœuds: {str(e)}")
#             return {}
#     def generate_challenge(self, skill_label: str, user_age: int) -> Dict[str, Any]:
#         """
#         Génère un défi pour une compétence donnée.
        
#         Args:
#             skill_label: Libellé de la compétence
#             user_age: Âge de l'utilisateur
            
#         Returns:
#             Dict[str, Any]: Défi généré avec récompense XP
#         """
#         try:
#             # Déterminer le niveau de difficulté en fonction de l'âge
#             if user_age < 18:
#                 difficulty = "débutant"
#                 xp_reward = random.randint(10, 30)
#             elif user_age < 25:
#                 difficulty = "intermédiaire"
#                 xp_reward = random.randint(20, 50)
#             else:
#                 difficulty = "avancé"
#                 xp_reward = random.randint(40, 100)
            
#             # Générer un prompt pour le LLM
#             prompt = f"""
#             Génère un défi pratique pour développer la compétence "{skill_label}" à un niveau {difficulty}.
#             Le défi doit être:
#             1. Concret et actionnable
#             2. Réalisable en moins d'une semaine
#             3. Adapté à une personne de {user_age} ans
#             4. Mesurable (comment savoir qu'on a réussi)
            
#             Format: Un titre court et une description détaillée en 3-4 phrases.
#             """
            
#             # Simuler une réponse LLM (à remplacer par un appel API réel)
#             # Note: Dans une implémentation réelle, vous utiliseriez un appel à une API LLM
            
#             # Exemples de défis prédéfinis par compétence (simulation)
#             challenge_templates = {
#                 "communication": {
#                     "débutant": {
#                         "title": "Présentation Express",
#                         "description": "Préparez et enregistrez une présentation de 2 minutes sur un sujet qui vous passionne. Partagez-la avec au moins deux personnes et demandez-leur un retour constructif. Concentrez-vous sur la clarté de votre message et votre langage corporel."
#                     },
#                     "intermédiaire": {
#                         "title": "Débat Constructif",
#                         "description": "Organisez un mini-débat avec des amis sur un sujet controversé. Votre mission est de défendre un point de vue opposé au vôtre pendant 10 minutes. Concentrez-vous sur l'écoute active et l'argumentation sans agressivité."
#                     },
#                     "avancé": {
#                         "title": "Négociation Win-Win",
#                         "description": "Identifiez une situation réelle nécessitant une négociation (achat, projet professionnel, etc.). Préparez une stratégie visant un résultat gagnant-gagnant, menez la négociation et documentez le processus et les résultats obtenus."
#                     }
#                 },
#                 "programmation": {
#                     "débutant": {
#                         "title": "Application Todo List",
#                         "description": "Créez une application simple de liste de tâches avec les fonctionnalités d'ajout, de suppression et de marquage comme terminé. Utilisez HTML, CSS et JavaScript de base. Testez votre application avec au moins 10 tâches différentes."
#                     },
#                     "intermédiaire": {
#                         "title": "API Météo Interactive",
#                         "description": "Développez une application web qui utilise une API météo pour afficher les prévisions d'une ville choisie par l'utilisateur. Implémentez une interface réactive qui change en fonction des conditions météorologiques et permettez la sauvegarde des villes favorites."
#                     },
#                     "avancé": {
#                         "title": "Système de Recommandation",
#                         "description": "Créez un algorithme de recommandation simple basé sur le contenu pour suggérer des produits/films/livres. Implémentez-le dans une application avec une base de données, testez-le avec des données réelles et mesurez sa précision avec des métriques appropriées."
#                     }
#                 }
#             }
            
#             # Déterminer la catégorie de compétence (simplifiée)
#             skill_category = "communication"  # Par défaut
#             for category in challenge_templates.keys():
#                 if category.lower() in skill_label.lower():
#                     skill_category = category
#                     break
            
#             # Si la catégorie n'existe pas, utiliser une catégorie par défaut
#             if skill_category not in challenge_templates:
#                 skill_category = list(challenge_templates.keys())[0]
            
#             # Récupérer le défi correspondant
#             challenge = challenge_templates.get(skill_category, {}).get(difficulty, {})
            
#             if not challenge:
#                 # Défi générique si aucun défi spécifique n'est trouvé
#                 challenge = {
#                     "title": f"Maîtrisez {skill_label}",
#                     "description": f"Recherchez et suivez un tutoriel en ligne sur {skill_label}. Pratiquez les concepts appris pendant au moins 3 heures réparties sur une semaine. Créez un petit projet démontrant votre compréhension et partagez-le avec un ami ou un collègue pour obtenir des commentaires."
#                 }
            
#             # Construire la réponse
#             challenge_data = {
#                 "skill_id": skill_label.replace(" ", "_").lower(),
#                 "skill_label": skill_label,
#                 "title": challenge.get("title", f"Défi: {skill_label}"),
#                 "description": challenge.get("description", f"Pratiquez {skill_label} pendant une semaine et documentez votre progression."),
#                 "difficulty": difficulty,
#                 "xp_reward": xp_reward,
#                 "duration_days": random.randint(3, 7)
#             }
            
#             logger.info(f"Défi généré pour la compétence '{skill_label}': {challenge_data['title']}")
#             return challenge_data
#         except Exception as e:
#             logger.error(f"Erreur lors de la génération du défi: {str(e)}")
#             return {
#                 "skill_label": skill_label,
#                 "title": f"Explorez {skill_label}",
#                 "description": f"Apprenez les bases de {skill_label} à travers des ressources en ligne et pratiquez régulièrement.",
#                 "difficulty": "intermédiaire",
#                 "xp_reward": 25,
#                 "duration_days": 5
#             }
#     def create_skill_tree(self, db: Session, user_id: int, max_depth: int = 3, max_nodes_per_level: int = 5) -> Dict[str, Any]:
#         """
#         Crée un arbre de compétences complet pour un utilisateur.
#         """
#         try:
#             # Récupérer l'âge de l'utilisateur
#             query = text("SELECT age FROM user_profiles WHERE user_id = :user_id")
#             result = db.execute(query, {"user_id": user_id}).fetchone()
#             user_age = result[0] if result and result[0] else 25
            
#             # Extraire les compétences d'ancrage
#             anchor_skills = self.extract_anchor_skills(db, user_id)
#             if not anchor_skills:
#                 logger.error(f"Aucune compétence d'ancrage trouvée pour l'utilisateur {user_id}")
#                 return {}
            
#             # Créer un graphe pour chaque compétence d'ancrage
#             all_nodes = []
#             all_edges = []
            
#             for anchor_skill in anchor_skills:
#                 # Créer un graphe pour cette compétence
#                 graph_data = self.traverse_skill_graph([anchor_skill], max_depth, max_nodes_per_level)
                
#                 # Convertir les nœuds et les arêtes au format attendu par le frontend
#                 nodes = []
#                 for node_id, node_data in graph_data.get("nodes", {}).items():
#                     # Marquer la visibilité des nœuds
#                     is_visible = node_id in graph_data.get("anchor_nodes", [])
                    
#                     # Générer un défi pour les nœuds visibles
#                     challenge_data = {}
#                     if is_visible:
#                         skill_label = node_data.get("label", f"Compétence {node_id}")
#                         challenge_data = self.generate_challenge(skill_label, user_age)
                    
#                     competence_node = {
#                         "id": node_id,
#                         "skill_id": node_id,
#                         "skill_label": node_data.get("label", f"Compétence {node_id}"),
#                         "challenge": challenge_data.get("description", ""),
#                         "xp_reward": challenge_data.get("xp_reward", 25),
#                         "visible": is_visible,
#                         "revealed": is_visible,
#                         "state": "locked",
#                         "notes": "",
#                         "graph_id": str(uuid4())  # Unique graph ID for each anchor skill's tree
#                     }
#                     nodes.append(competence_node)
                
#                 # Ajouter les nœuds et les arêtes à la liste principale
#                 all_nodes.extend(nodes)
#                 all_edges.extend(graph_data.get("edges", []))
            
#             # Construire la réponse finale
#             skill_tree = {
#                 "nodes": all_nodes,
#                 "edges": all_edges,
#                 "graph_id": str(uuid4())
#             }
            
#             logger.info(f"Arbre de compétences créé avec succès pour l'utilisateur {user_id}")
#             return skill_tree
            
#         except Exception as e:
#             logger.error(f"Erreur lors de la création de l'arbre de compétences: {str(e)}")
#             return {}
#     def save_skill_tree(self, db: Session, user_id: int, tree_data: Dict[str, Any]) -> str:
#         """
#         Sauvegarde l'arbre de compétences dans la base de données.
        
#         Args:
#             db: Session de base de données
#             user_id: ID de l'utilisateur
#             tree_data: Données de l'arbre de compétences
            
#         Returns:
#             str: ID du graphe sauvegardé
#         """
#         try:
#             import json
#             import numpy as np
            
#             # Classe personnalisée pour encoder les objets numpy en JSON
#             class NumpyEncoder(json.JSONEncoder):
#                 def default(self, obj):
#                     if isinstance(obj, np.ndarray):
#                         return obj.tolist()
#                     if isinstance(obj, np.integer):
#                         return int(obj)
#                     if isinstance(obj, np.floating):
#                         return float(obj)
#                     return super(NumpyEncoder, self).default(obj)
            
#             # Nettoyer les données pour s'assurer qu'elles sont sérialisables
#             def clean_for_json(data):
#                 if isinstance(data, dict):
#                     return {k: clean_for_json(v) for k, v in data.items()}
#                 elif isinstance(data, list):
#                     return [clean_for_json(item) for item in data]
#                 elif isinstance(data, np.ndarray):
#                     return data.tolist()
#                 elif isinstance(data, (np.integer, np.floating)):
#                     return float(data) if isinstance(data, np.floating) else int(data)
#                 else:
#                     return data
            
#             # Nettoyer les données avant la sérialisation
#             clean_tree_data = clean_for_json(tree_data)
            
#             # Créer une nouvelle instance de UserSkillTree
#             skill_tree = UserSkillTree(
#                 user_id=user_id,
#                 tree_data=clean_tree_data  # JSONB will handle the serialization
#             )
            
#             # Ajouter et sauvegarder dans la base de données
#             db.add(skill_tree)
#             db.commit()
#             db.refresh(skill_tree)
            
#             logger.info(f"Arbre de compétences sauvegardé avec succès pour l'utilisateur {user_id}, ID: {skill_tree.graph_id}")
#             return skill_tree.graph_id
#         except Exception as e:
#             logger.error(f"Erreur lors de la sauvegarde de l'arbre de compétences: {str(e)}")
#             db.rollback()
#             return ""
    
#     def complete_challenge(self, db: Session, node_id: int, user_id: int) -> bool:
#         """
#         Marque un défi comme complété et accorde des XP.
        
#         Args:
#             db: Session de base de données
#             node_id: ID du nœud
#             user_id: ID de l'utilisateur
            
#         Returns:
#             bool: True si le défi a été complété avec succès
#         """
#         try:
#             # Récupérer les informations du défi
#             query = text("""
#                 SELECT tree_data 
#                 FROM user_skill_trees 
#                 WHERE user_id = :user_id 
#                 ORDER BY created_at DESC 
#                 LIMIT 1
#             """)
            
#             result = db.execute(query, {"user_id": user_id}).fetchone()
#             if not result or not result[0]:
#                 logger.error(f"Aucun arbre de compétences trouvé pour l'utilisateur {user_id}")
#                 return False
            
#             import json
#             import numpy as np
            
#             # Classe personnalisée pour encoder les objets numpy en JSON
#             class NumpyEncoder(json.JSONEncoder):
#                 def default(self, obj):
#                     if isinstance(obj, np.ndarray):
#                         return obj.tolist()
#                     if isinstance(obj, np.integer):
#                         return int(obj)
#                     if isinstance(obj, np.floating):
#                         return float(obj)
#                     return super(NumpyEncoder, self).default(obj)
            
#             # Nettoyer les données pour s'assurer qu'elles sont sérialisables
#             def clean_for_json(data):
#                 if isinstance(data, dict):
#                     return {k: clean_for_json(v) for k, v in data.items()}
#                 elif isinstance(data, list):
#                     return [clean_for_json(item) for item in data]
#                 elif isinstance(data, np.ndarray):
#                     return data.tolist()
#                 elif isinstance(data, (np.integer, np.floating)):
#                     return float(data) if isinstance(data, np.floating) else int(data)
#                 else:
#                     return data
            
#             tree_data = json.loads(result[0])
            
#             # Vérifier si le défi existe
#             challenges = tree_data.get("challenges", {})
#             if str(node_id) not in challenges:
#                 logger.error(f"Défi {node_id} non trouvé pour l'utilisateur {user_id}")
#                 return False
            
#             challenge = challenges[str(node_id)]
#             xp_reward = challenge.get("xp_reward", 25)
#             skill_label = challenge.get("skill_label", "Compétence inconnue")
            
#             # Mettre à jour les XP de l'utilisateur
#             update_query = text("""
#                 UPDATE user_profiles 
#                 SET xp = xp + :xp_reward 
#                 WHERE user_id = :user_id
#             """)
            
#             db.execute(update_query, {"user_id": user_id, "xp_reward": xp_reward})
            
#             # Enregistrer la complétion du défi
#             completion_query = text("""
#                 INSERT INTO challenge_completions (user_id, node_id, challenge_title, xp_earned, completed_at)
#                 VALUES (:user_id, :node_id, :challenge_title, :xp_earned, NOW())
#             """)
            
#             db.execute(completion_query, {
#                 "user_id": user_id,
#                 "node_id": node_id,
#                 "challenge_title": challenge.get("title", f"Défi {node_id}"),
#                 "xp_earned": xp_reward
#             })
            
#             # Mettre à jour le niveau de compétence de l'utilisateur
#             skill_update_query = text("""
#                 INSERT INTO user_skills (user_id, skill_id, skill_label, proficiency_level, last_updated)
#                 VALUES (:user_id, :skill_id, :skill_label, 1, NOW())
#                 ON CONFLICT (user_id, skill_id) 
#                 DO UPDATE SET proficiency_level = user_skills.proficiency_level + 1, last_updated = NOW()
#             """)
            
#             db.execute(skill_update_query, {
#                 "user_id": user_id,
#                 "skill_id": node_id,
#                 "skill_label": skill_label
#             })
            
#             db.commit()
            
#             # Émettre un événement public
#             domain = tree_data.get("metadata", {}).get("domain", "compétence")
#             self.emit_public_event(db, user_id, domain)
            
#             logger.info(f"Défi {node_id} complété avec succès pour l'utilisateur {user_id}, {xp_reward} XP gagnés")
#             return True
#         except Exception as e:
#             logger.error(f"Erreur lors de la complétion du défi: {str(e)}")
#             db.rollback()
#     def emit_public_event(self, db: Session, user_id: int, domain: str) -> bool:
#         """
#         Émet un événement public dans le flux d'activité.
        
#         Args:
#             db: Session de base de données
#             user_id: ID de l'utilisateur
#             domain: Domaine de compétence
            
#         Returns:
#             bool: True si l'événement a été émis avec succès
#         """
#         try:
#             # Récupérer les informations de l'utilisateur
#             user_query = text("""
#                 SELECT username, first_name, last_name
#                 FROM users
#                 WHERE id = :user_id
#             """)
            
#             user_result = db.execute(user_query, {"user_id": user_id}).fetchone()
#             if not user_result:
#                 logger.error(f"Utilisateur {user_id} non trouvé")
#                 return False
            
#             username = user_result[0]
#             full_name = f"{user_result[1]} {user_result[2]}" if user_result[1] and user_result[2] else username
            
#             # Créer un message d'événement
#             event_message = f"{full_name} a progressé dans le domaine de {domain}"
            
#             # Insérer l'événement dans la base de données
#             event_query = text("""
#                 INSERT INTO activity_feed (user_id, event_type, event_message, created_at)
#                 VALUES (:user_id, 'skill_progress', :event_message, NOW())
#             """)
            
#             db.execute(event_query, {
#                 "user_id": user_id,
#                 "event_message": event_message
#             })
            
#             db.commit()
            
#             logger.info(f"Événement public émis pour l'utilisateur {user_id} dans le domaine {domain}")
#             return True
#         except Exception as e:
#             logger.error(f"Erreur lors de l'émission de l'événement public: {str(e)}")
#             db.rollback()
#             return False

import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
import pinecone
from pinecone import Pinecone
import random
import networkx as nx
from uuid import uuid4
from app.models import UserSkillTree
import openai
import traceback
import json
from datetime import datetime
from sentence_transformers import SentenceTransformer

# Import our new services
from .LLMcompetence_service import LLMCompetenceService
from .esco_formatting_service import ESCOFormattingService

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Pinecone
PINECONE_INDEX = "esco-368"

class CompetenceTreeService:
    """
    Service pour générer des arbres de compétences personnalisés avec des défis dynamiques.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CompetenceTreeService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialise le service de compétences.
        """
        if self._initialized:
            return
            
        self.pinecone_client = None
        self.index = None
        self.embedding_model = None
        self.gnn_model = None
        
        # Initialize new services
        self.llm_service = LLMCompetenceService()
        self.esco_service = ESCOFormattingService()
        
        try:
            # Initialize core components
            if not self._initialize_pinecone():
                logger.error("Failed to initialize Pinecone")
                return
            logger.info("Pinecone initialized successfully")
            
            # Try to initialize optional components
            self._initialize_embedding_model()
            self._initialize_gnn_model()
            
            self._initialized = True
            logger.info("CompetenceTreeService initialized successfully")
        except Exception as e:
            logger.error(f"Error during service initialization: {str(e)}")
            logger.error(traceback.format_exc())
    
    def _initialize_pinecone(self) -> bool:
        """
        Initialise la connexion à Pinecone.
        
        Returns:
            bool: True si l'initialisation a réussi, False sinon
        """
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                logger.error("Clé API Pinecone non définie dans les variables d'environnement")
                return False
            
            self.pinecone_client = Pinecone(api_key=api_key)
            self.index = self.pinecone_client.Index(PINECONE_INDEX)
            logger.info(f"Connexion à l'index Pinecone '{PINECONE_INDEX}' établie avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Pinecone: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def _initialize_embedding_model(self):
        """
        Initialise le modèle d'embedding pour la recherche vectorielle (lazy loading).
        """
        # Don't initialize here - use lazy loading in get_embedding_model()
        self.embedding_model = None
        logger.info("Embedding model will be loaded on first use (lazy loading)")
    
    def get_embedding_model(self):
        """Get or initialize the embedding model with lazy loading"""
        if self.embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading competence tree embedding model...")
                # Force CPU to avoid MPS issues on macOS
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                logger.info("Competence tree embedding model loaded successfully on CPU")
            except Exception as e:
                logger.error(f"Failed to initialize embedding model: {str(e)}")
                logger.error(traceback.format_exc())
                raise e
        return self.embedding_model
    
    def _initialize_gnn_model(self):
        """
        Initialize the GNN model for graph traversal.
        """
        try:
            import torch
            model_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "services", "GNN", "best_model_20250520_022237.pt"
            )
            
            if not os.path.exists(model_path):
                logger.warning(f"GNN model file not found: {model_path}")
                return
            
            # Load the checkpoint
            checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
            
            # Initialize the model
            from .GNN.GraphSage import CareerTreeModel
            self.gnn_model = CareerTreeModel(
                input_dim=384,  # Embedding dimension
                hidden_dim=128,
                output_dim=128,
                dropout=0.2
            )
            
            # Load model weights
            if "model_state_dict" not in checkpoint:
                logger.warning("Checkpoint does not contain 'model_state_dict'")
                return
            
            self.gnn_model.load_state_dict(checkpoint["model_state_dict"])
            self.gnn_model.eval()  # Set to evaluation mode
            
            logger.info("GNN model loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize GNN model: {str(e)}")
            logger.warning(traceback.format_exc())
            self.gnn_model = None
    
    def _convert_score_to_similarity(self, score: float) -> float:
        """
        Convertit un score de distance Pinecone en score de similarité.
        
        Args:
            score: Score de distance Pinecone
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        return 1.0 - score
    
    def get_user_embedding(self, db: Session, user_id: int) -> Optional[np.ndarray]:
        """
        Récupère l'embedding de compétences d'un utilisateur depuis la base de données.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            np.ndarray: Embedding de l'utilisateur ou None en cas d'échec
        """
        try:
            # Récupérer l'embedding depuis la base de données
            query = text("SELECT esco_embedding FROM user_profiles WHERE user_id = :user_id")
            result = db.execute(query, {"user_id": user_id}).fetchone()
            
            if not result or not result[0]:
                logger.error(f"Aucun embedding trouvé pour l'utilisateur {user_id}")
                return None
            
            # Convertir la chaîne en tableau numpy
            import ast
            embedding = np.array(ast.literal_eval(result[0]), dtype=np.float32)
            logger.info(f"Embedding récupéré avec succès pour l'utilisateur {user_id}: {embedding.shape}")
            return embedding
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'embedding: {str(e)}")
            return None
    
    def infer_anchor_skills(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        Infer 5 anchor skills from user profile following palmier specification.
        
        This method:
        1. Uses LLM to extract 5 skills from user narrative + psychometric data
        2. Formats skills using ESCO templates
        3. Generates embeddings and matches in Pinecone
        4. Returns anchor skill IDs with metadata
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of 5 anchor skill dictionaries with Pinecone matches
        """
        try:
            logger.info(f"Starting anchor skill inference for user {user_id}")
            
            # Step 1: LLM Inference - Extract 5 skills from user profile
            inferred_skills = self.llm_service.infer_anchor_skills(db, user_id)
            if not inferred_skills:
                logger.error(f"No skills inferred for user {user_id}")
                return []
            
            logger.info(f"LLM inferred {len(inferred_skills)} skills for user {user_id}")
            
            # Step 2: Get user context for ESCO formatting
            user_context = self.llm_service.get_user_profile_data(db, user_id)
            
            # Step 3: ESCO Formatting - Format each skill according to ESCO standards  
            formatted_skills = self.esco_service.format_multiple_skills(inferred_skills, user_context.get("demographics", {}))
            
            # Step 4: Pinecone Matching - Generate embeddings and find matches
            anchor_skills = []
            for formatted_skill in formatted_skills:
                try:
                    # Create searchable text for embedding
                    searchable_text = self.esco_service.create_searchable_text(formatted_skill)
                    
                    # Generate embedding
                    try:
                        embedding_model = self.get_embedding_model()
                    except Exception as e:
                        logger.warning(f"Embedding model not available, using fallback: {str(e)}")
                        continue
                    
                    embedding = self.get_embedding_model().encode([searchable_text])[0]
                    
                    # Query Pinecone for top match
                    matches = self.query_skill_recommendations(embedding, top_k=1)
                    
                    if matches:
                        match = matches[0]
                        anchor_skill = {
                            "id": match["id"],
                            "original_label": formatted_skill["original_label"], 
                            "esco_label": formatted_skill["esco_label"],
                            "esco_description": formatted_skill["esco_description"],
                            "score": match["score"],
                            "metadata": match["metadata"],
                            "justification": formatted_skill.get("original_justification", ""),
                            "confidence": formatted_skill.get("confidence", 0.5),
                            "category": formatted_skill.get("category", "general"),
                            "applications": formatted_skill.get("applications", [])
                        }
                        anchor_skills.append(anchor_skill)
                        logger.info(f"Found Pinecone match for skill '{formatted_skill['esco_label']}': {match['id']}")
                    else:
                        logger.warning(f"No Pinecone match found for skill: {formatted_skill['esco_label']}")
                        
                except Exception as e:
                    logger.error(f"Error processing skill '{formatted_skill.get('esco_label', 'unknown')}': {str(e)}")
                    continue
            
            if len(anchor_skills) < 3:
                logger.error(f"Only found {len(anchor_skills)} valid anchor skills for user {user_id}")
                return []
            
            logger.info(f"Successfully inferred {len(anchor_skills)} anchor skills for user {user_id}")
            return anchor_skills[:5]  # Ensure exactly 5 or fewer
            
        except Exception as e:
            logger.error(f"Error inferring anchor skills for user {user_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return []

    def query_skill_recommendations(self, embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Interroge l'index Pinecone pour obtenir les recommandations de compétences.
        
        Args:
            embedding: Embedding de l'utilisateur
            top_k: Nombre de recommandations à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des recommandations de compétences
        """
        try:
            if self.index is None:
                logger.info("Index Pinecone non initialisé, tentative d'initialisation...")
                if not self._initialize_pinecone():
                    logger.error("Impossible d'initialiser Pinecone")
                    return []
                logger.info("Index Pinecone initialisé avec succès")
            
            vector = embedding.tolist()
            logger.info(f"Vecteur d'embedding préparé pour la requête Pinecone: {len(vector)} dimensions")
            
            # Interroger Pinecone pour les compétences uniquement
            logger.info("Envoi de la requête à Pinecone...")
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                filter={"type": {"$eq": "skill"}},
                include_metadata=True
            )
            logger.info(f"Réponse reçue de Pinecone: {len(results.matches)} résultats")
            
            recommendations = []
            for match in results.matches:
                try:
                    similarity = self._convert_score_to_similarity(match.score)
                    recommendation = {
                        "id": match.id,
                        "score": similarity,
                        "metadata": match.metadata
                    }
                    recommendations.append(recommendation)
                    logger.info(f"Recommandation ajoutée: {match.id} (score: {similarity:.2f})")
                except Exception as e:
                    logger.error(f"Erreur lors du traitement du résultat Pinecone {match.id}: {str(e)}")
                    continue
            
            logger.info(f"Récupération de {len(recommendations)} recommandations de compétences réussie")
            return recommendations
        except Exception as e:
            logger.error(f"Erreur lors de la requête Pinecone: {str(e)}")
            import traceback
            logger.error(f"Traceback complet: {traceback.format_exc()}")
            return []
    
    def _generate_challenge_with_llm(self, skill_label: str, difficulty: str, user_age: int) -> Dict[str, Any]:
        """
        Génère un défi pour une compétence en utilisant un LLM.
        
        Args:
            skill_label: Libellé de la compétence
            difficulty: Niveau de difficulté (débutant, intermédiaire, avancé)
            user_age: Âge de l'utilisateur
            
        Returns:
            Dict[str, Any]: Défi généré par le LLM
        """
        try:
            # Configure OpenAI
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            if not os.getenv("OPENAI_API_KEY"):
                logger.error("Clé API OpenAI non définie")
                return None

            # Construire le prompt pour le LLM
            prompt = f"""
            Tu dois générer un défi pratique pour développer la compétence "{skill_label}" à un niveau {difficulty}.
            
            Contraintes:
            - Le défi doit être adapté à une personne de {user_age} ans
            - Le défi doit être réalisable en moins d'une semaine
            - Le défi doit être concret et actionnable
            - Le défi doit être mesurable (comment savoir qu'on a réussi)
            
            IMPORTANT: Réponds UNIQUEMENT avec un objet JSON valide, sans aucun texte supplémentaire.
            Format JSON requis:
            {{
                "title": "Titre court et accrocheur",
                "description": "Description détaillée en 3-4 phrases",
                "success_criteria": "Comment mesurer le succès",
                "estimated_duration": "Durée estimée en heures",
                "resources_needed": "Ressources nécessaires"
            }}
            """

            # Appeler l'API OpenAI avec fallback
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",  # This model supports JSON mode
                    messages=[
                        {"role": "system", "content": "Tu es un expert en développement de compétences et en création de défis d'apprentissage. Tu réponds UNIQUEMENT en JSON valide, sans aucun texte supplémentaire."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500,
                    response_format={"type": "json_object"}  # Force JSON response
                )
            except Exception as e:
                if "response_format" in str(e):
                    logger.warning(f"JSON format not supported for challenge generation, trying without response_format: {str(e)}")
                    # Fallback without response_format
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Tu es un expert en développement de compétences. Réponds UNIQUEMENT en JSON dans ce format exact: {\"title\": \"titre\", \"description\": \"description\", \"success_criteria\": \"critères\", \"estimated_duration\": \"durée\", \"resources_needed\": \"ressources\"}"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                else:
                    raise e

            # Extraire la réponse
            if not response.choices:
                logger.error("LLM response has no choices")
                return None
                
            challenge_json = response.choices[0].message.content
            logger.debug(f"LLM raw output for {skill_label}: {challenge_json}")
            
            # Valider que la réponse n'est pas vide
            if not challenge_json or not challenge_json.strip():
                logger.error(f"Empty LLM response for skill {skill_label}")
                return None
            
            try:
                # Parser la réponse JSON
                challenge_data = json.loads(challenge_json)
                
                # Valider la structure de la réponse
                required_fields = ["title", "description", "success_criteria", "estimated_duration", "resources_needed"]
                missing_fields = [field for field in required_fields if field not in challenge_data]
                
                if missing_fields:
                    logger.error(f"LLM response missing required fields for skill {skill_label}: {missing_fields}")
                    return None
                
                return challenge_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response for skill {skill_label}: {str(e)}")
                logger.error(f"Raw response: {challenge_json}")
                return None

        except Exception as e:
            logger.error(f"Erreur lors de la génération du défi avec LLM pour {skill_label}: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def generate_challenge(self, skill_label: str, user_age: int) -> Dict[str, Any]:
        """
        Génère un défi pour une compétence donnée en utilisant un LLM.
        
        Args:
            skill_label: Libellé de la compétence
            user_age: Âge de l'utilisateur
            
        Returns:
            Dict[str, Any]: Défi généré avec récompense XP
        """
        try:
            # Déterminer le niveau de difficulté en fonction de l'âge
            if user_age < 18:
                difficulty = "débutant"
                xp_reward = random.randint(10, 30)
            elif user_age < 25:
                difficulty = "intermédiaire"
                xp_reward = random.randint(20, 50)
            else:
                difficulty = "avancé"
                xp_reward = random.randint(40, 100)
            
            # Générer le défi avec le LLM
            llm_challenge = self._generate_challenge_with_llm(skill_label, difficulty, user_age)
            
            if not llm_challenge:
                # Fallback si le LLM échoue
                logger.warning(f"Utilisation du défi par défaut pour {skill_label}")
                llm_challenge = {
                    "title": f"Maîtrisez {skill_label}",
                    "description": f"Recherchez et suivez un tutoriel en ligne sur {skill_label}. Pratiquez les concepts appris pendant au moins 3 heures.",
                    "success_criteria": "Compléter le tutoriel et créer un petit projet démontrant la compréhension",
                    "estimated_duration": "3-5 heures",
                    "resources_needed": "Accès Internet, ordinateur"
                }
            
            # Construire la réponse finale
            challenge_data = {
                "skill_id": skill_label.replace(" ", "_").lower(),
                "skill_label": skill_label,
                "title": llm_challenge.get("title", f"Défi: {skill_label}"),
                "description": llm_challenge.get("description", f"Pratiquez {skill_label} pendant une semaine."),
                "success_criteria": llm_challenge.get("success_criteria", "Compléter le défi avec succès"),
                "estimated_duration": llm_challenge.get("estimated_duration", "3-5 heures"),
                "resources_needed": llm_challenge.get("resources_needed", "Accès Internet"),
                "xp_reward": xp_reward,
                "difficulty": difficulty
            }
            
            return challenge_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du défi: {str(e)}")
            return None

    def create_skill_tree(self, db: Session, user_id: int, max_depth: int = 3, max_nodes_per_level: int = 5) -> Dict[str, Any]:
        """
        Crée un arbre de compétences pour un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            max_depth: Profondeur maximale de l'arbre
            max_nodes_per_level: Nombre maximum de nœuds par niveau
            
        Returns:
            Dict[str, Any]: Arbre de compétences généré
        """
        try:
            # Generate a single UUID for the entire tree
            graph_id = str(uuid4())
            logger.info(f"Generated new graph_id: {graph_id} for user {user_id}")
            
            # Récupérer l'âge de l'utilisateur
            query = text("SELECT age FROM user_profiles WHERE user_id = :user_id")
            result = db.execute(query, {"user_id": user_id}).fetchone()
            user_age = result[0] if result and result[0] else 25
            logger.info(f"Âge de l'utilisateur {user_id}: {user_age}")
            
            # Step 1: Infer anchor skills using new LLM pipeline
            anchor_skills = self.infer_anchor_skills(db, user_id)
            if not anchor_skills:
                logger.error(f"No anchor skills inferred for user {user_id}")
                return {}
            logger.info(f"Anchor skills inferred for user {user_id}: {len(anchor_skills)}")
            
            # Step 2: For now, use enhanced simple skill tree with connections
            # GraphSAGE traversal is temporarily disabled due to performance issues
            logger.info(f"Creating enhanced skill tree for user {user_id} with {len(anchor_skills)} anchor skills")
            gamified_graph = self._create_enhanced_skill_tree(anchor_skills, user_age, graph_id, db, max_depth, max_nodes_per_level)
            
            # Ensure anchors are stored properly
            if not gamified_graph.get("anchors"):
                gamified_graph["anchors"] = [skill["id"] for skill in anchor_skills]
            if not gamified_graph.get("anchor_metadata"):
                gamified_graph["anchor_metadata"] = anchor_skills
            
            logger.info(f"Storing {len(anchor_skills)} anchor skills in tree data for user {user_id}")
            for skill in anchor_skills:
                logger.debug(f"Anchor skill: {skill.get('esco_label', skill.get('original_label', 'Unknown'))}")
            
            logger.info(f"Arbre de compétences créé avec succès pour l'utilisateur {user_id} avec graph_id {graph_id}")
            return gamified_graph
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'arbre de compétences: {str(e)}")
            logger.error(traceback.format_exc())
            return {}
    
    def create_skill_tree_from_anchors(self, db: Session, user_id: int, anchor_skills: List[str], 
                                     max_depth: int = 3, max_nodes_per_level: int = 5, 
                                     include_occupations: bool = True) -> Dict[str, Any]:
        """
        Create a skill tree from specific anchor skills provided by the user.
        
        Args:
            db: Database session
            user_id: User ID
            anchor_skills: List of 5 ESCO skill IDs
            max_depth: Maximum tree depth
            max_nodes_per_level: Maximum nodes per level
            include_occupations: Whether to include occupation nodes
            
        Returns:
            Dict containing the generated tree data
        """
        try:
            # Generate a single UUID for the entire tree
            graph_id = str(uuid4())
            logger.info(f"Generated new graph_id: {graph_id} for user {user_id} with provided anchor skills")
            
            # Get user age for challenge generation
            query = text("SELECT age FROM user_profiles WHERE user_id = :user_id")
            result = db.execute(query, {"user_id": user_id}).fetchone()
            user_age = result[0] if result and result[0] else 25
            logger.info(f"User age for {user_id}: {user_age}")
            
            # Validate and format anchor skills
            formatted_anchors = []
            for skill_id in anchor_skills:
                # Format skill data for tree generation
                skill_data = {
                    "id": skill_id,
                    "esco_id": skill_id,
                    "esco_label": f"Skill {skill_id}",  # This will be enriched by ESCO lookup
                    "is_anchor": True
                }
                formatted_anchors.append(skill_data)
            
            logger.info(f"Creating tree from {len(formatted_anchors)} anchor skills for user {user_id}")
            
            # Use the enhanced skill tree creation method
            gamified_graph = self._create_enhanced_skill_tree(
                formatted_anchors, 
                user_age, 
                graph_id, 
                db, 
                max_depth, 
                max_nodes_per_level
            )
            
            # Ensure anchors are stored properly
            gamified_graph["anchors"] = anchor_skills
            gamified_graph["anchor_metadata"] = formatted_anchors
            gamified_graph["graph_id"] = graph_id
            
            logger.info(f"Skill tree created successfully from anchor skills for user {user_id}")
            return gamified_graph
            
        except Exception as e:
            logger.error(f"Error creating skill tree from anchors: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _create_enhanced_skill_tree(self, anchor_skills: List[Dict[str, Any]], user_age: int, graph_id: str, db: Session, max_depth: int = 3, max_nodes_per_level: int = 5) -> Dict[str, Any]:
        """
        Create an enhanced skill tree using proper graph traversal like the occupation tree.
        
        This method:
        1. Uses GraphTraversalService for proper multi-level expansion
        2. Creates a connected skill tree similar to the inspiration image
        3. Applies gamification rules properly
        4. Generates challenges for all nodes
        
        Args:
            anchor_skills: List of anchor skills with Pinecone IDs
            user_age: User age for challenge generation
            graph_id: Unique graph identifier
            db: Database session
            
        Returns:
            Enhanced skill tree structure with proper connections
        """
        try:
            # Import GraphTraversalService - try multiple import methods
            import sys
            import os
            
            # Add path to sys.path to import graph_traversal_service
            backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            competence_tree_dev_path = os.path.join(backend_path, "dev", "competenceTree_dev")
            
            logger.info(f"Looking for graph_traversal_service at: {competence_tree_dev_path}")
            
            if not os.path.exists(competence_tree_dev_path):
                logger.error(f"competenceTree_dev path does not exist: {competence_tree_dev_path}")
                raise ImportError(f"Cannot find competenceTree_dev at: {competence_tree_dev_path}")
                
            if competence_tree_dev_path not in sys.path:
                sys.path.insert(0, competence_tree_dev_path)
                
            from graph_traversal_service import GraphTraversalService
            logger.info(f"Successfully imported GraphTraversalService from: {competence_tree_dev_path}")
            
            # Initialize graph traversal service
            try:
                graph_service = GraphTraversalService()
                logger.info("GraphTraversalService initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize GraphTraversalService: {str(e)}")
                # Fall back to simplified tree if graph service fails
                return self._create_simple_skill_tree(anchor_skills, user_age, graph_id)
            
            # Extract anchor node IDs for graph traversal
            anchor_node_ids = [skill["id"] for skill in anchor_skills]
            logger.info(f"Starting graph traversal from {len(anchor_node_ids)} anchor nodes")
            
            # Traverse the graph from anchor nodes with conservative parameters to prevent timeouts
            graph_data = graph_service.traverse_graph(
                anchor_node_ids=anchor_node_ids,
                max_depth=min(max_depth, 3),  # Limit depth to prevent explosion
                min_similarity=0.5,  # Higher threshold for better connections
                max_nodes_per_level=min(max_nodes_per_level, 3)  # Conservative limit to prevent timeout
            )
            
            if not graph_data.get("nodes"):
                logger.warning("Graph traversal returned no nodes, falling back to simple tree")
                return self._create_simple_skill_tree(anchor_skills, user_age, graph_id)
            
            logger.info(f"Graph traversal successful: {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges")
            
            # Convert graph data to competence tree format
            processed_nodes = []
            anchor_lookup = {skill["id"]: skill for skill in anchor_skills}
            
            logger.info(f"Processing {len(graph_data['nodes'])} nodes from graph traversal")
            logger.info(f"Anchor lookup has {len(anchor_lookup)} entries: {list(anchor_lookup.keys())}")
            
            anchor_count = 0
            for node_id, node_info in graph_data["nodes"].items():
                is_anchor = node_info.get("is_anchor", False)
                depth = node_info.get("depth", 0)
                
                if is_anchor:
                    anchor_count += 1
                    logger.info(f"Processing anchor node {anchor_count}: {node_id} -> {node_info.get('label', 'No label')}")
                
                # Get skill label from metadata or ESCO label
                skill_label = node_info.get("label", "")
                if not skill_label and node_id in anchor_lookup:
                    skill_label = anchor_lookup[node_id]["esco_label"]
                if not skill_label:
                    skill_label = node_info.get("metadata", {}).get("preferredLabel", node_id)
                
                # Generate challenge for anchor nodes only to prevent too many LLM calls
                challenge_data = {}
                if is_anchor:  # Only generate challenges for anchor nodes to prevent timeout
                    challenge_data = self.generate_challenge(skill_label, user_age)
                
                # Determine initial visibility based on gamification rules
                is_visible = is_anchor  # Anchors always visible
                is_revealed = is_anchor  # Anchors always revealed
                initial_state = "available" if is_anchor else "locked"
                
                # Apply 80% visibility rule for non-anchor nodes (increased for better tree display)
                if not is_anchor and depth <= 2 and random.random() < 0.8:
                    is_visible = True
                    is_revealed = True
                    initial_state = "available"
                    # Skip challenge generation for non-anchor nodes to prevent timeout
                    # Challenges will be generated when nodes are revealed through gameplay
                
                processed_node = {
                    "id": node_id,
                    "label": skill_label,
                    "type": node_info.get("type", "skill"),
                    "depth": depth,
                    "is_anchor": is_anchor,
                    "graph_id": graph_id,
                    "challenge": challenge_data.get("description", ""),
                    "xp_reward": challenge_data.get("xp_reward", 25),
                    "visible": is_visible,
                    "revealed": is_revealed,
                    "state": initial_state,
                    "notes": "",
                    "metadata": node_info.get("metadata", {}),
                    "similarity_score": node_info.get("similarity_score", 0.5)
                }
                
                # Add anchor-specific metadata
                if is_anchor and node_id in anchor_lookup:
                    anchor_data = anchor_lookup[node_id]
                    processed_node.update({
                        "esco_label": anchor_data.get("esco_label", skill_label),
                        "esco_description": anchor_data.get("esco_description", ""),
                        "justification": anchor_data.get("justification", ""),
                        "confidence": anchor_data.get("confidence", 0.5),
                        "category": anchor_data.get("category", "general"),
                        "applications": anchor_data.get("applications", [])
                    })
                
                processed_nodes.append(processed_node)
            
            # Convert edges to the expected format
            processed_edges = []
            for edge in graph_data.get("edges", []):
                processed_edges.append({
                    "source": edge["source"],
                    "target": edge["target"],
                    "weight": edge.get("weight", 1.0),
                    "type": edge.get("type", "similarity")
                })
            
            # Add occupations connected to skills (like in the inspiration image)
            occupation_nodes, occupation_edges = self._add_connected_occupations(
                processed_nodes, anchor_skills, graph_service, user_age, graph_id
            )
            
            # Combine all nodes and edges
            all_nodes = processed_nodes + occupation_nodes
            all_edges = processed_edges + occupation_edges
            
            logger.info(f"Enhanced skill tree created with {len(all_nodes)} total nodes ({len(processed_nodes)} skills, {len(occupation_nodes)} occupations) and {len(all_edges)} edges")
            
            return {
                "nodes": all_nodes,
                "edges": all_edges,
                "graph_id": graph_id,
                "anchors": [skill["id"] for skill in anchor_skills],
                "anchor_metadata": anchor_skills,
                "tree_type": "enhanced_competence_tree",
                "generation_method": "graph_traversal"
            }
            
        except Exception as e:
            logger.error(f"Error creating enhanced skill tree with graph traversal: {str(e)}")
            logger.error(traceback.format_exc())
            # Fall back to simple tree
            return self._create_simple_skill_tree(anchor_skills, user_age, graph_id)
    
    def _add_connected_occupations(self, skill_nodes: List[Dict], anchor_skills: List[Dict], 
                                 graph_service, user_age: int, graph_id: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Add occupation nodes connected to skills (like in the inspiration image).
        
        Args:
            skill_nodes: Current skill nodes
            anchor_skills: Original anchor skills
            graph_service: Graph traversal service
            user_age: User age
            graph_id: Graph identifier
            
        Returns:
            Tuple of (occupation_nodes, occupation_edges)
        """
        try:
            occupation_nodes = []
            occupation_edges = []
            
            # Find occupations related to anchor skills through Pinecone
            if self.index:
                for anchor_skill in anchor_skills:
                    try:
                        # Query for related occupations (limited to prevent timeout)
                        results = self.index.query(
                            id=anchor_skill["id"],
                            top_k=1,  # Get only top 1 related occupation per anchor to prevent timeout
                            filter={"type": {"$eq": "occupation"}},
                            include_metadata=True
                        )
                        
                        for match in results.matches:
                            if match.score < 0.6:  # Only high-similarity occupations
                                continue
                                
                            occupation_id = match.id
                            occupation_metadata = match.metadata
                            occupation_label = occupation_metadata.get("preferredLabel", 
                                                                     occupation_metadata.get("title", occupation_id))
                            
                            # Check if occupation already added
                            if any(node["id"] == occupation_id for node in occupation_nodes):
                                continue
                            
                            # Create occupation node
                            occupation_node = {
                                "id": occupation_id,
                                "label": occupation_label,
                                "type": "occupation",
                                "depth": 2,  # Occupations at depth 2
                                "is_anchor": False,
                                "graph_id": graph_id,
                                "challenge": "",  # Occupations don't have challenges
                                "xp_reward": 0,
                                "visible": random.random() < 0.5,  # 50% visible initially
                                "revealed": random.random() < 0.5,
                                "state": "locked",
                                "notes": "",
                                "metadata": occupation_metadata,
                                "similarity_score": self._convert_score_to_similarity(match.score)
                            }
                            
                            occupation_nodes.append(occupation_node)
                            
                            # Add edge from anchor skill to occupation
                            occupation_edges.append({
                                "source": anchor_skill["id"],
                                "target": occupation_id,
                                "weight": self._convert_score_to_similarity(match.score),
                                "type": "skill_to_occupation"
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error finding occupations for {anchor_skill['id']}: {str(e)}")
            
            logger.info(f"Added {len(occupation_nodes)} occupation nodes connected to skills")
            return occupation_nodes, occupation_edges
            
        except Exception as e:
            logger.error(f"Error adding connected occupations: {str(e)}")
            return [], []
    
    def _create_simple_skill_tree(self, anchor_skills: List[Dict[str, Any]], user_age: int, graph_id: str) -> Dict[str, Any]:
        """
        Create a simple skill tree when graph traversal fails.
        
        Args:
            anchor_skills: List of anchor skills
            user_age: User age for challenge generation
            graph_id: Unique graph identifier
            
        Returns:
            Simple skill tree structure
        """
        try:
            nodes = []
            edges = []
            
            for i, skill in enumerate(anchor_skills):
                # Generate challenge for this skill
                challenge_data = self.generate_challenge(skill["esco_label"], user_age)
                
                node = {
                    "id": skill["id"],
                    "label": skill["esco_label"],
                    "type": "skill",
                    "depth": 0,
                    "is_anchor": True,
                    "graph_id": graph_id,
                    "challenge": challenge_data.get("description", ""),
                    "xp_reward": challenge_data.get("xp_reward", 25),
                    "visible": True,
                    "revealed": True,
                    "state": "available",
                    "notes": "",
                    "metadata": skill.get("metadata", {})
                }
                nodes.append(node)
            
            logger.info(f"Created simple skill tree with {len(anchor_skills)} anchor skills for user")
            return {
                "nodes": nodes,
                "edges": edges,
                "graph_id": graph_id,
                "anchors": [skill["id"] for skill in anchor_skills],
                "anchor_metadata": anchor_skills
            }
            
        except Exception as e:
            logger.error(f"Error creating simple skill tree: {str(e)}")
            return {"nodes": [], "edges": [], "graph_id": graph_id}
    
    def _process_graph_nodes(self, graph_data: Dict[str, Any], anchor_skills: List[Dict[str, Any]], user_age: int, graph_id: str) -> Dict[str, Any]:
        """
        Process graph nodes and add challenge data.
        
        Args:
            graph_data: Raw graph data from traversal
            anchor_skills: Anchor skills with metadata
            user_age: User age for challenge generation
            graph_id: Unique graph identifier
            
        Returns:
            Processed graph data
        """
        try:
            # Create lookup for anchor skill metadata
            anchor_lookup = {skill["id"]: skill for skill in anchor_skills}
            
            # Process nodes
            if isinstance(graph_data.get("nodes"), dict):
                # Convert dict format to list format
                processed_nodes = []
                for node_id, node_data in graph_data["nodes"].items():
                    processed_node = self._process_single_node(node_data, anchor_lookup, user_age, graph_id)
                    processed_nodes.append(processed_node)
                graph_data["nodes"] = processed_nodes
            elif isinstance(graph_data.get("nodes"), list):
                # Process list format
                processed_nodes = []
                for node_data in graph_data["nodes"]:
                    processed_node = self._process_single_node(node_data, anchor_lookup, user_age, graph_id)
                    processed_nodes.append(processed_node)
                graph_data["nodes"] = processed_nodes
            
            graph_data["graph_id"] = graph_id
            return graph_data
            
        except Exception as e:
            logger.error(f"Error processing graph nodes: {str(e)}")
            return graph_data
    
    def _process_single_node(self, node_data: Dict[str, Any], anchor_lookup: Dict[str, Any], user_age: int, graph_id: str) -> Dict[str, Any]:
        """
        Process a single node and add required fields.
        
        Args:
            node_data: Raw node data
            anchor_lookup: Lookup for anchor skill metadata
            user_age: User age for challenge generation
            graph_id: Unique graph identifier
            
        Returns:
            Processed node data
        """
        node_id = node_data.get("id", "")
        skill_label = node_data.get("label", node_id)
        depth = node_data.get("depth", 0)
        is_anchor = node_id in anchor_lookup
        
        # Only generate challenge for anchor nodes initially (to avoid hundreds of API calls)
        challenge_data = None
        if is_anchor:
            challenge_data = self.generate_challenge(skill_label, user_age)
        
        processed_node = {
            "id": node_id,
            "label": skill_label,
            "type": node_data.get("type", "skill"),
            "depth": depth,
            "is_anchor": is_anchor,
            "graph_id": graph_id,
            "challenge": challenge_data.get("description", "") if challenge_data else "",
            "xp_reward": challenge_data.get("xp_reward", 25) if challenge_data else 25,
            "visible": is_anchor,  # Only anchors visible initially
            "revealed": is_anchor,  # Only anchors revealed initially
            "state": "available" if is_anchor else "locked",
            "notes": "",
            "metadata": node_data.get("metadata", {})
        }
        
        # Add anchor-specific metadata
        if is_anchor and node_id in anchor_lookup:
            anchor_data = anchor_lookup[node_id]
            processed_node.update({
                "esco_label": anchor_data.get("esco_label", skill_label),
                "esco_description": anchor_data.get("esco_description", ""),
                "justification": anchor_data.get("justification", ""),
                "confidence": anchor_data.get("confidence", 0.5),
                "category": anchor_data.get("category", "general"),
                "applications": anchor_data.get("applications", [])
            })
        
        return processed_node
    
    def _apply_gamification_rules(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply gamification rules including 70% hidden nodes.
        
        Args:
            graph_data: Processed graph data
            
        Returns:
            Gamified graph data
        """
        try:
            nodes = graph_data.get("nodes", [])
            if not nodes:
                return graph_data
            
            # Separate anchor and non-anchor nodes
            anchor_nodes = [node for node in nodes if node.get("is_anchor", False)]
            non_anchor_nodes = [node for node in nodes if not node.get("is_anchor", False)]
            
            # Calculate how many non-anchor nodes to reveal (30% as per palmier spec)
            total_non_anchors = len(non_anchor_nodes)
            nodes_to_reveal = max(1, int(total_non_anchors * 0.3))
            
            # Randomly select nodes to reveal (prioritize depth 1 nodes)
            depth_1_nodes = [node for node in non_anchor_nodes if node.get("depth", 0) == 1]
            other_nodes = [node for node in non_anchor_nodes if node.get("depth", 0) != 1]
            
            # First reveal some depth 1 nodes, then others
            revealed_nodes = []
            if depth_1_nodes:
                depth_1_to_reveal = min(len(depth_1_nodes), max(1, nodes_to_reveal // 2))
                revealed_nodes.extend(random.sample(depth_1_nodes, depth_1_to_reveal))
                nodes_to_reveal -= depth_1_to_reveal
            
            if nodes_to_reveal > 0 and other_nodes:
                other_to_reveal = min(len(other_nodes), nodes_to_reveal)
                revealed_nodes.extend(random.sample(other_nodes, other_to_reveal))
            
            # Update visibility for revealed nodes
            revealed_ids = {node["id"] for node in revealed_nodes}
            for node in nodes:
                if not node.get("is_anchor", False):
                    if node["id"] in revealed_ids:
                        node["visible"] = True
                        node["revealed"] = True
                        node["state"] = "available"
                    else:
                        node["visible"] = False
                        node["revealed"] = False
                        node["state"] = "hidden"
            
            logger.info(f"Applied gamification: {len(anchor_nodes)} anchors, {len(revealed_nodes)}/{total_non_anchors} non-anchors revealed")
            return graph_data
            
        except Exception as e:
            logger.error(f"Error applying gamification rules: {str(e)}")
            return graph_data
    
    def save_skill_tree(self, db: Session, user_id: int, tree_data: Dict[str, Any]) -> str:
        """
        Sauvegarde l'arbre de compétences dans la base de données.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            tree_data: Données de l'arbre de compétences
            
        Returns:
            str: ID du graphe sauvegardé (UUID)
        """
        try:
            import json
            import numpy as np
            
            # Classe personnalisée pour encoder les objets numpy en JSON
            class NumpyEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, np.ndarray):
                        return obj.tolist()
                    if isinstance(obj, np.integer):
                        return int(obj)
                    if isinstance(obj, np.floating):
                        return float(obj)
                    return super(NumpyEncoder, self).default(obj)
            
            # Nettoyer les données pour s'assurer qu'elles sont sérialisables
            def clean_for_json(data):
                if isinstance(data, dict):
                    return {k: clean_for_json(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [clean_for_json(item) for item in data]
                elif isinstance(data, np.ndarray):
                    return data.tolist()
                elif isinstance(data, (np.integer, np.floating)):
                    return float(data) if isinstance(data, np.floating) else int(data)
                else:
                    return data
            
            # Nettoyer les données avant la sérialisation
            clean_tree_data = clean_for_json(tree_data)
            
            # Get the graph_id from the tree data
            graph_id = tree_data.get("graph_id")
            if not graph_id:
                logger.error("No graph_id found in tree data")
                return None
            
            # Create new UserSkillTree instance with competenceTree column (as per palmier spec)
            skill_tree = UserSkillTree(
                user_id=user_id,
                graph_id=graph_id,  # Use the UUID from tree_data
                tree_data=clean_tree_data  # Store as JSONB directly
            )
            
            # Sauvegarder dans la base de données
            db.add(skill_tree)
            db.commit()
            db.refresh(skill_tree)
            
            logger.info(f"Arbre de compétences sauvegardé avec succès pour l'utilisateur {user_id} avec graph_id {graph_id}")
            return graph_id  # Return the UUID
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'arbre de compétences: {str(e)}")
            db.rollback()
            return None
    
    def complete_challenge(self, db: Session, node_id: str, user_id: int) -> Dict[str, Any]:
        """
        Complete a challenge and update user progress following palmier specification.
        
        Args:
            db: Database session
            node_id: ESCO node ID to complete
            user_id: User ID
            
        Returns:
            Dict with completion status and updated information
        """
        try:
            # Get the user's latest skill tree
            skill_tree = db.query(UserSkillTree).filter(
                UserSkillTree.user_id == user_id
            ).order_by(UserSkillTree.created_at.desc()).first()
            
            if not skill_tree:
                logger.error(f"No skill tree found for user {user_id}")
                return {"success": False, "error": "No skill tree found"}
            
            # Parse tree data
            tree_data = skill_tree.tree_data
            if isinstance(tree_data, str):
                tree_data = json.loads(tree_data)
            
            # Find the node to complete
            nodes = tree_data.get("nodes", [])
            node_to_complete = None
            node_index = -1
            
            for i, node in enumerate(nodes):
                if node.get("id") == node_id:
                    node_to_complete = node
                    node_index = i
                    break
            
            if not node_to_complete:
                logger.error(f"Node {node_id} not found in user {user_id}'s skill tree")
                return {"success": False, "error": "Node not found"}
            
            # Check if node is available to complete
            if node_to_complete.get("state") not in ["available", "locked"]:
                logger.warning(f"Node {node_id} is not available for completion (state: {node_to_complete.get('state')})")
                return {"success": False, "error": "Node not available for completion"}
            
            # Mark node as completed
            nodes[node_index]["state"] = "completed"
            nodes[node_index]["completed_at"] = json.dumps(datetime.now().isoformat())
            
            # Get XP reward
            xp_reward = node_to_complete.get("xp_reward", 25)
            
            # Update user progress
            from ..models.user_progress import UserProgress
            user_progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
            
            if user_progress:
                user_progress.total_xp = (user_progress.total_xp or 0) + xp_reward
                # Update level based on XP (simple progression: level = XP // 100 + 1)
                user_progress.level = (user_progress.total_xp // 100) + 1
                user_progress.last_completed_node = node_id
            else:
                # Create new progress record
                user_progress = UserProgress(
                    user_id=user_id,
                    total_xp=xp_reward,
                    level=1,
                    last_completed_node=node_id
                )
                db.add(user_progress)
            
            # Reveal children nodes (find edges where source is the completed node)
            edges = tree_data.get("edges", [])
            children_revealed = 0
            
            # Get user age for challenge generation
            query = text("SELECT age FROM user_profiles WHERE user_id = :user_id")
            result = db.execute(query, {"user_id": user_id}).fetchone()
            user_age = result[0] if result and result[0] else 25
            
            for edge in edges:
                if edge.get("source") == node_id:
                    target_id = edge.get("target")
                    # Find and reveal the target node
                    for i, node in enumerate(nodes):
                        if node.get("id") == target_id and node.get("state") == "hidden":
                            # Generate challenge for newly revealed node
                            if not nodes[i].get("challenge"):
                                skill_label = nodes[i].get("label", nodes[i].get("id", ""))
                                challenge_data = self.generate_challenge(skill_label, user_age)
                                if challenge_data:
                                    nodes[i]["challenge"] = challenge_data.get("description", "")
                                    nodes[i]["xp_reward"] = challenge_data.get("xp_reward", 25)
                            
                            nodes[i]["visible"] = True
                            nodes[i]["revealed"] = True
                            nodes[i]["state"] = "available"
                            children_revealed += 1
                            break
            
            # Update tree data
            tree_data["nodes"] = nodes
            skill_tree.tree_data = tree_data
            
            # Commit all changes
            db.commit()
            
            logger.info(f"Challenge {node_id} completed for user {user_id}: +{xp_reward} XP, {children_revealed} children revealed")
            
            return {
                "success": True,
                "xp_earned": xp_reward,
                "total_xp": user_progress.total_xp,
                "level": user_progress.level,
                "children_revealed": children_revealed,
                "node_state": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error completing challenge {node_id} for user {user_id}: {str(e)}")
            logger.error(traceback.format_exc())
            db.rollback()
            return {"success": False, "error": str(e)} 