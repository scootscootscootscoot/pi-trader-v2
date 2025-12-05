import requests
import logging
import json
import time
import os
from typing import List, Dict, Optional, Any, Union

logger = logging.getLogger(__name__)

# Custom Exceptions
class OpenRouterError(Exception):
    """Base exception for OpenRouter API errors"""
    pass

class OpenRouterRateLimitError(OpenRouterError):
    """Raised when rate limit is exceeded"""
    pass

class OpenRouterAuthenticationError(OpenRouterError):
    """Raised when authentication fails"""
    pass

class OpenRouterModelError(OpenRouterError):
    """Raised when model is invalid or unavailable"""
    pass

class OpenRouterClient:
    """
    OpenRouter API client for chat completions.
    Includes rate limiting for free tier (1 request per 15 minutes)
    and automatic retry logic with error handling.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None,
                 base_url: str = "https://openrouter.ai/api/v1"):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            model: Default model to use (defaults to OPENROUTER_MODEL env var or openai/gpt-3.5-turbo)
            base_url: API base URL
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")

        self.model = model or os.getenv('OPENROUTER_MODEL') or "openai/gpt-3.5-turbo"
        self.base_url = base_url.rstrip('/')

        # Rate limiting for free tier: 1 request per 15 minutes
        self.rate_limit_seconds = 15 * 60  # 900 seconds
        self.last_request_time = 0.0

        logger.info("OpenRouter client initialized successfully")

    def call_chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None,
                           max_tokens: int = 1000, temperature: float = 0.7,
                           retry_count: int = 3, **kwargs) -> Dict[str, Any]:
        """
        Make a chat completion API call to OpenRouter.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (overrides default)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            retry_count: Number of retries on failure
            **kwargs: Additional parameters for the API

        Returns:
            Dict containing the API response

        Raises:
            OpenRouterRateLimitError: When free tier rate limit is hit
            OpenRouterAuthenticationError: When API key is invalid
            OpenRouterModelError: When model is invalid
            OpenRouterError: For other API errors
        """
        # Use provided model or default
        model = model or self.model

        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://trading-bot.local",  # Optional referrer
            "X-Title": "Trading Bot"  # Optional app identifier
        }

        last_exception = None

        for attempt in range(retry_count):
            try:
                # Rate limiting check
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.rate_limit_seconds:
                    sleep_time = self.rate_limit_seconds - time_since_last
                    logger.warning(f"Rate limit active. Sleeping for {sleep_time:.1f} seconds")
                    time.sleep(sleep_time)

                # Update last request time before making the call
                self.last_request_time = time.time()

                # Make the API call
                logger.debug(f"Making OpenRouter API call to {model}")
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)

                # Handle different response codes
                if response.status_code == 200:
                    response_data = response.json()

                    # Validate response structure
                    if "choices" not in response_data:
                        raise OpenRouterError(f"Invalid response structure: {response_data}")

                    logger.info(f"OpenRouter API call successful for model {model}")
                    return response_data

                elif response.status_code == 401:
                    raise OpenRouterAuthenticationError(f"Authentication failed: Invalid API key")

                elif response.status_code == 403:
                    raise OpenRouterModelError(f"Access forbidden for model {model}")

                elif response.status_code == 404:
                    raise OpenRouterModelError(f"Model {model} not found")

                elif response.status_code == 422:
                    raise OpenRouterModelError(f"Validation error for model {model}: {response.text}")

                elif response.status_code == 429:
                    if attempt < retry_count - 1:
                        # Rate limit hit, wait before retry
                        retry_after = response.headers.get('Retry-After')
                        if retry_after:
                            wait_time = min(int(retry_after), 60)  # Cap at 1 minute
                        else:
                            wait_time = 30  # Default wait time
                        logger.warning(f"Rate limit hit, retrying in {wait_time} seconds (attempt {attempt + 1}/{retry_count})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise OpenRouterRateLimitError(f"Rate limit exceeded for model {model}")

                elif response.status_code >= 500:
                    # Server error, retry with exponential backoff
                    if attempt < retry_count - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                        logger.warning(f"Server error {response.status_code}, retrying in {wait_time} seconds (attempt {attempt + 1}/{retry_count})")
                        time.sleep(wait_time)
                        continue

                # Default error handling
                raise OpenRouterError(f"OpenRouter API error {response.status_code}: {response.text}")

            except requests.RequestException as e:
                last_exception = e
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Network error: {e}, retrying in {wait_time} seconds (attempt {attempt + 1}/{retry_count})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise OpenRouterError(f"Network error after {retry_count} attempts: {e}") from e

            except OpenRouterError:
                # Re-raise custom exceptions immediately
                raise

        # If we get here, all retries failed
        if last_exception:
            raise OpenRouterError(f"Failed after {retry_count} attempts: {last_exception}") from last_exception

        raise OpenRouterError(f"Failed after {retry_count} attempts")

    def set_model(self, model: str):
        """
        Set the default model for future requests.

        Args:
            model: Model identifier (e.g., 'openai/gpt-3.5-turbo')
        """
        if not model or not isinstance(model, str):
            raise ValueError("Model must be a non-empty string")
        self.model = model
        logger.info(f"Default model set to {model}")

    def get_model(self) -> str:
        """Get the current default model."""
        return self.model

    def is_rate_limited(self) -> bool:
        """
        Check if currently rate limited.

        Returns:
            True if next request would be rate limited
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        return time_since_last < self.rate_limit_seconds

    def time_until_next_request(self) -> float:
        """
        Get seconds until next request is allowed.

        Returns:
            Seconds to wait, or 0 if ready
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        return max(0, self.rate_limit_seconds - time_since_last)

# Convenience functions
def chat_completion(messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Convenience function for chat completion using default client.

    Args:
        messages: List of message dicts
        model: Model to use (optional)
        **kwargs: Additional parameters

    Returns:
        API response dict
    """
    client = OpenRouterClient()
    return client.call_chat_completion(messages, model=model, **kwargs)

# Global client instance for convenience
_default_client = None

def get_default_client() -> OpenRouterClient:
    """Get or create the default client instance."""
    global _default_client
    if _default_client is None:
        _default_client = OpenRouterClient()
    return _default_client

def set_default_model(model: str):
    """Set the default model for the default client."""
    client = get_default_client()
    client.set_model(model)
