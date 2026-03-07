"""Product Manager agent - defines challenges and goals."""

from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.ai.ollama_client import OllamaClient


class ProductManagerAgent(BaseAgent):
    """Defines challenges and goals for world evolution."""
    
    def __init__(self, ollama_client: OllamaClient):
        super().__init__("Product Manager", ollama_client)
    
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze world state and generate challenges."""
        world_state = context.get("world_state", {})
        entities = world_state.get("entities", [])
        events = world_state.get("events", [])
        
        # Analyze current state
        analysis = {
            "entity_count": len(entities),
            "recent_events": len([e for e in events[-10:]]),
            "physics_zones": len(world_state.get("physics", {}).get("gravity", {}).get("zones", []))
        }
        
        # Generate challenge using AI
        prompt = f"""Analyze the current virtual world state and generate a new challenge for the development team.

Current world state:
- Entities: {analysis['entity_count']}
- Recent events: {analysis['recent_events']}
- Physics zones: {analysis['physics_zones']}

Generate a creative challenge that will evolve the world. Examples:
- Create an entity that survives in negative gravity zones
- Add a new physics rule for dimensional warping
- Design an anomaly that affects time flow
- Create a new type of energy field

Provide a clear, actionable challenge description."""
        
        challenge_text = self.ollama.generate(
            prompt,
            model=self.ollama.reasoning_model,
            temperature=0.8,
            max_tokens=500
        )
        
        return {
            "analysis": analysis,
            "challenge": challenge_text.strip(),
            "priority": "medium"
        }
    
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Define challenge for other agents."""
        thoughts = context.get("thoughts", {})
        challenge = thoughts.get("challenge", "No challenge generated")
        
        return {
            "status": "success",
            "agent": self.name,
            "challenge": challenge,
            "analysis": thoughts.get("analysis", {}),
            "next_agent": "developer"
        }
