"""Developer agent - implements new features and code."""

from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.agents.prompt_context import (
    ENTITIES_MODULE_PATH,
    PHYSICS_MODULE_PATH,
    EVENTS_MODULE_PATH,
    ENTITY_TYPES_LIST,
    ENTITY_CONTRACT,
    WORLD_SCHEMA_SUMMARY,
)
from backend.ai.ollama_client import OllamaClient


class DeveloperAgent(BaseAgent):
    """Writes and updates simulation code."""
    
    def __init__(self, ollama_client: OllamaClient):
        super().__init__("Developer", ollama_client)
    
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan implementation for challenge. Skip LLM if plan and implementation_type/hint already provided (e.g. by Planner)."""
        plan = context.get("plan", "")
        impl_type = context.get("implementation_type") or context.get("implementation_hint", "")
        if impl_type in ("entity", "physics", "event", "general") and plan:
            return {"plan": plan, "implementation_type": impl_type if impl_type != "" else "general"}

        challenge = context.get("challenge", "")
        world_state = context.get("world_state", {})
        impl_hint = context.get("implementation_hint", "")
        impl_type = impl_hint if impl_hint in ("entity", "physics", "event") else self._determine_type(challenge)

        prompt = f"""You are the Developer for an AI virtual world. You will implement the challenge by writing code that will be injected into this codebase.

Challenge: {challenge}

World schema summary:
{WORLD_SCHEMA_SUMMARY}

Codebase paths:
- Entities (new entity classes): {ENTITIES_MODULE_PATH}
- Physics rules: {PHYSICS_MODULE_PATH}
- Events: {EVENTS_MODULE_PATH}

Current world: {len(world_state.get('entities', []))} entities, physics dimensions {world_state.get('physics', {}).get('dimensions', 4)}.

Implementation type for this task: {impl_type}.

Provide a short implementation plan (3-5 bullet points): which file to modify, what to add (e.g. new class name, method signatures), and how it fits the challenge."""

        plan_text = self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.7,
            max_tokens=1000
        )

        return {
            "plan": plan_text.strip(),
            "implementation_type": impl_type,
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
            "next_agent": "applier"
        }
    
    def _generate_entity_code(self, challenge: str, plan: str) -> str:
        """Generate entity class code plus ENTITY_TYPES entry."""
        prompt = f"""Generate runnable Python code for a NEW entity class. File: {ENTITIES_MODULE_PATH}.

Challenge: {challenge}
Plan: {plan}

Existing entity types in this file: {', '.join(ENTITY_TYPES_LIST)}. Do not duplicate them.

Entity contract (you must follow this):
{ENTITY_CONTRACT}

Requirements:
1. Define exactly one new class that inherits from Entity (import from the same module or use Entity from typing if needed—in this codebase Entity is in the same file).
2. Constructor: __init__(self, entity_id: str, position: Dict[str, float], properties: Dict[str, Any] = None), call super().__init__(entity_id, position, properties), then set any custom attributes from self.properties.
3. Implement update(self, world_state: Dict[str, Any]) -> Dict[str, Any]: update self.age and self.properties as needed, return a dict with at least position, properties.
4. to_dict() is inherited; ensure your class has id, position, properties, age (base class provides these).
5. At the end of your response, add the ENTITY_TYPES registration line. Format: ENTITY_TYPES["YourClassName"] = YourClassName (so the applier can add it to the dict). Output as a single block: first the full class code, then a blank line, then the single line for ENTITY_TYPES.

Output ONLY valid Python. No markdown code fences, no explanations, no triple backticks. Code only."""
        
        return self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.7,
            max_tokens=2000
        )
    
    def _generate_physics_code(self, challenge: str, plan: str) -> str:
        """Generate physics rule code."""
        prompt = f"""Generate runnable Python code for a physics rule. File: {PHYSICS_MODULE_PATH}.

Challenge: {challenge}
Plan: {plan}

Implement a function or method that applies the physics rule. It may read world_state["physics"] and optionally modify gravity/timeFlow zones. Output ONLY valid Python. No markdown, no explanations, no code fences."""
        
        return self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.7,
            max_tokens=1000
        )
    
    def _generate_event_code(self, challenge: str, plan: str) -> str:
        """Generate event code."""
        prompt = f"""Generate runnable Python code for a new event type. File: {EVENTS_MODULE_PATH}.

Challenge: {challenge}
Plan: {plan}

Create a function that generates this type of event (returns a dict with type, description, etc.). Output ONLY valid Python. No markdown, no explanations, no code fences."""
        
        return self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.7,
            max_tokens=1000
        )
    
    def _generate_general_code(self, challenge: str, plan: str) -> str:
        """Generate general implementation code (default: entity)."""
        prompt = f"""Generate runnable Python code to implement this challenge. Prefer adding a new entity class to {ENTITIES_MODULE_PATH} if the challenge is ambiguous.

Challenge: {challenge}
Plan: {plan}

Entity contract if adding an entity:
{ENTITY_CONTRACT}
Existing entity types: {', '.join(ENTITY_TYPES_LIST)}. Include ENTITY_TYPES registration if you add a new class.

Output ONLY valid Python. No markdown, no explanations, no code fences."""
        
        return self.ollama.generate(
            prompt,
            model=self.ollama.coder_model,
            temperature=0.7,
            max_tokens=2000
        )
