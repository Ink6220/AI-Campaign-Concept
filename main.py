import asyncio
from qwen_market.orchestrator import orchestrator

if __name__ == "__main__":
    user_prompt = """{
      "industry": "Healthy Food Delivery",
      "target_audience": {
        "age": "25-35",
        "location": "Bangkok",
        "lifestyle": "Working Millennials"
      },
      "budget_range": "500,000 THB",
      "campaign_objective": "Lead Generation"
    }"""

    results = asyncio.run(orchestrator(user_prompt))
    for k, v in results.items():
        print(f"\n=== {k.upper()} ===\n{v}\n")