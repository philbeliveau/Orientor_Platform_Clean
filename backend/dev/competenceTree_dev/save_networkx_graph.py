"""
Script utilitaire pour créer et sauvegarder le graphe NetworkX.

Ce script charge les données du graphe à partir des fichiers dans le dossier data/,
crée un graphe NetworkX, puis le sauvegarde dans un fichier pickle pour une utilisation ultérieure.
"""

import os
import sys
import json
import logging
import pickle
import torch
import networkx as nx
from pathlib import Path

# Configuration du logger
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_networkx_graph():
    """
    Crée et sauvegarde le graphe NetworkX à partir des données dans le dossier data/.
    """
    try:
        # Chemin vers le dossier de données
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        
        # Chemins vers les fichiers de données
        idx2node_path = os.path.join(data_dir, "idx2node.json")
        node2idx_path = os.path.join(data_dir, "node2idx.json")
        node_metadata_path = os.path.join(data_dir, "node_metadata.json")
        edge_index_path = os.path.join(data_dir, "edge_index.pt")
        edge_type_path = os.path.join(data_dir, "edge_type.json")
        edge_type_indices_path = os.path.join(data_dir, "edge_type_indices.json")
        
        # Chemin de sortie pour le graphe NetworkX
        output_path = os.path.join(data_dir, "networkx_graph.pkl")
        
        # Charger les mappages d'index
        logger.info("Chargement des mappages d'index...")
        with open(idx2node_path, 'r') as f:
            idx2node = json.load(f)
        
        with open(node2idx_path, 'r') as f:
            node2idx = json.load(f)
        
        # Charger les métadonnées des nœuds
        logger.info("Chargement des métadonnées des nœuds...")
        with open(node_metadata_path, 'r') as f:
            node_metadata = json.load(f)
        
        # Charger les index d'arêtes
        logger.info("Chargement des index d'arêtes...")
        edge_index = torch.load(edge_index_path)
        
        # Charger les informations sur les types d'arêtes (optionnel)
        edge_type = {}
        edge_type_indices = {}
        
        if os.path.exists(edge_type_path):
            logger.info("Chargement des types d'arêtes...")
            with open(edge_type_path, 'r') as f:
                edge_type = json.load(f)
        
        if os.path.exists(edge_type_indices_path):
            logger.info("Chargement des indices des types d'arêtes...")
            with open(edge_type_indices_path, 'r') as f:
                edge_type_indices = json.load(f)
        
        # Créer le graphe NetworkX
        logger.info("Création du graphe NetworkX...")
        G = nx.Graph()
        
        # Ajouter les nœuds avec leurs métadonnées
        logger.info(f"Ajout de {len(node_metadata)} nœuds au graphe...")
        for node_id, metadata in node_metadata.items():
            G.add_node(node_id, **metadata)
        
        # Ajouter les arêtes
        logger.info(f"Ajout de {edge_index.shape[1]} arêtes au graphe...")
        edges_added = 0
        
        for i in range(edge_index.shape[1]):
            if i % 10000 == 0 and i > 0:
                logger.info(f"Progression: {i}/{edge_index.shape[1]} arêtes ajoutées...")
            
            src_idx = edge_index[0, i].item()
            tgt_idx = edge_index[1, i].item()
            
            # Convertir les indices en IDs de nœuds
            src_id = idx2node.get(str(src_idx))
            tgt_id = idx2node.get(str(tgt_idx))
            
            if src_id and tgt_id:
                # Déterminer le type d'arête si disponible
                edge_type_value = "default"
                if str(i) in edge_type_indices:
                    type_idx = edge_type_indices[str(i)]
                    edge_type_value = edge_type.get(str(type_idx), "default")
                
                # Ajouter l'arête avec un poids par défaut de 1.0
                G.add_edge(src_id, tgt_id, weight=1.0, type=edge_type_value)
                edges_added += 1
        
        logger.info(f"Graphe NetworkX créé avec {len(G.nodes)} nœuds et {edges_added} arêtes")
        
        # Sauvegarder le graphe
        logger.info(f"Sauvegarde du graphe dans {output_path}...")
        with open(output_path, 'wb') as f:
            pickle.dump(G, f)
        
        logger.info("Graphe sauvegardé avec succès!")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la création et de la sauvegarde du graphe: {str(e)}")
        return False

if __name__ == "__main__":
    save_networkx_graph()