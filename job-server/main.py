from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Union, Optional
import uvicorn
from loguru import logger

# Import the agent
from llm_agent import GeminiJobSearchAgent

# Configure global logging
logger.add("fastapi_server.log", rotation="10 MB", level="INFO")

app = FastAPI()

# Get the extension ID from your manifest
EXTENSION_ID = "cmjebemeaofofjkcblgngnngmdmnaclm"

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        f"chrome-extension://{EXTENSION_ID}",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Explicit OPTIONS handler for the endpoint
@app.options("/search_jobs/")
async def options_search_jobs():
    return {"message": "OK"}


class JobSearchRequest(BaseModel):
    companies: str
    position: str
    country: Optional[str] = "United States"


@app.post("/search_jobs/")
async def search_jobs(request: JobSearchRequest):
    """
    Endpoint for job search
    """
    try:
        logger.info(f"Received job search request: {request}")

        # Initialize agent
        agent = GeminiJobSearchAgent()

        # Process job search
        result = agent.process_agent_workflow(
            request.companies, request.position, request.country
        )

        logger.success("Job search completed successfully")
        return {"job_urls": result}

    except Exception as e:
        logger.error(f"Error in job search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
