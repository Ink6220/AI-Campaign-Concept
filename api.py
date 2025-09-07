"""
API Module for Qwen Marketing Campaign Generator

This module provides RESTful API endpoints for generating and managing
marketing campaigns using Qwen AI.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from qwen_market.orchestrator import orchestrator
from qwen_market.prompts import prompt_representer
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field  # type: ignore
import uvicorn
import asyncio
import json
import logging
import aiohttp  # Add aiohttp for async HTTP requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Campaign Generator API",
    description="API for generating and managing marketing campaigns using Qwen AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
# In production, replace "*" with specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import List

class CampaignRequest(BaseModel):
    """
    Request model for campaign generation.
    
    Attributes:
        industry: The industry for the campaign (e.g., "Fashion", "Technology")
        target_audience: Dictionary containing audience details (age, location, lifestyle)
        genders: List of target genders (["men", "women", "non-binary"])
        budget_range: Budget range for the campaign
        campaign_objective: Primary objective of the campaign
        constraints: Any constraints or limitations for the campaign
        additional_comments: Additional notes or requirements
        callback_url: Optional URL for async callback when campaign is ready
    """
    industry: str = Field(..., min_length=2, max_length=100)
    target_audience: Dict[str, str] = Field(
        ...,
        example={
            "age": "18-35",
            "location": "Bangkok",
            "lifestyle": "Tech-savvy, social media active"
        }
    )
    genders: List[str] = Field(
        ...,
        description="List of target genders (men, women, non-binary, all)",
        example=["men", "women"]
    )
    budget_range: str = Field(..., example="฿50,000-100,000")
    campaign_objective: str = Field(
        ...,
        description="Primary goal of the campaign",
        example="Brand Awareness"
    )
    constraints: str = Field(
        default="",
        description="Any constraints or limitations (e.g., 'no-alcohol, family-friendly')"
    )
    additional_comments: str = Field(
        default="",
        description="Additional notes or specific requirements"
    )
    callback_url: Optional[str] = Field(
        default=None,
        description="Optional URL for async callback when campaign is ready"
    )

@app.post(
    "/generate-campaign",
    response_model=Dict[str, Any],
    summary="Generate a new marketing campaign",
    description="""
    Generates a marketing campaign based on the provided parameters.
    This endpoint processes the request and returns a structured campaign.
    """
)
async def generate_campaign(request: CampaignRequest):
    """
    Generate a marketing campaign based on the provided parameters.
    
    Args:
        request: CampaignRequest containing all necessary parameters
        
    Returns:
        Dict containing the generated campaign data
        
    Raises:
        HTTPException: If there's an error during campaign generation
    """
    try:
        logger.info(f"Received campaign generation request for {request.industry}")
        
        # Convert request to dictionary for easier manipulation
        request_data = request.dict()
        
        # Log the request (excluding sensitive data in production)
        logger.debug(f"Request data: {request_data}")
        
        # Format the prompt for the orchestrator
        prompt = (
            f"Generate a marketing campaign with the following details:\n"
            f"Industry: {request_data['industry']}\n"
            f"Target Audience: {request_data['target_audience']}\n"
            f"Genders: {', '.join(request_data['genders'])}\n"
            f"Budget Range: {request_data['budget_range']}\n"
            f"Objective: {request_data['campaign_objective']}\n"
            f"Constraints: {request_data['constraints']}\n"
            f"Additional Comments: {request_data['additional_comments']}"
        )
        
        logger.debug("Formatted prompt for orchestrator")
        
        # Generate the campaign using the orchestrator
        campaign_result = await orchestrator(prompt)
        
        # Parse the campaign result if it's a string
        if isinstance(campaign_result, str):
            try:
                import json
                campaign_data = json.loads(campaign_result)
            except json.JSONDecodeError:
                campaign_data = {"error": "Failed to parse campaign result"}
        else:
            campaign_data = campaign_result
        
        # Check if async processing is requested
        if request.callback_url:
            logger.info(f"Initiating async processing with callback to {request.callback_url}")
            # Process in background
            asyncio.create_task(process_async_campaign(request_data, request.callback_url))
            return {
                "status": "processing",
                "message": "Campaign generation started. You will receive a callback when ready.",
                "callback_url": request.callback_url
            }
        
        # Process synchronously if no callback URL provided
        logger.info("Processing campaign generation synchronously")
        result = await orchestrator(prompt)
        logger.info("Campaign generation completed successfully")
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error generating campaign: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to generate campaign",
                "error": str(e)
            }
        )

@app.post(
    "/regenerate-campaign",
    response_model=Dict[str, Any],
    summary="Regenerate a marketing campaign",
    description="""
    Regenerates a marketing campaign with modified parameters.
    Useful for refining or tweaking an existing campaign.
    """
)
async def regenerate_campaign(request: Request):
    """
    Regenerate a marketing campaign with optional modifications.
    
    Args:
        request: Raw request containing regeneration parameters
        
    Returns:
        Dict containing the regenerated campaign data
    """
    try:
        logger.info("Received campaign regeneration request")
        data = await request.json()
        
        # Add regeneration flag to the data
        data['is_regeneration'] = True
        
        # Log the request data (sanitize in production)
        logger.debug(f"Regeneration data: {data}")
        
        # Format the prompt for the orchestrator
        prompt = (
            f"Regenerate marketing campaign with the following modifications:\n"
            f"Original Parameters: {json.dumps(data, indent=2)}\n"
            f"Please refine the campaign based on the original parameters."
        )
        
        logger.debug("Formatted regeneration prompt for orchestrator")
        result = await orchestrator(prompt)
        logger.info("Campaign regeneration completed successfully")
        
        return {
            "status": "success",
            "data": result
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"Error regenerating campaign: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to regenerate campaign",
                "error": str(e)
            }
        )

async def process_async_campaign(request_data: Dict[str, Any], callback_url: str) -> None:
    """
    Process campaign generation asynchronously and send result to callback URL.
    
    Args:
        request_data: Dictionary containing campaign parameters
        callback_url: URL to send the result to when processing is complete
    """
    try:
        logger.info(f"Starting async processing for callback URL: {callback_url}")
        
        # Format the prompt for the orchestrator
        prompt = (
            f"Generate a marketing campaign with the following details:\n"
            f"Industry: {request_data['industry']}\n"
            f"Target Audience: {request_data['target_audience']}\n"
            f"Genders: {', '.join(request_data['genders'])}\n"
            f"Budget Range: {request_data['budget_range']}\n"
            f"Objective: {request_data['campaign_objective']}\n"
            f"Constraints: {request_data['constraints']}\n"
            f"Additional Comments: {request_data['additional_comments']}"
        )
        
        # Generate campaign
        result = await orchestrator(prompt)
        
        # Prepare success response
        response = {
            "status": "success",
            "data": result
        }
        
        # Make HTTP POST to the callback URL
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(callback_url, json=response) as resp:
                    if resp.status != 200:
                        logger.error(f"Callback failed with status {resp.status}")
                    else:
                        logger.info(f"Successfully sent callback to {callback_url}")
        except Exception as e:
            logger.error(f"Error sending callback: {str(e)}")
        
        logger.info(f"Async processing completed for {callback_url}")
        
    except Exception as e:
        logger.error(f"Error in async processing: {str(e)}", exc_info=True)
        # Send error to callback URL
        error_response = {
            "status": "error",
            "message": f"Failed to generate campaign: {str(e)}"
        }
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(callback_url, json=error_response)
        except Exception as callback_error:
            logger.error(f"Failed to send error callback: {str(callback_error)}")


@app.get(
    "/",
    summary="API Status",
    description="Check if the API is running and get basic information"
)
async def root():
    """
    Root endpoint that returns API status and version information.
    
    Returns:
        Dict containing API status and documentation links
    """
    return {
        "status": "running",
        "message": "Welcome to the Campaign Generator API",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json"
        },
        "endpoints": {
            "generate_campaign": {
                "method": "POST",
                "path": "/generate-campaign",
                "description": "Generate a new marketing campaign"
            },
            "regenerate_campaign": {
                "method": "POST",
                "path": "/regenerate-campaign",
                "description": "Regenerate a marketing campaign with modifications"
            }
        }
    }

if __name__ == "__main__":
    """
    Main entry point for running the API server.
    
    This starts a uvicorn server with hot-reload enabled for development.
    In production, use a proper ASGI server like uvicorn with gunicorn.
    """
    # Configure uvicorn to run the FastAPI app
    # In production, you might want to use a different configuration
    uvicorn.run(
        "api:app",
        host="0.0.0.0",  # Bind to all network interfaces
        port=8000,       # Default port
        reload=True,     # Enable auto-reload in development
        log_level="info" # Set log level
    )
