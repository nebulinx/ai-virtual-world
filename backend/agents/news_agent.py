"""News agent - generates news from world events."""

import re
from typing import Dict, Any, List
from datetime import datetime
from backend.agents.base_agent import BaseAgent
from backend.ai.ollama_client import OllamaClient
from backend.config import NEWS_JSON_PATH
from backend.world.schemas import validate_news_json
import json
from pathlib import Path

NEWS_JSON_FORMAT_INSTRUCTION = (
    'You must respond with exactly a single JSON object with two keys: "headline" and "body". '
    'Both must be non-empty strings. Headline: one specific, catchy phrase (no generic "World Update"). '
    'Body: 2-4 sentences with cause, effect, or implications. Use concrete names (entity types, event types). '
    'No other text, no markdown, no code fences. Example: {"headline": "Title", "body": "Sentence one. Sentence two."}'
)


class NewsAgent(BaseAgent):
    """Generates real-time news about world events."""
    
    def __init__(self, ollama_client: OllamaClient):
        super().__init__("News Agent", ollama_client)
        self.news_path = Path(NEWS_JSON_PATH)
    
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze world events for news generation."""
        world_state = context.get("world_state", {})
        events = world_state.get("events", [])
        entities = world_state.get("entities", [])
        anomalies = world_state.get("anomalies", [])
        physics = world_state.get("physics", {})
        
        # Get recent events (last 5)
        recent_events = events[-5:] if events else []
        
        # Entity type names for context
        entity_types = list({e.get("type") for e in entities if e.get("type")})
        # Recent event types and descriptions
        recent_event_summary = [
            {"type": e.get("type", "unknown"), "description": (e.get("description") or "")[:200]}
            for e in recent_events
        ]
        gravity = physics.get("gravity", {})
        gravity_zones = gravity.get("zones", [])
        time_flow = physics.get("timeFlow", {})
        dimensions = physics.get("dimensions", 4)
        
        significant_events = [
            e for e in recent_events
            if e.get("type") in ["dimensional_rift", "temporal_distortion", "energy_storm"]
        ]
        
        return {
            "recent_events": recent_events,
            "significant_events": significant_events,
            "entity_count": len(entities),
            "entity_types": entity_types,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "recent_event_summary": recent_event_summary,
            "gravity_zones": gravity_zones,
            "time_flow_zones": time_flow.get("zones", []),
            "dimensions": dimensions,
            "world_timestamp": world_state.get("timestamp", ""),
            "news_items_to_generate": min(3, len(significant_events) + 1),
        }
    
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate news articles."""
        thoughts = context.get("thoughts", {})
        world_state = context.get("world_state", {})
        recent_events = thoughts.get("recent_events", [])
        significant_events = thoughts.get("significant_events", [])
        world_context = {
            "entity_types": thoughts.get("entity_types", []),
            "recent_event_summary": thoughts.get("recent_event_summary", []),
            "gravity_zones": thoughts.get("gravity_zones", []),
            "dimensions": thoughts.get("dimensions", 4),
            "anomaly_count": thoughts.get("anomaly_count", 0),
        }
        
        news_items = []
        
        # Generate news for significant events
        for event in significant_events[:3]:  # Limit to 3
            news_item = self._generate_news_for_event(event, world_context)
            if news_item:
                news_items.append(news_item)
        
        # Generate general world update if no significant events
        if not news_items:
            news_item = self._generate_general_update(world_state, thoughts)
            if news_item:
                news_items.append(news_item)
        
        # Save news to file
        self._save_news(news_items)
        
        return {
            "status": "success",
            "agent": self.name,
            "news_items_generated": len(news_items),
            "news_items": news_items,
            "next_agent": None  # End of cycle
        }
    
    def _generate_news_for_event(
        self, event: Dict[str, Any], world_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate news article for a specific event. Never return empty headline/body."""
        event_type = event.get("type", "unknown")
        description = event.get("description", "") or "An event occurred in the virtual world."
        category = self._categorize_event(event_type)
        entity_types = world_context.get("entity_types", [])
        dimensions = world_context.get("dimensions", 4)
        
        prompt = f"""Write an in-world "reporter" style news article about this virtual world event. Be specific and vivid; mention cause, effect, or implications. Use concrete names (entity types, zones) where relevant.

Event type: {event_type}
Description: {description}

World context: entities present: {entity_types or 'none'}; dimensions: {dimensions}. Category for tone: {category}.

{NEWS_JSON_FORMAT_INSTRUCTION}"""
        
        news_data = self._parse_news_response(
            self.ollama.generate(
                prompt,
                model=self.ollama.reasoning_model,
                temperature=0.8,
                max_tokens=400,
            )
        )
        headline = (news_data.get("headline") or "").strip()
        body = (news_data.get("body") or "").strip()
        if not headline:
            headline = f"{event_type.replace('_', ' ').title()}: {description[:60]}..." if len(description) > 60 else f"{event_type.replace('_', ' ').title()}"
        if not body:
            body = f"{description} Observers report potential impact across the simulation."
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "headline": headline,
            "body": body,
            "category": category,
        }
    
    def _generate_general_update(
        self, world_state: Dict[str, Any], thoughts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate general world update news. Never return empty headline/body."""
        entity_count = len(world_state.get("entities", []))
        events_count = len(world_state.get("events", []))
        entity_types = thoughts.get("entity_types", [])
        recent_event_summary = thoughts.get("recent_event_summary", [])
        gravity_zones = thoughts.get("gravity_zones", [])
        dimensions = thoughts.get("dimensions", 4)
        anomaly_count = thoughts.get("anomaly_count", 0)
        
        prompt = f"""Write a descriptive, in-world news update about the current state of the virtual simulation. Be specific: name entity types, mention recent activity or anomalies, or physics (gravity zones, dimensions). Headline must be concrete, not generic "World Update".

Current state: {entity_count} entities (types: {entity_types}), {events_count} total events, {anomaly_count} anomalies. Dimensions: {dimensions}. Gravity zones: {len(gravity_zones)}.
Recent events: {recent_event_summary[-3:] if recent_event_summary else 'none'}.

{NEWS_JSON_FORMAT_INSTRUCTION}"""
        
        news_data = self._parse_news_response(
            self.ollama.generate(
                prompt,
                model=self.ollama.reasoning_model,
                temperature=0.7,
                max_tokens=400,
            )
        )
        headline = (news_data.get("headline") or "").strip()
        body = (news_data.get("body") or "").strip()
        if not headline:
            headline = (
                f"Simulation status: {', '.join(entity_types[:3]) or 'empty world'}"
                if entity_types else "Simulation status update"
            )
        if not body:
            parts = [f"The simulation holds {entity_count} entities"]
            if entity_types:
                parts.append(f" ({', '.join(entity_types[:5])})")
            parts.append(f", {events_count} recorded events, and {dimensions} dimensions.")
            body = "".join(parts)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "headline": headline,
            "body": body,
            "category": "entity",
        }

    def _parse_news_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response into {headline, body}. Returns dict with at least empty values."""
        try:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {"headline": data.get("headline", ""), "body": data.get("body", "")}
        except (json.JSONDecodeError, TypeError):
            pass
        lines = [l.strip() for l in response.strip().split("\n") if l.strip()]
        headline = lines[0].replace('"', "").replace("headline:", "").strip() if lines else ""
        body = " ".join(l.replace("body:", "").strip() for l in lines[1:]) if len(lines) > 1 else ""
        return {"headline": headline, "body": body}
    
    def _categorize_event(self, event_type: str) -> str:
        """Categorize event type."""
        if "gravity" in event_type or "physics" in event_type:
            return "physics"
        elif "entity" in event_type:
            return "entity"
        else:
            return "anomaly"
    
    def _save_news(self, news_items: List[Dict[str, Any]]) -> None:
        """Save news items to JSON file. Skip any item with empty headline or body."""
        valid = [
            n for n in news_items
            if (n.get("headline") or "").strip() and (n.get("body") or "").strip()
        ]
        if not valid:
            return
        existing_news = {"latest": []}
        if self.news_path.exists():
            try:
                with open(self.news_path, "r") as f:
                    existing_news = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        existing_news["latest"] = (existing_news.get("latest") or []) + valid
        existing_news["latest"] = existing_news["latest"][-50:]
        if validate_news_json(existing_news):
            self.news_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.news_path, "w") as f:
                json.dump(existing_news, f, indent=2)
