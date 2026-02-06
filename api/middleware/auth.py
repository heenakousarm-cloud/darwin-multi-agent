"""
API Key Authentication Middleware

Verifies that incoming requests have a valid API key in the Authorization header.
Expected format: Authorization: Bearer darwin_sk_xxxxx
"""

import os
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Load API key from environment
DARWIN_API_KEY = os.getenv("DARWIN_API_KEY")

if not DARWIN_API_KEY:
    print("⚠️  Warning: DARWIN_API_KEY not set. API authentication will fail.")

security = HTTPBearer()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify the API key from the Authorization header.
    
    Args:
        credentials: The HTTP Bearer credentials from the request
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If the API key is invalid or missing
    """
    if not DARWIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: DARWIN_API_KEY not set",
        )
    
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Use 'Bearer'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if credentials.credentials != DARWIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return credentials.credentials
