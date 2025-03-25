import os
import json
from typing import List, Dict, Union
from loguru import logger

# Import utility functions
from utils import string_to_company_list, advanced_job_search


class JobSearchAgent:
    def __init__(self, log_file: str = "job_search_agent.log"):
        """
        Initialize JobSearchAgent with logging configuration.

        Args:
            log_file (str): Path to the log file
        """
        # Configure logger
        logger.remove()  # Remove default logger
        logger.add(log_file, rotation="10 MB", level="INFO")

        logger.info("JobSearchAgent initialized")

    def process_agent_workflow(
        self, companies: str, position: str, country: str = "United States"
    ) -> Dict[str, Union[str, List[str]]]:
        """
        Orchestrate the job search workflow.

        Args:
            companies (str): Comma-separated list of companies
            position (str): Job position to search for
            country (str, optional): Country to search jobs in. Defaults to "United States"

        Returns:
            Dict[str, Union[str, List[str]]]: Job search results
        """
        try:
            logger.info(f"Starting job search workflow for {position} in {country}")

            # Step 1: Convert companies string to list
            company_list = string_to_company_list(companies)
            logger.info(f"Processed company list: {company_list}")

            # Step 2: Perform advanced job search
            job_results = advanced_job_search(company_list, position, country)
            logger.success("Job search completed successfully")

            return job_results

        except Exception as e:
            logger.error(f"Error in job search workflow: {e}")
            return {"error": str(e), "status": "failed"}


# Example usage
def main():
    agent = JobSearchAgent()
    results = agent.process_agent_workflow(
        "Google, Microsoft, Amazon", "Software Engineer", "United States"
    )

    # Pretty print results
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
