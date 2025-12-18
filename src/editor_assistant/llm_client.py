"""
LLM Client for interacting with the API.
"""

import os
import time
import hashlib
import requests
from collections import deque, OrderedDict
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from .config.logging_config import warning, progress, user_message
from .config.constants import (
    MAX_API_RETRIES,
    INITIAL_RETRY_DELAY_SECONDS,
    MIN_REQUEST_INTERVAL_SECONDS,
    MAX_REQUESTS_PER_MINUTE,
    RATE_LIMIT_WARNINGS_ENABLED,
    RESPONSE_CACHE_ENABLED,
    RESPONSE_CACHE_MAX_SIZE,
    RESPONSE_CACHE_TTL_SECONDS,
)

# set up the LLM model details
from .config.set_llm import LLMModel, ALL_MODEL_DETAILS


class ResponseCache:
    """LRU cache for LLM responses with TTL support."""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self._cache: OrderedDict[str, Tuple[str, float]] = OrderedDict()
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0

    def _make_key(self, prompt: str, model: str) -> str:
        """Create a cache key from prompt and model."""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt: str, model: str) -> Optional[str]:
        """Get cached response if exists and not expired."""
        key = self._make_key(prompt, model)

        if key not in self._cache:
            self._misses += 1
            return None

        response, timestamp = self._cache[key]

        # Check TTL expiration
        if self._ttl_seconds > 0:
            if time.time() - timestamp > self._ttl_seconds:
                del self._cache[key]
                self._misses += 1
                return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        self._hits += 1
        return response

    def set(self, prompt: str, model: str, response: str) -> None:
        """Store response in cache."""
        key = self._make_key(prompt, model)

        # Remove oldest if at capacity
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)

        self._cache[key] = (response, time.time())

    def get_stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "size": len(self._cache),
            "max_size": self._max_size,
        }

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0


