"""LLM service for Ollama integration."""

import logging
from typing import Optional
import requests
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM inference via Ollama."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.connect_timeout = settings.ollama_connect_timeout
        self.read_timeout = max(settings.ollama_read_timeout, settings.ollama_timeout)
        self.chat_endpoint = f"{self.base_url}/api/chat"
        self.generate_endpoint = f"{self.base_url}/api/generate"

    def _post_ollama(self, endpoint: str, payload: dict, operation: str) -> requests.Response:
        """Post to Ollama with one retry for transient read timeouts."""
        max_attempts = 2
        for attempt in range(1, max_attempts + 1):
            try:
                return requests.post(
                    endpoint,
                    json=payload,
                    timeout=(self.connect_timeout, self.read_timeout),
                )
            except requests.exceptions.ReadTimeout as exc:
                logger.warning(
                    f"Ollama {operation} timeout on attempt {attempt}/{max_attempts} "
                    f"(read_timeout={self.read_timeout}s): {str(exc)}"
                )
                if attempt == max_attempts:
                    raise
        raise RuntimeError(f"Ollama {operation} request failed")
    
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama service not available: {str(e)}")
            return False
    
    def is_model_available(self) -> bool:
        """Check if the configured Ollama model is installed locally."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
            models = response.json().get("models", [])
            model_names = {model.get("name") for model in models}
            return self.model in model_names
        except Exception as e:
            logger.warning(f"Could not check Ollama models: {str(e)}")
            return False
    
    def chat(self, messages: list, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Send chat request to Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            temperature: LLM temperature (0.0-1.0)
            
        Returns:
            Generated response text
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": settings.ollama_num_predict,
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            logger.info(f"Sending chat request to Ollama ({self.model})")
            response = self._post_ollama(self.chat_endpoint, payload, "chat")
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                logger.error(f"Ollama returned status {response.status_code}: {response.text}")
                return ""
        
        except Exception as e:
            logger.error(f"Error calling Ollama chat API: {str(e)}")
            return ""
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate text using Ollama.
        
        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            temperature: LLM temperature (0.0-1.0)
            
        Returns:
            Generated text
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": settings.ollama_num_predict,
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            logger.info(f"Sending generate request to Ollama ({self.model})")
            response = self._post_ollama(self.generate_endpoint, payload, "generate")
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama returned status {response.status_code}: {response.text}")
                return ""
        
        except Exception as e:
            logger.error(f"Error calling Ollama generate API: {str(e)}")
            return ""
