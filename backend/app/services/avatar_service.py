import os
import logging
import requests
import uuid
from typing import Dict, Any, Optional
from openai import OpenAI
from sqlalchemy.orm import Session
from ..models.user_representation import UserRepresentation
from ..utils.database import get_db

# Configuration du logging
logger = logging.getLogger(__name__)

# Récupérer la clé API OpenAI depuis les variables d'environnement
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY n'est pas définie. Le service Avatar ne fonctionnera pas correctement.")

# Initialisation du client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

class AvatarService:
    """
    Service pour générer des avatars personnalisés avec OpenAI GPT et DALL-E.
    """
    
    @staticmethod
    async def generate_avatar_description(
        user_data: Dict[str, Any],
        language: str = "fr"
    ) -> str:
        """
        Génère une description d'avatar basée sur les données utilisateur.
        
        Args:
            user_data: Données de l'utilisateur (profil, compétences, etc.)
            language: Langue pour la description ("fr" ou "en")
            
        Returns:
            str: Description de l'avatar
        """
        if not client:
            logger.warning("Client OpenAI non initialisé, retour d'une description par défaut")
            return AvatarService._get_default_avatar_description(language)
        
        try:
            # Construire le prompt pour la description d'avatar
            prompt = AvatarService._build_avatar_description_prompt(user_data, language)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en création d'avatars personnalisés. Tu crées des descriptions détaillées et créatives d'avatars basées sur les profils des utilisateurs."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            description = response.choices[0].message.content.strip()
            logger.info("Description d'avatar générée avec succès")
            return description
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la description d'avatar: {str(e)}")
            return AvatarService._get_default_avatar_description(language)
    
    @staticmethod
    async def generate_avatar_image(description: str) -> Optional[str]:
        """
        Génère une image d'avatar avec DALL-E 3.
        
        Args:
            description: Description de l'avatar
            
        Returns:
            str: URL de l'image générée ou None en cas d'erreur
        """
        if not client:
            logger.warning("Client OpenAI non initialisé")
            return None
        
        try:
            # Améliorer la description pour DALL-E avec un style plus fantastique
            enhanced_prompt = f"Fantasy character portrait: {description}. Digital art style, magical and ethereal appearance, fantasy elements like glowing eyes or mystical aura, vibrant colors, enchanted background with subtle magical effects, no text or writing anywhere in the image, high quality digital illustration, fantasy art style."
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info("Image d'avatar générée avec succès")
            return image_url
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'image d'avatar: {str(e)}")
            return None
    
    @staticmethod
    async def download_and_save_image(image_url: str, user_id: int) -> Optional[str]:
        """
        Télécharge et sauvegarde l'image d'avatar localement.
        
        Args:
            image_url: URL de l'image à télécharger
            user_id: ID de l'utilisateur
            
        Returns:
            str: Chemin local de l'image sauvegardée ou None en cas d'erreur
        """
        try:
            # Générer un nom de fichier unique
            filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.png"
            local_path = f"static/avatars/{filename}"
            full_path = os.path.join(os.getcwd(), local_path)
            
            # Créer le dossier s'il n'existe pas
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Télécharger l'image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Sauvegarder l'image
            with open(full_path, 'wb') as f:
                f.write(response.content)
            
            # Retourner l'URL relative pour l'API
            api_url = f"/static/avatars/{filename}"
            logger.info(f"Image d'avatar sauvegardée: {api_url}")
            return api_url
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement/sauvegarde de l'image: {str(e)}")
            return None
    
    @staticmethod
    async def update_user_avatar(
        db: Session,
        user_id: int,
        avatar_name: str,
        avatar_description: str,
        avatar_image_url: Optional[str]
    ) -> UserRepresentation:
        """
        Met à jour ou crée une représentation utilisateur avec les données d'avatar.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            avatar_name: Nom de l'avatar
            avatar_description: Description de l'avatar
            avatar_image_url: URL de l'image d'avatar
            
        Returns:
            UserRepresentation: Représentation utilisateur mise à jour
        """
        try:
            # Chercher une représentation existante pour cet utilisateur
            user_repr = db.query(UserRepresentation).filter(
                UserRepresentation.user_id == user_id,
                UserRepresentation.source == "avatar_generation"
            ).first()
            
            if user_repr:
                # Mettre à jour la représentation existante
                user_repr.avatar_name = avatar_name
                user_repr.avatar_description = avatar_description
                user_repr.avatar_image_url = avatar_image_url
                user_repr.summary = f"Avatar généré: {avatar_name}"
            else:
                # Créer une nouvelle représentation
                user_repr = UserRepresentation(
                    user_id=user_id,
                    source="avatar_generation",
                    format_version="v1",
                    data={"avatar_generated": True},
                    avatar_name=avatar_name,
                    avatar_description=avatar_description,
                    avatar_image_url=avatar_image_url,
                    summary=f"Avatar généré: {avatar_name}"
                )
                db.add(user_repr)
            
            db.commit()
            db.refresh(user_repr)
            logger.info(f"Avatar mis à jour pour l'utilisateur {user_id}")
            return user_repr
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'avatar: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def _build_avatar_description_prompt(user_data: Dict[str, Any], language: str) -> str:
        """
        Construit le prompt pour générer la description d'avatar.
        """
        if language == "en":
            prompt = f"""
            Create a detailed avatar description for a professional user based on their profile:
            
            User Data: {user_data}
            
            Generate a creative and professional avatar description that reflects:
            - Their personality traits
            - Their professional interests
            - Their skills and competencies
            - A modern, approachable appearance
            
            The description should be suitable for generating an illustration and be 2-3 sentences long.
            """
        else:  # français
            prompt = f"""
            Crée une description détaillée d'avatar fantastique pour un utilisateur basée sur son profil:
            
            Données utilisateur: {user_data}
            
            Génère une description d'avatar créative et fantastique qui reflète:
            - Ses traits de personnalité sous forme de caractéristiques magiques
            - Ses intérêts professionnels transformés en éléments fantastiques
            - Ses compétences représentées par des pouvoirs ou attributs mystiques
            - Une apparence fantastique avec des éléments magiques (yeux brillants, aura colorée, etc.)
            
            Style: personnage de fantasy, art numérique, éléments magiques, couleurs vibrantes.
            La description doit être adaptée pour générer une illustration fantastique et faire 2-3 phrases.
            IMPORTANT: Aucun texte ne doit apparaître dans l'image générée.
            """
        
        return prompt
    
    @staticmethod
    def _get_default_avatar_description(language: str) -> str:
        """
        Retourne une description d'avatar par défaut.
        """
        if language == "en":
            return "A mystical fantasy character with glowing eyes and a magical aura, representing wisdom and potential, with ethereal features and enchanted elements surrounding them."
        else:  # français
            return "Un personnage fantastique mystique avec des yeux brillants et une aura magique, représentant la sagesse et le potentiel, avec des traits éthérés et des éléments enchantés qui l'entourent."