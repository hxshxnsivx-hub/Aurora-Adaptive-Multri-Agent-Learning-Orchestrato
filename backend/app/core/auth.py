"""
Authentication and authorization utilities.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import logging

from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get the current authenticated user from JWT token.
    This is a placeholder implementation - in production, this would:
    1. Validate the JWT token with Auth0
    2. Extract user information from the token
    3. Fetch or create user record in database
    """
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # TODO: Implement actual JWT validation with Auth0
        # For now, return a mock user for development
        
        token = credentials.credentials
        
        # In production, validate token with Auth0
        # payload = jwt.decode(
        #     token, 
        #     settings.AUTH0_CLIENT_SECRET, 
        #     algorithms=[settings.JWT_ALGORITHM],
        #     audience=settings.AUTH0_AUDIENCE,
        #     issuer=f"https://{settings.AUTH0_DOMAIN}/"
        # )
        
        # For development, create a mock user
        mock_user = User(
            id="mock-user-id",
            email="user@example.com",
            auth0_id="auth0|mock-user",
            is_active=True
        )
        
        return mock_user
        
    except JWTError as e:
        logger.error(f"JWT validation error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify that the current user has admin privileges."""
    # TODO: Implement admin role checking
    # For now, allow all authenticated users
    return current_user