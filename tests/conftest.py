"""Pytest configuration and fixtures for API testing."""
import os
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import app after path is set
try:
    from api import app
except ImportError:
    import sys
    print("Error importing app. Python path:", sys.path)
    raise

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_campaign_data():
    """Return sample campaign data for testing."""
    return {
        "industry": "Fashion Retail",
        "target_audience": {
            "age": {"min": 18, "max": 35},
            "location": "Bangkok",
            "lifestyle": "Fashion-conscious, active on social media"
        },
        "genders": ["men", "women"],
        "budget_range": "Medium (฿50,000-100,000)",
        "campaign_objective": "Brand Awareness",
        "constraints": "Must be family-friendly",
        "additional_comments": "Focus on sustainable fashion"
    }

@pytest.fixture
def mock_orchestrator():
    """Mock the orchestrator for testing."""
    with patch('qwen_market.orchestrator.orchestrator') as mock:
        yield mock

@pytest.fixture
async def async_client():
    """Async test client for testing async endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
