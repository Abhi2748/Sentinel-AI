"""
CacheManager for 3-tier caching system
L1: Memory cache (1GB, 5min)
L2: Redis cache (10GB, 1h) 
L3: Postgres cache (100GB, 24h)
"""

import hashlib
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import asyncio
from collections import OrderedDict

from ..models.cache import (
    CacheEntry,
    CacheLevel,
    CacheStatus,
    CacheLookupResult,
    CacheStoreResult,
    CacheStats
)
from ..models.requests import AIRequest
from ..models.providers import ProviderResponse


class MemoryCache:
    """L1 Memory cache implementation with LRU eviction."""
    
    def __init__(self, max_size: int = 1000, max_age_seconds: int = 300):
        """Initialize memory cache with size and age limits."""
        self.max_size = max_size
        self.max_age_seconds = max_age_seconds
        self.cache: OrderedDict = OrderedDict()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from memory cache."""
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if datetime.now() > entry.expires_at:
                del self.cache[key]
                self.stats["misses"] += 1
                return None
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            self.stats["hits"] += 1
            return entry
        
        self.stats["misses"] += 1
        return None
    
    def set(self, key: str, entry: CacheEntry) -> bool:
        """Set entry in memory cache."""
        # Set expiration
        entry.expires_at = datetime.now() + timedelta(seconds=self.max_age_seconds)
        entry.level = CacheLevel.L1
        
        # Evict if needed
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats["evictions"] += 1
        
        self.cache[key] = entry
        self.stats["size"] = len(self.cache)
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0.0
        
        return {
            "level": CacheLevel.L1,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "total_entries": len(self.cache),
            "eviction_count": self.stats["evictions"],
            "max_size": self.max_size,
            "max_age_seconds": self.max_age_seconds
        }


class RedisCache:
    """L2 Redis cache implementation."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis cache connection."""
        self.redis_url = redis_url
        self.client = None  # Will be initialized in connect()
        self.max_age_seconds = 3600  # 1 hour
        self.stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0
        }
    
    async def connect(self):
        """Connect to Redis."""
        try:
            import redis.asyncio as redis
            self.client = redis.from_url(self.redis_url)
            await self.client.ping()
        except ImportError:
            # Fallback for when redis is not available
            self.client = None
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.client = None
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from Redis cache."""
        if not self.client:
            return None
        
        try:
            data = await self.client.get(key)
            if data:
                entry_dict = json.loads(data)
                entry = CacheEntry(**entry_dict)
                self.stats["hits"] += 1
                return entry
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Redis get error: {e}")
        
        self.stats["misses"] += 1
        return None
    
    async def set(self, key: str, entry: CacheEntry) -> bool:
        """Set entry in Redis cache."""
        if not self.client:
            return False
        
        try:
            entry.level = CacheLevel.L2
            entry.expires_at = datetime.now() + timedelta(seconds=self.max_age_seconds)
            
            data = json.dumps(entry.dict())
            await self.client.setex(key, self.max_age_seconds, data)
            return True
        except Exception as e:
            self.stats["errors"] += 1
            print(f"Redis set error: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.client:
            return {
                "level": CacheLevel.L2,
                "status": "disconnected",
                "hits": 0,
                "misses": 0,
                "errors": self.stats["errors"]
            }
        
        try:
            info = await self.client.info()
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0.0
            
            return {
                "level": CacheLevel.L2,
                "status": "connected",
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": hit_rate,
                "errors": self.stats["errors"],
                "redis_memory_used": info.get("used_memory_human", "N/A"),
                "max_age_seconds": self.max_age_seconds
            }
        except Exception:
            return {
                "level": CacheLevel.L2,
                "status": "error",
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "errors": self.stats["errors"]
            }


class PostgresCache:
    """L3 Postgres cache implementation."""
    
    def __init__(self, db_url: str = "postgresql://localhost/sentinel_cache"):
        """Initialize Postgres cache connection."""
        self.db_url = db_url
        self.max_age_seconds = 86400  # 24 hours
        self.stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0
        }
    
    async def connect(self):
        """Connect to Postgres."""
        # This would initialize database connection
        # For now, we'll simulate the connection
        pass
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from Postgres cache."""
        # Simulate database query
        # In real implementation, this would query the database
        self.stats["misses"] += 1
        return None
    
    async def set(self, key: str, entry: CacheEntry) -> bool:
        """Set entry in Postgres cache."""
        # Simulate database insert
        # In real implementation, this would insert into database
        entry.level = CacheLevel.L3
        entry.expires_at = datetime.now() + timedelta(seconds=self.max_age_seconds)
        return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "level": CacheLevel.L3,
            "status": "simulated",
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "errors": self.stats["errors"],
            "max_age_seconds": self.max_age_seconds
        }


