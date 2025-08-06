"""
IntelligentRoutingEngine
Keeps cost, reliability and compliance guarantees.
"""

import time
import uuid
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime

from .complexity import ComplexityAnalyzer
from .providers import ProviderRegistry
from .cache import CacheManager
from .budget import BudgetController
from .prompt_opt import PromptOptimizer
from ..models.requests import AIRequest, AIResponse
from ..models.providers import ProviderResponse, ProviderSelection


class IntelligentRouter:
    """
    Intelligent routing engine that maintains cost, reliability and compliance guarantees.
    Implements the core routing logic as specified in the blueprint.
    """
    
    def __init__(self):
        """Initialize the intelligent router with all components."""
        self.analyzer = ComplexityAnalyzer()
        self.registry = ProviderRegistry()
        self.cache = CacheManager()
        self.budget = BudgetController()
        self.optimizer = PromptOptimizer()
    
    async def route_request(self, request: AIRequest) -> AIResponse:
        """
        Route an AI request through the intelligent routing system.
        
        Args:
            request: The AI request to process
            
        Returns:
            AIResponse with the generated content and metadata
        """
        start_time = time.time()
        
        # Generate request ID if not provided
        if not request.request_id:
            request.request_id = str(uuid.uuid4())
        
        try:
            # 1. Optimize prompt
            optimized_prompt, optimization_stats = self.optimizer.optimize_request(request)
            
            # 2. Analyze complexity
            complexity_result = self.analyzer.analyze_request(request)
            complexity_score = complexity_result.score
            
            # 3. Check budget authorization
            estimated_cost = self.budget.estimate_request_cost(request, complexity_score.overall_score)
            auth = await self.budget.check_authorization(request, estimated_cost)
            
            if not auth.approved:
                return AIResponse(
                    content="",
                    model_used="",
                    provider_used="",
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    cost_usd=0.0,
                    cost_currency="USD",
                    latency_ms=(time.time() - start_time) * 1000,
                    cache_hit=False,
                    request_id=request.request_id,
                    user_id=request.user_id,
                    success=False,
                    error=f"Budget exceeded: {auth.message}"
                )
            
            # 4. Try cache lookup
            cache_result = await self.cache.lookup(optimized_prompt)
            if cache_result.found and cache_result.entry:
                # Return cached response
                cached_entry = cache_result.entry
                return AIResponse(
                    content=cached_entry.value,
                    model_used=cached_entry.model_used,
                    provider_used=cached_entry.provider_used,
                    prompt_tokens=cached_entry.prompt_tokens,
                    completion_tokens=cached_entry.completion_tokens,
                    total_tokens=cached_entry.total_tokens,
                    cost_usd=cached_entry.cost_usd,
                    cost_currency="USD",
                    latency_ms=cache_result.lookup_time_ms,
                    cache_hit=True,
                    cache_level=cache_result.level.value if cache_result.level else None,
                    request_id=request.request_id,
                    user_id=request.user_id,
                    success=True,
                    created_at=datetime.now().isoformat()
                )
            
            # 5. Select provider based on complexity
            selection = self.registry.select(complexity_score, request.requirements)
            
            # 6. Execute with fallbacks
            provider_response = await self.registry.execute_chain(optimized_prompt, selection, request)
            
            # 7. Record usage in budget
            await self.budget.record_usage(request, provider_response.cost_usd)
            
            # 8. Store in cache
            await self.cache.store(optimized_prompt, provider_response)
            
            # 9. Create final response
            total_latency = (time.time() - start_time) * 1000
            
            return AIResponse(
                content=provider_response.content,
                model_used=provider_response.model_used,
                provider_used=provider_response.provider_id,
                prompt_tokens=provider_response.prompt_tokens,
                completion_tokens=provider_response.completion_tokens,
                total_tokens=provider_response.total_tokens,
                cost_usd=provider_response.cost_usd,
                cost_currency=provider_response.cost_currency,
                latency_ms=total_latency,
                cache_hit=False,
                request_id=request.request_id,
                user_id=request.user_id,
                success=True,
                created_at=datetime.now().isoformat(),
                metadata={
                    "complexity_level": complexity_score.level.value,
                    "complexity_score": complexity_score.overall_score,
                    "optimization_reduction": optimization_stats.get("reduction_percentage", 0),
                    "provider_selection": selection.selection_reason,
                    "budget_status": auth.status.value,
                    "cache_lookup_time_ms": cache_result.lookup_time_ms
                }
            )
            
        except Exception as e:
            # Handle errors
            total_latency = (time.time() - start_time) * 1000
            
            return AIResponse(
                content="",
                model_used="",
                provider_used="",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                cost_currency="USD",
                latency_ms=total_latency,
                cache_hit=False,
                request_id=request.request_id,
                user_id=request.user_id,
                success=False,
                error=str(e),
                created_at=datetime.now().isoformat()
            )
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        cache_stats = await self.cache.get_stats()
        provider_metrics = self.registry.get_all_metrics()
        
        return {
            "cache_stats": [stat.dict() for stat in cache_stats],
            "provider_metrics": [metric.dict() for metric in provider_metrics],
            "complexity_cache_stats": self.analyzer.get_cache_stats(),
            "overall_cache_hit_rate": self.cache.get_cache_hit_rate(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_budget_summary(self, request: AIRequest) -> List[Dict[str, Any]]:
        """Get budget summary for all levels in the hierarchy."""
        return await self.budget.get_hierarchy_summary(request)
    
    async def clear_caches(self) -> None:
        """Clear all caches."""
        await self.cache.clear_all()
        self.analyzer.clear_cache()