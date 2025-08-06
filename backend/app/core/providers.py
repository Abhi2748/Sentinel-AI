"""
Provider Registry and Management
Handles multiple AI providers with circuit breakers and intelligent selection.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import aiohttp
import logging

from ..models.providers import ProviderDecision, ProviderConfig, CircuitBreakerState
from ..models.complexity import ComplexityScore


class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    LOCAL = "local"


@dataclass
class ProviderStats:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0
    last_request_time: float = 0.0


class CircuitBreaker:
    """Circuit breaker pattern for provider reliability."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitBreakerState.CLOSED
        
    def record_success(self):
        """Record a successful request."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        
    def record_failure(self):
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            
    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
            
        if self.state == CircuitBreakerState.OPEN:
            # Check if timeout has passed
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
            
        # HALF_OPEN state
        return True


class ProviderAdapter:
    """Base class for provider adapters."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.stats = ProviderStats()
        self.circuit_breaker = CircuitBreaker()
        
    async def execute(self, prompt: str) -> Dict[str, Any]:
        """Execute a request to the provider."""
        if not self.circuit_breaker.can_execute():
            raise Exception(f"Circuit breaker open for {self.config.name}")
            
        try:
            start_time = time.time()
            result = await self._make_request(prompt)
            
            # Update stats
            response_time = time.time() - start_time
            self.stats.total_requests += 1
            self.stats.successful_requests += 1
            self.stats.avg_response_time = (
                (self.stats.avg_response_time * (self.stats.total_requests - 1) + response_time) 
                / self.stats.total_requests
            )
            self.stats.last_request_time = time.time()
            self.stats.total_cost += result.get('cost', 0.0)
            
            self.circuit_breaker.record_success()
            return result
            
        except Exception as e:
            self.stats.total_requests += 1
            self.stats.failed_requests += 1
            self.circuit_breaker.record_failure()
            raise e
            
    async def _make_request(self, prompt: str) -> Dict[str, Any]:
        """Make the actual request to the provider."""
        raise NotImplementedError


