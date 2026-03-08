"""Core world state management engine."""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from backend.config import WORLD_JSON_PATH, HISTORY_DIR
from backend.world.schemas import validate_world_json


class WorldEngine:
    """Manages world state, entities, physics, and events."""
    
    def __init__(self):
        self.world_path = Path(WORLD_JSON_PATH)
        self.history_dir = Path(HISTORY_DIR)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.world_state: Dict[str, Any] = {}
        self.load_world()
    
    def load_world(self) -> None:
        """Load world state from JSON file."""
        if self.world_path.exists():
            try:
                with open(self.world_path, 'r') as f:
                    self.world_state = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._initialize_world()
        else:
            self._initialize_world()
    
    def _initialize_world(self) -> None:
        """Initialize a new world state."""
        self.world_state = {
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "physics": {
                "gravity": {
                    "default": -9.8,
                    "zones": []
                },
                "timeFlow": {
                    "default": 1.0,
                    "zones": []
                },
                "dimensions": 4
            },
            "entities": [],
            "terrain": {},
            "events": [],
            "anomalies": [],
            "evolution_log": [],
        }
        self.save_world()

    EVOLUTION_LOG_CAP = 50

    def append_evolution_entry(self, cycle_index: int, summary: str) -> None:
        """Append a per-cycle evolution entry so every commit has a real world change."""
        from datetime import timezone
        entry = {
            "cycle": cycle_index,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": (summary or "").strip() or f"Cycle {cycle_index}",
        }
        log = self.world_state.setdefault("evolution_log", [])
        log.append(entry)
        self.world_state["evolution_log"] = log[-self.EVOLUTION_LOG_CAP:]
    
    def save_world(self) -> None:
        """Save world state to JSON file."""
        self.world_state["timestamp"] = datetime.utcnow().isoformat()
        
        # Validate before saving
        if not validate_world_json(self.world_state):
            raise ValueError("World state validation failed")
        
        # Create backup to history
        self._save_to_history()
        
        # Save current state
        self.world_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.world_path, 'w') as f:
            json.dump(self.world_state, f, indent=2)
    
    def _save_to_history(self) -> None:
        """Save snapshot to history directory."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        history_file = self.history_dir / f"world_{timestamp}.json"
        with open(history_file, 'w') as f:
            json.dump(self.world_state, f, indent=2)
    
    def get_world_state(self) -> Dict[str, Any]:
        """Get current world state."""
        return self.world_state.copy()
    
    def update_physics(self, physics_updates: Dict[str, Any]) -> None:
        """Update physics properties."""
        self.world_state["physics"].update(physics_updates)
        self.save_world()
    
    def add_entity(self, entity: Dict[str, Any]) -> str:
        """Add a new entity to the world."""
        if "id" not in entity:
            entity["id"] = f"entity_{len(self.world_state['entities'])}"
        self.world_state["entities"].append(entity)
        self.save_world()
        return entity["id"]
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing entity."""
        for i, entity in enumerate(self.world_state["entities"]):
            if entity["id"] == entity_id:
                self.world_state["entities"][i].update(updates)
                self.save_world()
                return True
        return False
    
    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity from the world."""
        initial_count = len(self.world_state["entities"])
        self.world_state["entities"] = [
            e for e in self.world_state["entities"] if e["id"] != entity_id
        ]
        if len(self.world_state["entities"]) < initial_count:
            self.save_world()
            return True
        return False
    
    def add_event(self, event: Dict[str, Any]) -> None:
        """Add a world event."""
        if "timestamp" not in event:
            event["timestamp"] = datetime.utcnow().isoformat()
        self.world_state["events"].append(event)
        # Keep only last 100 events
        if len(self.world_state["events"]) > 100:
            self.world_state["events"] = self.world_state["events"][-100:]
        self.save_world()
    
    def add_anomaly(self, anomaly: Dict[str, Any]) -> None:
        """Add an anomaly to the world."""
        if "id" not in anomaly:
            anomaly["id"] = f"anomaly_{len(self.world_state['anomalies'])}"
        self.world_state["anomalies"].append(anomaly)
        self.save_world()
    
    def tick(self) -> None:
        """Advance world simulation by one tick (legacy alias)."""
        self.run_entity_tick()

    def run_entity_tick(self) -> None:
        """Run each entity's update(world_state) and apply results back to the world."""
        try:
            from backend.world.entities import ENTITY_TYPES
        except ImportError:
            return
        world_copy = self.get_world_state()
        for i, entity_data in enumerate(list(self.world_state["entities"])):
            entity_type = entity_data.get("type")
            if not entity_type or entity_type not in ENTITY_TYPES:
                continue
            try:
                cls = ENTITY_TYPES[entity_type]
                pos = entity_data.get("position") or {}
                props = entity_data.get("properties") or {}
                inst = cls(
                    entity_data.get("id", ""),
                    {"x": pos.get("x", 0), "y": pos.get("y", 0), "z": pos.get("z", 0), "w": pos.get("w", 0)},
                    props,
                )
                inst.age = entity_data.get("age", 0)
                result = inst.update(world_copy)
                if isinstance(result, dict):
                    if "position" in result:
                        self.world_state["entities"][i]["position"] = result["position"]
                    if "properties" in result:
                        self.world_state["entities"][i]["properties"] = result["properties"]
                    if "age" in result:
                        self.world_state["entities"][i]["age"] = result["age"]
                    elif hasattr(inst, "age"):
                        self.world_state["entities"][i]["age"] = inst.age
            except Exception:
                continue
