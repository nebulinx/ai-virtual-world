"""Refactor agent - optimizes and improves code."""

from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.ai.ollama_client import OllamaClient


class RefactorAgent(BaseAgent):
    """Optimizes existing code and improves implementations."""
    
    def __init__(self, ollama_client: OllamaClient):
        super().__init__("Refactor", ollama_client)
    
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for optimization opportunities."""
        code_changes = context.get("code_changes", [])
        world_state = context.get("world_state", {})
        
        if not code_changes:
            return {
                "analysis": "No code changes to refactor",
                "optimizations": []
            }
        
        # Analyze code quality
        prompt = f"""Analyze the following code changes and suggest optimizations:

Code changes: {code_changes}

Consider:
1. Performance improvements
2. Code readability
3. Error handling
4. Code structure
5. Best practices

Provide specific optimization suggestions."""
        
        suggestions = self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.5,
            max_tokens=1000
        )
        
        return {
            "analysis": "Code review completed",
            "suggestions": suggestions.strip(),
            "optimizations": self._extract_optimizations(suggestions)
        }
    
    def _extract_optimizations(self, suggestions: str) -> list:
        """Extract optimization points from suggestions."""
        # Simple extraction - can be enhanced
        optimizations = []
        lines = suggestions.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['optimize', 'improve', 'refactor', 'better']):
                optimizations.append(line.strip())
        return optimizations[:5]  # Limit to 5
    
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations."""
        thoughts = context.get("thoughts", {})
        suggestions = thoughts.get("suggestions", "")
        
        if not suggestions or "No code changes" in thoughts.get("analysis", ""):
            return {
                "status": "skipped",
                "agent": self.name,
                "message": "No refactoring needed",
                "next_agent": "tester"
            }
        
        return {
            "status": "success",
            "agent": self.name,
            "optimizations": thoughts.get("optimizations", []),
            "suggestions": suggestions,
            "next_agent": "tester"
        }
