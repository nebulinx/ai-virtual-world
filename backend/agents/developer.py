"""Developer agent - implements new features and code."""

from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.ai.ollama_client import OllamaClient


class DeveloperAgent(BaseAgent):
    """Writes and updates simulation code."""
    
    def __init__(self, ollama_client: OllamaClient):
        super().__init__("Developer", ollama_client)
    
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan implementation for challenge."""
        challenge = context.get("challenge", "")
        world_state = context.get("world_state", {})
        
        # Analyze what needs to be implemented
        prompt = f"""You are a developer implementing a feature for a virtual world simulation.

Challenge: {challenge}

Current world state summary:
- Entities: {len(world_state.get('entities', []))}
- Physics dimensions: {world_state.get('physics', {}).get('dimensions', 4)}

Plan the implementation:
1. Determine if this requires a new entity, physics rule, or event
2. Identify which files need to be modified
3. Outline the code structure needed

Provide a clear implementation plan."""
        
        plan_text = self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.7,
            max_tokens=1000
        )
        
        return {
            "plan": plan_text.strip(),
            "implementation_type": self._determine_type(challenge)
        }
    
    def _determine_type(self, challenge: str) -> str:
        """Determine what type of implementation is needed."""
        challenge_lower = challenge.lower()
        if "entity" in challenge_lower:
            return "entity"
        elif "physics" in challenge_lower or "gravity" in challenge_lower:
            return "physics"
        elif "event" in challenge_lower or "anomaly" in challenge_lower:
            return "event"
        else:
            return "general"
    
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code implementation."""
        challenge = context.get("challenge", "")
        thoughts = context.get("thoughts", {})
        plan = thoughts.get("plan", "")
        impl_type = thoughts.get("implementation_type", "general")
        
        # Generate code based on implementation type
        if impl_type == "entity":
            code = self._generate_entity_code(challenge, plan)
        elif impl_type == "physics":
            code = self._generate_physics_code(challenge, plan)
        elif impl_type == "event":
            code = self._generate_event_code(challenge, plan)
        else:
            code = self._generate_general_code(challenge, plan)
        
        return {
            "status": "success",
            "agent": self.name,
            "implementation_type": impl_type,
            "code": code,
            "plan": plan,
            "next_agent": "tester"
        }
    
    def _generate_entity_code(self, challenge: str, plan: str) -> str:
        """Generate entity class code."""
        prompt = f"""Generate Python code for a new entity class based on this challenge:

Challenge: {challenge}
Plan: {plan}

Create a new entity class that:
1. Inherits from Entity base class
2. Has an update() method
3. Has a to_dict() method
4. Implements unique behavior based on the challenge

Return only the class code, no explanations."""
        
        return self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.7,
            max_tokens=1500
        )
    
    def _generate_physics_code(self, challenge: str, plan: str) -> str:
        """Generate physics rule code."""
        prompt = f"""Generate Python code for a new physics rule based on this challenge:

Challenge: {challenge}
Plan: {plan}

Create a function or method that implements the physics rule.
Return only the code, no explanations."""
        
        return self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.7,
            max_tokens=1000
        )
    
    def _generate_event_code(self, challenge: str, plan: str) -> str:
        """Generate event code."""
        prompt = f"""Generate Python code for a new event type based on this challenge:

Challenge: {challenge}
Plan: {plan}

Create a function that generates this type of event.
Return only the code, no explanations."""
        
        return self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.7,
            max_tokens=1000
        )
    
    def _generate_general_code(self, challenge: str, plan: str) -> str:
        """Generate general implementation code."""
        prompt = f"""Generate Python code to implement this challenge:

Challenge: {challenge}
Plan: {plan}

Return only the code, no explanations."""
        
        return self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.7,
            max_tokens=1500
        )
