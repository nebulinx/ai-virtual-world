"""News agent - generates news from world events."""

from typing import Dict, Any, List
from datetime import datetime
from backend.agents.base_agent import BaseAgent
from backend.ai.ollama_client import OllamaClient
from backend.config import NEWS_JSON_PATH
from backend.world.schemas import validate_news_json
import json
from pathlib import Path


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
        
        # Get recent events (last 5)
        recent_events = events[-5:] if events else []
        
        # Analyze significant changes
        significant_events = [
            e for e in recent_events
            if e.get("type") in ["dimensional_rift", "temporal_distortion", "energy_storm"]
        ]
        
        return {
            "recent_events": recent_events,
            "significant_events": significant_events,
            "entity_count": len(entities),
            "anomaly_count": len(anomalies),
            "news_items_to_generate": min(3, len(significant_events) + 1)
        }
    
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate news articles."""
        thoughts = context.get("thoughts", {})
        recent_events = thoughts.get("recent_events", [])
        significant_events = thoughts.get("significant_events", [])
        
        news_items = []
        
        # Generate news for significant events
        for event in significant_events[:3]:  # Limit to 3
            news_item = self._generate_news_for_event(event)
            if news_item:
                news_items.append(news_item)
        
        # Generate general world update if no significant events
        if not news_items:
            news_item = self._generate_general_update(context.get("world_state", {}))
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
    
    def _generate_news_for_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Generate news article for a specific event."""
        event_type = event.get("type", "unknown")
        description = event.get("description", "")
        
        prompt = f"""Write a news article in the style of "alien news" reporting about this virtual world event:

Event Type: {event_type}
Description: {description}

Write a creative, engaging news headline and body that describes this event in an interesting way.
Format as JSON with "headline" and "body" fields. Keep it concise (2-3 sentences for body)."""
        
        try:
            response = self.ollama.generate(
                prompt,
                model=self.ollama.reasoning_model,
                temperature=0.8,
                max_tokens=300
            )
            
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                news_data = json.loads(json_match.group())
            else:
                # Fallback: create from response
                lines = response.strip().split('\n')
                headline = lines[0].replace('"', '').replace('headline:', '').strip()
                body = ' '.join(lines[1:]).replace('body:', '').strip()
                news_data = {"headline": headline, "body": body}
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "headline": news_data.get("headline", f"Event: {event_type}"),
                "body": news_data.get("body", description),
                "category": self._categorize_event(event_type)
            }
        except Exception as e:
            # Fallback news item
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "headline": f"World Event: {event_type}",
                "body": description,
                "category": self._categorize_event(event_type)
            }
    
    def _generate_general_update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general world update news."""
        entity_count = len(world_state.get("entities", []))
        events_count = len(world_state.get("events", []))
        
        prompt = f"""Write a brief news update about the virtual world:

Current state:
- Entities: {entity_count}
- Total events: {events_count}

Write a creative headline and 2-3 sentence update about the world's current state.
Format as JSON with "headline" and "body" fields."""
        
        try:
            response = self.ollama.generate(
                prompt,
                model=self.ollama.reasoning_model,
                temperature=0.7,
                max_tokens=200
            )
            
            import re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                news_data = json.loads(json_match.group())
            else:
                lines = response.strip().split('\n')
                headline = lines[0].replace('"', '').replace('headline:', '').strip()
                body = ' '.join(lines[1:]).replace('body:', '').strip()
                news_data = {"headline": headline, "body": body}
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "headline": news_data.get("headline", "World Update"),
                "body": news_data.get("body", f"The world currently has {entity_count} entities."),
                "category": "entity"
            }
        except Exception:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "headline": "World Status Update",
                "body": f"The virtual world continues to evolve with {entity_count} active entities.",
                "category": "entity"
            }
    
    def _categorize_event(self, event_type: str) -> str:
        """Categorize event type."""
        if "gravity" in event_type or "physics" in event_type:
            return "physics"
        elif "entity" in event_type:
            return "entity"
        else:
            return "anomaly"
    
    def _save_news(self, news_items: List[Dict[str, Any]]) -> None:
        """Save news items to JSON file."""
        # Load existing news
        existing_news = {"latest": []}
        if self.news_path.exists():
            try:
                with open(self.news_path, 'r') as f:
                    existing_news = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Add new items
        existing_news["latest"].extend(news_items)
        
        # Keep only last 50 items
        existing_news["latest"] = existing_news["latest"][-50:]
        
        # Validate before saving
        if validate_news_json(existing_news):
            self.news_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.news_path, 'w') as f:
                json.dump(existing_news, f, indent=2)
