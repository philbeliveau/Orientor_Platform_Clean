import os
import logging
from openai import OpenAI
from typing import Dict, List, Any, Optional

# Configuration du logging
logger = logging.getLogger(__name__)

# Récupérer la clé API OpenAI depuis les variables d'environnement
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY n'est pas définie. Le service LLM ne fonctionnera pas correctement.")

# Initialisation du client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

class LLMService:
    """
    Service pour interagir avec les modèles de langage (LLM) comme OpenAI GPT.
    """
    
    @staticmethod
    async def generate_holland_profile_description(
        riasec_scores: Dict[str, float],
        top_3_code: str,
        user_profile: Optional[Dict[str, Any]] = None,
        user_skills: Optional[List[Dict[str, Any]]] = None,
        saved_recommendations: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Génère une description personnalisée du profil RIASEC de l'utilisateur
        en utilisant un modèle de langage.
        
        Args:
            riasec_scores: Dictionnaire contenant les scores pour chaque dimension RIASEC
            top_3_code: Le code Holland à 3 lettres dominant
            user_profile: Informations du profil utilisateur (optionnel)
            user_skills: Compétences de l'utilisateur (optionnel)
            saved_recommendations: Recommandations sauvegardées par l'utilisateur (optionnel)
            
        Returns:
            str: Description personnalisée du profil
        """
        try:
            # Construire le prompt pour le LLM
            prompt = "Génère une description de profil personnalisée pour un étudiant avec les informations suivantes:\n\n"
            
            # Ajouter les scores RIASEC
            prompt += "## Scores RIASEC:\n"
            prompt += f"R (Réaliste): {riasec_scores.get('r_score', 0)}\n"
            prompt += f"I (Investigateur): {riasec_scores.get('i_score', 0)}\n"
            prompt += f"A (Artistique): {riasec_scores.get('a_score', 0)}\n"
            prompt += f"S (Social): {riasec_scores.get('s_score', 0)}\n"
            prompt += f"E (Entreprenant): {riasec_scores.get('e_score', 0)}\n"
            prompt += f"C (Conventionnel): {riasec_scores.get('c_score', 0)}\n"
            prompt += f"Code dominant: {top_3_code}\n\n"
            
            # Ajouter les informations du profil utilisateur si disponibles
            if user_profile:
                prompt += "## Profil utilisateur:\n"
                if user_profile.get("name"):
                    prompt += f"Nom: {user_profile.get('name')}\n"
                if user_profile.get("age"):
                    prompt += f"Âge: {user_profile.get('age')}\n"
                if user_profile.get("education_level") or user_profile.get("major"):
                    education = []
                    if user_profile.get("education_level"):
                        education.append(user_profile.get("education_level"))
                    if user_profile.get("major"):
                        education.append(f"Spécialisation en {user_profile.get('major')}")
                    prompt += f"Formation: {', '.join(education)}\n"
                if user_profile.get("job_title") or user_profile.get("years_experience"):
                    experience = []
                    if user_profile.get("job_title"):
                        experience.append(user_profile.get("job_title"))
                    if user_profile.get("years_experience"):
                        experience.append(f"{user_profile.get('years_experience')} ans d'expérience")
                    prompt += f"Expérience professionnelle: {', '.join(experience)}\n"
                if user_profile.get("interests") and isinstance(user_profile.get("interests"), list):
                    prompt += f"Intérêts: {', '.join(user_profile.get('interests'))}\n"
                prompt += "\n"
            
            # Ajouter les compétences de l'utilisateur si disponibles
            if user_skills and len(user_skills) > 0:
                prompt += "## Compétences de l'utilisateur:\n"
                for skill in user_skills:
                    # Extraire les compétences avec leurs niveaux
                    skills_to_display = [
                        ("Créativité", skill.get("creativity", 0)),
                        ("Leadership", skill.get("leadership", 0)),
                        ("Littératie numérique", skill.get("digital_literacy", 0)),
                        ("Pensée critique", skill.get("critical_thinking", 0)),
                        ("Résolution de problèmes", skill.get("problem_solving", 0)),
                        ("Pensée analytique", skill.get("analytical_thinking", 0)),
                        ("Attention aux détails", skill.get("attention_to_detail", 0)),
                        ("Collaboration", skill.get("collaboration", 0)),
                        ("Adaptabilité", skill.get("adaptability", 0)),
                        ("Indépendance", skill.get("independence", 0)),
                        ("Évaluation", skill.get("evaluation", 0)),
                        ("Prise de décision", skill.get("decision_making", 0)),
                        ("Tolérance au stress", skill.get("stress_tolerance", 0))
                    ]
                    
                    # Afficher uniquement les compétences qui ont une valeur
                    for skill_name, skill_level in skills_to_display:
                        if skill_level:
                            prompt += f"- {skill_name} (Niveau: {skill_level}/5)\n"
                prompt += "\n"
            
            # Ajouter les recommandations sauvegardées si disponibles
            if saved_recommendations and len(saved_recommendations) > 0:
                prompt += "## Recommandations sauvegardées:\n"
                for rec in saved_recommendations:
                    label = rec.get("label", "")
                    description = rec.get("description", "")
                    main_duties = rec.get("main_duties", "")
                    oasis_code = rec.get("oasis_code", "")
                    
                    if label:
                        prompt += f"- {label}"
                        if oasis_code:
                            prompt += f" (Code: {oasis_code})"
                        if description:
                            prompt += f": {description[:100]}..."
                        if main_duties:
                            prompt += f" Tâches principales: {main_duties[:100]}..."
                        prompt += "\n"
                prompt += "\n"
            
            # Ajouter les instructions pour la génération de la description
            prompt += """
La description doit inclure:
1. Une analyse personnalisée qui intègre à la fois les résultats RIASEC et les informations du profil
2. Une explication des traits dominants et de leur signification dans le contexte des expériences et intérêts de l'utilisateur
3. Des suggestions de domaines d'études ou de carrières qui correspondent à ce profil, en tenant compte des compétences existantes
4. Des conseils pour développer les compétences liées à ces traits, en s'appuyant sur les recommandations déjà sauvegardées
5. Une analyse de la cohérence entre les résultats RIASEC et les choix/intérêts actuels de l'utilisateur

Réponds en français et utilise un ton professionnel mais accessible.
"""
            
            # Appeler l'API OpenAI avec la nouvelle interface (sans await)
            response = client.chat.completions.create(
                model="gpt-4",  # Utiliser GPT-4 pour une meilleure qualité
                messages=[
                    {"role": "system", "content": "Tu es un conseiller d'orientation professionnelle expert qui analyse les profils RIASEC (Holland Code) et fournit des conseils personnalisés."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extraire et retourner la réponse avec la nouvelle structure
            description = response.choices[0].message.content.strip()
            return description
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la description du profil: {str(e)}")
            # Retourner une description par défaut en cas d'erreur
            return f"""
Votre profil RIASEC dominant est {top_3_code}.

Ce code indique vos préférences professionnelles selon le modèle Holland. Les personnes avec ce profil ont généralement des intérêts et des compétences qui correspondent à ces trois dimensions.

Pour obtenir une analyse plus détaillée, veuillez réessayer ultérieurement ou contacter un conseiller d'orientation.
"""

    @staticmethod
    async def fallback_description(top_3_code: str) -> str:
        """
        Génère une description de base en cas d'échec de l'appel à l'API.
        
        Args:
            top_3_code: Le code Holland à 3 lettres dominant
            
        Returns:
            str: Description de base du profil
        """
        try:
            # Essayer d'utiliser l'API avec un prompt simple
            prompt = f"""
            Génère une description simple pour un profil RIASEC avec le code {top_3_code}.
            Explique brièvement ce que signifie chaque lettre du code et quels types de carrières pourraient convenir à ce profil.
            Garde la réponse concise, environ 200 mots.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Utiliser un modèle moins coûteux pour le fallback
                messages=[
                    {"role": "system", "content": "Tu es un conseiller d'orientation qui explique les codes RIASEC."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel au fallback LLM: {str(e)}")
            
            # Fallback statique en cas d'échec de l'API
            descriptions = {
                'R': "Les personnes de type Réaliste préfèrent travailler avec des objets, des machines, des outils, des plantes ou des animaux. Elles aiment les activités pratiques et concrètes.",
                'I': "Les personnes de type Investigateur aiment observer, apprendre, analyser et résoudre des problèmes. Elles sont curieuses, méthodiques et précises.",
                'A': "Les personnes de type Artistique aiment les activités créatives qui permettent de s'exprimer librement. Elles sont imaginatives, intuitives et originales.",
                'S': "Les personnes de type Social aiment travailler avec les autres pour les informer, les aider, les soigner ou les divertir. Elles sont empathiques, patientes et communicatives.",
                'E': "Les personnes de type Entreprenant aiment influencer, persuader et diriger les autres. Elles sont énergiques, ambitieuses et sociables.",
                'C': "Les personnes de type Conventionnel aiment suivre des procédures établies et respecter des règles. Elles sont organisées, précises et efficaces."
            }
            
            description = f"Votre profil RIASEC dominant est {top_3_code}.\n\n"
            
            for letter in top_3_code:
                if letter in descriptions:
                    description += f"{letter} - {descriptions[letter]}\n\n"
            
            description += "Ce code indique vos préférences professionnelles selon le modèle Holland. Pour obtenir des conseils plus personnalisés, consultez un conseiller d'orientation."
            
            return description