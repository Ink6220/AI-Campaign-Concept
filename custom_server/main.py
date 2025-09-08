from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vllm import AsyncLLMEngine, SamplingParams
from typing import List
import uvicorn
import asyncio
import logging
from time import time

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("qwen_api")

# FastAPI app setup
app = FastAPI(
    title="Qwen Marketing API",
    description="Production-ready FastAPI wrapper for Qwen Marketing model",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # สำหรับ production แนะนำ restrict origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (simple per-process)
RATE_LIMIT = 10  # max requests per IP per minute
rate_limit_store = {}

def check_rate_limit(client_ip: str):
    now = int(time())
    window = now // 60
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = {}
    client_window = rate_limit_store[client_ip]
    client_window[window] = client_window.get(window, 0) + 1
    if client_window[window] > RATE_LIMIT:
        return False
    return True

# LLM Engine Initialization
engine = AsyncLLMEngine("komsan/Qwen-Campaign-Concept")

class GenerationRequest(BaseModel):
    prompt: str
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 1.0

# Routes
@app.post("/generate")
async def generate_text(request: Request, payload: GenerationRequest):
    """
    Generate text using the Qwen Marketing model
    """
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"Received request from {client_ip}: prompt length {len(payload.prompt)}")

    try:
        # Generate text
        result = await engine.generate(
            payload.prompt,
            sampling_params=SamplingParams(
                temperature=payload.temperature,
                top_p=payload.top_p,
                max_tokens=payload.max_tokens
            )
        )

        # Extract generated text (first output)
        generated_text = result[0].outputs[0].text if result and result[0].outputs else ""

        logger.info(f"Generated text length: {len(generated_text)}")

        return {
            "status": "success",
            "generated_text": generated_text,
            "model": "komsan/Qwen-Campaign-Concept"
        }

    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": "komsan/Qwen-Campaign-Concept"}

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Properly close the LLM engine on shutdown"""
    logger.info("Shutting down engine...")
    await engine.close()

# Main entrypoint
if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # ไฟล์นี้ชื่อ main.py
        host="0.0.0.0",
        port=8000,
        reload=False,  # production
        workers=1      # ใช้ 1 worker ต่อ GPU โมเดล
    )