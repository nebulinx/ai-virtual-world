"""Entity definitions and behaviors."""

from typing import Dict, Any, List
from abc import ABC, abstractmethod
import random


class Entity(ABC):
    """Base class for all world entities."""
    
    def __init__(self, entity_id: str, position: Dict[str, float], properties: Dict[str, Any] = None):
        self.id = entity_id
        self.position = position
        self.properties = properties or {}
        self.age = 0
    
    @abstractmethod
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Update entity state based on world conditions."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.__class__.__name__,
            "position": self.position,
            "properties": self.properties,
            "age": self.age
        }


class EnergyVortex(Entity):
    """Creates gravity wells and spawns particles."""
    
    def __init__(self, entity_id: str, position: Dict[str, float], properties: Dict[str, Any] = None):
        super().__init__(entity_id, position, properties)
        self.energy_level = self.properties.get("energy_level", 100.0)
        self.radius = self.properties.get("radius", 5.0)
        self.particles_spawned = 0
    
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Update vortex state."""
        self.age += 1
        self.energy_level -= 0.1
        
        # Spawn particles occasionally
        if random.random() < 0.1:
            self.particles_spawned += 1
        
        # Update properties
        self.properties["energy_level"] = self.energy_level
        self.properties["particles_spawned"] = self.particles_spawned
        
        return {
            "position": self.position,
            "properties": self.properties,
            "gravity_well": {
                "strength": self.energy_level * 0.1,
                "radius": self.radius
            }
        }


class CrystalFormation(Entity):
    """Crystalline structures that grow over time."""
    
    def __init__(self, entity_id: str, position: Dict[str, float], properties: Dict[str, Any] = None):
        super().__init__(entity_id, position, properties)
        self.size = self.properties.get("size", 1.0)
        self.growth_rate = self.properties.get("growth_rate", 0.01)
    
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Update crystal growth."""
        self.age += 1
        self.size += self.growth_rate
        self.properties["size"] = self.size
        
        return {
            "position": self.position,
            "properties": self.properties
        }


class TemporalAnomaly(Entity):
    """Regions where time flows at different rates."""
    
    def __init__(self, entity_id: str, position: Dict[str, float], properties: Dict[str, Any] = None):
        super().__init__(entity_id, position, properties)
        self.time_factor = self.properties.get("time_factor", 1.5)
        self.radius = self.properties.get("radius", 10.0)
    
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Update temporal anomaly."""
        self.age += 1
        # Time factor fluctuates
        self.time_factor += random.uniform(-0.1, 0.1)
        self.time_factor = max(0.1, min(5.0, self.time_factor))
        self.properties["time_factor"] = self.time_factor
        
        return {
            "position": self.position,
            "properties": self.properties,
            "time_zone": {
                "factor": self.time_factor,
                "radius": self.radius
            }
        }


class QuantumParticle(Entity):
    """Particles that exist in multiple states simultaneously."""
    
    def __init__(self, entity_id: str, position: Dict[str, float], properties: Dict[str, Any] = None):
        super().__init__(entity_id, position, properties)
        self.quantum_states = self.properties.get("quantum_states", 2)
        self.current_state = 0
    
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Update quantum particle state."""
        self.age += 1
        # Quantum state changes probabilistically
        if random.random() < 0.3:
            self.current_state = (self.current_state + 1) % self.quantum_states
        
        # Position can be in superposition
        offset = random.uniform(-0.5, 0.5)
        new_position = {
            "x": self.position.get("x", 0) + offset,
            "y": self.position.get("y", 0) + offset,
            "z": self.position.get("z", 0) + offset,
            "w": self.position.get("w", 0) + offset * 0.1
        }
        self.position = new_position
        self.properties["current_state"] = self.current_state
        
        return {
            "position": self.position,
            "properties": self.properties
        }


# Entity registry for dynamic creation
ENTITY_TYPES = {
    "EnergyVortex": EnergyVortex,
    "CrystalFormation": CrystalFormation,
    "TemporalAnomaly": TemporalAnomaly,
    "QuantumParticle": QuantumParticle
}


def create_entity(entity_type: str, entity_id: str, position: Dict[str, float], properties: Dict[str, Any] = None) -> Entity:
    """Factory function to create entities."""
    if entity_type not in ENTITY_TYPES:
        raise ValueError(f"Unknown entity type: {entity_type}")
    return ENTITY_TYPES[entity_type](entity_id, position, properties)


from typing import Dict, Any
from backend.world.entities import Entity, ENTITY_TYPES

class AdaptiveEntity(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Implement logic to adapt to varying dimensions
        # Example: Adjust properties based on world_state
        if 'dimension' in world_state:
            if world_state['dimension'] == 'high':
                self.properties['strength'] *= 1.1
            elif world_state['dimension'] == 'low':
                self.properties['strength'] *= 0.9
        return super().update(world_state)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.__class__.__name__,
            "position": self.position,
            "properties": self.properties,
            "age": self.age
        }

# Register the new entity type
ENTITY_TYPES["AdaptiveEntity"] = AdaptiveEntity

from typing import Dict, Any
import time

class Entity:
    def __init__(self, position: Dict[str, float], properties: Dict[str, Any]):
        self.position = position
        self.properties = properties
        self.age = 0

    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def to_dict(self):
        return {
            "position": self.position,
            "properties": self.properties,
            "age": self.age
        }

class TimeDilationZone:
    def __init__(self, time_rate: float):
        self.time_rate = time_rate

    def update_time(self, elapsed_time: float) -> float:
        return elapsed_time * self.time_rate

class DynamicTimeDilationEntity(Entity):
    def __init__(self, position: Dict[str, float], properties: Dict[str, Any], zone: TimeDilationZone):
        super().__init__(position, properties)
        self.zone = zone

    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        elapsed_time = time.time() - self.properties.get("last_update_time", 0)
        actual_time_passed = self.zone.update_time(elapsed_time)
        self.age += actual_time_passed
        self.properties["last_update_time"] = time.time()
        return self.to_dict()

    def to_dict(self):
        return {
            **super().to_dict(),
            "zone": self.zone.time_rate
        }

ENTITY_TYPES = {
    "DynamicTimeDilationEntity": DynamicTimeDilationEntity
}

from backend.world.entities import Entity, ENTITY_TYPES
from typing import Dict, Any

class AlternateVersionEntity(Entity):
    def __init__(self, position: Dict[str, int], properties: Dict[str, Any], age: int, version: str):
        super().__init__(position, properties, age)
        self.version = version

    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Example update logic based on the version
        if self.version == "v1":
            self.properties["power"] += 1
        elif self.version == "v2":
            self.properties["energy"] += 2
        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "properties": self.properties,
            "age": self.age,
            "version": self.version
        }

ENTITY_TYPES["AlternateVersionEntity"] = AlternateVersionEntity