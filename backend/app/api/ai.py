"""
AI API endpoints for intelligent routing and request handling.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from ..core.router import IntelligentRouter
from ..models.requests import AIRequest, AIResponse
from ..models.auth import AuthContext

router = APIRouter(prefix="/v1/ai", tags=["AI"])

# Initialize the intelligent router
router_instance = IntelligentRouter()


@router.post("/chat", response_model=AIResponse)
async def chat_completion(request: AIRequest, auth: AuthContext = Depends()):
    """
    Main AI chat completion endpoint with intelligent routing.
    
    Args:
        request: The AI request with prompt and requirements
        auth: Authentication context
        
    Returns:
        AIResponse with the generated content or error
    """
    try:
        # Add auth context to request
        request.user_id = auth.user_id
        request.team_id = auth.team_id
        request.company_id = auth.company_id
        
        # Route the request through intelligent router
        response = await router_instance.route_request(request)
        
        return response
        
    except Exception as e:
        logging.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics(auth: AuthContext = Depends()) -> Dict[str, Any]:
    """
    Get routing metrics and statistics.
    
    Args:
        auth: Authentication context
        
    Returns:
        Dictionary with various metrics
    """
    try:
        metrics = await router_instance.get_metrics()
        return {
            "status": "success",
            "data": metrics
        }
        
    except Exception as e:
        logging.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy", "service": "sentinel-ai"}