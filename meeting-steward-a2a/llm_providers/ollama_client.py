"""Ollama HTTP client for local LLM inference."""

import json
import logging
import subprocess
import time
from typing import Any, Dict, List, Optional

import requests

from app_config import settings


logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama's HTTP API."""
    
    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Ollama client.
        
        Args:
            host: Ollama API endpoint (defaults to settings)
            model: Default model name (defaults to settings)
        """
        self.host = host or settings.ollama_host
        self.default_model = model or settings.model_name
        self.timeout = 120  # 2 minutes timeout for long generations
        
    def ensure_model_available(self, model: Optional[str] = None) -> bool:
        """
        Ensure a model is available, pulling it if necessary.
        
        Args:
            model: Model name to check (defaults to default_model)
            
        Returns:
            True if model is available
        """
        model = model or self.default_model
        
        # Check if model exists
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [m.get("name", "").split(":")[0] for m in models]
            
            # Check if model is already pulled
            if model in model_names or f"{model}:latest" in [m.get("name") for m in models]:
                logger.info(f"Model {model} is already available")
                return True
            
            # Pull the model
            logger.info(f"Model {model} not found. Pulling from Ollama...")
            result = subprocess.run(
                ["ollama", "pull", model],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for model pull
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully pulled model {model}")
                return True
            else:
                logger.error(f"Failed to pull model {model}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error ensuring model availability: {e}")
            return False
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a chat completion request to Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to default_model)
            temperature: Sampling temperature (defaults to settings)
            max_retries: Maximum number of retries (defaults to settings)
            **kwargs: Additional parameters for Ollama API
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If request fails after all retries
        """
        model = model or self.default_model
        temperature = temperature if temperature is not None else settings.default_temperature
        max_retries = max_retries or settings.max_retries
        
        # Ensure model is available
        self.ensure_model_available(model)
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                **kwargs
            }
        }
        
        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.host}/api/chat",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                content = result.get("message", {}).get("content", "")
                
                if not content:
                    raise ValueError("Empty response from Ollama")
                
                logger.debug(f"Ollama response (attempt {attempt + 1}): {content[:100]}...")
                return content
                
            except Exception as e:
                last_error = e
                logger.warning(f"Ollama request failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception(f"Ollama chat failed after {max_retries} attempts: {last_error}")
    
    def parse_json_response(self, response: str, schema_class: Optional[Any] = None) -> Dict:
        """
        Parse JSON from LLM response with error handling.
        
        Args:
            response: Raw LLM response text
            schema_class: Optional Pydantic model for validation
            
        Returns:
            Parsed JSON dict or validated Pydantic model
        """
        # Try to find JSON in the response
        response = response.strip()
        
        # Remove markdown code blocks if present
        if response.startswith("```"):
            lines = response.split("\n")
            # Remove first line (```json) and last line (```)
            response = "\n".join(lines[1:-1]) if len(lines) > 2 else response
        
        try:
            data = json.loads(response)
            
            # Validate with Pydantic if schema provided
            if schema_class:
                return schema_class(**data)
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")


# Global client instance
ollama_client = OllamaClient()
