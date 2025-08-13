
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
from app.models.tree_path import TreePath
from app.schemas.tree import TreePathCreate, TreePath as TreePathSchema
from uuid import UUID

router = APIRouter(
    prefix="/tree-paths",
    tags=["tree-paths"],
    dependencies=[Depends(get_current_user)],
)

@router.post("/", response_model=TreePathSchema)
async def create_tree_path(
    tree_path: TreePathCreate, 
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    db_tree_path = await db.treepath.create(
        data={
            "user_id": current_user.id,
            "tree_type": tree_path.tree_type,
            "tree_json": tree_path.tree_json
        }
    )
    return db_tree_path

@router.get("/", response_model=List[TreePathSchema])
async def get_user_tree_paths(
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    return await db.treepath.find_many(
        where={"user_id": current_user.id}
    )

@router.get("/{tree_path_id}", response_model=TreePathSchema)
async def get_tree_path(
    tree_path_id: UUID,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    tree_path = await db.treepath.find_first(
        where={
            "id": str(tree_path_id),
            "user_id": current_user.id
        }
    )
    
    if not tree_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree path not found"
        )
    
    return tree_path

@router.delete("/{tree_path_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tree_path(
    tree_path_id: UUID,
    db: Prisma = Depends(get_prisma_client),
    current_user: User = Depends(get_current_user)
):
    tree_path = await db.treepath.find_first(
        where={
            "id": str(tree_path_id),
            "user_id": current_user.id
        }
    )
    
    if not tree_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree path not found"
        )
    
    await db.treepath.delete(
        where={"id": tree_path.id}
    )
    return None 