# Import key components to make them easily accessible
from .models import (
    CampaignDirection,
    StrategyAgentOutput,
    CreativeConceptAgentOutput,
    ChannelPlannerAgentOutput,
    KPIGeneratorAgentOutput,
    EvaluatorValidatorAgentOutput,
    PresenterAgentOutput,
    create_campaign_config
)
from .orchestrator import orchestrator

# Version
__version__ = "0.1.0"
