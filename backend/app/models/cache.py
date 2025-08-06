"""
Cache models for 3-tier caching system (L1 Memory, L2 Redis, L3 Postgres)
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class CacheLevel(str, Enum):
    """Cache tier levels"""
    L1 = "l1"  # Memory cache (1GB, 5min)
    L2 = "l2"  # Redis cache (10GB, 1h)
    L3 = "l3"  # Postgres cache (100GB, 24h)


class CacheStatus(str, Enum):
    """Cache operation status"""
    HIT = "hit"
    MISS = "miss"
    STORED = "stored"
    EVICTED = "evicted"
    ERROR = "error"


class CacheEntry(BaseModel):
    """Cache entry with metadata"""
    
    # Core data
    key: str = Field(..., description="Cache key (prompt hash)")
    value: str = Field(..., description="Cached response content")
    level: CacheLevel = Field(..., description="Cache level")
    
    # Metadata
    prompt_hash: str = Field(..., description="Hash of the original prompt")
    response_hash: str = Field(..., description="Hash of the response")
    
    # Performance metrics
    prompt_tokens: int = Field(..., ge=0, description="Tokens in the prompt")
    completion_tokens: int = Field(..., ge=0, description="Tokens in the completion")
    total_tokens: int = Field(..., ge=0, description="Total tokens used")
    
    # Cost information
    cost_usd: float = Field(..., ge=0, description="Cost in USD")
    model_used: str = Field(..., description="Model that generated the response")
    provider_used: str = Field(..., description="Provider that handled the request")
    
    # Timestamps
    created_at: datetime = Field(..., description="Cache entry creation time")
    accessed_at: Optional[datetime] = Field(None, description="Last access time")
    expires_at: Optional[datetime] = Field(None, description="Expiration time")
    
    # Usage tracking
    access_count: int = Field(0, ge=0, description="Number of times accessed")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CacheStats(BaseModel):
    """Cache statistics and metrics"""
    
    level: CacheLevel = Field(..., description="Cache level")
    
    # Hit/miss statistics
    hits: int = Field(0, ge=0, description="Number of cache hits")
    misses: int = Field(0, ge=0, description="Number of cache misses")
    hit_rate: float = Field(0.0, ge=0.0, le=1.0, description="Cache hit rate")
    
    # Storage statistics
    total_entries: int = Field(0, ge=0, description="Total number of entries")
    total_size_bytes: int = Field(0, ge=0, description="Total size in bytes")
    max_size_bytes: int = Field(0, ge=0, description="Maximum size in bytes")
    usage_percentage: float = Field(0.0, ge=0.0, le=1.0, description="Storage usage percentage")
    
    # Performance metrics
    avg_access_time_ms: float = Field(0.0, ge=0, description="Average access time in milliseconds")
    eviction_count: int = Field(0, ge=0, description="Number of entries evicted")
    
    # Cost savings
    cost_saved_usd: float = Field(0.0, ge=0, description="Cost saved through caching")
    tokens_saved: int = Field(0, ge=0, description="Tokens saved through caching")
    
    # Timestamps
    last_updated: datetime = Field(..., description="Last statistics update")


class CacheLookupResult(BaseModel):
    """Result of a cache lookup operation"""
    
    found: bool = Field(..., description="Whether entry was found in cache")
    level: Optional[CacheLevel] = Field(None, description="Cache level where found")
    entry: Optional[CacheEntry] = Field(None, description="Cache entry if found")
    
    # Performance metrics
    lookup_time_ms: float = Field(..., ge=0, description="Lookup time in milliseconds")
    levels_checked: int = Field(0, ge=0, description="Number of cache levels checked")
    
    # Status
    status: CacheStatus = Field(..., description="Cache operation status")
    error: Optional[str] = Field(None, description="Error message if any")


class CacheStoreResult(BaseModel):
    """Result of a cache store operation"""
    
    success: bool = Field(..., description="Whether store operation was successful")
    level: CacheLevel = Field(..., description="Cache level where stored")
    
    # Storage metrics
    store_time_ms: float = Field(..., ge=0, description="Store time in milliseconds")
    size_bytes: int = Field(0, ge=0, description="Size of stored entry in bytes")
    
    # Status
    status: CacheStatus = Field(..., description="Cache operation status")
    error: Optional[str] = Field(None, description="Error message if any")
    
    # Eviction info
    evicted_entries: int = Field(0, ge=0, description="Number of entries evicted during store")
    eviction_reason: Optional[str] = Field(None, description="Reason for eviction if any")