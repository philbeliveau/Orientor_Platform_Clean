import os
import sys
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

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
    from langchain.schema.runnable import RunnableSequence
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

# Templates de prompts pour les différents formateurs ESCO

ESCO_OCCUPATION_TEMPLATE = """
Tu es un expert en formatage de données pour l'alignement sémantique ESCO.

Ta tâche est de reformater un profil utilisateur pour qu'il corresponde au format des descriptions d'occupation ESCO.

Voici le format ESCO occupation de référence:
```
conceptUri: http://data.europa.eu/esco/occupation/[id]
notation: [code numérique]
Label: [titre de l'occupation]
Alternative_label: [titres alternatifs séparés par |]
Description: [description détaillée de l'occupation]
KnowledgeSkillCompetence: [compétences requises]
BroaderRelations: [occupations plus larges]
NarrowerRelations: [occupations plus spécifiques]
```

Voici le profil utilisateur à reformater:
{user_profile}

INSTRUCTIONS:
1. Génère un conceptUri fictif basé sur le profil de l'utilisateur
2. Utilise le titre du poste comme "Label"
3. Crée des titres alternatifs basés sur les compétences et les objectifs de carrière
4. Génère une description détaillée basée sur l'expérience et les objectifs
5. Liste les compétences clés dans "KnowledgeSkillCompetence"
6. Suggère des relations hiérarchiques pertinentes

Retourne UNIQUEMENT le profil reformaté, sans commentaires.
"""

ESCO_SKILL_TEMPLATE = """
Tu es un expert en formatage de données pour l'alignement sémantique ESCO.

Ta tâche est de reformater une compétence utilisateur selon le format des descriptions de compétences ESCO.

Voici le format ESCO skill de référence:
```
conceptUri: http://data.europa.eu/esco/skill/[id]
notation: [code numérique]
preferredLabel: [nom de la compétence]
altLabels: [alternatives séparées par |]
description: [description détaillée]
skillType: knowledge/skill/competence
reuseLevel: transversal/sector-specific/occupation-specific
```

Compétence à formater: {skill_name}
Niveau de l'utilisateur: {skill_level}
Contexte du profil: {user_context}

INSTRUCTIONS:
1. Génère un conceptUri fictif pour cette compétence
2. Utilise le nom de la compétence comme "preferredLabel"
3. Crée des labels alternatifs pertinents
4. Génère une description détaillée de la compétence
5. Classifie le type de compétence (knowledge/skill/competence)
6. Détermine le niveau de réutilisation approprié

Retourne UNIQUEMENT la compétence reformatée, sans commentaires.
"""

ESCO_SKILLGROUP_TEMPLATE = """
Tu es un expert en formatage de données pour l'alignement sémantique ESCO.

Ta tâche est de reformater un groupe de compétences selon le format ESCO.

Voici le format ESCO skillgroup de référence:
```
conceptUri: http://data.europa.eu/esco/skillgroup/[id]
notation: [code numérique]
preferredLabel: [nom du groupe]
description: [description du groupe]
includes: [compétences incluses séparées par |]
```

Groupe de compétences: {group_label}
Compétences incluses: {skill_names}
Contexte utilisateur: {user_context}
Profil RIASEC: {riasec_profile}

INSTRUCTIONS:
1. Génère un conceptUri fictif pour ce groupe
2. Utilise le label du groupe comme "preferredLabel"
3. Crée une description cohérente du groupe
4. Liste toutes les compétences incluses

Retourne UNIQUEMENT le groupe reformaté, sans commentaires.
"""

ESCO_FULL_PROFILE_TEMPLATE = """
Tu es un expert en formatage de données pour l'alignement sémantique ESCO.

Ta tâche est de créer un profil ESCO complet combinant occupation, compétences et groupes.

Éléments à combiner:
- Profil d'occupation: {occupation_profile}
- Profil de compétences: {skill_profiles}
- Groupe de compétences: {skillgroup_profile}
- Contexte utilisateur: {user_context}
- Profil RIASEC: {riasec_profile}

INSTRUCTIONS:
1. Crée un profil unifié qui combine tous les éléments
2. Assure la cohérence entre l'occupation et les compétences
3. Maintiens la structure ESCO appropriée
4. Optimise pour l'alignement sémantique

Retourne un profil ESCO complet et cohérent.
"""

