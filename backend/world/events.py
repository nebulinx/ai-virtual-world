"""Stochastic event system for world evolution."""

import random
from typing import Dict, List, Any
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """Types of stochastic events."""
    GRAVITY_FLUCTUATION = "gravity_fluctuation"
    ENERGY_STORM = "energy_storm"
    TEMPORAL_DISTORTION = "temporal_distortion"
    DIMENSIONAL_RIFT = "dimensional_rift"
    ENTITY_SPAWN = "entity_spawn"
    ENTITY_DESPAWN = "entity_despawn"


class EventGenerator:
    """Generates random events that modify the world."""
    
    def __init__(self, world_state: Dict[str, Any]):
        self.world_state = world_state
        self.event_probabilities = {
            EventType.GRAVITY_FLUCTUATION: 0.3,
            EventType.ENERGY_STORM: 0.2,
            EventType.TEMPORAL_DISTORTION: 0.15,
            EventType.DIMENSIONAL_RIFT: 0.1,
            EventType.ENTITY_SPAWN: 0.15,
            EventType.ENTITY_DESPAWN: 0.1
        }
    
    def generate_event(self) -> Dict[str, Any]:
        """Generate a random event based on probabilities."""
        event_type = self._select_event_type()
        
        if event_type == EventType.GRAVITY_FLUCTUATION:
            return self._create_gravity_fluctuation()
        elif event_type == EventType.ENERGY_STORM:
            return self._create_energy_storm()
        elif event_type == EventType.TEMPORAL_DISTORTION:
            return self._create_temporal_distortion()
        elif event_type == EventType.DIMENSIONAL_RIFT:
            return self._create_dimensional_rift()
        elif event_type == EventType.ENTITY_SPAWN:
            return self._create_entity_spawn()
        elif event_type == EventType.ENTITY_DESPAWN:
            return self._create_entity_despawn()
        
        return {}
    
    def _select_event_type(self) -> EventType:
        """Select event type based on probabilities."""
        rand = random.random()
        cumulative = 0.0
        
        for event_type, probability in self.event_probabilities.items():
            cumulative += probability
            if rand <= cumulative:
                return event_type
        
        return EventType.GRAVITY_FLUCTUATION
    
    def _create_gravity_fluctuation(self) -> Dict[str, Any]:
        """Create a gravity fluctuation event."""
        # Random position in world
        position = {
            "x": random.uniform(-50, 50),
            "y": random.uniform(-50, 50),
            "z": random.uniform(-50, 50),
            "w": random.uniform(-10, 10)
        }
        
        # Random gravity value (can be negative for anti-gravity)
        gravity = random.uniform(-20.0, 20.0)
        radius = random.uniform(5, 20)
        duration = random.uniform(10, 60)  # seconds
        
        return {
            "type": EventType.GRAVITY_FLUCTUATION.value,
            "timestamp": datetime.utcnow().isoformat(),
            "position": position,
            "gravity": gravity,
            "radius": radius,
            "duration": duration,
            "description": f"Gravity fluctuation detected: {gravity:.2f} m/s² in {radius:.1f}m radius"
        }
    
    def _create_energy_storm(self) -> Dict[str, Any]:
        """Create an energy storm event."""
        position = {
            "x": random.uniform(-50, 50),
            "y": random.uniform(-50, 50),
            "z": random.uniform(-50, 50),
            "w": random.uniform(-10, 10)
        }
        
        intensity = random.uniform(0.5, 2.0)
        radius = random.uniform(10, 30)
        duration = random.uniform(5, 30)
        
        return {
            "type": EventType.ENERGY_STORM.value,
            "timestamp": datetime.utcnow().isoformat(),
            "position": position,
            "intensity": intensity,
            "radius": radius,
            "duration": duration,
            "description": f"Energy storm detected: intensity {intensity:.2f}, radius {radius:.1f}m"
        }
    
    def _create_temporal_distortion(self) -> Dict[str, Any]:
        """Create a temporal distortion event."""
        position = {
            "x": random.uniform(-50, 50),
            "y": random.uniform(-50, 50),
            "z": random.uniform(-50, 50),
            "w": random.uniform(-10, 10)
        }
        
        time_factor = random.uniform(0.1, 3.0)  # Time flows 0.1x to 3x normal speed
        radius = random.uniform(5, 15)
        duration = random.uniform(20, 120)
        
        return {
            "type": EventType.TEMPORAL_DISTORTION.value,
            "timestamp": datetime.utcnow().isoformat(),
            "position": position,
            "time_factor": time_factor,
            "radius": radius,
            "duration": duration,
            "description": f"Temporal distortion: time flows {time_factor:.2f}x normal speed"
        }
    
    def _create_dimensional_rift(self) -> Dict[str, Any]:
        """Create a dimensional rift event."""
        position = {
            "x": random.uniform(-50, 50),
            "y": random.uniform(-50, 50),
            "z": random.uniform(-50, 50),
            "w": random.uniform(-10, 10)
        }
        
        stability = random.uniform(0.3, 1.0)
        radius = random.uniform(3, 10)
        
        return {
            "type": EventType.DIMENSIONAL_RIFT.value,
            "timestamp": datetime.utcnow().isoformat(),
            "position": position,
            "stability": stability,
            "radius": radius,
            "description": f"Dimensional rift opened: stability {stability:.2f}"
        }
    
    def _create_entity_spawn(self) -> Dict[str, Any]:
        """Create an entity spawn event."""
        entity_types = ["EnergyVortex", "CrystalFormation", "TemporalAnomaly", "QuantumParticle"]
        entity_type = random.choice(entity_types)
        
        position = {
            "x": random.uniform(-50, 50),
            "y": random.uniform(-50, 50),
            "z": random.uniform(-50, 50),
            "w": random.uniform(-10, 10)
        }
        
        return {
            "type": EventType.ENTITY_SPAWN.value,
            "timestamp": datetime.utcnow().isoformat(),
            "position": position,
            "entity_type": entity_type,
            "description": f"New {entity_type} spawned at {position}"
        }
    
    def _create_entity_despawn(self) -> Dict[str, Any]:
        """Create an entity despawn event."""
        entities = self.world_state.get("entities", [])
        if not entities:
            return {}
        
        entity = random.choice(entities)
        
        return {
            "type": EventType.ENTITY_DESPAWN.value,
            "timestamp": datetime.utcnow().isoformat(),
            "entity_id": entity.get("id"),
            "entity_type": entity.get("type"),
            "description": f"{entity.get('type')} {entity.get('id')} despawned"
        }
    
    def apply_event_to_world(self, event: Dict[str, Any], world_engine) -> None:
        """Apply an event to the world state."""
        event_type = event.get("type")
        
        if event_type == EventType.GRAVITY_FLUCTUATION.value:
            # Add gravity zone
            from backend.world.physics import PhysicsEngine
            physics = PhysicsEngine(self.world_state)
            zone = physics.create_gravity_zone(
                event["position"],
                event["radius"],
                event["gravity"]
            )
            self.world_state["physics"]["gravity"]["zones"].append(zone)
            world_engine.add_event(event)
        
        elif event_type == EventType.TEMPORAL_DISTORTION.value:
            # Add time zone
            from backend.world.physics import PhysicsEngine
            physics = PhysicsEngine(self.world_state)
            zone = physics.create_time_zone(
                event["position"],
                event["radius"],
                event["time_factor"]
            )
            self.world_state["physics"]["timeFlow"]["zones"].append(zone)
            world_engine.add_event(event)
        
        elif event_type == EventType.ENTITY_SPAWN.value:
            # Spawn new entity
            from backend.world.entities import create_entity
            entity = create_entity(
                event["entity_type"],
                f"entity_{len(self.world_state['entities'])}",
                event["position"]
            )
            world_engine.add_entity(entity.to_dict())
            world_engine.add_event(event)
        
        elif event_type == EventType.ENTITY_DESPAWN.value:
            # Remove entity
            entity_id = event.get("entity_id")
            if entity_id:
                world_engine.remove_entity(entity_id)
                world_engine.add_event(event)
        
        else:
            # Other events just get logged
            world_engine.add_event(event)
