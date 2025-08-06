"""
Complexity analysis models for intelligent routing decisions
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class ComplexityLevel(str, Enum):
    """Complexity levels for prompt analysis"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class ComplexityFactor(str, Enum):
    """Factors that contribute to complexity"""
    LENGTH = "length"
    TECHNICAL_TERMS = "technical_terms"
    MULTI_STEP = "multi_step"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    CONTEXT_DEPENDENT = "context_dependent"


class ComplexityScore(BaseModel):
    """Comprehensive complexity analysis result"""
    
    # Overall score
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall complexity score (0-1)")
    level: ComplexityLevel = Field(..., description="Complexity level classification")
    
    # Factor breakdown
    factors: Dict[ComplexityFactor, float] = Field(..., description="Individual factor scores")
    factor_weights: Dict[ComplexityFactor, float] = Field(..., description="Weights for each factor")
    
    # Text analysis
    word_count: int = Field(..., ge=0, description="Number of words in prompt")
    character_count: int = Field(..., ge=0, description="Number of characters in prompt")
    sentence_count: int = Field(..., ge=0, description="Number of sentences in prompt")
    
    # Technical indicators
    technical_term_count: int = Field(0, ge=0, description="Number of technical terms detected")
    code_blocks: int = Field(0, ge=0, description="Number of code blocks")
    urls: int = Field(0, ge=0, description="Number of URLs")
    
    # Semantic analysis
    topics: List[str] = Field(default_factory=list, description="Detected topics")
    intent: Optional[str] = Field(None, description="Detected intent (question, generation, analysis, etc.)")
    domain: Optional[str] = Field(None, description="Detected domain (technical, creative, business, etc.)")
    
    # Performance implications
    estimated_tokens: int = Field(..., ge=0, description="Estimated token count")
    estimated_cost_usd: float = Field(..., ge=0, description="Estimated cost in USD")
    recommended_provider: Optional[str] = Field(None, description="Recommended provider based on complexity")
    
    # Metadata
    analysis_time_ms: float = Field(..., ge=0, description="Analysis time in milliseconds")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in analysis")


class ComplexityThresholds(BaseModel):
    """Thresholds for complexity level classification"""
    
    simple_threshold: float = Field(0.25, ge=0.0, le=1.0, description="Threshold for simple complexity")
    moderate_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Threshold for moderate complexity")
    complex_threshold: float = Field(0.75, ge=0.0, le=1.0, description="Threshold for complex complexity")
    
    # Factor-specific thresholds
    length_threshold: int = Field(100, ge=0, description="Word count threshold for length factor")
    technical_threshold: int = Field(5, ge=0, description="Technical term threshold")
    code_threshold: int = Field(1, ge=0, description="Code block threshold")
    
    # Cost thresholds
    cost_threshold_simple: float = Field(0.01, ge=0, description="Cost threshold for simple requests")
    cost_threshold_moderate: float = Field(0.05, ge=0, description="Cost threshold for moderate requests")
    cost_threshold_complex: float = Field(0.15, ge=0, description="Cost threshold for complex requests")


class ComplexityAnalysisConfig(BaseModel):
    """Configuration for complexity analysis"""
    
    # Analysis settings
    enable_semantic_analysis: bool = Field(True, description="Enable semantic analysis")
    enable_cost_estimation: bool = Field(True, description="Enable cost estimation")
    enable_provider_recommendation: bool = Field(True, description="Enable provider recommendation")
    
    # Thresholds
    thresholds: ComplexityThresholds = Field(..., description="Complexity thresholds")
    
    # Factor weights
    factor_weights: Dict[ComplexityFactor, float] = Field(..., description="Weights for complexity factors")
    
    # Performance settings
    max_analysis_time_ms: float = Field(100.0, ge=0, description="Maximum analysis time in milliseconds")
    cache_analysis_results: bool = Field(True, description="Cache analysis results")
    
    # Technical term detection
    technical_terms_file: Optional[str] = Field(None, description="File containing technical terms")
    domain_specific_terms: Dict[str, List[str]] = Field(default_factory=dict, description="Domain-specific terms")


class ComplexityAnalysisResult(BaseModel):
    """Complete complexity analysis result with metadata"""
    
    # Analysis result
    score: ComplexityScore = Field(..., description="Complexity score")
    
    # Input information
    prompt_hash: str = Field(..., description="Hash of analyzed prompt")
    prompt_preview: str = Field(..., description="First 100 characters of prompt")
    
    # Analysis metadata
    analysis_id: str = Field(..., description="Unique analysis identifier")
    analysis_timestamp: str = Field(..., description="Analysis timestamp")
    analysis_version: str = Field(..., description="Analysis algorithm version")
    
    # Performance metrics
    total_analysis_time_ms: float = Field(..., ge=0, description="Total analysis time")
    cache_hit: bool = Field(False, description="Whether result was from cache")
    
    # Recommendations
    recommended_providers: List[str] = Field(default_factory=list, description="Recommended providers")
    cost_optimization_suggestions: List[str] = Field(default_factory=list, description="Cost optimization suggestions")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional analysis metadata")