def format_esco_occupation(profile: Dict[str, Any], skills: Dict[str, Any], riasec: Dict[str, Any]) -> Optional[str]:
    """
    Formate un profil utilisateur selon le style ESCO occupation.
    
    Args:
        profile: Données du profil utilisateur
        skills: Données des compétences
        riasec: Données RIASEC
        
    Returns:
        Profil formaté selon ESCO occupation ou None en cas d'erreur
    """
    if not check_dependencies() or not OPENAI_API_KEY:
        return None
    
    try:
        # Préparer le contexte utilisateur
        user_profile = f"""
        Nom: {profile.get('name', 'N/A')}
        Âge: {profile.get('age', 'N/A')}
        Éducation: {profile.get('education_level', 'N/A')}
        Spécialisation: {profile.get('major', 'N/A')}
        Poste actuel: {profile.get('job_title', 'N/A')}
        Expérience: {profile.get('years_experience', 'N/A')} ans
        Objectifs: {profile.get('career_goals', 'N/A')}
        Compétences: {skills}
        RIASEC: {riasec}
        """
        
        # Créer le modèle LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=OPENAI_API_KEY
        )
        
        # Créer et exécuter le prompt
        prompt = PromptTemplate(
            input_variables=["user_profile"],
            template=ESCO_OCCUPATION_TEMPLATE
        )
        
        chain = prompt | llm
        result = chain.invoke({"user_profile": user_profile})
        
        return result.content.strip()
        
    except Exception as e:
        print(f"Erreur lors du formatage ESCO occupation: {str(e)}")
        return None

def format_esco_skill(skill_name: str, skill_level: float, user_context: Dict[str, Any]) -> Optional[str]:
    """
    Formate une compétence selon le style ESCO skill.
    
    Args:
        skill_name: Nom de la compétence
        skill_level: Niveau de la compétence (0-5)
        user_context: Contexte du profil utilisateur
        
    Returns:
        Compétence formatée selon ESCO skill ou None en cas d'erreur
    """
    if not check_dependencies() or not OPENAI_API_KEY:
        return None
    
    try:
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=OPENAI_API_KEY
        )
        
        prompt = PromptTemplate(
            input_variables=["skill_name", "skill_level", "user_context"],
            template=ESCO_SKILL_TEMPLATE
        )
        
        chain = prompt | llm
        result = chain.invoke({
            "skill_name": skill_name,
            "skill_level": skill_level,
            "user_context": str(user_context)
        })
        
        return result.content.strip()
        
    except Exception as e:
        print(f"Erreur lors du formatage ESCO skill: {str(e)}")
        return None

def format_esco_skillgroup(group_label: str, skill_names: List[str], 
                          user_context: Dict[str, Any], riasec_profile: Dict[str, Any]) -> Optional[str]:
    """
    Formate un groupe de compétences selon le style ESCO skillgroup.
    
    Args:
        group_label: Label du groupe de compétences
        skill_names: Liste des noms de compétences
        user_context: Contexte du profil utilisateur
        riasec_profile: Profil RIASEC
        
    Returns:
        Groupe formaté selon ESCO skillgroup ou None en cas d'erreur
    """
    if not check_dependencies() or not OPENAI_API_KEY:
        return None
    
    try:
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=OPENAI_API_KEY
        )
        
        prompt = PromptTemplate(
            input_variables=["group_label", "skill_names", "user_context", "riasec_profile"],
            template=ESCO_SKILLGROUP_TEMPLATE
        )
        
        chain = prompt | llm
        result = chain.invoke({
            "group_label": group_label,
            "skill_names": " | ".join(skill_names),
            "user_context": str(user_context),
            "riasec_profile": str(riasec_profile)
        })
        
        return result.content.strip()
        
    except Exception as e:
        print(f"Erreur lors du formatage ESCO skillgroup: {str(e)}")
        return None