class OpenAIAdapter(ProviderAdapter):
    """OpenAI provider adapter."""
    
    async def _make_request(self, prompt: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    raise Exception(f"OpenAI API error: {response.status}")
                    
                result = await response.json()
                return {
                    "content": result["choices"][0]["message"]["content"],
                    "cost": self._calculate_cost(result),
                    "provider": "openai",
                    "model": self.config.model
                }
                
    def _calculate_cost(self, result: Dict[str, Any]) -> float:
        """Calculate cost based on token usage."""
        # Simplified cost calculation - in production, use actual pricing
        tokens_used = result.get("usage", {}).get("total_tokens", 0)
        return tokens_used * 0.000002  # Approximate cost per token


class AnthropicAdapter(ProviderAdapter):
    """Anthropic provider adapter."""
    
    async def _make_request(self, prompt: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            headers = {
                "x-api-key": self.config.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    raise Exception(f"Anthropic API error: {response.status}")
                    
                result = await response.json()
                return {
                    "content": result["content"][0]["text"],
                    "cost": self._calculate_cost(result),
                    "provider": "anthropic",
                    "model": self.config.model
                }
                
    def _calculate_cost(self, result: Dict[str, Any]) -> float:
        """Calculate cost based on token usage."""
        # Simplified cost calculation
        tokens_used = result.get("usage", {}).get("input_tokens", 0) + result.get("usage", {}).get("output_tokens", 0)
        return tokens_used * 0.000003  # Approximate cost per token


class GroqAdapter(ProviderAdapter):
    """Groq provider adapter."""
    
    async def _make_request(self, prompt: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    raise Exception(f"Groq API error: {response.status}")
                    
                result = await response.json()
                return {
                    "content": result["choices"][0]["message"]["content"],
                    "cost": self._calculate_cost(result),
                    "provider": "groq",
                    "model": self.config.model
                }
                
    def _calculate_cost(self, result: Dict[str, Any]) -> float:
        """Calculate cost based on token usage."""
        # Simplified cost calculation
        tokens_used = result.get("usage", {}).get("total_tokens", 0)
        return tokens_used * 0.000001  # Approximate cost per token


class ProviderRegistry:
    """Registry for managing multiple AI providers."""
    
    def __init__(self):
        self.providers: Dict[str, ProviderAdapter] = {}
        self.provider_configs: Dict[str, ProviderConfig] = {}
        
    def register_provider(self, config: ProviderConfig):
        """Register a new provider."""
        if config.provider_type == ProviderType.OPENAI:
            adapter = OpenAIAdapter(config)
        elif config.provider_type == ProviderType.ANTHROPIC:
            adapter = AnthropicAdapter(config)
        elif config.provider_type == ProviderType.GROQ:
            adapter = GroqAdapter(config)
        else:
            raise ValueError(f"Unsupported provider type: {config.provider_type}")
            
        self.providers[config.name] = adapter
        self.provider_configs[config.name] = config
        
    def select(self, complexity_score: ComplexityScore, requirements: Dict[str, Any]) -> ProviderDecision:
        """
        Select the best provider based on complexity and requirements.
        
        Args:
            complexity_score: The complexity analysis result
            requirements: Additional requirements (speed, cost, etc.)
            
        Returns:
            ProviderDecision with selected provider and fallbacks
        """
        available_providers = [
            name for name, adapter in self.providers.items()
            if adapter.circuit_breaker.can_execute()
        ]
        
        if not available_providers:
            raise Exception("No available providers")
            
        # Simple selection logic - can be enhanced with ML
        if complexity_score.score < 0.3:
            # Simple tasks - use fastest/cheapest
            selected = self._select_by_speed(available_providers)
        elif complexity_score.score < 0.7:
            # Medium complexity - use balanced provider
            selected = self._select_by_balance(available_providers)
        else:
            # Complex tasks - use most capable
            selected = self._select_by_capability(available_providers)
            
        # Create fallback chain
        fallbacks = [p for p in available_providers if p != selected]
        
        return ProviderDecision(
            primary_provider=selected,
            fallback_providers=fallbacks,
            confidence=complexity_score.confidence
        )
        
    def _select_by_speed(self, available: List[str]) -> str:
        """Select provider based on speed."""
        # Prefer Groq for speed
        if "groq" in available:
            return "groq"
        return available[0]
        
    def _select_by_balance(self, available: List[str]) -> str:
        """Select provider based on balance of speed and capability."""
        # Prefer OpenAI for balance
        if "openai" in available:
            return "openai"
        return available[0]
        
    def _select_by_capability(self, available: List[str]) -> str:
        """Select provider based on capability."""
        # Prefer Anthropic for complex tasks
        if "anthropic" in available:
            return "anthropic"
        return available[0]
        
    async def execute_chain(self, prompt: str, decision: ProviderDecision) -> Dict[str, Any]:
        """
        Execute request with fallback chain.
        
        Args:
            prompt: The prompt to execute
            decision: Provider decision with primary and fallbacks
            
        Returns:
            Response from the successful provider
        """
        providers_to_try = [decision.primary_provider] + decision.fallback_providers
        
        for provider_name in providers_to_try:
            try:
                provider = self.providers[provider_name]
                result = await provider.execute(prompt)
                return result
            except Exception as e:
                logging.warning(f"Provider {provider_name} failed: {e}")
                continue
                
        raise Exception("All providers failed")
        
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers."""
        stats = {}
        for name, provider in self.providers.items():
            stats[name] = {
                "total_requests": provider.stats.total_requests,
                "success_rate": (
                    provider.stats.successful_requests / provider.stats.total_requests
                    if provider.stats.total_requests > 0 else 0
                ),
                "avg_response_time": provider.stats.avg_response_time,
                "total_cost": provider.stats.total_cost,
                "circuit_breaker_state": provider.circuit_breaker.state.value
            }
        return stats