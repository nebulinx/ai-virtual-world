"""Ollama API client for AI model integration."""

import requests
import time
from typing import Optional, Dict, Any, List
from backend.config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_CODER_MODEL, OLLAMA_REASONING_MODEL


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = OLLAMA_HOST):
        self.base_url = base_url.rstrip('/')
        self.coder_model = OLLAMA_CODER_MODEL
        self.reasoning_model = OLLAMA_REASONING_MODEL
        self.current_model: Optional[str] = None
    
    def _check_connection(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=30)
            return response.status_code == 200
        except Exception:
            return False
    
    def _ensure_model_loaded(self, model: str) -> bool:
        """Ensure a model is loaded (unload current if different)."""
        if self.current_model == model:
            return True
        
        # Unload current model if different
        if self.current_model:
            try:
                requests.post(
                    f"{self.base_url}/api/generate",
                    json={"model": self.current_model, "prompt": "", "stream": False},
                    timeout=10
                )
            except Exception:
                pass
        
        # Load new model by making a test request
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": "test",
                    "stream": False,
                    "options": {"num_predict": 1}
                },
                timeout=300  # Increased to 5 minutes for large model loading
            )
            if response.status_code == 200:
                self.current_model = model
                return True
        except Exception as e:
            print(f"Error loading model {model}: {e}")
        
        return False
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        retries: int = 5
    ) -> str:
        """Generate text using Ollama API."""
        # Select model: single OLLAMA_MODEL overrides coder/reasoning
        if model is None:
            if OLLAMA_MODEL:
                model = OLLAMA_MODEL
            elif any(keyword in prompt.lower() for keyword in ["code", "function", "class", "import", "def"]):
                model = self.coder_model
            else:
                model = self.reasoning_model
        
        # Ensure model is loaded
        if not self._ensure_model_loaded(model):
            raise ConnectionError(f"Failed to load model: {model}")
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system:
            payload["system"] = system
        
        for attempt in range(retries):
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=600  # Increased to 10 minutes for large model generation
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                else:
                    raise ConnectionError(f"Failed to generate after {retries} attempts: {e}")
        
        return ""
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        retries: int = 5
    ) -> str:
        """Chat completion using Ollama API."""
        if model is None:
            if OLLAMA_MODEL:
                model = OLLAMA_MODEL
            else:
                content = " ".join([msg.get("content", "") for msg in messages])
                if any(keyword in content.lower() for keyword in ["code", "function", "class", "import", "def"]):
                    model = self.coder_model
                else:
                    model = self.reasoning_model

        if not self._ensure_model_loaded(model):
            raise ConnectionError(f"Failed to load model: {model}")
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        for attempt in range(retries):
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=600  # Increased to 10 minutes for large model chat
                )
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise ConnectionError(f"Failed to chat after {retries} attempts: {e}")
        
        return ""
    
    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=30)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception:
            return []
