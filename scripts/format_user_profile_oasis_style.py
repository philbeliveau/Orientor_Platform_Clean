import os
import sys
from typing import Dict, Any, List, Optional

# Vérifier les dépendances requises
DEPENDENCIES_MET = True
MISSING_DEPENDENCIES = []

try:
    from dotenv import load_dotenv
except ImportError:
    DEPENDENCIES_MET = False
    MISSING_DEPENDENCIES.append("python-dotenv")

try:
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
except ImportError:
    DEPENDENCIES_MET = False
    MISSING_DEPENDENCIES.append("langchain")

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    DEPENDENCIES_MET = False
    MISSING_DEPENDENCIES.append("langchain-openai")

# Fonction pour vérifier les dépendances
def check_dependencies():
    """Vérifie si toutes les dépendances sont installées et affiche un message d'erreur si ce n'est pas le cas."""
    if not DEPENDENCIES_MET:
        print("Erreur: Certaines dépendances requises ne sont pas installées.")
        print("Veuillez installer les packages suivants:")
        for dep in MISSING_DEPENDENCIES:
            print(f"  - {dep}")
        print("\nVous pouvez les installer avec la commande:")
        print(f"pip install {' '.join(MISSING_DEPENDENCIES)}")
        return False
    return True

# Charger les variables d'environnement si la dépendance est disponible
if "dotenv" not in MISSING_DEPENDENCIES:
    load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Template de prompt pour le formatage du profil utilisateur
PROFILE_FORMAT_TEMPLATE = """
Tu es un expert en formatage de données pour l'alignement sémantique.
Ta tâche est de reformater un profil utilisateur pour qu'il corresponde au format des descriptions d'emploi OaSIS.

Voici le format OaSIS de référence:
```
oasis_code: [code]
OaSIS Label - Final_x: [titre]
Job title text: [titres alternatifs séparés par |]
top_3_code: [code RIASEC]
Employment requirement: [exigences d'emploi]
Main duties: [tâches principales]
Leadership: [score]
Critical Thinking: [score]
... (autres compétences)
```

Voici le profil utilisateur à reformater:
- Nom: {name}
- Âge: {age}
- Niveau d'éducation: {education_level}
- Spécialisation: {major}
- Objectifs de carrière: {career_goals}
- Histoire personnelle: {story}
- Compétences: {skills}
- Titre du poste actuel: {job_title}
- Années d'expérience: {years_experience}

Scores de compétences (sur 5.0):
- Créativité: {creativity}
- Leadership: {leadership}
- Pensée critique: {critical_thinking}
- Résolution de problèmes: {problem_solving}
- Pensée analytique: {analytical_thinking}
- Attention aux détails: {attention_to_detail}
- Collaboration: {collaboration}
- Évaluation: {evaluation}
- Prise de décision: {decision_making}
- Tolérance au stress: {stress_tolerance}

Code RIASEC: {riasec_code}

Recommandations sauvegardées: {saved_recommendations}

INSTRUCTIONS IMPORTANTES:
1. Génère un code OaSIS fictif basé sur le titre du poste (format: 5 chiffres suivis d'un point et 2 chiffres)
2. Utilise le titre du poste actuel comme "OaSIS Label - Final_x"
3. Crée des titres alternatifs basés sur le titre actuel et les compétences pour "Job title text"
4. Utilise le code RIASEC fourni pour "top_3_code"
5. Formule les "Employment requirement" en fonction du niveau d'éducation et de la spécialisation
6. Résume les "Main duties" en fonction des objectifs de carrière, de l'histoire et des compétences
7. Convertis tous les scores de compétences sur une échelle de 0.0 à 5.0 (arrondi à 0.5 près)
8. N'utilise PAS d'adjectifs abstraits comme "motivé" ou "passionné"
9. Intègre les recommandations sauvegardées dans la description des tâches principales et des compétences
10. Si des recommandations sauvegardées sont fournies, ajoute une section "Related occupations" avec ces recommandations
11. Assure-toi que le résultat final est une chaîne multiligne unique avec le même format que l'exemple OaSIS

Retourne UNIQUEMENT le profil reformaté, sans commentaires ni explications supplémentaires.
"""

