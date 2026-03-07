"""Base agent class with Ollama integration."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.ai.ollama_client import OllamaClient


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str, ollama_client: Optional[OllamaClient] = None):
        self.name = name
        self.ollama = ollama_client or OllamaClient()
        self.history: list = []
    
    @abstractmethod
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Agent reasoning process."""
        pass
    
    @abstractmethod
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Agent action execution."""
        pass
    
    def validate(self, result: Dict[str, Any]) -> bool:
        """Validate agent result."""
        return isinstance(result, dict) and "status" in result
    
    def generate_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Generate prompt for AI model."""
        context_str = self._format_context(context)
        return f"""You are {self.name}, an AI agent in a virtual world simulation system.

Task: {task}

Context:
{context_str}

Provide your response in a structured format."""
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary as string."""
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                value_str = str(value)[:200]  # Truncate long dicts
            elif isinstance(value, list):
                value_str = f"[{len(value)} items]"
            else:
                value_str = str(value)[:200]
            lines.append(f"{key}: {value_str}")
        return "\n".join(lines)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent workflow: think -> act -> validate."""
        try:
            # Think phase
            thoughts = self.think(context)
            
            # Act phase
            result = self.act({**context, **thoughts})
            
            # Validate phase
            if not self.validate(result):
                result = {
                    "status": "error",
                    "message": "Validation failed",
                    "agent": self.name
                }
            
            # Record in history
            self.history.append({
                "context": context,
                "thoughts": thoughts,
                "result": result
            })
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "agent": self.name
            }
