import os
import logging
from openai import OpenAI
from typing import Dict, List, Any, Optional

# Configuration du logging
logger = logging.getLogger(__name__)

# Récupérer la clé API OpenAI depuis les variables d'environnement
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY n'est pas définie. Le service LLM HEXACO ne fonctionnera pas correctement.")

# Initialisation du client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

class LLMHexacoService:
    """
    Service pour générer des descriptions personnalisées des profils HEXACO
    en utilisant des modèles de langage comme OpenAI GPT.
    """
    
    @staticmethod
    async def generate_hexaco_profile_description(
        hexaco_scores: Dict[str, Any],
        user_profile: Optional[Dict[str, Any]] = None,
        user_skills: Optional[List[Dict[str, Any]]] = None,
        saved_recommendations: Optional[List[Dict[str, Any]]] = None,
        language: str = "fr"
    ) -> str:
        """
        Génère une description personnalisée du profil HEXACO de l'utilisateur.
        
        Args:
            hexaco_scores: Dictionnaire contenant les scores HEXACO (domaines et facettes)
            user_profile: Informations du profil utilisateur (optionnel)
            user_skills: Compétences de l'utilisateur (optionnel)
            saved_recommendations: Recommandations sauvegardées par l'utilisateur (optionnel)
            language: Langue pour la description ("fr" ou "en")
            
        Returns:
            str: Description personnalisée du profil HEXACO
        """
        if not client:
            logger.warning("Client OpenAI non initialisé, retour d'une description par défaut")
            return LLMHexacoService._get_default_description(hexaco_scores, language)
        
        try:
            # Construire le prompt pour le LLM
            prompt = LLMHexacoService._build_hexaco_prompt(
                hexaco_scores, user_profile, user_skills, saved_recommendations, language
            )
            
            # Appeler l'API OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": LLMHexacoService._get_system_prompt(language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            description = response.choices[0].message.content.strip()
            logger.info("Description HEXACO générée avec succès par LLM")
            return description
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la description HEXACO: {e}")
            return LLMHexacoService._get_default_description(hexaco_scores, language)
    
    @staticmethod
    def _get_system_prompt(language: str) -> str:
        """Retourne le prompt système selon la langue."""
        if language == "en":
            return """You are an expert psychologist specializing in HEXACO personality assessment. 
            Generate personalized, insightful, and constructive personality descriptions based on HEXACO scores.
            Your descriptions should be:
            - Professional yet accessible
            - Balanced (highlighting both strengths and areas for development)
            - Actionable (providing practical insights)
            - Encouraging and positive in tone
            - Around 400-600 words
            Focus on how the personality traits translate into real-world behaviors, career implications, and personal development opportunities."""
        else:
            return """Vous êtes un psychologue expert spécialisé dans l'évaluation de personnalité HEXACO.
            Générez des descriptions de personnalité personnalisées, perspicaces et constructives basées sur les scores HEXACO.
            Vos descriptions doivent être :
            - Professionnelles mais accessibles
            - Équilibrées (mettant en avant les forces et les axes de développement)
            - Pratiques (fournissant des insights actionnables)
            - Encourageantes et positives dans le ton
            - D'environ 400-600 mots
            Concentrez-vous sur la façon dont les traits de personnalité se traduisent en comportements concrets, implications professionnelles et opportunités de développement personnel."""
    
    @staticmethod
    def _build_hexaco_prompt(
        hexaco_scores: Dict[str, Any],
        user_profile: Optional[Dict[str, Any]],
        user_skills: Optional[List[Dict[str, Any]]],
        saved_recommendations: Optional[List[Dict[str, Any]]],
        language: str
    ) -> str:
        """Construit le prompt pour la génération de description HEXACO."""
        
        if language == "en":
            prompt = "Generate a personalized HEXACO personality profile description for a student with the following information:\n\n"
            prompt += "## HEXACO Scores:\n"
        else:
            prompt = "Génère une description de profil personnalité HEXACO personnalisée pour un étudiant avec les informations suivantes:\n\n"
            prompt += "## Scores HEXACO:\n"
        
        # Ajouter les scores des domaines
        domains = hexaco_scores.get("domains", {})
        for domain, score in domains.items():
            prompt += f"{domain}: {score}/5.0\n"
        
        # Ajouter les scores des facettes les plus significatives
        facets = hexaco_scores.get("facets", {})
        if facets:
            if language == "en":
                prompt += "\n## Key Facet Scores:\n"
            else:
                prompt += "\n## Scores des Facettes Clés:\n"
            
            # Trier les facettes par score pour mettre en avant les plus élevées et les plus basses
            sorted_facets = sorted(facets.items(), key=lambda x: x[1], reverse=True)
            top_facets = sorted_facets[:6]  # Top 6 facettes
            bottom_facets = sorted_facets[-3:]  # Bottom 3 facettes
            
            for facet, score in top_facets + bottom_facets:
                prompt += f"{facet}: {score}/5.0\n"
        
        # Ajouter les percentiles si disponibles
        percentiles = hexaco_scores.get("percentiles", {})
        if percentiles:
            if language == "en":
                prompt += "\n## Percentile Rankings:\n"
            else:
                prompt += "\n## Classements Percentiles:\n"
            
            for trait, percentile in list(percentiles.items())[:6]:  # Limiter aux domaines principaux
                prompt += f"{trait}: {percentile}e percentile\n"
        
        # Ajouter les informations du profil utilisateur si disponibles
        if user_profile:
            if language == "en":
                prompt += "\n## User Context:\n"
            else:
                prompt += "\n## Contexte Utilisateur:\n"
            
            if user_profile.get("age"):
                if language == "en":
                    prompt += f"Age: {user_profile['age']} years\n"
                else:
                    prompt += f"Âge: {user_profile['age']} ans\n"
            
            if user_profile.get("field_of_study"):
                if language == "en":
                    prompt += f"Field of study: {user_profile['field_of_study']}\n"
                else:
                    prompt += f"Domaine d'études: {user_profile['field_of_study']}\n"
            
            if user_profile.get("career_interests"):
                if language == "en":
                    prompt += f"Career interests: {', '.join(user_profile['career_interests'])}\n"
                else:
                    prompt += f"Intérêts professionnels: {', '.join(user_profile['career_interests'])}\n"
        
        # Ajouter les compétences si disponibles
        if user_skills:
            if language == "en":
                prompt += "\n## User Skills:\n"
            else:
                prompt += "\n## Compétences Utilisateur:\n"
            
            skill_names = [skill.get("name", skill.get("skill_name", "")) for skill in user_skills[:5]]
            prompt += f"{', '.join(filter(None, skill_names))}\n"
        
        # Ajouter les recommandations sauvegardées si disponibles
        if saved_recommendations:
            if language == "en":
                prompt += "\n## Saved Career Recommendations:\n"
            else:
                prompt += "\n## Recommandations Professionnelles Sauvegardées:\n"
            
            rec_titles = [rec.get("title", rec.get("job_title", "")) for rec in saved_recommendations[:3]]
            prompt += f"{', '.join(filter(None, rec_titles))}\n"
        
        # Ajouter les instructions finales
        if language == "en":
            prompt += """\n## Instructions:
            Please provide a comprehensive personality analysis that:
            1. Explains what these HEXACO scores mean in practical terms
            2. Describes how these traits manifest in daily life and relationships
            3. Identifies key strengths and potential challenges
            4. Suggests career paths and work environments that would be a good fit
            5. Provides actionable advice for personal and professional development
            6. Maintains an encouraging and constructive tone throughout
            
            Structure the response with clear sections and make it engaging and personally relevant."""
        else:
            prompt += """\n## Instructions:
            Veuillez fournir une analyse de personnalité complète qui :
            1. Explique ce que ces scores HEXACO signifient en termes pratiques
            2. Décrit comment ces traits se manifestent dans la vie quotidienne et les relations
            3. Identifie les forces clés et les défis potentiels
            4. Suggère des parcours professionnels et des environnements de travail adaptés
            5. Fournit des conseils actionnables pour le développement personnel et professionnel
            6. Maintient un ton encourageant et constructif tout au long
            
            Structurez la réponse avec des sections claires et rendez-la engageante et personnellement pertinente."""
        
        return prompt
    
    @staticmethod
    def _get_default_description(hexaco_scores: Dict[str, Any], language: str) -> str:
        """Génère une description par défaut basée sur les scores HEXACO."""
        domains = hexaco_scores.get("domains", {})
        
        if language == "en":
            description = "## Your HEXACO Personality Profile\n\n"
            description += "Based on your responses to the HEXACO-PI-R assessment, here's an overview of your personality profile:\n\n"
            
            # Analyser les domaines dominants
            sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)
            
            if sorted_domains:
                highest_domain = sorted_domains[0]
                description += f"**Dominant Trait: {highest_domain[0]}** (Score: {highest_domain[1]}/5.0)\n"
                description += LLMHexacoService._get_domain_description(highest_domain[0], "en")
                description += "\n\n"
            
            description += "**Overall Profile Summary:**\n"
            for domain, score in sorted_domains:
                level = "High" if score >= 4.0 else "Moderate" if score >= 3.0 else "Low"
                description += f"- {domain}: {level} ({score}/5.0)\n"
            
            description += "\nThis profile provides insights into your natural tendencies and preferences. "
            description += "Remember that personality is just one aspect of who you are, and you have the ability to develop and adapt in any area."
            
        else:
            description = "## Votre Profil de Personnalité HEXACO\n\n"
            description += "Basé sur vos réponses au test HEXACO-PI-R, voici un aperçu de votre profil de personnalité :\n\n"
            
            # Analyser les domaines dominants
            sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)
            
            if sorted_domains:
                highest_domain = sorted_domains[0]
                description += f"**Trait Dominant : {highest_domain[0]}** (Score : {highest_domain[1]}/5.0)\n"
                description += LLMHexacoService._get_domain_description(highest_domain[0], "fr")
                description += "\n\n"
            
            description += "**Résumé du Profil Global :**\n"
            for domain, score in sorted_domains:
                level = "Élevé" if score >= 4.0 else "Modéré" if score >= 3.0 else "Faible"
                description += f"- {domain} : {level} ({score}/5.0)\n"
            
            description += "\nCe profil fournit des insights sur vos tendances et préférences naturelles. "
            description += "Rappelez-vous que la personnalité n'est qu'un aspect de qui vous êtes, et vous avez la capacité de vous développer et de vous adapter dans n'importe quel domaine."
        
        return description
    
    @staticmethod
    def _get_domain_description(domain: str, language: str) -> str:
        """Retourne une description courte d'un domaine HEXACO."""
        descriptions = {
            "fr": {
                "Honesty-Humility": "Vous tendez à être sincère, équitable et modeste dans vos interactions.",
                "Emotionality": "Vous ressentez les émotions de manière intense et êtes sensible aux besoins des autres.",
                "Extraversion": "Vous êtes sociable, énergique et à l'aise dans les interactions sociales.",
                "Agreeableness": "Vous êtes coopératif, patient et indulgent envers les autres.",
                "Conscientiousness": "Vous êtes organisé, discipliné et orienté vers les objectifs.",
                "Openness": "Vous êtes ouvert aux nouvelles expériences, créatif et intellectuellement curieux."
            },
            "en": {
                "Honesty-Humility": "You tend to be sincere, fair, and modest in your interactions.",
                "Emotionality": "You experience emotions intensely and are sensitive to others' needs.",
                "Extraversion": "You are sociable, energetic, and comfortable in social interactions.",
                "Agreeableness": "You are cooperative, patient, and forgiving toward others.",
                "Conscientiousness": "You are organized, disciplined, and goal-oriented.",
                "Openness": "You are open to new experiences, creative, and intellectually curious."
            }
        }
        
        return descriptions.get(language, {}).get(domain, "")
    
    @staticmethod
    async def get_or_generate_personality_insights(
        user_id: int,
        hexaco_scores: Dict[str, Any],
        db_session,
        user_profile: Optional[Dict[str, Any]] = None,
        user_skills: Optional[List[Dict[str, Any]]] = None,
        saved_recommendations: Optional[List[Dict[str, Any]]] = None,
        language: str = "fr",
        force_regenerate: bool = False
    ) -> str:
        """
        Récupère l'analyse de personnalité existante ou en génère une nouvelle si nécessaire.
        
        Args:
            user_id: ID de l'utilisateur
            hexaco_scores: Scores HEXACO
            db_session: Session de base de données
            user_profile: Profil utilisateur (optionnel)
            user_skills: Compétences utilisateur (optionnel)
            saved_recommendations: Recommandations sauvegardées (optionnel)
            language: Langue pour la description
            force_regenerate: Forcer la régénération même si une analyse existe
            
        Returns:
            str: Description de personnalité (existante ou nouvellement générée)
        """
        if not force_regenerate:
            # Essayer de récupérer l'analyse existante depuis la base de données
            try:
                from sqlalchemy import text
                query = text("""
                    SELECT narrative_description
                    FROM personality_profiles
                    WHERE user_id = :user_id AND profile_type = 'hexaco'
                    AND narrative_description IS NOT NULL
                    ORDER BY computed_at DESC
                    LIMIT 1
                """)
                
                result = db_session.execute(query, {"user_id": user_id}).fetchone()
                if result and result.narrative_description:
                    logger.info(f"Analyse HEXACO existante récupérée pour utilisateur {user_id}")
                    return result.narrative_description
                    
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération de l'analyse existante: {e}")
        
        # Générer une nouvelle analyse si aucune n'existe ou si forcée
        logger.info(f"Génération d'une nouvelle analyse HEXACO pour utilisateur {user_id}")
        return await LLMHexacoService.generate_hexaco_profile_description(
            hexaco_scores=hexaco_scores,
            user_profile=user_profile,
            user_skills=user_skills,
            saved_recommendations=saved_recommendations,
            language=language
        )
    
    @staticmethod
    async def generate_career_recommendations(
        hexaco_scores: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
        language: str = "fr"
    ) -> List[str]:
        """
        Génère des recommandations de carrière basées sur le profil HEXACO.
        
        Args:
            hexaco_scores: Scores HEXACO de l'utilisateur
            user_context: Contexte utilisateur (études, intérêts, etc.)
            language: Langue pour les recommandations
            
        Returns:
            Liste de recommandations de carrière
        """
        if not client:
            return LLMHexacoService._get_default_career_recommendations(hexaco_scores, language)
        
        try:
            if language == "en":
                prompt = "Based on the following HEXACO personality scores, suggest 5-7 specific career paths that would be a good fit:\n\n"
            else:
                prompt = "Basé sur les scores de personnalité HEXACO suivants, suggérez 5-7 parcours professionnels spécifiques qui seraient adaptés :\n\n"
            
            domains = hexaco_scores.get("domains", {})
            for domain, score in domains.items():
                prompt += f"{domain}: {score}/5.0\n"
            
            if user_context:
                if language == "en":
                    prompt += f"\nUser context: {user_context}\n"
                else:
                    prompt += f"\nContexte utilisateur: {user_context}\n"
            
            if language == "en":
                prompt += "\nProvide specific job titles and brief explanations of why they fit this personality profile."
            else:
                prompt += "\nFournissez des titres de postes spécifiques et de brèves explications sur pourquoi ils correspondent à ce profil de personnalité."
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a career counselor specializing in personality-based career guidance." if language == "en" 
                                 else "Vous êtes un conseiller en orientation spécialisé dans l'orientation professionnelle basée sur la personnalité."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            recommendations_text = response.choices[0].message.content.strip()
            # Diviser en liste de recommandations
            recommendations = [rec.strip() for rec in recommendations_text.split('\n') if rec.strip() and not rec.strip().startswith('#')]
            
            logger.info("Recommandations de carrière HEXACO générées avec succès")
            return recommendations[:7]  # Limiter à 7 recommandations
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations de carrière HEXACO: {e}")
            return LLMHexacoService._get_default_career_recommendations(hexaco_scores, language)
    
    @staticmethod
    def _get_default_career_recommendations(hexaco_scores: Dict[str, Any], language: str) -> List[str]:
        """Génère des recommandations de carrière par défaut basées sur les scores HEXACO."""
        domains = hexaco_scores.get("domains", {})
        recommendations = []
        
        # Logique simple basée sur les domaines dominants
        sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_domains:
            return ["Conseiller en orientation", "Généraliste"] if language == "fr" else ["Career Counselor", "Generalist"]
        
        highest_domain = sorted_domains[0][0]
        
        career_mapping = {
            "fr": {
                "Honesty-Humility": ["Travailleur social", "Conseiller éthique", "Médiateur"],
                "Emotionality": ["Psychologue", "Infirmier", "Conseiller"],
                "Extraversion": ["Commercial", "Manager", "Animateur"],
                "Agreeableness": ["Enseignant", "Ressources humaines", "Thérapeute"],
                "Conscientiousness": ["Comptable", "Chef de projet", "Analyste"],
                "Openness": ["Designer", "Chercheur", "Artiste"]
            },
            "en": {
                "Honesty-Humility": ["Social Worker", "Ethics Advisor", "Mediator"],
                "Emotionality": ["Psychologist", "Nurse", "Counselor"],
                "Extraversion": ["Sales Representative", "Manager", "Event Coordinator"],
                "Agreeableness": ["Teacher", "Human Resources", "Therapist"],
                "Conscientiousness": ["Accountant", "Project Manager", "Analyst"],
                "Openness": ["Designer", "Researcher", "Artist"]
            }
        }
        
        return career_mapping.get(language, {}).get(highest_domain, ["Généraliste"] if language == "fr" else ["Generalist"])