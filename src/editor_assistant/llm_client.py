"""
LLM Client for interacting with the API.
"""

import os
import time
import requests
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
from .config.logging_config import warning

# set up the LLM model details
from .config.set_llm import LLMModel, ALL_MODEL_DETAILS


class LLMClient:
    """Client for interacting with the LLM API."""
    
    @staticmethod
    def get_supported_models():
        return [model.value for model in LLMModel]

    def __init__(self, model_name: str):
        """
        Initialize the LLM client for a specific model.
        The client automatically determines the service provider and settings.
        
        Args:
            model_name: The name of the model to use, as defined in the LLMModel enum.
        """
        try:
            self.model_enum = LLMModel(model_name)
        except ValueError:
            raise ValueError(f"Model '{model_name}' is not defined in LLMModel enum.")

        # 1. Get all settings and details for the requested model from the pre-built map
        provider_settings, model_details = ALL_MODEL_DETAILS[self.model_enum]
        
        # 2. Get the API key
        self.api_key = os.environ.get(provider_settings.api_key_env_var)
        if not self.api_key:
            raise ValueError(
                f"API key environment variable '{provider_settings.api_key_env_var}' is not set."
            )
            
        # 3. Set up client properties from the loaded settings
        self.context_window = provider_settings.context_window
        self.max_tokens = provider_settings.max_tokens
        self.model_name = model_name
        self.model = model_details.id  # Use the specific ID for the API call
        self.pricing = model_details.pricing
        self.pricing_currency = provider_settings.pricing_currency
        self.temperature = provider_settings.temperature
        
        # 4. Set up API URL and headers (all providers use OpenAI-compatible format)
        self.api_url = provider_settings.api_base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # set up the request overrides if there is any
        self.request_overrides = provider_settings.request_overrides or {}
        
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
    
    def generate_response(self, prompt: str, 
                          request_name: str = "unnamed_request") -> str:
        """
        Generate a response using the LLM API.
        
        Args:
            prompt: The prompt to send to the API
            request_name: Name of the request for token tracking
            
        Returns:
            Dictionary containing the response text and token usage
        """
        start_time = time.time()
        
        # Build request data (all providers use OpenAI-compatible format)
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.request_overrides
        }
        
        # Implement retry logic with exponential backoff
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract response text (all providers use OpenAI-compatible format)
                response_text = result["choices"][0]["message"]["content"]
                # Track token usage
                input_tokens = result.get("usage", {}).get("prompt_tokens", 0)
                output_tokens = result.get("usage", {}).get("completion_tokens", 0)
                
                # Calculate costs
                input_cost = (input_tokens / 1_000_000) * self.pricing.input
                output_cost = (output_tokens / 1_000_000) * self.pricing.output
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
                
                return response_text
            
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(
                        f"Failed to generate response after "
                        f"{max_retries} attempts: {str(e)}"
                    )
                warning(f"API request failed ({str(e)}), retrying in {retry_delay} seconds...")
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
        
        # Create output directory for this paper
        output_dir.mkdir(parents=True, exist_ok=True)

        # # Save as JSON
        # with open(output_dir / "token_usage.json", 'w', encoding='utf-8') as f:
        #     json.dump(report, f, indent=2)
        
        # Also save a human-readable summary
        with open(output_dir / f"token_usage_{project_name}.txt", 'w', encoding='utf-8') as f:
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
            f.write(f"  Input Cost: {self.pricing_currency}{token_usage['cost']['input_cost']:.6f}\n")
            f.write(f"  Output Cost: {self.pricing_currency}{token_usage['cost']['output_cost']:.6f}\n")
            f.write(f"  Total Cost: {self.pricing_currency}{token_usage['cost']['total_cost']:.6f}\n\n")
            
            # Add detailed request information
            f.write("Detailed Usage by Request:\n")
            for i, req in enumerate(token_usage["requests"]):
                f.write(f"  Request {i+1}: {req['name']}\n")
                f.write(f"    Timestamp: {req.get('timestamp', 'N/A')}\n")
                f.write(f"    Input Tokens: {req['input_tokens']}\n")
                f.write(f"    Output Tokens: {req['output_tokens']}\n")
                f.write(f"    Total Tokens: {req['total_tokens']}\n")
                f.write(f"    Process Time: {req['process_time']:.2f} seconds\n")
                f.write(f"    Input Cost: {self.pricing_currency}{req['input_cost']:.6f}\n")
                f.write(f"    Output Cost: {self.pricing_currency}{req['output_cost']:.6f}\n")
                f.write(f"    Total Cost: {self.pricing_currency}{req['total_cost']:.6f}\n\n")

        # Import here to avoid circular imports
        from .config.logging_config import user_message, progress
        
        # Show concise summary using logging system
        progress(f"Token usage: {total_tokens} tokens ({self.pricing_currency}{token_usage['cost']['total_cost']:.4f}) in {token_usage['process_times']['total_time']:.1f}s")
        
        # Full report saved to file (mentioned only in debug mode)
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Detailed token usage report saved to: {output_dir / 'token_usage.txt'}")
 