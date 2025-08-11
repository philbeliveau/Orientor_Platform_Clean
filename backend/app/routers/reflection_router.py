from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List


from ..utils.database import get_db
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

def ensure_sequence_exists(db: Session):
    """Ensure the auto-increment sequence exists for the reflection table"""
    try:
        from sqlalchemy import text
        # Check if sequence exists
        result = db.execute(text("SELECT 1 FROM pg_sequences WHERE schemaname='public' AND sequencename='strengths_reflection_responses_id_seq'"))
        if not result.fetchone():
            # Sequence doesn't exist, create it
            max_result = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM strengths_reflection_responses"))
            max_id = max_result.scalar()
            start_val = max_id + 1
            
            # Create sequence
            db.execute(text(f"""
                CREATE SEQUENCE strengths_reflection_responses_id_seq
                START WITH {start_val}
                INCREMENT BY 1
                NO MINVALUE
                NO MAXVALUE
                CACHE 1
            """))
            
            # Set column default
            db.execute(text("""
                ALTER TABLE strengths_reflection_responses 
                ALTER COLUMN id SET DEFAULT nextval('strengths_reflection_responses_id_seq')
            """))
            
            # Set ownership
            db.execute(text("""
                ALTER SEQUENCE strengths_reflection_responses_id_seq 
                OWNED BY strengths_reflection_responses.id
            """))
            
            db.commit()
    except Exception as e:
        # If we can't create the sequence, we'll handle it in the insert logic
        pass

def load_questions_from_db(db: Session) -> List[ReflectionQuestionBase]:
    """Load questions from database."""
    try:
        questions = db.query(ReflectionQuestion).order_by(ReflectionQuestion.id).all()
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
async def get_reflection_questions(db: Session = Depends(get_db)):
    """Récupère toutes les questions de réflexion depuis la base de données."""
    return load_questions_from_db(db)

@router.get("/responses/{user_id}", response_model=List[ReflectionResponse])
async def get_user_responses(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère toutes les réponses sauvegardées d'un utilisateur."""
    # Vérifier que l'utilisateur peut accéder à ces réponses
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these responses"
        )
    
    responses = db.query(StrengthsReflectionResponse).filter(
        StrengthsReflectionResponse.user_id == user_id
    ).all()
    
    return responses

@router.get("/responses", response_model=List[ReflectionResponse])
async def get_current_user_responses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère toutes les réponses sauvegardées de l'utilisateur actuel."""
    responses = db.query(StrengthsReflectionResponse).filter(
        StrengthsReflectionResponse.user_id == current_user.id
    ).all()
    
    return responses

@router.post("/responses", response_model=ReflectionResponse)
async def save_response(
    response_data: ReflectionResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sauvegarde ou met à jour une réponse de réflexion."""
    # Ensure sequence exists before attempting any operations
    ensure_sequence_exists(db)
    
    # Charger les questions pour obtenir le texte et la catégorie
    questions = load_questions_from_db(db)
    question = next((q for q in questions if q.id == response_data.question_id), None)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Vérifier si une réponse existe déjà
    existing_response = db.query(StrengthsReflectionResponse).filter(
        StrengthsReflectionResponse.user_id == current_user.id,
        StrengthsReflectionResponse.question_id == response_data.question_id
    ).first()
    
    if existing_response:
        # Mettre à jour la réponse existante
        existing_response.response = response_data.response
        db.commit()
        db.refresh(existing_response)
        return existing_response
    else:
        # Créer une nouvelle réponse
        new_response = StrengthsReflectionResponse(
            user_id=current_user.id,
            question_id=response_data.question_id,
            prompt_text=question.question,
            response=response_data.response
        )
        db.add(new_response)
        db.commit()
        db.refresh(new_response)
        return new_response

@router.put("/responses/{response_id}", response_model=ReflectionResponse)
async def update_response(
    response_id: int,
    response_data: ReflectionResponseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Met à jour une réponse existante."""
    response = db.query(StrengthsReflectionResponse).filter(
        StrengthsReflectionResponse.id == response_id,
        StrengthsReflectionResponse.user_id == current_user.id
    ).first()
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )
    
    if response_data.response is not None:
        response.response = response_data.response
    
    db.commit()
    db.refresh(response)
    return response

@router.post("/responses/batch", response_model=List[ReflectionResponse])
async def save_responses_batch(
    batch_data: ReflectionResponseBatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sauvegarde plusieurs réponses en lot."""
    # Ensure sequence exists before attempting any operations
    ensure_sequence_exists(db)
    
    questions = load_questions_from_db(db)
    questions_dict = {q.id: q for q in questions}
    
    saved_responses = []
    
    for response_data in batch_data.responses:
        question = questions_dict.get(response_data.question_id)
        if not question:
            continue  # Ignorer les questions invalides
        
        # Vérifier si une réponse existe déjà
        existing_response = db.query(StrengthsReflectionResponse).filter(
            StrengthsReflectionResponse.user_id == current_user.id,
            StrengthsReflectionResponse.question_id == response_data.question_id
        ).first()
        
        if existing_response:
            # Mettre à jour la réponse existante
            existing_response.response = response_data.response
            saved_responses.append(existing_response)
        else:
            # Créer une nouvelle réponse
            new_response = StrengthsReflectionResponse(
                user_id=current_user.id,
                question_id=response_data.question_id,
                prompt_text=question.question,
                response=response_data.response
            )
            db.add(new_response)
            saved_responses.append(new_response)
    
    db.commit()
    
    # Rafraîchir tous les objets
    for response in saved_responses:
        db.refresh(response)
    
    return saved_responses

@router.delete("/responses/{response_id}")
async def delete_response(
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprime une réponse."""
    response = db.query(StrengthsReflectionResponse).filter(
        StrengthsReflectionResponse.id == response_id,
        StrengthsReflectionResponse.user_id == current_user.id
    ).first()
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )
    
    db.delete(response)
    db.commit()
    
    return {"message": "Response deleted successfully"}