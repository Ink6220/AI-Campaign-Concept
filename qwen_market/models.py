from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class CampaignDirection(str, Enum):
    awareness = "Awareness"
    engagement = "Engagement"
    lead = "Lead Generation"
    conversion = "Conversion"

class StrategyAgentOutput(BaseModel):
    consumer_insight: str
    market_context: str
    opportunities_and_challenges: List[str]
    recommended_direction: CampaignDirection
    reasoning: str

class CreativeConceptAgentOutput(BaseModel):
    big_idea: str
    key_messages: List[str]
    campaign_themes: List[str]
    storytelling_hooks: List[str]

class MediaAllocation(BaseModel):
    platform: str
    allocation: str  # e.g., "30%"

class ChannelPlannerAgentOutput(BaseModel):
    media_mix: List[MediaAllocation]
    activity_formats: List[Dict[str, List[str]]]
    rationale: str

class KPIGeneratorAgentOutput(BaseModel):
    budget: str
    estimated_metrics: Dict[str, str]  # e.g., {"Reach": "2,000,000"}
    assumptions_used: List[str]

class ValidationStatus(str, Enum):
    valid = "Valid"
    needs_revision = "Needs Revision"
    unrealistic = "Unrealistic"

class EvaluatorValidatorAgentOutput(BaseModel):
    validation_status: ValidationStatus
    flagged_issues: List[str]
    recommendations: List[str]

class PresenterAgentOutput(BaseModel):
    big_idea: str
    key_messages: list[str]
    channels: list[str]
    kpis: dict

def create_campaign_config(
    industry: str,
    target_audience: Dict[str, Dict[str, str]],
    budget_range: Dict[str, float],
    campaign_objective: str
) -> Dict:
    """
    Create a campaign configuration dictionary.
    
    Args:
        industry: The industry for the campaign (e.g., 'Retail', 'Technology')
        target_audience: Dictionary containing audience details with keys:
            - age: Dict with min_age and max_age
            - location: Dict with country, city, etc.
            - lifestyle: Dict with interests, behaviors, etc.
        budget_range: Dictionary with 'min' and 'max' budget in THB
        campaign_objective: The main objective of the campaign
        
    Returns:
        Dict: Structured campaign configuration
    """
    return {
        "industry": {"name": industry},
        "target_audience": {
            "age": target_audience.get("age", {}),
            "location": target_audience.get("location", {}),
            "lifestyle": target_audience.get("lifestyle", {})
        },
        "budget_range": {
            "min": budget_range.get("min", 0),
            "max": budget_range.get("max", 0),
            "currency": "THB"
        },
        "campaign_objective": campaign_objective
    }
