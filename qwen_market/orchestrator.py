from typing import Dict, Any
import asyncio
from .services import agents

async def orchestrator(user_prompt: str) -> Dict[str, Any]:
    """
    Orchestrates the execution of all agents in sequence.
    
    Args:
        user_prompt: The user's input prompt containing campaign details
        
    Returns:
        Dict containing outputs from all agents
    """
    # 1. Strategy Agent
    strategy = await agents.run_strategy_agent(user_prompt)
    
    # 2. Creative Concept Agent
    concept = await agents.run_creative_concept_agent(strategy, user_prompt)
    
    # 3. Channel Planner Agent
    channel = await agents.run_channel_planner_agent(strategy, concept, user_prompt)
    
    # 4. KPI Generator Agent
    kpi = await agents.run_kpi_generator_agent(strategy, concept, channel, user_prompt)
    
    # 5. Evaluator/Validator Agent
    senior = await agents.run_evaluator_validator_agent(
        strategy, concept, channel, kpi, user_prompt
    )
    
    # 6. Presenter Agent (final deck in Thai)
    presenter = await agents.run_presenter_agent(
        strategy, concept, channel, kpi, senior, user_prompt
    )
    
    # Return only the presenter's output
    return presenter
