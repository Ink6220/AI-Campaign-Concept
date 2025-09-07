"""Tests for data models."""
import pytest
from qwen_market.models import (
    CampaignDirection,
    StrategyAgentOutput,
    CreativeConceptAgentOutput,
    MediaAllocation,
    ChannelPlannerAgentOutput,
    KPIGeneratorAgentOutput,
    ValidationStatus,
    EvaluatorValidatorAgentOutput,
    PresenterAgentOutput,
    create_campaign_config
)

def test_campaign_direction_enum():
    """Test CampaignDirection enum values."""
    assert CampaignDirection.awareness == "Awareness"
    assert CampaignDirection.engagement == "Engagement"
    assert CampaignDirection.lead == "Lead Generation"
    assert CampaignDirection.conversion == "Conversion"

def test_strategy_agent_output():
    """Test StrategyAgentOutput model."""
    data = {
        "consumer_insight": "Young adults prefer eco-friendly products",
        "market_context": "Growing trend in sustainability",
        "opportunities_and_challenges": ["High demand", "Market saturation"],
        "recommended_direction": CampaignDirection.awareness,
        "reasoning": "Target audience responds well to environmental messages"
    }
    output = StrategyAgentOutput(**data)
    assert output.recommended_direction == CampaignDirection.awareness
    assert len(output.opportunities_and_challenges) == 2

def test_creative_concept_agent_output():
    """Test CreativeConceptAgentOutput model."""
    data = {
        "big_idea": "Eco-conscious lifestyle",
        "key_messages": ["Save the planet", "Sustainable choices"],
        "campaign_themes": ["Green living"],
        "storytelling_hooks": ["Personal impact stories"]
    }
    output = CreativeConceptAgentOutput(**data)
    assert output.big_idea == "Eco-conscious lifestyle"
    assert len(output.key_messages) == 2

def test_create_campaign_config():
    """Test create_campaign_config function."""
    config = create_campaign_config(
        industry="Fashion",
        target_audience={
            "age": {"min": "18", "max": "35"},
            "location": {"country": "Thailand", "city": "Bangkok"},
            "lifestyle": {"interests": ["fashion", "sustainability"]}
        },
        budget_range={"min": 50000, "max": 100000},
        campaign_objective="Brand Awareness"
    )
    
    assert config["industry"]["name"] == "Fashion"
    assert config["target_audience"]["age"]["min"] == "18"
    assert config["budget_range"]["min"] == 50000
    assert config["campaign_objective"] == "Brand Awareness"
