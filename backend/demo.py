"""
Demo script for Sentinel-AI 2.0
Shows how to use the application programmatically
"""

import asyncio
import json
from datetime import datetime

# This would normally import the actual modules
# For demo purposes, we'll show the structure

def demo_api_usage():
    """Demonstrate API usage patterns."""
    print("🚀 Sentinel-AI 2.0 Demo")
    print("=" * 50)
    
    # Example 1: Simple request
    print("\n📝 Example 1: Simple request")
    simple_request = {
        "prompt": "Hello, how are you?",
        "user_id": "demo_user_1",
        "team_id": "demo_team",
        "company_id": "demo_company",
        "priority": "normal",
        "temperature": 0.2
    }
    
    print("Request:")
    print(json.dumps(simple_request, indent=2))
    
    # Example 2: Complex request
    print("\n🧠 Example 2: Complex request")
    complex_request = {
        "prompt": "Please analyze the following code and explain the algorithm complexity, then suggest optimizations: def fibonacci(n): if n <= 1: return n; return fibonacci(n-1) + fibonacci(n-2)",
        "user_id": "demo_user_2",
        "team_id": "demo_team",
        "company_id": "demo_company",
        "priority": "high",
        "temperature": 0.1,
        "max_tokens": 1000
    }
    
    print("Request:")
    print(json.dumps(complex_request, indent=2))
    
    # Example 3: Budget check
    print("\n💰 Example 3: Budget summary request")
    budget_request = {
        "prompt": "Test budget",
        "user_id": "demo_user_1",
        "team_id": "demo_team",
        "company_id": "demo_company"
    }
    
    print("Request:")
    print(json.dumps(budget_request, indent=2))

def demo_curl_commands():
    """Show curl commands for testing."""
    print("\n🔄 Curl Commands for Testing")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Health check
    print("\n1. Health Check:")
    print(f"curl {base_url}/health")
    
    # Simple chat completion
    print("\n2. Simple Chat Completion:")
    print(f'''curl -X POST "{base_url}/v1/chat/completions" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "prompt": "Hello, how are you?",
    "user_id": "demo_user",
    "team_id": "demo_team",
    "company_id": "demo_company",
    "priority": "normal"
  }}' ''')
    
    # Complex chat completion
    print("\n3. Complex Chat Completion:")
    print(f'''curl -X POST "{base_url}/v1/chat/completions" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "prompt": "Please analyze this code: def fibonacci(n): if n <= 1: return n; return fibonacci(n-1) + fibonacci(n-2)",
    "user_id": "demo_user",
    "team_id": "demo_team",
    "company_id": "demo_company",
    "priority": "high",
    "max_tokens": 1000
  }}' ''')
    
    # System stats
    print("\n4. System Statistics:")
    print(f"curl {base_url}/v1/stats")
    
    # Budget summary
    print("\n5. Budget Summary:")
    print(f'''curl -X POST "{base_url}/v1/budget/summary" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "prompt": "test",
    "user_id": "demo_user",
    "team_id": "demo_team",
    "company_id": "demo_company"
  }}' ''')
    
    # Clear caches
    print("\n6. Clear Caches:")
    print(f"curl -X POST {base_url}/v1/cache/clear")

def demo_features():
    """Demonstrate key features."""
    print("\n✨ Key Features Demo")
    print("=" * 50)
    
    features = [
        {
            "name": "Intelligent Routing",
            "description": "Automatically selects the best provider based on complexity",
            "example": "Simple requests → Groq, Complex requests → Anthropic"
        },
        {
            "name": "3-Tier Caching",
            "description": "L1 Memory (5min), L2 Redis (1h), L3 Postgres (24h)",
            "example": "75% cache hit rate target"
        },
        {
            "name": "Budget Control",
            "description": "Hierarchical budgets: User → Team → Company",
            "example": "Automatic authorization and alerts"
        },
        {
            "name": "Prompt Optimization",
            "description": "≥50% token reduction while maintaining quality",
            "example": "Removes redundancy, simplifies language"
        },
        {
            "name": "Circuit Breakers",
            "description": "Automatic fallback when providers fail",
            "example": "99.9% uptime guarantee"
        },
        {
            "name": "Cost Reduction",
            "description": "75% average cost reduction target",
            "example": "Through intelligent routing and caching"
        }
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"\n{i}. {feature['name']}")
        print(f"   {feature['description']}")
        print(f"   Example: {feature['example']}")

def demo_architecture():
    """Show the system architecture."""
    print("\n🏗️ System Architecture")
    print("=" * 50)
    
    architecture = """
Client SDK / REST / LangChain
            │
┌────────────┤ API Gateway ├────────────┐
│  Auth • Rate-Limit • Trace • JWT      │
└───────┬───────────────────────────────┘
        │
┌────────────┐ Intelligent Routing ┌────────────┐
│ QueryAnalyzer → ComplexityScorer │
│ ModelSelector → Router → Fallback │
└───────┬───────────────────────────┘
        │
┌──────────────┐ Provider Managers ┌──────────────┐
│ OpenAI • Anthropic • Groq • Local │
└───────┬───────────────────────────┘
        │
┌────────────┐ Data Layer ┌─────────┐
│ L1 • L2 • L3 Cache       │
│ Postgres + Analytics     │
└────────────┴─────────────┘
"""
    
    print(architecture)

def main():
    """Run the demo."""
    demo_api_usage()
    demo_curl_commands()
    demo_features()
    demo_architecture()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\nTo run the actual application:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start the server: uvicorn app.main:app --reload")
    print("3. Visit: http://localhost:8000/docs")
    print("4. Test the endpoints using the interactive Swagger UI")

if __name__ == "__main__":
    main()