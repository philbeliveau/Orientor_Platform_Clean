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

Ta tâche est de formater un profil utilisateur selon les directives OaSIS (Occupation and Skills in Semantic Integration System).

CONTEXTE:
- Tu as reçu des données de profil utilisateur depuis plusieurs sources
- Tu dois créer un profil formaté qui maximise la qualité des embeddings sémantiques
- Le profil sera utilisé pour la recherche vectorielle et les recommandations de carrière

DIRECTIVES DE FORMATAGE OaSIS:

1. STRUCTURE HIÉRARCHIQUE:
   - Commence par les informations démographiques de base
   - Continue avec les objectifs de carrière et aspirations
   - Développe les compétences et expériences
   - Termine par les intérêts personnels et qualités uniques

2. LANGUE ET STYLE:
   - Utilise un langage professionnel mais accessible
   - Privilégie les termes spécifiques du domaine professionnel
   - Évite les expressions vagues ("bon", "excellent")
   - Utilise des verbes d'action et des descriptions concrètes

3. OPTIMISATION SÉMANTIQUE:
   - Intègre des mots-clés pertinents pour la recherche d'emploi
   - Utilise la terminologie standard de l'industrie
   - Lie les compétences aux contextes d'application
   - Crée des connexions logiques entre les différents éléments

4. COHÉRENCE NARRATIVE:
   - Assure-toi que tous les éléments s'alignent avec les objectifs de carrière
   - Crée une progression logique du profil
   - Élimine les contradictions ou incohérences

DONNÉES D'ENTRÉE:
{input_data}

PROFIL OASIS FORMATÉ:
Génère un profil utilisateur professionnel et cohérent qui respecte les directives OaSIS ci-dessus.

Le profil doit être formaté comme un texte continu, bien structuré, qui pourra être efficacement transformé en embeddings pour la recherche sémantique et les recommandations de carrière.
"""

def format_user_profile(profile_data: Dict[str, Any], 
                       skills_data: Dict[str, Any] = None,
                       riasec_data: Dict[str, Any] = None,
                       recommendations_data: List[Dict[str, Any]] = None) -> Optional[str]:
    """
    Formate un profil utilisateur selon les directives OaSIS.
    
    Args:
        profile_data: Données du profil utilisateur
        skills_data: Données des compétences (optionnel)
        riasec_data: Données RIASEC (optionnel)
        recommendations_data: Données des recommandations sauvegardées (optionnel)
        
    Returns:
        Profil formaté selon les directives OaSIS ou None en cas d'erreur
    """
    
    # Vérifier les dépendances
    if not check_dependencies():
        return None
    
    # Vérifier la clé API
    if not OPENAI_API_KEY:
        print("Erreur: La clé API OpenAI n'est pas configurée.")
        print("Veuillez définir la variable d'environnement OPENAI_API_KEY.")
        return None
    
    try:
        # Préparer les données d'entrée
        input_data = {
            "profile": profile_data,
            "skills": skills_data or {},
            "riasec": riasec_data or {},
            "recommendations": recommendations_data or []
        }
        
        # Créer le modèle LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=OPENAI_API_KEY
        )
        
        # Créer le template de prompt
        prompt = PromptTemplate(
            input_variables=["input_data"],
            template=PROFILE_FORMAT_TEMPLATE
        )
        
        # Créer la chaîne LLM
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Exécuter le formatage
        result = chain.run(input_data=str(input_data))
        
        return result.strip()
        
    except Exception as e:
        print(f"Erreur lors du formatage du profil OaSIS: {str(e)}")
        return None

def format_user_profile_simple(profile_data: Dict[str, Any]) -> str:
    """
    Version simplifiée du formatage sans utiliser LLM (fallback).
    
    Args:
        profile_data: Données du profil utilisateur
        
    Returns:
        Profil formaté de manière simple
    """
    try:
        # Extraire les informations de base
        name = profile_data.get("name", "Professionnel")
        age = profile_data.get("age", "")
        education = profile_data.get("education_level", "")
        major = profile_data.get("major", "")
        career_goals = profile_data.get("career_goals", "")
        interests = profile_data.get("interests", "")
        hobbies = profile_data.get("hobbies", "")
        skills = profile_data.get("skills", "")
        
        # Construire le profil formaté
        formatted_profile = f"""Profil professionnel: {name}
        
Informations démographiques:
{"Âge: " + str(age) + " ans. " if age else ""}{"Niveau d'éducation: " + education + ". " if education else ""}{"Domaine d'études: " + major + ". " if major else ""}

Objectifs de carrière:
{career_goals if career_goals else "En développement"}

Compétences:
{skills if skills else "Compétences variées en développement"}

Centres d'intérêt:
{interests if interests else "Intérêts diversifiés"}

Activités personnelles:
{hobbies if hobbies else "Activités variées"}

Ce profil reflète un professionnel en développement avec des objectifs clairs et des compétences en progression."""
        
        return formatted_profile.strip()
        
    except Exception as e:
        print(f"Erreur lors du formatage simple: {str(e)}")
        return "Profil utilisateur en cours de développement professionnel."

# Fonction principale pour le formatage avec fallback
def format_user_profile_with_fallback(profile_data: Dict[str, Any], 
                                    skills_data: Dict[str, Any] = None,
                                    riasec_data: Dict[str, Any] = None,
                                    recommendations_data: List[Dict[str, Any]] = None) -> str:
    """
    Formate un profil utilisateur avec fallback vers une version simple.
    
    Args:
        profile_data: Données du profil utilisateur
        skills_data: Données des compétences (optionnel)
        riasec_data: Données RIASEC (optionnel)
        recommendations_data: Données des recommandations sauvegardées (optionnel)
        
    Returns:
        Profil formaté (version complète ou simple selon la disponibilité)
    """
    
    # Essayer d'abord le formatage complet avec LLM
    formatted_profile = format_user_profile(profile_data, skills_data, riasec_data, recommendations_data)
    
    # Si ça échoue, utiliser la version simple
    if formatted_profile is None:
        print("Utilisation du formatage simple comme fallback")
        formatted_profile = format_user_profile_simple(profile_data)
    
    return formatted_profile

# Test du module si exécuté directement
if __name__ == "__main__":
    # Test avec des données d'exemple
    test_profile = {
        "name": "Test User",
        "age": 25,
        "education_level": "Bachelor's",
        "major": "Computer Science",
        "career_goals": "Software Developer",
        "interests": "Programming, AI, Technology",
        "hobbies": "Reading, Gaming",
        "skills": "Python, JavaScript, Problem Solving"
    }
    
    print("Test du formatage OaSIS:")
    result = format_user_profile_with_fallback(test_profile)
    print(result)