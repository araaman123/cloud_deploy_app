"""Authentication routes."""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
import httpx
import secrets
from config import settings

router = APIRouter()


@router.post("/github")
async def github_auth(code: str):
    """
    GitHub OAuth callback endpoint.
    
    Exchanges authorization code for access token and creates/updates user.
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required"
        )
    
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"}
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token"
            )
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain access token"
            )
        
        # Get user info from GitHub
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user information"
            )
        
        user_data = user_response.json()
    
    # TODO: Create or update user in database
    # TODO: Generate JWT token
    
    return {
        "message": "Authentication successful",
        "user": {
            "id": user_data.get("id"),
            "login": user_data.get("login"),
            "email": user_data.get("email"),
        },
        "access_token": secrets.token_urlsafe(32),
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout():
    """Logout endpoint."""
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user():
    """Get current user information."""
    # TODO: Implement JWT validation
    return {"message": "User information endpoint", "user_id": "current_user"}
