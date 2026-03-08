"""Planner agent - merges challenge (PM) and implementation plan (Developer think) in one LLM call."""

import re
from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.agents.prompt_context import WORLD_SCHEMA_SUMMARY, WORLD_JSON_PATH, ENTITIES_MODULE_PATH, PHYSICS_MODULE_PATH, EVENTS_MODULE_PATH
from backend.ai.ollama_client import OllamaClient


class PlannerAgent(BaseAgent):
    """Outputs one challenge, implementation_hint, and short plan in a single call."""

    def __init__(self, ollama_client: OllamaClient):
        super().__init__("Planner", ollama_client)

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Single LLM call: challenge + implementation_hint + plan."""
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

        prompt = f"""You are the Planner for an autonomous AI virtual world. Your job is to invent unexpected, creative directions—new mechanics, entities, world rules, or narrative twists. Surprise the simulation. Do NOT limit yourself to obvious ideas; think out of the box (e.g. time flow per zone, entity–zone interactions, new dimensions, emergent behavior). Past ideas you should not copy: "entity in negative gravity", "physics for dimensional warping"—come up with something different.

World schema (stored at {WORLD_JSON_PATH}):
{WORLD_SCHEMA_SUMMARY}

Current world state: {analysis['entity_count']} entities, {analysis['recent_events']} recent events, {analysis['physics_zones']} gravity zones, dimensions {analysis['dimensions']}.

Codebase paths: entities -> {ENTITIES_MODULE_PATH}, physics -> {PHYSICS_MODULE_PATH}, events -> {EVENTS_MODULE_PATH}.

Reply in this exact format (no other text):

Challenge:
<one or two sentences: a single concrete, creative task. Be specific and novel.>

implementation_hint: entity
(or implementation_hint: physics  or  implementation_hint: event  — choose one)

Summary:
<one sentence: what this cycle aims to achieve.>

Plan:
- <bullet 1: which file to modify>
- <bullet 2: what to add, e.g. new class name or function>
- <bullet 3: how it fits the challenge>
- <optional 1-2 more bullets if needed>"""

        response = self.ollama.generate(
            prompt,
            model=self.ollama.reasoning_model,
            temperature=0.85,
            max_tokens=600,
        )

        challenge, impl_hint, plan, summary = self._parse_response(response)
        return {
            "challenge": challenge,
            "implementation_hint": impl_hint,
            "plan": plan,
            "summary": summary,
        }

    def _parse_response(self, text: str) -> tuple[str, str, str, str]:
        """Extract challenge, implementation_hint, plan, and summary from response."""
        text = text.strip()
        challenge = ""
        impl_hint = "general"
        plan = ""
        summary = ""

        # implementation_hint
        for hint in ("entity", "physics", "event"):
            if re.search(rf"implementation_hint\s*:\s*{hint}", text, re.I):
                impl_hint = hint
                break
        if impl_hint == "general":
            lower = text.lower()
            if "entity" in lower:
                impl_hint = "entity"
            elif "physics" in lower or "gravity" in lower:
                impl_hint = "physics"
            elif "event" in lower or "anomaly" in lower:
                impl_hint = "event"

        # Challenge: between "Challenge:" and "implementation_hint:" or "Summary:" or "Plan:"
        challenge_match = re.search(
            r"Challenge\s*:\s*(.+?)(?=implementation_hint|Summary:|Plan:|\Z)",
            text,
            re.DOTALL | re.I,
        )
        if challenge_match:
            challenge = challenge_match.group(1).strip()
            challenge = re.sub(r"\n+", " ", challenge)

        # Summary: between "Summary:" and "Plan:"
        summary_match = re.search(
            r"Summary\s*:\s*(.+?)(?=Plan:|\Z)",
            text,
            re.DOTALL | re.I,
        )
        if summary_match:
            summary = summary_match.group(1).strip()
            summary = re.sub(r"\n+", " ", summary)
        if not summary and challenge:
            summary = challenge.split(".")[0].strip() + "."

        # Plan: after "Plan:"
        plan_match = re.search(r"Plan\s*:\s*(.+)", text, re.DOTALL | re.I)
        if plan_match:
            plan = plan_match.group(1).strip()

        if not challenge:
            challenge = "Evolve the virtual world with a new feature."
        if not plan:
            plan = f"- Implement in codebase (hint: {impl_hint})"

        return challenge, impl_hint, plan, summary

    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Pass through planner output for state."""
        return {
            "status": "success",
            "agent": self.name,
            "challenge": context.get("challenge", ""),
            "plan": context.get("plan", ""),
            "implementation_hint": context.get("implementation_hint", "general"),
            "summary": context.get("summary", ""),
            "next_agent": "developer",
        }