def format_esco_full_profile(occupation_profile: str, skill_profiles: List[str], 
                            skillgroup_profile: str, user_context: Dict[str, Any], 
                            riasec_profile: Dict[str, Any]) -> Optional[str]:
    """
    Crée un profil ESCO complet combinant tous les éléments.
    
    Args:
        occupation_profile: Profil d'occupation formaté
        skill_profiles: Liste des profils de compétences formatés
        skillgroup_profile: Profil de groupe de compétences formaté
        user_context: Contexte du profil utilisateur
        riasec_profile: Profil RIASEC
        
    Returns:
        Profil ESCO complet ou None en cas d'erreur
    """
    if not check_dependencies() or not OPENAI_API_KEY:
        return None
    
    try:
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=OPENAI_API_KEY
        )
        
        prompt = PromptTemplate(
            input_variables=["occupation_profile", "skill_profiles", "skillgroup_profile", 
                           "user_context", "riasec_profile"],
            template=ESCO_FULL_PROFILE_TEMPLATE
        )
        
        chain = prompt | llm
        result = chain.invoke({
            "occupation_profile": occupation_profile,
            "skill_profiles": "\n---\n".join(skill_profiles),
            "skillgroup_profile": skillgroup_profile,
            "user_context": str(user_context),
            "riasec_profile": str(riasec_profile)
        })
        
        return result.content.strip()
        
    except Exception as e:
        print(f"Erreur lors du formatage ESCO full profile: {str(e)}")
        return None

# Fonctions de fallback simples
def simple_esco_occupation_format(profile: Dict[str, Any]) -> str:
    """Version simple du formatage ESCO occupation sans LLM."""
    return f"""conceptUri: http://data.europa.eu/esco/occupation/user_{profile.get('job_title', 'professional').lower().replace(' ', '_')}
notation: 99999
Label: {profile.get('job_title', 'Professional')}
Alternative_label: {profile.get('career_goals', 'Career professional')}
Description: Professional with {profile.get('years_experience', 0)} years of experience in {profile.get('major', 'their field')}.
KnowledgeSkillCompetence: {profile.get('skills', 'Various professional skills')}
BroaderRelations: Professional occupations
NarrowerRelations: Specialized {profile.get('job_title', 'professional')} roles"""

def simple_esco_skill_format(skill_name: str, skill_level: float) -> str:
    """Version simple du formatage ESCO skill sans LLM."""
    return f"""conceptUri: http://data.europa.eu/esco/skill/{skill_name.lower().replace(' ', '_')}
notation: 88888
preferredLabel: {skill_name}
altLabels: {skill_name} capability
description: Professional {skill_name} capability at level {skill_level}
skillType: skill
reuseLevel: transversal"""

# Test des fonctions si exécuté directement
if __name__ == "__main__":
    if check_dependencies():
        # Test avec des données d'exemple
        test_profile = {
            "name": "Test User",
            "age": 25,
            "education_level": "Bachelor's",
            "major": "Computer Science",
            "job_title": "Software Developer",
            "years_experience": 3,
            "career_goals": "Senior Full-Stack Developer",
            "skills": "Python, JavaScript, React"
        }
        
        test_skills = {"programming": 4.0, "problem_solving": 4.5}
        test_riasec = {"top_3_code": "RIC"}
        
        print("Test des fonctions de formatage ESCO:")
        
        # Test occupation
        occupation = format_esco_occupation(test_profile, test_skills, test_riasec)
        if occupation:
            print("ESCO Occupation:")
            print(occupation)
        else:
            print("Fallback ESCO Occupation:")
            print(simple_esco_occupation_format(test_profile))
        
        print("\n" + "="*50 + "\n")
        
        # Test skill
        skill = format_esco_skill("programming", 4.0, test_profile)
        if skill:
            print("ESCO Skill:")
            print(skill)
        else:
            print("Fallback ESCO Skill:")
            print(simple_esco_skill_format("programming", 4.0))
    else:
        print("Dépendances manquantes. Utilisation des fonctions de fallback.")
        test_profile = {"job_title": "Developer", "years_experience": 3, "major": "CS"}
        print("Fallback ESCO Occupation:")
        print(simple_esco_occupation_format(test_profile))