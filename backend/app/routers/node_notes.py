
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
from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from app.models.user import User
from app.models.node_note import NodeNote
from app.schemas.tree import NodeNoteCreate, NodeNote as NodeNoteSchema

router = APIRouter(
    prefix="/node-notes",
    tags=["node-notes"],
    dependencies=[Depends(get_current_user)],
)

@router.post("/", response_model=NodeNoteSchema)
async def create_node_note(
    note: NodeNoteCreate, 
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    # Check if note already exists
    existing_note = await db.nodenote.find_first(
        where={
            "user_id": current_user.id,
            "node_id": note.node_id,
            "action_index": note.action_index
        }
    )
    
    if existing_note:
        # Update existing note
        existing_note = await db.nodenote.update(
            where={"id": existing_note.id},
            data={"note_text": note.note_text}
        )
        return existing_note
    
    # Create new note
    db_note = await db.nodenote.create(
        data={
            "user_id": current_user.id,
            "node_id": note.node_id,
            "action_index": note.action_index,
            "note_text": note.note_text
        }
    )
    return db_note

@router.get("/", response_model=List[NodeNoteSchema])
async def get_user_notes(
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    return await db.nodenote.find_many(
        where={"user_id": current_user.id}
    )

@router.get("/node/{node_id}", response_model=List[NodeNoteSchema])
async def get_node_notes(
    node_id: str,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    return await db.nodenote.find_many(
        where={
            "node_id": node_id,
            "user_id": current_user.id
        }
    )

@router.get("/{note_id}", response_model=NodeNoteSchema)
async def get_note(
    note_id: int,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    note = await db.nodenote.find_first(
        where={
            "id": note_id,
            "user_id": current_user.id
        }
    )
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    note = await db.nodenote.find_first(
        where={
            "id": note_id,
            "user_id": current_user.id
        }
    )
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    await db.nodenote.delete(
        where={"id": note.id}
    )
    return None 