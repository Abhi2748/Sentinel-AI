"""
IntelligentRoutingEngine
Keeps cost, reliability and compliance guarantees.
"""

from typing import Optional, Dict, Any
from .complexity import ComplexityAnalyzer
from .providers import ProviderRegistry
from .cache import CacheManager
from .budget import BudgetController
from .prompt_opt import PromptOptimizer
from ..models.requests import AIRequest, AIResponse
from ..models.complexity import ComplexityScore
from ..models.providers import ProviderDecision


class IntelligentRouter:
    def __init__(self):
        self.analyzer = ComplexityAnalyzer()
        self.registry = ProviderRegistry()
        self.cache = CacheManager()
        self.budget = BudgetController()
        self.optimizer = PromptOptimizer()

    async def route_request(self, request: AIRequest) -> AIResponse:
        """
        Main routing logic with cost, reliability and compliance guarantees.
        
        Args:
            request: The AI request to process
            
        Returns:
            AIResponse with the result or error
        """
        try:
            # 1. Optimise prompt
            optimised_prompt = self.optimizer.optimise(request.prompt)
            
            # 2. Check budget
            auth = await self.budget.check_authorization(request)
            if not auth.approved:
                return AIResponse(
                    error="Budget exceeded",
                    success=False,
                    cost=0.0,
                    provider="none",
                    cache_hit=False
                )

            # 3. Try cache
            if cached := await self.cache.lookup(optimised_prompt):
                return cached

            # 4. Analyse complexity & pick provider
            score = self.analyzer.analyse(optimised_prompt)
            decision = self.registry.select(score, request.requirements)

            # 5. Execute with fallbacks (circuit breaker inside)
            response = await decision.execute_chain(optimised_prompt)

            # 6. Store cache & metrics
            await self.cache.store(optimised_prompt, response)
            
            return response
            
        except Exception as e:
            return AIResponse(
                error=f"Routing error: {str(e)}",
                success=False,
                cost=0.0,
                provider="none",
                cache_hit=False
            )

    async def get_metrics(self) -> Dict[str, Any]:
        """Get routing metrics for monitoring."""
        return {
            "cache_hit_rate": await self.cache.get_hit_rate(),
            "budget_usage": await self.budget.get_usage_stats(),
            "provider_stats": await self.registry.get_stats(),
            "complexity_distribution": await self.analyzer.get_stats()
        }