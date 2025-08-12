from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.utils.clerk_auth import get_current_user_with_db_sync as get_current_user
from app.utils.database import get_db
from app.models.user import User

router = APIRouter()

@router.get("/test-token")
async def test_token_verification(current_user: User = Depends(get_current_user)):
    """Test endpoint to verify Clerk token validation"""
    try:
        return {
            "status": "success",
            "user_id": current_user.id,
            "clerk_user_id": current_user.clerk_user_id,
            "token_valid": True,
            "authentication_method": "clerk_standard"
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token validation failed: {str(e)}"
        )
