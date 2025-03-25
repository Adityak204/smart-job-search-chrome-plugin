import re
import requests
import time
import random
from typing import List, Dict
from urllib.parse import urlencode
from loguru import logger
from bs4 import BeautifulSoup
import json

# Common headers for all requests
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
    "DNT": "1",
}


def string_to_company_list(companies_string: str) -> List[str]:
    """
    Convert a comma-separated string of companies to a clean list of companies.
    """
    logger.info(f"Processing company string: {companies_string}")
    companies = [
        company.strip() for company in companies_string.split(",") if company.strip()
    ]
    companies = [company.title() for company in companies]
    logger.success(f"Processed companies: {companies}")
    return companies


def get_random_delay():
    """Return a random delay between 2-5 seconds to avoid rate limiting"""
    return random.uniform(2, 5)


def find_exact_linkedin_job_links(
    company: str, position: str, country: str
) -> List[str]:
    """
    Scrape LinkedIn to find exact job post links with improved scraping logic.
    """
    logger.info(f"Searching LinkedIn for {position} at {company} in {country}")
    exact_job_links = []

    try:
        time.sleep(get_random_delay())

        base_url = "https://www.linkedin.com/jobs/search"
        params = {
            "keywords": f"{position} {company}",
            "location": country,
            "f_C": company.lower().replace(" ", ""),
            "position": "1",
            "pageNum": "0",
        }

        headers = {
            **COMMON_HEADERS,
            "x-li-lang": "en_US",
            "x-requested-with": "XMLHttpRequest",
        }

        search_url = f"{base_url}?{urlencode(params)}"
        logger.debug(f"LinkedIn search URL: {search_url}")

        response = requests.get(
            search_url, headers=headers, timeout=10, allow_redirects=True
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # LinkedIn job cards can have different class names - try multiple patterns
        job_card_patterns = [
            "base-card",  # Most common
            "job-search-card",
            "jobs-search-results__list-item",
        ]

        job_cards = []
        for pattern in job_card_patterns:
            job_cards.extend(soup.find_all("div", class_=re.compile(pattern)))
            if job_cards:
                break

        for card in job_cards[:5]:  # Limit to first 5 results
            link = card.find("a", href=True)
            if link and "/jobs/view/" in link["href"]:
                job_url = link["href"].split("?")[0]  # Remove tracking parameters
                exact_job_links.append(job_url)
                logger.success(f"Found LinkedIn job link: {job_url}")

    except requests.RequestException as e:
        logger.error(f"LinkedIn request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected LinkedIn error: {str(e)}")

    return exact_job_links


def find_exact_glassdoor_job_links(
    company: str, position: str, country: str
) -> List[str]:
    """
    Scrape Glassdoor to find exact job post links with improved session handling.
    """
    logger.info(f"Searching Glassdoor for {position} at {company} in {country}")
    exact_job_links = []

    try:
        time.sleep(get_random_delay())

        # Create a session with proper headers
        session = requests.Session()

        # Important: Set realistic headers
        headers = {
            **COMMON_HEADERS,
            "Host": "www.glassdoor.com",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        session.headers.update(headers)

        # First make a request to the homepage to get cookies
        logger.debug("Making initial request to Glassdoor homepage")
        home_response = session.get(
            "https://www.glassdoor.com", timeout=10, allow_redirects=True
        )
        home_response.raise_for_status()

        # Now prepare the search URL
        base_url = "https://www.glassdoor.com/Job/jobs.htm"
        params = {
            "sc.keyword": f"{position} {company}",
            "locT": "N",
            "locId": "1",  # United States
            "jobType": "all",
        }

        search_url = f"{base_url}?{urlencode(params)}"
        logger.debug(f"Glassdoor search URL: {search_url}")

        # Make the search request
        logger.debug("Making search request to Glassdoor")
        response = session.get(search_url, timeout=10, allow_redirects=True)
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Glassdoor has multiple structures for job listings
        job_selectors = [
            "li.react-job-listing",  # Modern selector
            "li.jl",  # Older selector
            "div.jobContainer",  # Another variant
            "div.jobListing",  # Another variant
        ]

        job_cards = []
        for selector in job_selectors:
            job_cards.extend(soup.select(selector))
            if job_cards:
                break

        logger.debug(f"Found {len(job_cards)} job cards")

        for card in job_cards[:5]:  # Limit to first 5 results
            try:
                # Try multiple ways to find the link
                link = None
                link_selectors = [
                    "a[href*='/Job/']",  # Modern links
                    "a.jobLink",  # Older class
                    "a.jobTitle",  # Another variant
                ]

                for selector in link_selectors:
                    link = card.select_one(selector)
                    if link and link.has_attr("href"):
                        break

                if link and link.has_attr("href"):
                    job_path = link["href"].split("?")[0]  # Remove query params
                    if not job_path.startswith("http"):
                        job_path = f"https://www.glassdoor.com{job_path}"

                    # Validate it's a job URL
                    if "/Job/" in job_path:
                        exact_job_links.append(job_path)
                        logger.success(f"Found Glassdoor job link: {job_path}")
            except Exception as e:
                logger.warning(f"Error processing job card: {str(e)}")
                continue

    except requests.RequestException as e:
        logger.error(f"Glassdoor request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected Glassdoor error: {str(e)}")

    return exact_job_links


def advanced_job_search(
    companies: List[str], position: str, country: str
) -> Dict[str, Dict[str, List[str]]]:
    """
    Perform advanced job search with better error handling and rate limiting.
    """
    logger.info(f"Starting advanced job search for {position} in {country}")

    job_search_results = {}

    for company in companies:
        try:
            time.sleep(get_random_delay())

            logger.info(f"Processing company: {company}")

            linkedin_links = find_exact_linkedin_job_links(company, position, country)
            # glassdoor_links = find_exact_glassdoor_job_links(company, position, country)

            job_search_results[company] = {
                "LinkedIn": linkedin_links,
                # "Glassdoor": glassdoor_links,
            }

            logger.success(f"Completed job search for {company}")

        except Exception as e:
            logger.error(f"Error processing {company}: {str(e)}")
            # job_search_results[company] = {"LinkedIn": [], "Glassdoor": []}
            job_search_results[company] = {
                "LinkedIn": [],
            }

    return job_search_results
