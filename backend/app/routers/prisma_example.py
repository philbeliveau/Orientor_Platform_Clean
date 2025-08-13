"""
Example FastAPI router using Prisma ORM
Demonstrates type-safe database operations with Prisma
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

# Import your existing auth
from ..utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from ..models.user import User as SQLAlchemyUser

# Import Prisma client
from ..utils.prisma_client import get_prisma_client, PrismaUserService, prisma_health_check
from prisma import Prisma

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/prisma", tags=["Prisma Examples"])

@router.get("/health")
async def check_prisma_health():
    """
    Health check endpoint for Prisma database connection
    """
    try:
        health_status = await prisma_health_check()
        if health_status["status"] == "healthy":
            return JSONResponse(
                status_code=200,
                content=health_status
            )
        else:
            return JSONResponse(
                status_code=503,
                content=health_status
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": str(e)}
        )

@router.get("/users/me/prisma")
async def get_current_user_prisma(
    current_user: SQLAlchemyUser = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Get current user data using Prisma (compared to SQLAlchemy)
    Shows how to integrate Prisma with your existing Clerk auth
    """
    try:
        # Use Prisma to get user data with type safety
        prisma_user = await db.users.find_unique(
            where={"clerk_user_id": current_user.clerk_user_id},
            include={
                "user_profiles": True,
                "conversations": {
                    "take": 5,
                    "order_by": {"created_at": "desc"}
                }
            }
        )
        
        if not prisma_user:
            raise HTTPException(status_code=404, detail="User not found in Prisma")
        
        return {
            "message": "User data retrieved with Prisma",
            "user_data": prisma_user.dict(),
            "comparison": {
                "sqlalchemy_id": current_user.id,
                "prisma_id": prisma_user.id,
                "clerk_id": current_user.clerk_user_id
            }
        }
    except Exception as e:
        logger.error(f"Error fetching user with Prisma: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/users/search")
async def search_users_prisma(
    query: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Results limit"),
    current_user: SQLAlchemyUser = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Search users using Prisma with type-safe queries
    Demonstrates advanced querying capabilities
    """
    try:
        # Type-safe search with Prisma
        users = await db.users.find_many(
            where={
                "OR": [
                    {"first_name": {"contains": query, "mode": "insensitive"}},
                    {"last_name": {"contains": query, "mode": "insensitive"}},
                    {"email": {"contains": query, "mode": "insensitive"}}
                ]
            },
            include={
                "user_profiles": {
                    "select": {
                        "name": True,
                        "age": True,
                        "major": True
                    }
                }
            },
            take=limit,
            order_by={"created_at": "desc"}
        )
        
        return {
            "message": f"Found {len(users)} users matching '{query}'",
            "users": [user.dict() for user in users],
            "search_metadata": {
                "query": query,
                "limit": limit,
                "total_found": len(users)
            }
        }
    except Exception as e:
        logger.error(f"Error searching users with Prisma: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/conversations/recent")
async def get_recent_conversations(
    limit: int = Query(20, ge=1, le=100),
    current_user: SQLAlchemyUser = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Get recent conversations using Prisma with relations
    Shows how to work with related data efficiently
    """
    try:
        conversations = await db.conversations.find_many(
            where={"user_id": current_user.id},
            include={
                "users": {
                    "select": {
                        "first_name": True,
                        "last_name": True,
                        "email": True
                    }
                },
                "chat_messages": {
                    "take": 5,
                    "order_by": {"created_at": "desc"},
                    "select": {
                        "content": True,
                        "role": True,
                        "created_at": True
                    }
                }
            },
            take=limit,
            order_by={"updated_at": "desc"}
        )
        
        return {
            "message": f"Retrieved {len(conversations)} recent conversations",
            "conversations": [conv.dict() for conv in conversations],
            "user_info": {
                "user_id": current_user.id,
                "clerk_id": current_user.clerk_user_id
            }
        }
    except Exception as e:
        logger.error(f"Error fetching conversations with Prisma: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/users/profile/update")
async def update_user_profile_prisma(
    profile_data: dict,
    current_user: SQLAlchemyUser = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Update user profile using Prisma transactions
    Demonstrates transactional operations with type safety
    """
    try:
        # Use Prisma transaction for atomic updates
        async with db.tx() as transaction:
            # Update user basic info
            updated_user = await transaction.users.update(
                where={"id": current_user.id},
                data={
                    "first_name": profile_data.get("first_name"),
                    "last_name": profile_data.get("last_name"),
                    "updated_at": "now()"
                }
            )
            
            # Update or create profile
            profile = await transaction.user_profiles.upsert(
                where={"user_id": current_user.id},
                data={
                    "create": {
                        "user_id": current_user.id,
                        **profile_data.get("profile", {})
                    },
                    "update": profile_data.get("profile", {})
                }
            )
        
        return {
            "message": "Profile updated successfully with Prisma",
            "user": updated_user.dict(),
            "profile": profile.dict()
        }
    except Exception as e:
        logger.error(f"Error updating profile with Prisma: {e}")
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")

@router.get("/analytics/user-stats")
async def get_user_analytics(
    current_user: SQLAlchemyUser = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Get user analytics using Prisma aggregations
    Demonstrates advanced querying and aggregations
    """
    try:
        # Aggregate user data with Prisma
        stats = await db.users.find_unique(
            where={"id": current_user.id},
            include={
                "_count": {
                    "conversations": True,
                    "chat_messages": True,
                    "saved_recommendations": True
                }
            }
        )
        
        # Get recent activity
        recent_activity = await db.chat_messages.find_many(
            where={"user_id": current_user.id},
            order_by={"created_at": "desc"},
            take=10,
            select={
                "created_at": True,
                "role": True,
                "conversations": {
                    "select": {"title": True}
                }
            }
        )
        
        return {
            "message": "User analytics retrieved with Prisma",
            "stats": {
                "total_conversations": stats._count.conversations if stats else 0,
                "total_messages": stats._count.chat_messages if stats else 0,
                "total_saved_recommendations": stats._count.saved_recommendations if stats else 0
            },
            "recent_activity": [activity.dict() for activity in recent_activity],
            "user_info": {
                "id": current_user.id,
                "member_since": stats.created_at.isoformat() if stats else None
            }
        }
    except Exception as e:
        logger.error(f"Error fetching analytics with Prisma: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

@router.get("/demo/raw-query")
async def demo_raw_query(
    current_user: SQLAlchemyUser = Depends(get_current_user),
    db: Prisma = Depends(get_prisma_client)
):
    """
    Demonstrate raw SQL queries with Prisma when needed
    Use sparingly - prefer type-safe Prisma queries
    """
    try:
        # Example raw query (use only when Prisma's query builder isn't sufficient)
        result = await db.execute_raw(
            """
            SELECT 
                COUNT(*) as total_users,
                COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '30 days') as recent_users,
                MAX(created_at) as latest_registration
            FROM users
            """
        )
        
        return {
            "message": "Raw query executed with Prisma",
            "database_stats": result[0] if result else {},
            "warning": "Raw queries should be used sparingly. Prefer Prisma's type-safe queries."
        }
    except Exception as e:
        logger.error(f"Error executing raw query: {e}")
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

# Add this router to your main FastAPI app:
# from app.routers import prisma_example
# app.include_router(prisma_example.router)