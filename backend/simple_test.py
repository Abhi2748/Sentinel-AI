"""
Simple test for Sentinel-AI 2.0 core logic
Tests the basic functionality without external dependencies
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test model imports
        from app.models.requests import AIRequest, AIResponse, RequestPriority
        from app.models.providers import ModelProvider
        from app.models.budget import BudgetLevel, BudgetStatus
        from app.models.cache import CacheLevel, CacheStatus
        from app.models.complexity import ComplexityLevel, ComplexityFactor
        print("✅ All model imports successful")
        
        # Test core imports
        from app.core.complexity import ComplexityAnalyzer
        from app.core.cache import CacheManager
        from app.core.budget import BudgetController
        from app.core.prompt_opt import PromptOptimizer
        from app.core.providers import ProviderRegistry
        print("✅ All core imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_models():
    """Test model creation and validation."""
    print("\n📝 Testing models...")
    
    try:
        from app.models.requests import AIRequest, RequestPriority
        from app.models.providers import ModelProvider
        
        # Test AIRequest creation
        request = AIRequest(
            prompt="Hello, how are you?",
            user_id="test_user",
            team_id="test_team",
            company_id="test_company",
            priority=RequestPriority.NORMAL
        )
        print("✅ AIRequest creation successful")
        
        # Test model validation
        assert request.prompt == "Hello, how are you?"
        assert request.user_id == "test_user"
        assert request.priority == RequestPriority.NORMAL
        print("✅ Model validation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_complexity_analyzer():
    """Test complexity analyzer functionality."""
    print("\n🧠 Testing complexity analyzer...")
    
    try:
        from app.core.complexity import ComplexityAnalyzer
        
        analyzer = ComplexityAnalyzer()
        
        # Test simple prompt
        simple_prompt = "Hello, how are you?"
        score = analyzer.analyse(simple_prompt)
        
        assert score.overall_score >= 0.0
        assert score.overall_score <= 1.0
        assert score.level in ["simple", "moderate", "complex", "very_complex"]
        print("✅ Simple prompt analysis successful")
        
        # Test complex prompt
        complex_prompt = "Please analyze the following code and explain the algorithm complexity, then suggest optimizations: def fibonacci(n): if n <= 1: return n; return fibonacci(n-1) + fibonacci(n-2)"
        score = analyzer.analyse(complex_prompt)
        
        assert score.overall_score >= 0.0
        assert score.overall_score <= 1.0
        print("✅ Complex prompt analysis successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Complexity analyzer test failed: {e}")
        return False

def test_prompt_optimizer():
    """Test prompt optimizer functionality."""
    print("\n🔧 Testing prompt optimizer...")
    
    try:
        from app.core.prompt_opt import PromptOptimizer
        
        optimizer = PromptOptimizer()
        
        # Test prompt optimization
        original_prompt = "Please, if you could kindly help me with this request, I would really appreciate it if you could analyze the following code and provide a detailed explanation."
        optimized_prompt = optimizer.optimise(original_prompt)
        
        assert len(optimized_prompt) < len(original_prompt)
        print("✅ Prompt optimization successful")
        
        # Test optimization stats
        stats = optimizer.get_optimization_stats(original_prompt, optimized_prompt)
        assert stats["reduction_percentage"] > 0
        print("✅ Optimization stats successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt optimizer test failed: {e}")
        return False

def test_provider_registry():
    """Test provider registry functionality."""
    print("\n🏢 Testing provider registry...")
    
    try:
        from app.core.providers import ProviderRegistry
        from app.models.complexity import ComplexityScore, ComplexityLevel
        
        registry = ProviderRegistry()
        
        # Test provider availability
        available_providers = registry.get_available_providers()
        assert len(available_providers) > 0
        print("✅ Provider availability check successful")
        
        # Test provider selection
        complexity_score = ComplexityScore(
            overall_score=0.3,
            level=ComplexityLevel.SIMPLE,
            factors={},
            factor_weights={},
            word_count=10,
            character_count=50,
            sentence_count=1,
            estimated_tokens=20,
            estimated_cost_usd=0.01,
            analysis_time_ms=1.0,
            confidence=0.8
        )
        
        selection = registry.select(complexity_score, {})
        assert selection.selected_provider in ["openai", "anthropic", "groq"]
        print("✅ Provider selection successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Provider registry test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Sentinel-AI 2.0 Core Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_models,
        test_complexity_analyzer,
        test_prompt_optimizer,
        test_provider_registry
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Core functionality is working.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the full application: uvicorn app.main:app --reload")
        print("3. Visit http://localhost:8000/docs for API documentation")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()