class LLMClient:
    """Client for interacting with the LLM API."""
    
    @staticmethod
    def get_supported_models():
        return [model.value for model in LLMModel]

    def __init__(self, model_name: str, thinking_level: str = None):
        """
        Initialize the LLM client for a specific model.
        The client automatically determines the service provider and settings.
        
        Args:
            model_name: The name of the model to use, as defined in the LLMModel enum.
            thinking_level: Optional thinking/reasoning level override (low, medium, high, minimal).
                          For Gemini 3+, maps to reasoning_effort in OpenAI-compatible format.
        """
        self._thinking_level = thinking_level
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
        self.request_overrides = dict(provider_settings.request_overrides or {})
        
        # Apply thinking_level override if provided (for Gemini 3+ via OpenAI-compat)
        if self._thinking_level:
            self.request_overrides["reasoning_effort"] = self._thinking_level
        
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

        # Initialize rate limiting state from provider config or use defaults
        if provider_settings.rate_limit:
            self._min_interval = provider_settings.rate_limit.min_interval_seconds
            self._max_rpm = provider_settings.rate_limit.max_requests_per_minute
        else:
            self._min_interval = MIN_REQUEST_INTERVAL_SECONDS
            self._max_rpm = MAX_REQUESTS_PER_MINUTE
        
        self._last_request_time = 0.0
        self._request_timestamps = deque(maxlen=self._max_rpm if self._max_rpm > 0 else 100)

        # Initialize response cache
        self._cache_enabled = RESPONSE_CACHE_ENABLED
        self._cache = ResponseCache(
            max_size=RESPONSE_CACHE_MAX_SIZE,
            ttl_seconds=RESPONSE_CACHE_TTL_SECONDS
        )

    def _wait_for_rate_limit(self) -> None:
        """
        Wait if necessary to respect rate limits.

        Enforces:
        1. Minimum interval between requests (per-provider configurable)
        2. Maximum requests per minute (per-provider configurable)
        """
        current_time = time.time()

        # Check minimum interval between requests
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_interval:
            wait_time = self._min_interval - time_since_last
            if RATE_LIMIT_WARNINGS_ENABLED:
                warning(f"Rate limiting: waiting {wait_time:.2f}s (min interval)")
            time.sleep(wait_time)
            current_time = time.time()

        # Check per-minute rate limit
        if self._max_rpm > 0:
            # Remove timestamps older than 60 seconds
            cutoff_time = current_time - 60
            while self._request_timestamps and self._request_timestamps[0] < cutoff_time:
                self._request_timestamps.popleft()

            # If at limit, wait until oldest request expires
            if len(self._request_timestamps) >= self._max_rpm:
                wait_time = self._request_timestamps[0] + 60 - current_time
                if wait_time > 0:
                    if RATE_LIMIT_WARNINGS_ENABLED:
                        warning(f"Rate limiting: waiting {wait_time:.2f}s (per-minute limit)")
                    time.sleep(wait_time)
                    current_time = time.time()

        # Record this request
        self._last_request_time = current_time
        self._request_timestamps.append(current_time)

    def generate_response(self, prompt: str,
                          request_name: str = "unnamed_request",
                          stream: bool = False) -> str:
        """
        Generate a response using the LLM API.

        Args:
            prompt: The prompt to send to the API
            request_name: Name of the request for token tracking
            stream: If True, stream the response and print in real-time

        Returns:
            The response text
        """
        # Check cache first (if enabled)
        if self._cache_enabled:
            cached_response = self._cache.get(prompt, self.model)
            if cached_response is not None:
                progress(f"Cache hit for {request_name}")
                return cached_response

        # Apply rate limiting before making request
        self._wait_for_rate_limit()

        start_time = time.time()

        # Build request data (all providers use OpenAI-compatible format)
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": stream,
            **self.request_overrides
        }
        
        # Implement retry logic with exponential backoff
        retry_delay = INITIAL_RETRY_DELAY_SECONDS

        for attempt in range(MAX_API_RETRIES):
            try:
                if stream:
                    response_text = self._stream_response(data, start_time, request_name)
                else:
                    response_text = self._non_stream_response(data, start_time, request_name)

                # Store in cache (if enabled)
                if self._cache_enabled:
                    self._cache.set(prompt, self.model, response_text)

                return response_text
            
            except requests.exceptions.RequestException as e:
                if attempt == MAX_API_RETRIES - 1:
                    raise Exception(
                        f"Failed to generate response after "
                        f"{MAX_API_RETRIES} attempts: {str(e)}"
                    )
                warning(f"API request failed ({str(e)}), retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

    def _non_stream_response(self, data: dict, start_time: float, request_name: str) -> str:
        """Handle non-streaming API response."""
        response = requests.post(self.api_url, headers=self.headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract response text
        response_text = result["choices"][0]["message"]["content"]
        
        # Track token usage
        input_tokens = result.get("usage", {}).get("prompt_tokens", 0)
        output_tokens = result.get("usage", {}).get("completion_tokens", 0)
        
        self._track_usage(input_tokens, output_tokens, start_time, request_name)
        
        return response_text

    def _stream_response(self, data: dict, start_time: float, request_name: str) -> str:
        """Handle streaming API response with real-time output."""
        import json
        import sys
        
        response = requests.post(
            self.api_url, 
            headers=self.headers, 
            json=data, 
            stream=True
        )
        response.raise_for_status()
        
        full_content = []
        input_tokens = 0
        output_tokens = 0
        
        for line in response.iter_lines():
            if not line:
                continue
            
            line_text = line.decode('utf-8')
            
            # Skip SSE prefix
            if line_text.startswith('data: '):
                line_text = line_text[6:]
            
            # Skip [DONE] marker
            if line_text.strip() == '[DONE]':
                break
            
            try:
                chunk = json.loads(line_text)
                
                # Extract content delta
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0].get('delta', {})
                    content = delta.get('content', '')
                    
                    if content:
                        full_content.append(content)
                        # Print in real-time
                        print(content, end='', flush=True)
                
                # Some APIs return usage in the final chunk
                if 'usage' in chunk and chunk['usage'] is not None:
                    input_tokens = chunk['usage'].get('prompt_tokens', 0)
                    output_tokens = chunk['usage'].get('completion_tokens', 0)
                    
            except json.JSONDecodeError:
                continue
        
        # Print newline after streaming completes
        print()
        
        response_text = ''.join(full_content)
        
        # Estimate tokens if not provided (for APIs that don't return usage in stream)
        if output_tokens == 0:
            output_tokens = len(response_text) // 4  # Rough estimate
        
        self._track_usage(input_tokens, output_tokens, start_time, request_name)
        
        return response_text

    def _track_usage(self, input_tokens: int, output_tokens: int, 
                     start_time: float, request_name: str) -> None:
        """Track token usage and costs."""
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
    
    def get_token_usage(self) -> Dict[str, Any]:
        """
        Get the current token usage statistics.

        Returns:
            Dictionary with token usage statistics
        """
        return self.token_usage

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache hit/miss stats
        """
        return self._cache.get_stats()

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache.clear()

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

        # Save a human-readable summary
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

        # Show concise summary using logging system
        progress(f"Token usage: {total_tokens} tokens ({self.pricing_currency}{token_usage['cost']['total_cost']:.4f}) in {token_usage['process_times']['total_time']:.1f}s")
        
        # Full report saved to file (mentioned only in debug mode)
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Detailed token usage report saved to: {output_dir / 'token_usage.txt'}")
 