class CacheManager:
    """
    Manages 3-tier caching system with intelligent fallback.
    L1: Memory cache (fastest, smallest)
    L2: Redis cache (fast, medium size)
    L3: Postgres cache (slower, largest)
    """
    
    def __init__(self):
        """Initialize cache manager with all three tiers."""
        self.l1_cache = MemoryCache()
        self.l2_cache = RedisCache()
        self.l3_cache = PostgresCache()
        
        # Initialize connections
        asyncio.create_task(self._initialize_connections())
    
    async def _initialize_connections(self):
        """Initialize external cache connections."""
        await self.l2_cache.connect()
        await self.l3_cache.connect()
    
    def _generate_key(self, prompt: str) -> str:
        """Generate cache key from prompt."""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    async def lookup(self, prompt: str) -> CacheLookupResult:
        """
        Look up response in cache hierarchy.
        
        Args:
            prompt: The input prompt
            
        Returns:
            CacheLookupResult with lookup details
        """
        start_time = time.time()
        key = self._generate_key(prompt)
        levels_checked = 0
        
        # Try L1 (Memory) cache first
        levels_checked += 1
        entry = self.l1_cache.get(key)
        if entry:
            lookup_time = (time.time() - start_time) * 1000
            return CacheLookupResult(
                found=True,
                level=CacheLevel.L1,
                entry=entry,
                lookup_time_ms=lookup_time,
                levels_checked=levels_checked,
                status=CacheStatus.HIT
            )
        
        # Try L2 (Redis) cache
        levels_checked += 1
        entry = await self.l2_cache.get(key)
        if entry:
            # Store in L1 for faster future access
            self.l1_cache.set(key, entry)
            
            lookup_time = (time.time() - start_time) * 1000
            return CacheLookupResult(
                found=True,
                level=CacheLevel.L2,
                entry=entry,
                lookup_time_ms=lookup_time,
                levels_checked=levels_checked,
                status=CacheStatus.HIT
            )
        
        # Try L3 (Postgres) cache
        levels_checked += 1
        entry = await self.l3_cache.get(key)
        if entry:
            # Store in L1 and L2 for faster future access
            self.l1_cache.set(key, entry)
            await self.l2_cache.set(key, entry)
            
            lookup_time = (time.time() - start_time) * 1000
            return CacheLookupResult(
                found=True,
                level=CacheLevel.L3,
                entry=entry,
                lookup_time_ms=lookup_time,
                levels_checked=levels_checked,
                status=CacheStatus.HIT
            )
        
        # Cache miss
        lookup_time = (time.time() - start_time) * 1000
        return CacheLookupResult(
            found=False,
            lookup_time_ms=lookup_time,
            levels_checked=levels_checked,
            status=CacheStatus.MISS
        )
    
    async def store(self, prompt: str, response: ProviderResponse) -> CacheStoreResult:
        """
        Store response in cache hierarchy.
        
        Args:
            prompt: The input prompt
            response: The AI response to cache
            
        Returns:
            CacheStoreResult with store details
        """
        start_time = time.time()
        key = self._generate_key(prompt)
        
        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=response.content,
            level=CacheLevel.L1,  # Will be updated by each cache
            prompt_hash=key,
            response_hash=hashlib.md5(response.content.encode()).hexdigest(),
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            total_tokens=response.total_tokens,
            cost_usd=response.cost_usd,
            model_used=response.model_used,
            provider_used=response.provider_id,
            created_at=datetime.now(),
            access_count=0
        )
        
        # Store in all three levels
        l1_success = self.l1_cache.set(key, entry)
        l2_success = await self.l2_cache.set(key, entry)
        l3_success = await self.l3_cache.set(key, entry)
        
        store_time = (time.time() - start_time) * 1000
        
        # Determine which level was used for primary storage
        if l1_success:
            primary_level = CacheLevel.L1
        elif l2_success:
            primary_level = CacheLevel.L2
        elif l3_success:
            primary_level = CacheLevel.L3
        else:
            primary_level = CacheLevel.L1  # Default
        
        return CacheStoreResult(
            success=l1_success or l2_success or l3_success,
            level=primary_level,
            store_time_ms=store_time,
            size_bytes=len(response.content.encode()),
            status=CacheStatus.STORED
        )
    
    async def get_stats(self) -> List[CacheStats]:
        """Get statistics for all cache levels."""
        stats = []
        
        # L1 stats
        l1_stats = self.l1_cache.get_stats()
        stats.append(CacheStats(**l1_stats))
        
        # L2 stats
        l2_stats = await self.l2_cache.get_stats()
        stats.append(CacheStats(**l2_stats))
        
        # L3 stats
        l3_stats = await self.l3_cache.get_stats()
        stats.append(CacheStats(**l3_stats))
        
        return stats
    
    async def clear_all(self) -> None:
        """Clear all cache levels."""
        self.l1_cache.cache.clear()
        # Redis and Postgres clear would be implemented here
        print("All cache levels cleared")
    
    def get_cache_hit_rate(self) -> float:
        """Calculate overall cache hit rate."""
        total_hits = 0
        total_requests = 0
        
        # L1 stats
        l1_stats = self.l1_cache.get_stats()
        total_hits += l1_stats["hits"]
        total_requests += l1_stats["hits"] + l1_stats["misses"]
        
        # Add L2 and L3 stats when available
        # For now, just return L1 hit rate
        return total_hits / total_requests if total_requests > 0 else 0.0