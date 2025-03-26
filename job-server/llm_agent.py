import os
import google.generativeai as genai
from typing import Dict, List, Optional
from loguru import logger
import json
from dotenv import load_dotenv
from utils import string_to_company_list, advanced_job_search

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


class GeminiJobSearchAgent:
    def __init__(self):
        self.system_prompt = """
        You are an advanced job search agent that helps job seekers find relevant positions. 
        You have access to specialized tools and should respond in EXACTLY one of these formats:
        
        1. TOOL_REQUEST: tool_name|input_json
        2. FINAL_OUTPUT: json_output
        
        Available Tools:
        1. string_to_company_list: Converts comma-separated company string to list
           - Input: {"companies_string": "Company1, Company2"}
           - Output: ["Company1", "Company2"]
        
        2. advanced_job_search: Finds job openings for given companies and position
           - Input: {"companies": ["Company1", "Company2"], "position": "Job Title", "country": "Country"}
           - Output: {"Company1": {"LinkedIn": ["url1", "url2"]}, "Company2": {"LinkedIn": ["url3"]}}
        
        Workflow Rules:
        1. First use string_to_company_list to process the raw input
        2. Then use advanced_job_search with the processed list
        3. Finally return the results as FINAL_OUTPUT
        
        Important Notes:
        - Always maintain the exact output format
        - The country parameter defaults to "United States"
        - Include all original companies in the output, even if no jobs found
        - Preserve the nested structure with platform keys (LinkedIn/Glassdoor)
        """
        self.chat = model.start_chat(history=[])
        logger.info("Gemini Job Search Agent initialized")

    def process_tool_request(self, tool_call: str) -> str:
        """Process the tool call and return JSON result"""
        try:
            tool_name, input_json = tool_call.split("|", 1)
            input_data = json.loads(input_json)

            if tool_name == "string_to_company_list":
                companies = string_to_company_list(input_data["companies_string"])
                return json.dumps(companies)

            elif tool_name == "advanced_job_search":
                results = advanced_job_search(
                    input_data["companies"],
                    input_data["position"],
                    input_data.get("country", "United States"),
                )
                return json.dumps(results)

            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            logger.error(f"Error processing tool: {e}")
            return json.dumps({"error": str(e)})

    def process_agent_workflow(
        self, companies: str, position: str, country: str = "United States"
    ) -> Dict:
        """Orchestrate the job search using Gemini agent"""
        try:
            # Initialize conversation with system prompt
            prompt = f"""
            Job Search Request:
            - Companies: {companies}
            - Position: {position}
            - Country: {country}
            
            Please process this request using the defined workflow.
            """

            response = self.chat.send_message(self.system_prompt + prompt)

            while True:
                logger.info(f"AGENT RESPONSE: {response.text}")
                content = response.text.strip()
                # logger.debug(f"Agent response: {content}")

                if content.startswith("TOOL_REQUEST:"):
                    tool_call = content.split(":", 1)[1].strip()
                    logger.info(f"Processing tool: {tool_call}")
                    tool_result = self.process_tool_request(tool_call)
                    response = self.chat.send_message(f"TOOL_RESULT: {tool_result}")

                elif content.startswith("FINAL_OUTPUT:"):
                    final_output = content.split(":", 1)[1].strip()
                    logger.success("Received final output from agent")
                    return json.loads(final_output)

                else:
                    # Guide the agent back to proper format if it deviates
                    response = self.chat.send_message(
                        "Please respond with either TOOL_REQUEST or FINAL_OUTPUT format. "
                        "Remember to maintain the exact JSON structures specified."
                    )

        except Exception as e:
            logger.error(f"Error in agent workflow: {e}")
            return {"error": str(e), "status": "failed"}
