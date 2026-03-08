"""Refactor agent - optimizes and improves code."""

from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.agents.prompt_context import ENTITY_CONTRACT
from backend.ai.ollama_client import OllamaClient


class RefactorAgent(BaseAgent):
    """Optimizes existing code and improves implementations."""
    
    def __init__(self, ollama_client: OllamaClient):
        super().__init__("Refactor", ollama_client)
    
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for optimization opportunities."""
        code_changes = context.get("code_changes", [])
        applier_result = context.get("applier_result", {})
        
        if not code_changes:
            return {
                "analysis": "No code changes to refactor",
                "optimizations": []
            }
        
        # Last change may have been applied to disk by Applier
        last_change = code_changes[-1] if code_changes else {}
        code = last_change.get("code", "")
        applied = applier_result.get("applied", False)
        
        prompt = f"""You are the Refactor agent. The previous step (Developer) produced code that may have been applied to the codebase by an Applier step. Your job is to review that code for safety and correctness.

Code that was produced (and possibly applied):
{code[:3000] if code else '(none)'}

Context: This is a virtual world simulation. Entity code must respect the contract: {ENTITY_CONTRACT}

Focus on:
1. Safety: no unsafe eval/exec, imports are from the project.
2. Schema: entities have update(world_state), to_dict(), position, properties, age.
3. Concrete, line-level suggestions (e.g. "Line X: add bounds check for radius").
4. Whether the code is ready to keep (approved) or should be improved.

Provide specific optimization or correctness suggestions. If the code looks good, say so briefly."""
        
        suggestions = self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.5,
            max_tokens=1000
        )
        
        return {
            "analysis": "Code review completed",
            "suggestions": suggestions.strip(),
            "optimizations": self._extract_optimizations(suggestions),
            "approved_code": "looks good" in suggestions.lower() or "ready" in suggestions.lower(),
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
        
        if not suggestions or "No code changes" in str(thoughts.get("analysis", "")):
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
            "approved_code": thoughts.get("approved_code", False),
            "next_agent": "tester"
        }
