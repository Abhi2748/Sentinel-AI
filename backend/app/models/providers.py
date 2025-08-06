"""
Provider models for AI model provider management and routing
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ProviderStatus(str, Enum):
    """Provider availability status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


class ProviderType(str, Enum):
    """Provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    LOCAL = "local"


class ModelCapability(str, Enum):
    """Model capabilities"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    CREATIVE_WRITING = "creative_writing"
    ANALYSIS = "analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"


class ProviderConfig(BaseModel):
    """Configuration for an AI provider"""
    
    # Basic information
    provider_id: str = Field(..., description="Unique provider identifier")
    provider_type: ProviderType = Field(..., description="Provider type")
    name: str = Field(..., description="Provider name")
    description: Optional[str] = Field(None, description="Provider description")
    
    # API configuration
    api_key: Optional[str] = Field(None, description="API key (encrypted)")
    base_url: Optional[str] = Field(None, description="Base URL for API")
    api_version: Optional[str] = Field(None, description="API version")
    
    # Status and availability
    status: ProviderStatus = Field(ProviderStatus.ACTIVE, description="Current status")
    is_enabled: bool = Field(True, description="Whether provider is enabled")
    
    # Performance settings
    timeout_seconds: float = Field(30.0, gt=0, description="Request timeout in seconds")
    max_retries: int = Field(3, ge=0, description="Maximum retry attempts")
    rate_limit_rpm: Optional[int] = Field(None, gt=0, description="Rate limit requests per minute")
    rate_limit_tpm: Optional[int] = Field(None, gt=0, description="Rate limit tokens per minute")
    
    # Cost configuration
    cost_per_1k_tokens_input: float = Field(..., ge=0, description="Cost per 1k input tokens")
    cost_per_1k_tokens_output: float = Field(..., ge=0, description="Cost per 1k output tokens")
    currency: str = Field("USD", description="Cost currency")
    
    # Model capabilities
    supported_models: List[str] = Field(default_factory=list, description="Supported model names")
    capabilities: List[ModelCapability] = Field(default_factory=list, description="Model capabilities")
    
    # Circuit breaker settings
    circuit_breaker_threshold: int = Field(5, ge=1, description="Circuit breaker failure threshold")
    circuit_breaker_timeout: int = Field(60, ge=1, description="Circuit breaker timeout in seconds")
    
    # Metadata
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ProviderMetrics(BaseModel):
    """Provider performance and usage metrics"""
    
    provider_id: str = Field(..., description="Provider identifier")
    
    # Request metrics
    total_requests: int = Field(0, ge=0, description="Total requests made")
    successful_requests: int = Field(0, ge=0, description="Successful requests")
    failed_requests: int = Field(0, ge=0, description="Failed requests")
    success_rate: float = Field(0.0, ge=0.0, le=1.0, description="Success rate")
    
    # Performance metrics
    avg_response_time_ms: float = Field(0.0, ge=0, description="Average response time")
    min_response_time_ms: float = Field(0.0, ge=0, description="Minimum response time")
    max_response_time_ms: float = Field(0.0, ge=0, description="Maximum response time")
    
    # Token metrics
    total_tokens_processed: int = Field(0, ge=0, description="Total tokens processed")
    total_input_tokens: int = Field(0, ge=0, description="Total input tokens")
    total_output_tokens: int = Field(0, ge=0, description="Total output tokens")
    
    # Cost metrics
    total_cost_usd: float = Field(0.0, ge=0, description="Total cost in USD")
    avg_cost_per_request: float = Field(0.0, ge=0, description="Average cost per request")
    
    # Error tracking
    error_counts: Dict[str, int] = Field(default_factory=dict, description="Error type counts")
    last_error: Optional[str] = Field(None, description="Last error message")
    last_error_time: Optional[datetime] = Field(None, description="Last error timestamp")
    
    # Circuit breaker
    circuit_breaker_trips: int = Field(0, ge=0, description="Number of circuit breaker trips")
    circuit_breaker_status: str = Field("closed", description="Current circuit breaker status")
    
    # Timestamps
    last_request_time: Optional[datetime] = Field(None, description="Last request timestamp")
    last_successful_request: Optional[datetime] = Field(None, description="Last successful request")
    metrics_updated_at: datetime = Field(..., description="Metrics update timestamp")


class ProviderResponse(BaseModel):
    """Response from an AI provider"""
    
    # Core response data
    content: str = Field(..., description="Generated content")
    model_used: str = Field(..., description="Model that generated the response")
    provider_id: str = Field(..., description="Provider that handled the request")
    
    # Token information
    prompt_tokens: int = Field(..., ge=0, description="Tokens in the prompt")
    completion_tokens: int = Field(..., ge=0, description="Tokens in the completion")
    total_tokens: int = Field(..., ge=0, description="Total tokens used")
    
    # Cost information
    cost_usd: float = Field(..., ge=0, description="Cost in USD")
    cost_currency: str = Field("USD", description="Cost currency")
    
    # Performance metrics
    response_time_ms: float = Field(..., ge=0, description="Response time in milliseconds")
    request_id: Optional[str] = Field(None, description="Provider's request ID")
    
    # Status
    success: bool = Field(True, description="Whether request was successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    # Metadata
    finish_reason: Optional[str] = Field(None, description="Finish reason (stop, length, etc.)")
    usage_metadata: Dict[str, Any] = Field(default_factory=dict, description="Usage metadata")
    provider_metadata: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific metadata")


class ProviderSelection(BaseModel):
    """Provider selection decision for routing"""
    
    selected_provider: str = Field(..., description="Selected provider ID")
    selected_model: str = Field(..., description="Selected model name")
    
    # Selection criteria
    complexity_score: float = Field(..., ge=0.0, le=1.0, description="Complexity score")
    cost_estimate: float = Field(..., ge=0, description="Estimated cost")
    performance_score: float = Field(..., ge=0.0, le=1.0, description="Performance score")
    
    # Alternative options
    alternative_providers: List[str] = Field(default_factory=list, description="Alternative providers considered")
    selection_reason: str = Field(..., description="Reason for selection")
    
    # Fallback information
    fallback_providers: List[str] = Field(default_factory=list, description="Fallback providers if primary fails")
    circuit_breaker_status: Dict[str, str] = Field(default_factory=dict, description="Circuit breaker status per provider")
    
    # Metadata
    selection_time_ms: float = Field(..., ge=0, description="Selection time in milliseconds")
    selection_algorithm: str = Field(..., description="Algorithm used for selection")