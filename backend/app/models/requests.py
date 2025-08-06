"""
Core request and response models for AI interactions
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class ModelProvider(str, Enum):
    """Supported AI model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    LOCAL = "local"


class RequestPriority(str, Enum):
    """Request priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AIRequest(BaseModel):
    """AI request model with all necessary metadata"""
    
    # Core request data
    prompt: str = Field(..., description="The input prompt for the AI model")
    model: Optional[str] = Field(None, description="Specific model to use")
    provider: Optional[ModelProvider] = Field(None, description="Preferred provider")
    
    # Request metadata
    user_id: str = Field(..., description="User identifier")
    team_id: Optional[str] = Field(None, description="Team identifier")
    company_id: Optional[str] = Field(None, description="Company identifier")
    
    # Configuration
    temperature: float = Field(0.2, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    priority: RequestPriority = Field(RequestPriority.NORMAL, description="Request priority")
    
    # Requirements and constraints
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Specific requirements")
    budget_limit: Optional[float] = Field(None, gt=0, description="Budget limit for this request")
    
    # Tracking
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    trace_id: Optional[str] = Field(None, description="Distributed tracing ID")


class AIResponse(BaseModel):
    """AI response model with comprehensive metadata"""
    
    # Core response data
    content: str = Field(..., description="Generated AI response content")
    model_used: str = Field(..., description="Model that generated the response")
    provider_used: ModelProvider = Field(..., description="Provider that handled the request")
    
    # Token information
    prompt_tokens: int = Field(..., ge=0, description="Tokens in the prompt")
    completion_tokens: int = Field(..., ge=0, description="Tokens in the completion")
    total_tokens: int = Field(..., ge=0, description="Total tokens used")
    
    # Cost information
    cost_usd: float = Field(..., ge=0, description="Cost in USD")
    cost_currency: str = Field("USD", description="Cost currency")
    
    # Performance metrics
    latency_ms: float = Field(..., ge=0, description="Response latency in milliseconds")
    cache_hit: bool = Field(False, description="Whether response was served from cache")
    cache_level: Optional[str] = Field(None, description="Cache level if hit")
    
    # Request tracking
    request_id: str = Field(..., description="Original request ID")
    user_id: str = Field(..., description="User who made the request")
    
    # Status
    success: bool = Field(True, description="Whether the request was successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    # Metadata
    created_at: Optional[str] = Field(None, description="Response creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BatchAIRequest(BaseModel):
    """Batch AI request model for multiple prompts"""
    
    requests: List[AIRequest] = Field(..., description="List of AI requests")
    batch_id: Optional[str] = Field(None, description="Batch identifier")
    parallel: bool = Field(True, description="Whether to process requests in parallel")