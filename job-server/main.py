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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobSearchRequest(BaseModel):
    companies: str
    position: str
    country: Optional[str] = "United States"


@app.post("/search_jobs/")
async def search_jobs(request: JobSearchRequest):
    """
    Endpoint for job search

    Args:
        request (JobSearchRequest): Job search parameters

    Returns:
        Dict[str, Dict[str, List[str]]]: Job search results
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


# For direct script running
if __name__ == "__main__":
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True)
