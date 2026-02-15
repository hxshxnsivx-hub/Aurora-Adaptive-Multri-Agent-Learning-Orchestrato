"""
Rate limiting middleware using Redis.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging
from typing import Callable

from app.core.config import settings
from app.core.redis import cache

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""
    
    def __init__(self, app, requests_per_minute: int = None, window_seconds: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Apply rate limiting based on client IP."""
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier (IP address or user ID if authenticated)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not await self._check_rate_limit(client_id):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per {self.window_seconds} seconds allowed",
                    "retry_after": self.window_seconds
                },
                headers={"Retry-After": str(self.window_seconds)}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = await self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_seconds)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID from JWT token if available
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In a real implementation, you would decode the JWT here
            # For now, use IP address
            pass
        
        # Use client IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return f"rate_limit:{client_ip}"
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limit using sliding window."""
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Redis key for this client's requests
        key = f"{client_id}:requests"
        
        try:
            # Get current request count in the window
            current_count = await cache.increment(key)
            
            if current_count == 1:
                # First request in window, set expiration
                await cache.expire(key, self.window_seconds)
            
            return current_count <= self.requests_per_minute
        
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Allow request if Redis is unavailable
            return True
    
    async def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        key = f"{client_id}:requests"
        
        try:
            current_count = await cache.get(key) or 0
            remaining = max(0, self.requests_per_minute - int(current_count))
            return remaining
        except Exception as e:
            logger.error(f"Error getting remaining requests: {e}")
            return self.requests_per_minute