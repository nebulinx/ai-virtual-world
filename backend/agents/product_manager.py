"""Product Manager agent - defines challenges and goals."""

from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.agents.prompt_context import WORLD_SCHEMA_SUMMARY, WORLD_JSON_PATH
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
        physics = world_state.get("physics", {})
        gravity_zones = physics.get("gravity", {}).get("zones", [])
        
        analysis = {
            "entity_count": len(entities),
            "recent_events": len(events[-10:]) if events else 0,
            "physics_zones": len(gravity_zones),
            "dimensions": physics.get("dimensions", 4),
        }
        
        prompt = f"""You are the Product Manager for an autonomous AI virtual world simulation. Your job is to output exactly ONE concrete challenge per cycle for the developer to implement.

World schema (stored at {WORLD_JSON_PATH}):
{WORLD_SCHEMA_SUMMARY}

Current world state:
- Entity count: {analysis['entity_count']}
- Recent events (last 10): {analysis['recent_events']}
- Physics gravity zones: {analysis['physics_zones']}
- Dimensions: {analysis['dimensions']}

Rules:
1. Output a single, actionable challenge in 1-2 clear sentences.
2. Do not output multiple challenges or bullet lists—only one challenge.
3. Prefer challenges that fit one of: new entity, new physics rule, or new event/anomaly type.
4. Examples: "Create an entity that survives in negative gravity zones." / "Add a physics rule for dimensional warping near vortices." / "Design an anomaly that affects time flow in a zone."

Reply with only the challenge text (1-2 sentences). Optionally end with a line "implementation_hint: entity" or "implementation_hint: physics" or "implementation_hint: event" to guide the developer."""
        
        challenge_text = self.ollama.generate(
            prompt,
            model=self.ollama.reasoning_model,
            temperature=0.8,
            max_tokens=500
        )
        
        impl_hint = "general"
        for hint in ("entity", "physics", "event"):
            if f"implementation_hint: {hint}" in challenge_text.lower():
                impl_hint = hint
                challenge_text = challenge_text.replace(f"implementation_hint: {hint}", "").strip()
        
        return {
            "analysis": analysis,
            "challenge": challenge_text.strip(),
            "priority": "medium",
            "implementation_hint": impl_hint,
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
            "implementation_hint": thoughts.get("implementation_hint", "general"),
            "next_agent": "developer"
        }
