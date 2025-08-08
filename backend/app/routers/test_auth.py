from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from ..utils.clerk_auth import verify_clerk_token_cached

router = APIRouter()
security = HTTPBearer()

@router.get("/test-token")
async def test_token_verification(credentials = Depends(security)):
    """Test endpoint to verify Clerk token validation"""
    try:
        token = credentials.credentials
        payload = await verify_clerk_token_cached(token)
        return {
            "status": "success",
            "user_id": payload.get("sub"),
            "token_valid": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token validation failed: {str(e)}"
        )