def format_user_profile(profile: Dict[str, Any], skills: Dict[str, float], riasec: Dict[str, str], saved_recommendations: List[Dict[str, str]] = None) -> Optional[str]:
    """
    Formate un profil utilisateur selon le style OaSIS pour l'alignement des embeddings.
    
    Args:
        profile: Dictionnaire contenant les informations de base du profil utilisateur
        skills: Dictionnaire contenant les scores de compétences de l'utilisateur
        riasec: Dictionnaire contenant les résultats du test RIASEC
        saved_recommendations: Liste de dictionnaires contenant les recommandations sauvegardées
        
    Returns:
        Une chaîne formatée selon le style OaSIS pour l'embedding
    """
    # Initialiser les recommandations sauvegardées si elles sont None
    if saved_recommendations is None:
        saved_recommendations = []
    # Vérifier que les clés nécessaires sont présentes
    required_profile_keys = [
        "user_id", "name", "age", "education_level", "major", 
        "career_goals", "story", "skills", "job_title", "years_experience"
    ]
    
    required_skills_keys = [
        "creativity", "leadership", "critical_thinking", "problem_solving",
        "analytical_thinking", "attention_to_detail", "collaboration",
        "evaluation", "decision_making", "stress_tolerance"
    ]
    
    # Vérifier les clés requises
    for key in required_profile_keys:
        if key not in profile:
            profile[key] = ""  # Valeur par défaut si manquante
    
    for key in required_skills_keys:
        if key not in skills:
            skills[key] = 3.0  # Valeur par défaut si manquante (score moyen)
    
    # Extraire le code RIASEC
    riasec_code = riasec.get("top_3_code", "RCI")  # Valeur par défaut si manquante
    
    # Formater les recommandations sauvegardées en une chaîne
    saved_recommendations_list = [rec.get("label", "") for rec in saved_recommendations if rec.get("label")]
    if saved_recommendations_list:
        saved_recommendations_str = ", ".join(saved_recommendations_list)
    else:
        saved_recommendations_str = "Aucune recommandation sauvegardée"
    
    # Créer un dictionnaire combiné pour le prompt
    prompt_data = {
        **profile,
        **skills,
        "riasec_code": riasec_code,
        "saved_recommendations": saved_recommendations_str
    }
    
    # Vérifier que toutes les dépendances sont installées
    if not check_dependencies():
        print("Impossible de formater le profil utilisateur: dépendances manquantes.")
        return None
        
    # Vérifier que la clé API OpenAI est disponible
    if not OPENAI_API_KEY:
        print("Erreur: La clé API OpenAI n'est pas définie dans les variables d'environnement.")
        print("Veuillez définir la variable d'environnement OPENAI_API_KEY.")
        return None
    
    try:
        # Initialiser le modèle LLM
        llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.2,
            api_key=OPENAI_API_KEY
        )
        
        # Créer le template de prompt
        prompt = PromptTemplate(
            input_variables=list(prompt_data.keys()),
            template=PROFILE_FORMAT_TEMPLATE
        )
        
        # Créer la chaîne LLM
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Exécuter la chaîne pour obtenir le profil formaté
        formatted_profile = chain.run(prompt_data)
    except Exception as e:
        print(f"Erreur lors du formatage du profil: {str(e)}")
        return None
    
    # Nettoyer le résultat (supprimer les espaces et les lignes vides au début et à la fin)
    formatted_profile = formatted_profile.strip()
    
    return formatted_profile

def example_usage():
    """Exemple d'utilisation de la fonction format_user_profile"""
    # Exemple de profil utilisateur
    profile = {
        "user_id": "user123",
        "name": "Marie Dupont",
        "age": 28,
        "education_level": "Master",
        "major": "Informatique",
        "career_goals": "Devenir développeuse full-stack senior et diriger une équipe de développement",
        "story": "J'ai commencé à coder à l'âge de 15 ans. Après mes études en informatique, j'ai travaillé pendant 3 ans dans une startup où j'ai développé des applications web.",
        "skills": "JavaScript, Python, React, Node.js, SQL, Git",
        "job_title": "Développeuse web",
        "years_experience": 3
    }
    
    # Exemple de scores de compétences
    skills = {
        "creativity": 3.5,
        "leadership": 2.8,
        "critical_thinking": 4.2,
        "problem_solving": 4.5,
        "analytical_thinking": 4.0,
        "attention_to_detail": 3.8,
        "collaboration": 3.5,
        "evaluation": 3.2,
        "decision_making": 3.0,
        "stress_tolerance": 3.5
    }
    
    # Exemple de résultats RIASEC
    riasec = {
        "top_3_code": "RIC"
    }
    
    # Exemple de recommandations sauvegardées
    saved_recommendations = [
        {"label": "Développeur d'applications web"},
        {"label": "Ingénieur logiciel full-stack"},
        {"label": "Architecte de solutions web"}
    ]
    
    # Formater le profil sans recommandations sauvegardées
    formatted_profile_without_recs = format_user_profile(profile, skills, riasec)
    
    # Formater le profil avec recommandations sauvegardées
    formatted_profile_with_recs = format_user_profile(profile, skills, riasec, saved_recommendations)
    
    # Afficher les résultats
    print("\nProfil formaté sans recommandations sauvegardées:")
    print("-" * 50)
    print(formatted_profile_without_recs)
    print("-" * 50)
    
    print("\nProfil formaté avec recommandations sauvegardées:")
    print("-" * 50)
    print(formatted_profile_with_recs)
    print("-" * 50)
    
    # Les résultats ont déjà été affichés ci-dessus

if __name__ == "__main__":
    if check_dependencies():
        example_usage()
    else:
        sys.exit(1)
