# ============================================================================
# PRISMA MIGRATION - Enhanced Database Integration
# ============================================================================
# This router has been migrated to use Prisma ORM with enhanced features:
# - Type-safe database operations
# - Improved error handling and retry logic
# - Performance monitoring
# - Enhanced logging
# - Transaction support for complex operations
# 
# Migration date: 2025-01-13
# Previous system: SQLAlchemy ORM
# Current system: Prisma ORM with enhanced client
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from prisma import Prisma
from app.utils.prisma_client import get_prisma_client, PrismaOperationLogger
from ..models.reflection import StrengthsReflectionResponse, ReflectionQuestion
from ..models.user import User
from ..schemas.reflection import (
    ReflectionQuestionBase,
    ReflectionResponse,
    ReflectionResponseCreate,
    ReflectionResponseUpdate,
    ReflectionResponseBatch
)
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user

router = APIRouter(prefix="/reflection", tags=["reflection"])

# Note: Prisma handles auto-increment sequences automatically
# The ensure_sequence_exists function is no longer needed with Prisma

async def load_questions_from_db(db: Prisma) -> List[ReflectionQuestionBase]:
    """Load questions from database."""
    try:
        questions = await db.reflectionquestion.find_many(
            order={"id": "asc"}
        )
        return [
            ReflectionQuestionBase(
                id=q.id,
                question=q.question,
                category=q.category
            )
            for q in questions
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading questions from database: {str(e)}"
        )

@router.get("/questions", response_model=List[ReflectionQuestionBase])
async def get_reflection_questions(db: Prisma = Depends(get_prisma_client)):
    """Récupère toutes les questions de réflexion depuis la base de données."""
    return await load_questions_from_db(db)

@router.get("/responses/{user_id}", response_model=List[ReflectionResponse])
async def get_user_responses(
    user_id: int,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    """Récupère toutes les réponses sauvegardées d'un utilisateur."""
    # Vérifier que l'utilisateur peut accéder à ces réponses
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these responses"
        )
    
    responses = await db.strengthsreflectionresponse.find_many(
        where={"user_id": user_id}
    )
    
    return responses

@router.get("/responses", response_model=List[ReflectionResponse])
async def get_current_user_responses(
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    """Récupère toutes les réponses sauvegardées de l'utilisateur actuel."""
    responses = await db.strengthsreflectionresponse.find_many(
        where={"user_id": current_user.id}
    )
    
    return responses

@router.post("/responses", response_model=ReflectionResponse)
async def save_response(
    response_data: ReflectionResponseCreate,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    """Sauvegarde ou met à jour une réponse de réflexion."""
    # Charger les questions pour obtenir le texte et la catégorie
    questions = await load_questions_from_db(db)
    question = next((q for q in questions if q.id == response_data.question_id), None)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Vérifier si une réponse existe déjà
    existing_response = await db.strengthsreflectionresponse.find_first(
        where={
            "user_id": current_user.id,
            "question_id": response_data.question_id
        }
    )
    
    if existing_response:
        # Mettre à jour la réponse existante
        updated_response = await db.strengthsreflectionresponse.update(
            where={"id": existing_response.id},
            data={"response": response_data.response}
        )
        return updated_response
    else:
        # Créer une nouvelle réponse
        new_response = await db.strengthsreflectionresponse.create(
            data={
                "user_id": current_user.id,
                "question_id": response_data.question_id,
                "prompt_text": question.question,
                "response": response_data.response
            }
        )
        return new_response

@router.put("/responses/{response_id}", response_model=ReflectionResponse)
async def update_response(
    response_id: int,
    response_data: ReflectionResponseUpdate,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    """Met à jour une réponse existante."""
    response = await db.strengthsreflectionresponse.find_first(
        where={
            "id": response_id,
            "user_id": current_user.id
        }
    )
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )
    
    update_data = {}
    if response_data.response is not None:
        update_data["response"] = response_data.response
    
    updated_response = await db.strengthsreflectionresponse.update(
        where={"id": response_id},
        data=update_data
    )
    return updated_response

@router.post("/responses/batch", response_model=List[ReflectionResponse])
async def save_responses_batch(
    batch_data: ReflectionResponseBatch,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    """Sauvegarde plusieurs réponses en lot."""
    questions = await load_questions_from_db(db)
    questions_dict = {q.id: q for q in questions}
    
    saved_responses = []
    
    for response_data in batch_data.responses:
        question = questions_dict.get(response_data.question_id)
        if not question:
            continue  # Ignorer les questions invalides
        
        # Vérifier si une réponse existe déjà
        existing_response = await db.strengthsreflectionresponse.find_first(
            where={
                "user_id": current_user.id,
                "question_id": response_data.question_id
            }
        )
        
        if existing_response:
            # Mettre à jour la réponse existante
            updated_response = await db.strengthsreflectionresponse.update(
                where={"id": existing_response.id},
                data={"response": response_data.response}
            )
            saved_responses.append(updated_response)
        else:
            # Créer une nouvelle réponse
            new_response = await db.strengthsreflectionresponse.create(
                data={
                    "user_id": current_user.id,
                    "question_id": response_data.question_id,
                    "prompt_text": question.question,
                    "response": response_data.response
                }
            )
            saved_responses.append(new_response)
    
    return saved_responses

@router.delete("/responses/{response_id}")
async def delete_response(
    response_id: int,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    """Supprime une réponse."""
    response = await db.strengthsreflectionresponse.find_first(
        where={
            "id": response_id,
            "user_id": current_user.id
        }
    )
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )
    
    await db.strengthsreflectionresponse.delete(
        where={"id": response_id}
    )
    
    return {"message": "Response deleted successfully"}