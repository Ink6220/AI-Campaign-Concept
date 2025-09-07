"""Tests for the API endpoints."""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_root_endpoint(test_client):
    """Test the root endpoint returns expected response."""
    response = test_client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "endpoints" in data

@pytest.mark.asyncio
async def test_generate_campaign_success(test_client):
    """Test campaign generation with valid data."""
    # Mock the orchestrator to return a sample response
    mock_response = {
        "big_idea": "Test Campaign",
        "key_messages": ["Message 1", "Message 2"],
        "presentation_deck": "# Test Presentation"
    }
    
    with patch('api.orchestrator', new_callable=AsyncMock) as mock_orchestrator:
        mock_orchestrator.return_value = mock_response
        
        # Test data matching the CampaignRequest model
        campaign_data = {
            "industry": "Fashion",
            "target_audience": {
                "age": "18-35",
                "location": "Bangkok",
                "lifestyle": "Fashion-conscious, social media active"
            },
            "genders": ["men", "women"],
            "budget_range": "฿50,000-100,000",
            "campaign_objective": "Brand Awareness",
            "constraints": "Must be family-friendly",
            "additional_comments": "Focus on sustainable fashion"
        }
        
        response = test_client.post("/generate-campaign", json=campaign_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert data["data"] == mock_response
        # The orchestrator is called twice in the implementation
        assert mock_orchestrator.await_count == 2

@pytest.mark.asyncio
async def test_generate_campaign_invalid_data(test_client):
    """Test campaign generation with invalid data."""
    # Missing required fields
    invalid_data = {
        "industry": "",  # Empty industry should be invalid
        "target_audience": {"age": {"min": 18, "max": 35}},
        "genders": ["invalid_gender"]  # Invalid enum value
    }
    response = test_client.post("/generate-campaign", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_regenerate_campaign(test_client):
    """Test campaign regeneration with valid data."""
    # Mock the orchestrator to return a sample response
    mock_response = {
        "big_idea": "Regenerated Campaign",
        "key_messages": ["Updated Message 1", "Updated Message 2"],
        "presentation_deck": "# Updated Presentation"
    }
    
    with patch('api.orchestrator', new_callable=AsyncMock) as mock_orchestrator:
        mock_orchestrator.return_value = mock_response
        
        # Test data for regeneration
        regenerate_data = {
            "industry": "Fashion",
            "target_audience": {
                "age": "18-35",
                "location": "Bangkok",
                "lifestyle": "Fashion-conscious, social media active"
            },
            "previous_results": {"key": "value"},  # Previous campaign data
            "modifications": {"tone": "More professional"}
        }
        
        response = test_client.post("/regenerate-campaign", json=regenerate_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert data["data"] == mock_response
        # The orchestrator should be called once for regeneration
        assert mock_orchestrator.await_count == 1
