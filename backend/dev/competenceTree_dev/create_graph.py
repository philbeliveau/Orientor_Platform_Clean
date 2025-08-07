"""
Script pour créer et sauvegarder le graphe NetworkX.

Ce script peut être exécuté séparément pour créer et sauvegarder le graphe NetworkX
avant de lancer l'application Streamlit.
"""

import os
import sys
import time
import logging
from save_networkx_graph import save_networkx_graph

# Configuration du logger
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Fonction principale pour créer et sauvegarder le graphe NetworkX.
    """
    # Chemin vers le graphe prétraité
    networkx_graph_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "networkx_graph.pkl")
    
    # Vérifier si le graphe prétraité existe déjà
    if os.path.exists(networkx_graph_path):
        logger.info(f"Le graphe prétraité existe déjà: {networkx_graph_path}")
        overwrite = input("Voulez-vous recréer le graphe? (o/n): ").lower()
        if overwrite != 'o':
            logger.info("Opération annulée.")
            return
    
    # Mesurer le temps d'exécution
    start_time = time.time()
    
    # Créer et sauvegarder le graphe
    logger.info("Création et sauvegarde du graphe NetworkX en cours...")
    success = save_networkx_graph()
    
    # Afficher le résultat
    if success:
        elapsed_time = time.time() - start_time
        logger.info(f"Graphe NetworkX créé et sauvegardé avec succès en {elapsed_time:.2f} secondes!")
        logger.info(f"Chemin du graphe: {networkx_graph_path}")
    else:
        logger.error("Erreur lors de la création et de la sauvegarde du graphe NetworkX.")

if __name__ == "__main__":
    main()