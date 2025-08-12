"""
Resume Router - Placeholder for future Reactive Resume integration

This router has been cleaned up from legacy authentication patterns.
When implementing resume functionality, use standard Clerk authentication:

from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user

@router.post("/endpoint")
async def my_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {"user_id": current_user.id}
"""

from fastapi import APIRouter

# Create router for future resume functionality
router = APIRouter(prefix="/resume", tags=["resume"])

# TODO: Implement resume endpoints with standard Clerk authentication
# when Reactive Resume integration is needed