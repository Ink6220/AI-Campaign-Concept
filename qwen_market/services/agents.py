import os
from typing import Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ..models import (
    StrategyAgentOutput,
    CreativeConceptAgentOutput,
    ChannelPlannerAgentOutput,
    KPIGeneratorAgentOutput,
    EvaluatorValidatorAgentOutput,
    PresenterAgentOutput
)
from .. import prompts

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "EMPTY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://fe931c1b9bb8.ngrok-free.app/v1")
)

async def run_agent(prompt: str, user_prompt: str, schema=None):
    response = await client.chat.completions.create(
        model="marketeam/Qwen-Marketing",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2048,
        temperature=0.7,
        top_p=0.8,
        presence_penalty=1.5,
        extra_body={
            "top_k": 20,
            "chat_template_kwargs": {"enable_thinking": False},
            **({"guided_json": schema} if schema else {}),
        },
    )
    return response.choices[0].message.content

async def run_strategy_agent(user_prompt: str) -> Dict[str, Any]:
    return await run_agent(
        prompts.prompt_strategy,
        user_prompt,
        StrategyAgentOutput.model_json_schema(),
    )

async def run_creative_concept_agent(strategy: str, user_prompt: str) -> Dict[str, Any]:
    return await run_agent(
        prompts.prompt_concept.format(Strategy=strategy),
        user_prompt,
        CreativeConceptAgentOutput.model_json_schema(),
    )

async def run_channel_planner_agent(strategy: str, concept: str, user_prompt: str) -> Dict[str, Any]:
    return await run_agent(
        prompts.prompt_channel.format(Strategy=strategy, Creative_Concept=concept),
        user_prompt,
        ChannelPlannerAgentOutput.model_json_schema(),
    )

async def run_kpi_generator_agent(strategy: str, concept: str, channel: str, user_prompt: str) -> Dict[str, Any]:
    return await run_agent(
        prompts.prompt_kpi.format(Strategy=strategy, Creative_Concept=concept, Channel=channel),
        user_prompt,
        KPIGeneratorAgentOutput.model_json_schema(),
    )

async def run_evaluator_validator_agent(strategy: str, concept: str, channel: str, kpi: str, user_prompt: str) -> Dict[str, Any]:
    return await run_agent(
        prompts.prompt_senior.format(Strategy=strategy, Creative_Concept=concept, Channel=channel, KPI=kpi),
        user_prompt,
        EvaluatorValidatorAgentOutput.model_json_schema(),
    )

async def run_presenter_agent(strategy: str, concept: str, channel: str, kpi: str, senior: str, user_prompt: str) -> Dict[str, Any]:
    return await run_agent(
        prompts.prompt_presenter.format(
            Strategy=strategy,
            Creative_Concept=concept,
            Channel=channel,
            KPI=kpi,
            Senior_comment=senior,
        ),
        user_prompt,
        PresenterAgentOutput.model_json_schema(),
    )
