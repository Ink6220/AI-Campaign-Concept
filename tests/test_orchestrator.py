"""Tests for the campaign orchestrator."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from qwen_market.orchestrator import orchestrator

@pytest.mark.asyncio
async def test_orchestrator_success():
    """Test the orchestrator with a successful campaign generation."""
    # Mock responses for each agent
    mock_strategy = {
        "consumer_insight": "Test insight",
        "recommended_direction": "Awareness"
    }
    mock_concept = {
        "big_idea": "Test Campaign",
        "key_messages": ["Message 1", "Message 2"]
    }
    mock_channel = {
        "media_mix": [{"platform": "Instagram", "allocation": "40%"}],
        "activity_formats": [{"social_media": ["Stories", "Reels"]}]
    }
    mock_kpi = {
        "budget": "100,000 THB",
        "estimated_metrics": {"reach": "1,000,000"}
    }
    mock_evaluator = {
        "validation_status": "Valid",
        "recommendations": ["Good to go"]
    }
    mock_presenter = {
        "big_idea": "Test Campaign",
        "key_messages": ["Message 1", "Message 2"],
        "presentation_deck": "# Test Presentation"
    }
    
    # Mock all agent functions
    with patch.multiple('qwen_market.services.agents',
                       run_strategy_agent=AsyncMock(return_value=mock_strategy),
                       run_creative_concept_agent=AsyncMock(return_value=mock_concept),
                       run_channel_planner_agent=AsyncMock(return_value=mock_channel),
                       run_kpi_generator_agent=AsyncMock(return_value=mock_kpi),
                       run_evaluator_validator_agent=AsyncMock(return_value=mock_evaluator),
                       run_presenter_agent=AsyncMock(return_value=mock_presenter)):
        
        # Test data
        prompt = "Generate a campaign for test"
        
        # Call the orchestrator
        result = await orchestrator(prompt)
        
        # Assertions
        assert result == mock_presenter
        assert "big_idea" in result
        assert "key_messages" in result
        assert "presentation_deck" in result

@pytest.mark.asyncio
async def test_orchestrator_error_handling():
    """Test the orchestrator's error handling when an agent fails."""
    # Create an async mock that raises an exception
    mock_strategy = AsyncMock()
    mock_strategy.side_effect = Exception("Strategy Agent Error")
    
    # Patch the agent function
    with patch('qwen_market.services.agents.run_strategy_agent', mock_strategy):
        # Test data
        prompt = "Generate a campaign for test"
        
        # Call the orchestrator and expect an exception
        with pytest.raises(Exception) as exc_info:
            await orchestrator(prompt)
            
        # Assertions
        assert "Strategy Agent Error" in str(exc_info.value)
        mock_strategy.assert_awaited_once()
