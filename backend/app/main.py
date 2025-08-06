"""
Sentinel-AI 2.0 FastAPI Application
Main entry point for the AI orchestration platform
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
from datetime import datetime

from .models.requests import AIRequest, AIResponse
from .core.router import IntelligentRouter

# Initialize FastAPI app
app = FastAPI(
    title="Sentinel-AI 2.0",
    description="AI Orchestration Platform with Intelligent Routing",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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

# Initialize router
router = IntelligentRouter()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Sentinel-AI 2.0 API",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


@app.post("/v1/chat/completions", response_model=AIResponse)
async def chat_completions(request: AIRequest):
    """
    Main chat completions endpoint.
    Routes requests through the intelligent routing system.
    """
    try:
        response = await router.route_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/stats")
async def get_stats():
    """Get system statistics."""
    try:
        stats = await router.get_system_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/budget/summary")
async def get_budget_summary(request: AIRequest):
    """Get budget summary for a request."""
    try:
        summary = await router.get_budget_summary(request)
        return {"budget_summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/cache/clear")
async def clear_caches():
    """Clear all caches."""
    try:
        await router.clear_caches()
        return {"message": "All caches cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )