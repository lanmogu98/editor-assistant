"""
LLM Client for interacting with the API.
"""

import os
import time
import requests
from datetime import datetime
from typing import Dict, Any
import json
from pathlib import Path
import logging

# set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from ..config.llms.llm_config import llm_config
if not llm_config:
    raise ValueError("LLM configuration not found. \
                        Please check the llm_config.py file.")

class LLMClient:
    """Client for interacting with the LLM API."""
    
    def __init__(self, model_name: str):
        """
        Initialize the LLM client.
        
        Args:
            model: Model to use for generation
        """
        self.api_key = os.environ.get("VOLC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. "
                "Set the VOLC_API_KEY environment variable."
            )
        self.model_context_window = llm_config["MODEL_CONTEXT_WINDOW"]
        self.max_tokens = llm_config["MAX_TOKENS"]
        self.model_name = model_name
        self.model = llm_config["MODELS"][model_name]
        self.api_url = llm_config["API_BASE_URL"]
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Initialize token tracking
        self.token_usage = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "requests": [],
            "process_times": {
                "total_time": 0,
                "request_times": []
            },
            "cost": {
                "input_cost": 0,
                "output_cost": 0,
                "total_cost": 0
            }
        }
        
        # Get pricing for the selected model
        self.pricing = llm_config["PRICING"].get(self.model_name, 
                                                 {"input": 0, "output": 0})
    
    def generate_response(self, prompt: str, 
                          request_name: str = "unnamed_request") -> Dict[str, Any]:
        """
        Generate a response using the LLM API.
        
        Args:
            prompt: The prompt to send to the API
            request_name: Name of the request for token tracking
            
        Returns:
            Dictionary containing the response text and token usage
        """
        start_time = time.time()
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": llm_config["TEMPERATURE"],
            "max_tokens": llm_config["MAX_TOKENS"]
        }
        
        # Implement retry logic with exponential backoff
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                response_text = result["choices"][0]["message"]["content"]
                
                # Track token usage
                input_tokens = result.get("usage", {}).get("prompt_tokens", 0)
                output_tokens = result.get("usage", {}).get("completion_tokens", 0)
                
                # Calculate costs
                input_cost = (input_tokens / 1_000_000) * self.pricing["input"]
                output_cost = (output_tokens / 1_000_000) * self.pricing["output"]
                total_cost = input_cost + output_cost
                
                # Track process time
                end_time = time.time()
                process_time = end_time - start_time
                
                # Update token usage tracking
                self.token_usage["total_input_tokens"] += input_tokens
                self.token_usage["total_output_tokens"] += output_tokens
                self.token_usage["process_times"]["total_time"] += process_time
                self.token_usage["cost"]["input_cost"] += input_cost
                self.token_usage["cost"]["output_cost"] += output_cost
                self.token_usage["cost"]["total_cost"] += total_cost
                
                self.token_usage["requests"].append({
                    "name": request_name,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "process_time": process_time,
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                    "total_cost": total_cost,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                self.token_usage["process_times"]["request_times"].append({
                    "name": request_name,
                    "process_time": process_time
                })
                
                return {
                    "text": response_text,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "process_time": process_time,
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                    "total_cost": total_cost
                }
            
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(
                        f"Failed to generate response after "
                        f"{max_retries} attempts: {str(e)}"
                    )
                
                print(f"API request failed, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
    
    def get_token_usage(self) -> Dict[str, Any]:
        """
        Get the current token usage statistics.
        
        Returns:
            Dictionary with token usage statistics
        """
        return self.token_usage
    
    def save_token_usage_report(self, project_name: str, output_dir: Path) -> None:
        """
        Save a report of token usage for the paper processing.
        
        Args:
            paper_name: Name of the paper
        """
        token_usage = self.token_usage
        
        # Create a formatted report
        report = {
            "project_name": project_name,
            "model": self.model,
            "model_name": self.model_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            #"token_usage": token_usage
        }
        
        # Calculate total tokens and estimated cost (if pricing info is available)
        total_tokens = token_usage["total_input_tokens"] + \
                        token_usage["total_output_tokens"]
        report["total_tokens"] = total_tokens
        report["total_process_time"] = token_usage["process_times"]["total_time"]
        report["total_cost"] = token_usage["cost"]["total_cost"]
        
        # Save as JSON
        token_dir = output_dir / "token_usage"
        token_dir.mkdir(parents=True, exist_ok=True)
        
        with open(token_dir / "token_usage.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        # Also save a human-readable summary
        with open(token_dir / "token_usage.txt", 'w', encoding='utf-8') as f:
            f.write(f"Token Usage Report for {project_name}\n")
            f.write(f"Generated on: {report['timestamp']}\n")
            f.write(f"Model: {report['model']} ({report['model_name']})\n\n")

            f.write("Summary:\n")
            f.write(f"  Total Input Tokens: {token_usage['total_input_tokens']}\n")
            f.write(f"  Total Output Tokens: {token_usage['total_output_tokens']}\n")
            f.write(f"  Total Tokens: {total_tokens}\n")
            f.write(
                f"  Total Process Time: "
                f"{token_usage['process_times']['total_time']:.2f} seconds\n"
            )
            f.write(f"  Input Cost: ¥{token_usage['cost']['input_cost']:.6f}\n")
            f.write(f"  Output Cost: ¥{token_usage['cost']['output_cost']:.6f}\n")
            f.write(f"  Total Cost: ¥{token_usage['cost']['total_cost']:.6f}\n\n")
            
            # Add detailed request information
            f.write("Detailed Usage by Request:\n")
            for i, req in enumerate(token_usage["requests"]):
                f.write(f"  Request {i+1}: {req['name']}\n")
                f.write(f"    Timestamp: {req.get('timestamp', 'N/A')}\n")
                f.write(f"    Input Tokens: {req['input_tokens']}\n")
                f.write(f"    Output Tokens: {req['output_tokens']}\n")
                f.write(f"    Total Tokens: {req['total_tokens']}\n")
                f.write(f"    Process Time: {req['process_time']:.2f} seconds\n")
                f.write(f"    Input Cost: ¥{req['input_cost']:.6f}\n")
                f.write(f"    Output Cost: ¥{req['output_cost']:.6f}\n")
                f.write(f"    Total Cost: ¥{req['total_cost']:.6f}\n\n")

        # print the summary to the console
        print (f"Token Usage Report for '{project_name}'")
        print (f"Generated on: on: {report['timestamp']}")
        print (f"Model: {report['model']} ({report['model_name']})\n")       

        print (f"  Total Input Tokens: {token_usage['total_input_tokens']}")
        print (f"  Total Output Tokens: {token_usage['total_output_tokens']}")
        print (f"  Total Tokens: {total_tokens}\n")
        print (
            f"  Total Process Time: "
            f"{token_usage['process_times']['total_time']:.2f} seconds"
        )
        print (f"  Input Cost: ¥{token_usage['cost']['input_cost']:.6f}")
        print (f"  Output Cost: ¥{token_usage['cost']['output_cost']:.6f}")
        print (f"  Total Cost: ¥{token_usage['cost']['total_cost']:.6f}\n")
