"""
ProviderRegistry for managing AI providers with circuit breakers and fallbacks
"""

import time
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ..models.providers import (
    ProviderConfig,
    ProviderStatus,
    ProviderType,
    ProviderResponse,
    ProviderSelection,
    ProviderMetrics
)
from ..models.requests import AIRequest
from ..models.complexity import ComplexityScore


class CircuitBreaker:
    """Circuit breaker pattern for provider fault tolerance."""
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"
    
    def record_success(self):
        if self.state == "half-open":
            self.state = "closed"
            self.failure_count = 0
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def can_execute(self) -> bool:
        if self.state == "closed":
            return True
        elif self.state == "open":
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                self.state = "half-open"
                return True
            return False
        return True


class ProviderRegistry:
    """Manages AI providers with intelligent selection and circuit breakers."""
    
    def __init__(self):
        self.providers: Dict[str, ProviderConfig] = {}
        self.metrics: Dict[str, ProviderMetrics] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._initialize_default_providers()
    
    def _initialize_default_providers(self):
        """Initialize default provider configurations."""
        providers = [
            ProviderConfig(
                provider_id="openai",
                provider_type=ProviderType.OPENAI,
                name="OpenAI",
                description="OpenAI GPT models",
                cost_per_1k_tokens_input=0.0015,
                cost_per_1k_tokens_output=0.002,
                supported_models=["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
                timeout_seconds=30,
                max_retries=3,
                circuit_breaker_threshold=5,
                circuit_breaker_timeout=60
            ),
            ProviderConfig(
                provider_id="anthropic",
                provider_type=ProviderType.ANTHROPIC,
                name="Anthropic",
                description="Anthropic Claude models",
                cost_per_1k_tokens_input=0.003,
                cost_per_1k_tokens_output=0.015,
                supported_models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                timeout_seconds=60,
                max_retries=3,
                circuit_breaker_threshold=3,
                circuit_breaker_timeout=120
            ),
            ProviderConfig(
                provider_id="groq",
                provider_type=ProviderType.GROQ,
                name="Groq",
                description="Groq fast inference models",
                cost_per_1k_tokens_input=0.0005,
                cost_per_1k_tokens_output=0.001,
                supported_models=["llama3-8b", "llama3-70b", "mixtral-8x7b"],
                timeout_seconds=15,
                max_retries=2,
                circuit_breaker_threshold=10,
                circuit_breaker_timeout=30
            )
        ]
        
        for config in providers:
            self.add_provider(config)
    
    def add_provider(self, config: ProviderConfig) -> None:
        """Add a new provider configuration."""
        self.providers[config.provider_id] = config
        self.metrics[config.provider_id] = ProviderMetrics(
            provider_id=config.provider_id,
            metrics_updated_at=datetime.now()
        )
        self.circuit_breakers[config.provider_id] = CircuitBreaker(
            failure_threshold=config.circuit_breaker_threshold,
            timeout_seconds=config.circuit_breaker_timeout
        )
    
    def get_available_providers(self) -> List[ProviderConfig]:
        """Get list of available providers."""
        available = []
        for provider_id, config in self.providers.items():
            if config.is_enabled and config.status == ProviderStatus.ACTIVE:
                circuit_breaker = self.circuit_breakers[provider_id]
                if circuit_breaker.can_execute():
                    available.append(config)
        return available
    
    def select(self, complexity_score: ComplexityScore, requirements: Dict[str, Any]) -> ProviderSelection:
        """Select the best provider based on complexity and requirements."""
        available_providers = self.get_available_providers()
        if not available_providers:
            raise ValueError("No available providers")
        
        # Score each provider
        provider_scores = []
        for provider in available_providers:
            score = self._calculate_provider_score(provider, complexity_score, requirements)
            provider_scores.append((provider, score))
        
        # Sort by score (higher is better)
        provider_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select best provider
        selected_provider, best_score = provider_scores[0]
        
        # Get alternatives and fallbacks
        alternative_providers = [p.provider_id for p, _ in provider_scores[1:3]]
        fallback_providers = [p.provider_id for p, _ in provider_scores[1:]]
        
        # Get circuit breaker status
        circuit_breaker_status = {}
        for provider_id in self.providers:
            circuit_breaker = self.circuit_breakers[provider_id]
            circuit_breaker_status[provider_id] = circuit_breaker.get_status()
        
        # Determine selection reason
        selection_reason = self._get_selection_reason(selected_provider, complexity_score)
        
        return ProviderSelection(
            selected_provider=selected_provider.provider_id,
            selected_model=self._select_model(selected_provider, complexity_score),
            complexity_score=complexity_score.overall_score,
            cost_estimate=complexity_score.estimated_cost_usd,
            performance_score=best_score,
            alternative_providers=alternative_providers,
            selection_reason=selection_reason,
            fallback_providers=fallback_providers,
            circuit_breaker_status=circuit_breaker_status,
            selection_time_ms=0.0,
            selection_algorithm="complexity_based"
        )
    
    def _calculate_provider_score(self, provider: ProviderConfig, 
                                complexity_score: ComplexityScore, 
                                requirements: Dict[str, Any]) -> float:
        """Calculate provider score based on multiple factors."""
        score = 0.0
        
        # Cost factor (lower cost = higher score)
        cost_score = 1.0 - (provider.cost_per_1k_tokens_input / 0.003)
        score += cost_score * 0.3
        
        # Performance factor (based on complexity)
        if complexity_score.level.value == "simple":
            if provider.provider_type == ProviderType.GROQ:
                score += 0.4
            elif provider.provider_type == ProviderType.OPENAI:
                score += 0.3
        elif complexity_score.level.value == "complex":
            if provider.provider_type == ProviderType.ANTHROPIC:
                score += 0.4
            elif provider.provider_type == ProviderType.OPENAI:
                score += 0.3
        
        # Reliability factor
        metrics = self.metrics.get(provider.provider_id)
        if metrics:
            reliability_score = metrics.success_rate
            score += reliability_score * 0.2
        
        # Availability factor
        circuit_breaker = self.circuit_breakers[provider.provider_id]
        if circuit_breaker.state == "closed":
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _select_model(self, provider: ProviderConfig, complexity_score: ComplexityScore) -> str:
        """Select the best model for the provider and complexity."""
        if not provider.supported_models:
            return "default"
        
        if complexity_score.level.value == "simple":
            for model in provider.supported_models:
                if "3.5" in model or "haiku" in model or "8b" in model:
                    return model
        elif complexity_score.level.value == "complex":
            for model in provider.supported_models:
                if "4" in model or "opus" in model or "70b" in model:
                    return model
        
        return provider.supported_models[0]
    
    def _get_selection_reason(self, provider: ProviderConfig, complexity_score: ComplexityScore) -> str:
        """Get human-readable reason for provider selection."""
        if provider.provider_type == ProviderType.GROQ and complexity_score.level.value == "simple":
            return "Selected Groq for fast, cost-effective simple request"
        elif provider.provider_type == ProviderType.ANTHROPIC and complexity_score.level.value == "complex":
            return "Selected Anthropic for complex reasoning task"
        elif provider.provider_type == ProviderType.OPENAI:
            return "Selected OpenAI for balanced performance and cost"
        else:
            return f"Selected {provider.name} based on complexity and requirements"
    
    async def execute_chain(self, prompt: str, selection: ProviderSelection, 
                           request: AIRequest) -> ProviderResponse:
        """Execute request with fallback chain."""
        start_time = time.time()
        
        # Try primary provider
        try:
            response = await self._execute_provider(
                selection.selected_provider,
                selection.selected_model,
                prompt,
                request
            )
            return response
        except Exception as e:
            self._record_provider_failure(selection.selected_provider, str(e))
            
            # Try fallback providers
            for fallback_provider in selection.fallback_providers:
                try:
                    response = await self._execute_provider(
                        fallback_provider,
                        self._select_fallback_model(fallback_provider),
                        prompt,
                        request
                    )
                    return response
                except Exception as fallback_e:
                    self._record_provider_failure(fallback_provider, str(fallback_e))
            
            raise Exception("All providers failed")
    
    async def _execute_provider(self, provider_id: str, model: str, 
                               prompt: str, request: AIRequest) -> ProviderResponse:
        """Execute request with specific provider."""
        provider = self.providers[provider_id]
        circuit_breaker = self.circuit_breakers[provider_id]
        
        if not circuit_breaker.can_execute():
            raise Exception(f"Provider {provider_id} circuit breaker is open")
        
        start_time = time.time()
        
        try:
            # Simulate provider execution
            await asyncio.sleep(0.1)
            
            # Generate mock response
            response = ProviderResponse(
                content=f"Mock response from {provider.name} for: {prompt[:100]}...",
                model_used=model,
                provider_id=provider_id,
                prompt_tokens=len(prompt) // 4,
                completion_tokens=len(prompt) // 8,
                total_tokens=len(prompt) // 3,
                cost_usd=0.01,
                cost_currency="USD",
                response_time_ms=(time.time() - start_time) * 1000,
                success=True
            )
            
            circuit_breaker.record_success()
            self._record_provider_success(provider_id, response)
            
            return response
            
        except Exception as e:
            circuit_breaker.record_failure()
            self._record_provider_failure(provider_id, str(e))
            raise
    
    def _select_fallback_model(self, provider_id: str) -> str:
        """Select model for fallback provider."""
        provider = self.providers[provider_id]
        if provider.supported_models:
            return provider.supported_models[0]
        return "default"
    
    def _record_provider_success(self, provider_id: str, response: ProviderResponse):
        """Record successful provider request."""
        if provider_id in self.metrics:
            metrics = self.metrics[provider_id]
            metrics.successful_requests += 1
            metrics.total_requests += 1
            metrics.success_rate = metrics.successful_requests / metrics.total_requests
            metrics.total_tokens_processed += response.total_tokens
            metrics.total_cost_usd += response.cost_usd
            metrics.avg_cost_per_request = metrics.total_cost_usd / metrics.total_requests
            metrics.last_successful_request = datetime.now()
            metrics.metrics_updated_at = datetime.now()
    
    def _record_provider_failure(self, provider_id: str, error: str):
        """Record failed provider request."""
        if provider_id in self.metrics:
            metrics = self.metrics[provider_id]
            metrics.failed_requests += 1
            metrics.total_requests += 1
            metrics.success_rate = metrics.successful_requests / metrics.total_requests
            metrics.last_error = error
            metrics.last_error_time = datetime.now()
            metrics.error_counts[error] = metrics.error_counts.get(error, 0) + 1
            metrics.metrics_updated_at = datetime.now()
    
    def get_all_metrics(self) -> List[ProviderMetrics]:
        """Get metrics for all providers."""
        return list(self.metrics.values())