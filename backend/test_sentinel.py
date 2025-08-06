"""
Simple test script for Sentinel-AI 2.0
Tests the core functionality without external dependencies
"""

import asyncio
import json
from datetime import datetime

# Import our modules
from app.models.requests import AIRequest, RequestPriority
from app.models.providers import ModelProvider
from app.core.router import IntelligentRouter


async def test_sentinel_ai():
    """Test the core Sentinel-AI functionality."""
    print("🚀 Testing Sentinel-AI 2.0...")
    
    # Initialize router
    router = IntelligentRouter()
    
    # Test 1: Simple request
    print("\n📝 Test 1: Simple request")
    simple_request = AIRequest(
        prompt="Hello, how are you?",
        user_id="test_user_1",
        team_id="test_team",
        company_id="test_company",
        priority=RequestPriority.NORMAL
    )
    
    response = await router.route_request(simple_request)
    print(f"✅ Simple request completed")
    print(f"   Content: {response.content[:100]}...")
    print(f"   Provider: {response.provider_used}")
    print(f"   Cost: ${response.cost_usd:.4f}")
    print(f"   Cache hit: {response.cache_hit}")
    print(f"   Success: {response.success}")
    
    # Test 2: Complex request
    print("\n🧠 Test 2: Complex request")
    complex_request = AIRequest(
        prompt="Please analyze the following code and explain the algorithm complexity, then suggest optimizations: def fibonacci(n): if n <= 1: return n; return fibonacci(n-1) + fibonacci(n-2)",
        user_id="test_user_2",
        team_id="test_team",
        company_id="test_company",
        priority=RequestPriority.HIGH
    )
    
    response = await router.route_request(complex_request)
    print(f"✅ Complex request completed")
    print(f"   Content: {response.content[:100]}...")
    print(f"   Provider: {response.provider_used}")
    print(f"   Cost: ${response.cost_usd:.4f}")
    print(f"   Cache hit: {response.cache_hit}")
    print(f"   Success: {response.success}")
    
    # Test 3: Cache test (same request should hit cache)
    print("\n💾 Test 3: Cache test")
    response2 = await router.route_request(simple_request)
    print(f"✅ Cache test completed")
    print(f"   Cache hit: {response2.cache_hit}")
    print(f"   Content: {response2.content[:100]}...")
    
    # Test 4: System stats
    print("\n📊 Test 4: System statistics")
    stats = await router.get_system_stats()
    print(f"✅ System stats retrieved")
    print(f"   Cache levels: {len(stats['cache_stats'])}")
    print(f"   Provider metrics: {len(stats['provider_metrics'])}")
    print(f"   Overall cache hit rate: {stats['overall_cache_hit_rate']:.2%}")
    
    # Test 5: Budget summary
    print("\n💰 Test 5: Budget summary")
    budget_summary = await router.get_budget_summary(simple_request)
    print(f"✅ Budget summary retrieved")
    for level_summary in budget_summary:
        print(f"   {level_summary['level']}: ${level_summary['used_usd']:.2f} / ${level_summary['limit_usd']:.2f}")
    
    print("\n🎉 All tests completed successfully!")
    return True


async def test_error_handling():
    """Test error handling."""
    print("\n⚠️ Testing error handling...")
    
    router = IntelligentRouter()
    
    # Test with invalid request
    try:
        invalid_request = AIRequest(
            prompt="",  # Empty prompt
            user_id="test_user",
            priority=RequestPriority.NORMAL
        )
        
        response = await router.route_request(invalid_request)
        print(f"✅ Error handling test completed")
        print(f"   Success: {response.success}")
        print(f"   Error: {response.error}")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    return True


if __name__ == "__main__":
    print("🧪 Starting Sentinel-AI 2.0 Tests")
    print("=" * 50)
    
    # Run tests
    asyncio.run(test_sentinel_ai())
    asyncio.run(test_error_handling())
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\nTo run the full application:")
    print("1. cd backend")
    print("2. pip install -r requirements.txt")
    print("3. uvicorn app.main:app --reload")
    print("4. Visit http://localhost:8000/docs")