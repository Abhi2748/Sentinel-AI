"""
Tests for the IntelligentRouter.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from ..app.core.router import IntelligentRouter
from ..app.models.requests import AIRequest, AIResponse


@pytest.fixture
def mock_router():
    """Create a router with mocked dependencies."""
    router = IntelligentRouter()
    
    # Mock the dependencies
    router.analyzer = Mock()
    router.registry = Mock()
    router.cache = Mock()
    router.budget = Mock()
    router.optimizer = Mock()
    
    return router


@pytest.mark.asyncio
async def test_route_request_success(mock_router):
    """Test successful request routing."""
    # Setup mocks
    mock_router.optimizer.optimise.return_value = "optimized prompt"
    mock_router.budget.check_authorization.return_value = Mock(approved=True)
    mock_router.cache.lookup.return_value = None
    mock_router.analyzer.analyse.return_value = Mock(score=0.5, confidence=0.8)
    mock_router.registry.select.return_value = Mock()
    mock_router.registry.execute_chain.return_value = {
        "content": "test response",
        "cost": 0.001,
        "provider": "openai",
        "model": "gpt-3.5-turbo"
    }
    
    # Create test request
    request = AIRequest(
        prompt="test prompt",
        requirements={},
        user_id="test_user"
    )
    
    # Execute
    response = await mock_router.route_request(request)
    
    # Assertions
    assert response.success is True
    assert response.content == "test response"
    assert response.cost == 0.001
    assert response.provider == "openai"


@pytest.mark.asyncio
async def test_route_request_budget_exceeded(mock_router):
    """Test request routing when budget is exceeded."""
    # Setup mocks
    mock_router.optimizer.optimise.return_value = "optimized prompt"
    mock_router.budget.check_authorization.return_value = Mock(approved=False)
    
    # Create test request
    request = AIRequest(
        prompt="test prompt",
        requirements={},
        user_id="test_user"
    )
    
    # Execute
    response = await mock_router.route_request(request)
    
    # Assertions
    assert response.success is False
    assert "Budget exceeded" in response.error


@pytest.mark.asyncio
async def test_route_request_cache_hit(mock_router):
    """Test request routing with cache hit."""
    # Setup mocks
    mock_router.optimizer.optimise.return_value = "optimized prompt"
    mock_router.budget.check_authorization.return_value = Mock(approved=True)
    mock_router.cache.lookup.return_value = AIResponse(
        content="cached response",
        success=True,
        cost=0.0005,
        provider="openai",
        cache_hit=True
    )
    
    # Create test request
    request = AIRequest(
        prompt="test prompt",
        requirements={},
        user_id="test_user"
    )
    
    # Execute
    response = await mock_router.route_request(request)
    
    # Assertions
    assert response.success is True
    assert response.content == "cached response"
    assert response.cache_hit is True


@pytest.mark.asyncio
async def test_route_request_exception(mock_router):
    """Test request routing when an exception occurs."""
    # Setup mocks to raise exception
    mock_router.optimizer.optimise.side_effect = Exception("Test error")
    
    # Create test request
    request = AIRequest(
        prompt="test prompt",
        requirements={},
        user_id="test_user"
    )
    
    # Execute
    response = await mock_router.route_request(request)
    
    # Assertions
    assert response.success is False
    assert "Routing error" in response.error