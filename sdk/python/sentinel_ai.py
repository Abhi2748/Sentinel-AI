"""
Sentinel-AI Python SDK
Easy-to-use client for intelligent AI routing.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    AUTO = "auto"


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatResponse:
    content: str
    provider: str
    model: str
    cost: float
    tokens_used: Optional[int] = None
    cache_hit: bool = False


class SentinelAIClient:
    """
    Sentinel-AI Python client for intelligent AI routing.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            
    def _get_session(self) -> aiohttp.ClientSession:
        if not self._session:
            raise RuntimeError("Client must be used as async context manager")
        return self._session
        
    async def chat(
        self,
        messages: List[ChatMessage],
        provider: ProviderType = ProviderType.AUTO,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> ChatResponse:
        """
        Send a chat completion request through intelligent routing.
        
        Args:
            messages: List of chat messages
            provider: AI provider to use (or AUTO for intelligent selection)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            ChatResponse with the AI response and metadata
        """
        session = self._get_session()
        
        payload = {
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "provider": provider.value,
            "requirements": {}
        }
        
        if max_tokens:
            payload["requirements"]["max_tokens"] = max_tokens
        if temperature:
            payload["requirements"]["temperature"] = temperature
        payload["requirements"].update(kwargs)
        
        async with session.post(
            f"{self.base_url}/v1/ai/chat",
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"API request failed: {response.status} - {error_text}")
                
            data = await response.json()
            
            return ChatResponse(
                content=data["content"],
                provider=data["provider"],
                model=data.get("model", "unknown"),
                cost=data.get("cost", 0.0),
                tokens_used=data.get("tokens_used"),
                cache_hit=data.get("cache_hit", False)
            )
            
    async def complete(
        self,
        prompt: str,
        provider: ProviderType = ProviderType.AUTO,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> ChatResponse:
        """
        Send a simple completion request.
        
        Args:
            prompt: The prompt to complete
            provider: AI provider to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            ChatResponse with the AI response and metadata
        """
        messages = [ChatMessage(role="user", content=prompt)]
        return await self.chat(messages, provider, max_tokens, temperature, **kwargs)
        
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get routing metrics and statistics.
        
        Returns:
            Dictionary with various metrics
        """
        session = self._get_session()
        
        async with session.get(f"{self.base_url}/v1/ai/metrics") as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"API request failed: {response.status} - {error_text}")
                
            return await response.json()


# Convenience functions for synchronous usage
def create_client(api_key: str, base_url: str = "http://localhost:8000") -> SentinelAIClient:
    """Create a Sentinel-AI client."""
    return SentinelAIClient(api_key, base_url)


async def chat_completion(
    api_key: str,
    messages: List[ChatMessage],
    base_url: str = "http://localhost:8000",
    **kwargs
) -> ChatResponse:
    """Simple function for chat completion."""
    async with SentinelAIClient(api_key, base_url) as client:
        return await client.chat(messages, **kwargs)


async def text_completion(
    api_key: str,
    prompt: str,
    base_url: str = "http://localhost:8000",
    **kwargs
) -> ChatResponse:
    """Simple function for text completion."""
    async with SentinelAIClient(api_key, base_url) as client:
        return await client.complete(prompt, **kwargs)


# Example usage
if __name__ == "__main__":
    async def main():
        # Example usage
        api_key = "your-api-key"
        
        async with SentinelAIClient(api_key) as client:
            # Chat completion
            messages = [
                ChatMessage(role="user", content="Hello, how are you?")
            ]
            response = await client.chat(messages)
            print(f"Response: {response.content}")
            print(f"Provider: {response.provider}")
            print(f"Cost: ${response.cost}")
            
            # Simple completion
            response = await client.complete("Explain quantum computing in simple terms")
            print(f"Response: {response.content}")
            
            # Get metrics
            metrics = await client.get_metrics()
            print(f"Metrics: {metrics}")
    
    asyncio.run(main())