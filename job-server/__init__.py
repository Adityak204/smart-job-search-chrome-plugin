import os
import json
from typing import List, Dict, Union
from utils import string_to_company_list, fetch_company_url, fetch_job_opening_url


class JobSearchAgent:
    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

    def process_agent_workflow(
        self, companies: str, position: str
    ) -> Dict[str, Union[str, List[str]]]:
        # Step 1: Convert companies string to list
        company_list = string_to_company_list(companies)

        # Step 2: Fetch company URLs
        company_urls = {}
        for company in company_list:
            url = fetch_company_url(company)
            if url:
                company_urls[company] = url

        # Step 3: Search for job openings
        job_results = {}
        for company, url in company_urls.items():
            job_search = fetch_job_opening_url(url, position)
            job_results[company] = job_search

        return job_results


# Example usage
def main():
    agent = JobSearchAgent()
    results = agent.process_agent_workflow(
        "Google, Microsoft, Amazon", "Software Engineer"
    )

    # Pretty print results
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
