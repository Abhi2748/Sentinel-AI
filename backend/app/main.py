"""
Sentinel-AI 2.0 Main Application
FastAPI application with intelligent routing and multi-provider support.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import os
from contextlib import asynccontextmanager

from .api.ai import router as ai_router
from .models.auth import AuthContext, TokenData
from .core.router import IntelligentRouter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Global router instance
router_instance: IntelligentRouter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    global router_instance
    router_instance = IntelligentRouter()
    logger.info("Sentinel-AI 2.0 started successfully")
    
    yield
    
    # Shutdown
    logger.info("Sentinel-AI 2.0 shutting down")


# Create FastAPI app
app = FastAPI(
    title="Sentinel-AI 2.0",
    description="Intelligent AI routing with multi-provider support",
    version="2.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> AuthContext:
    """
    Get current user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        AuthContext with user information
    """
    try:
        # In production, validate JWT token here
        # For now, create a mock auth context
        token = credentials.credentials
        
        # Mock token validation - replace with actual JWT validation
        if not token or token == "invalid":
            raise HTTPException(status_code=401, detail="Invalid token")
            
        # Parse token and extract user info
        # This is a simplified version - implement proper JWT validation
        return AuthContext(
            user_id="user_123",
            team_id="team_456",
            company_id="company_789",
            auth_level="user",
            permissions=["read", "write"]
        )
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# Include routers
app.include_router(ai_router, dependencies=[Depends(get_current_user)])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Sentinel-AI 2.0",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "sentinel-ai",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)