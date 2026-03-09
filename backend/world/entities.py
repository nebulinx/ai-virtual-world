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

from world.entities import Entity, ENTITY_TYPES

class SocialNetworkMember(Entity):
    def __init__(self, position, properties=None, age=0, relationships=None):
        super().__init__(position, properties, age)
        self.relationships = relationships if relationships is not None else {}

    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        new_properties = self.properties.copy()
        for relationship, strength in self.relationships.items():
            if relationship in world_state:
                related_entity = world_state[relationship]
                if related_entity.type == "SocialNetworkMember":
                    new_properties["influence"] += strength * related_entity.properties["influence"]
        return new_properties

    def to_dict(self):
        return {
            **super().to_dict(),
            "relationships": self.relationships
        }

ENTITY_TYPES["SocialNetworkMember"] = SocialNetworkMember

from typing import Dict, Any
from backend.world.entities import Entity, ENTITY_TYPES

class TimeZoneEntity(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Implement your time zone entity logic here
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "properties": self.properties,
            "age": self.age
        }

ENTITY_TYPES["TimeZoneEntity"] = TimeZoneEntity

from backend.world.entities import Entity, ENTITY_TYPES

class NewEntityName(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Implement update logic here
        pass

ENTITY_TYPES["NewEntityName"] = NewEntityName

from typing import Dict, Any

class Entity:
    def __init__(self, position: Dict[str, float], properties: Dict[str, Any], age: float):
        self.position = position
        self.properties = properties
        self.age = age

    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "properties": self.properties,
            "age": self.age
        }

class Zone:
    def __init__(self, time_speed: float):
        self.time_speed = time_speed
        self.entities = []

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def remove_entity(self, entity: Entity):
        self.entities.remove(entity)

    def update_entities(self, world_state: Dict[str, Any]):
        for entity in self.entities:
            entity.update(world_state)

ENTITY_TYPES = {}

class EnergyVortex(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Implement update logic for EnergyVortex
        return self.to_dict()

ENTITY_TYPES["EnergyVortex"] = EnergyVortex

class CrystalFormation(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Implement update logic for CrystalFormation
        return self.to_dict()

ENTITY_TYPES["CrystalFormation"] = CrystalFormation

class TemporalAnomaly(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Implement update logic for TemporalAnomaly
        return self.to_dict()

ENTITY_TYPES["TemporalAnomaly"] = TemporalAnomaly

class QuantumParticle(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Implement update logic for QuantumParticle
        return self.to_dict()

ENTITY_TYPES["QuantumParticle"] = QuantumParticle

from typing import Dict, Any

class Entity:
    def __init__(self, position: Dict[str, float], properties: Dict[str, Any]):
        self.position = position
        self.properties = properties
        self.age = 0

    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement update method")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "properties": self.properties,
            "age": self.age
        }

class EnergyVortex(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Example update logic for EnergyVortex
        self.age += 1
        self.position["x"] += 0.1
        return self.to_dict()

class CrystalFormation(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Example update logic for CrystalFormation
        self.age += 1
        self.position["y"] += 0.05
        return self.to_dict()

class TemporalAnomaly(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Example update logic for TemporalAnomaly
        self.age += 1
        self.position["z"] += 0.2
        return self.to_dict()

class QuantumParticle(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Example update logic for QuantumParticle
        self.age += 1
        self.position["x"] += 0.05
        self.position["y"] += 0.05
        self.position["z"] += 0.05
        return self.to_dict()

ENTITY_TYPES = {
    "EnergyVortex": EnergyVortex,
    "CrystalFormation": CrystalFormation,
    "TemporalAnomaly": TemporalAnomaly,
    "QuantumParticle": QuantumParticle
}

from backend.world.entities import Entity, ENTITY_TYPES
from typing import Dict, Any

class EvolutionCrystal(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Implement your logic here
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "properties": self.properties,
            "age": self.age
        }

ENTITY_TYPES["EvolutionCrystal"] = EvolutionCrystal

from backend.world.entities import Entity, ENTITY_TYPES, Position
import time

class Zone:
    def __init__(self, time_flow_speed: float):
        self.time_flow_speed = time_flow_speed

    def update_time_flow_speed(self, new_speed: float):
        self.time_flow_speed = new_speed

class EntityWithZoneSpeed(Entity):
    def __init__(self, position: Position, properties: Dict[str, Any], zone_speed: float):
        super().__init__(position, properties)
        self.zone_speed = zone_speed
        self.enter_time = time.time()

    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        current_time = time.time()
        time_passed = (current_time - self.enter_time) * self.zone_speed
        self.age += time_passed
        self.enter_time = current_time
        return super().update(world_state)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "zone_speed": self.zone_speed
        }

ENTITY_TYPES["EntityWithZoneSpeed"] = EntityWithZoneSpeed

from typing import Dict, Any
import random

class Entity:
    def __init__(self, position: Dict[str, float], properties: Dict[str, Any], age: int = 0):
        self.position = position
        self.properties = properties
        self.age = age

    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses should implement this!")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "properties": self.properties,
            "age": self.age
        }

class EnergyVortex(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Example update logic: increase time flow rate in the zone
        world_state["zones"][self.position["zone"]]["time_flow_rate"] += self.properties["intensity"]
        return world_state

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "type": "EnergyVortex"
        }

class CrystalFormation(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Example update logic: decrease time flow rate in the zone
        world_state["zones"][self.position["zone"]]["time_flow_rate"] -= self.properties["stability"]
        return world_state

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "type": "CrystalFormation"
        }

class TemporalAnomaly(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Example update logic: randomize time flow rate in the zone
        world_state["zones"][self.position["zone"]]["time_flow_rate"] = random.uniform(0.5, 1.5)
        return world_state

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "type": "TemporalAnomaly"
        }

class QuantumParticle(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Example update logic: no direct effect on time flow rate
        return world_state

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "type": "QuantumParticle"
        }

ENTITY_TYPES = {
    "EnergyVortex": EnergyVortex,
    "CrystalFormation": CrystalFormation,
    "TemporalAnomaly": TemporalAnomaly,
    "QuantumParticle": QuantumParticle
}

from backend.world.entities import Entity, ENTITY_TYPES
from typing import Dict, Any

class FifthDimensionalEntity(Entity):
    def __init__(self, position, properties, age, time_state):
        super().__init__(position, properties, age)
        self.time_state = time_state

    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Implement custom update logic here
        # Example: Adjust position based on time_state
        new_position = (self.position[0] + self.time_state, self.position[1], self.position[2])
        return {
            "position": new_position,
            "properties": self.properties,
            "age": self.age,
            "time_state": self.time_state
        }

    def to_dict(self):
        return {
            "type": "FifthDimensionalEntity",
            "position": self.position,
            "properties": self.properties,
            "age": self.age,
            "time_state": self.time_state
        }

ENTITY_TYPES["FifthDimensionalEntity"] = FifthDimensionalEntity

from typing import Dict, Any

class Entity:
    def __init__(self, position: Dict[str, float], properties: Dict[str, Any], age: int):
        self.position = position
        self.properties = properties
        self.age = age

    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "properties": self.properties,
            "age": self.age
        }

class TemporalAnomaly(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        new_position = {
            "x": self.position["x"] + 1,
            "y": self.position["y"],
            "z": self.position["z"]
        }
        self.position = new_position
        self.age += 1
        return super().to_dict()

ENTITY_TYPES = {
    "TemporalAnomaly": TemporalAnomaly
}

from typing import Dict, Any
from backend.world.entities import Entity, ENTITY_TYPES

class FifthDimensionalBeing(Entity):
    def __init__(self, position, properties, age):
        super().__init__(position, properties, age)
        self.fifth_dimensional_energy = properties.get('fifth_dimensional_energy', 0)

    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        new_position = self.position
        # Simulate movement and influence in the fifth dimension
        if self.fifth_dimensional_energy > 0:
            # Warp to a random position in 3D space
            new_position = (
                self.position[0] + (self.fifth_dimensional_energy * 0.1),
                self.position[1] + (self.fifth_dimensional_energy * 0.1),
                self.position[2] + (self.fifth_dimensional_energy * 0.1)
            )
            self.fifth_dimensional_energy -= 1

        new_properties = {
            **self.properties,
            'fifth_dimensional_energy': self.fifth_dimensional_energy
        }

        return {
            'position': new_position,
            'properties': new_properties,
            'age': self.age + 1
        }

ENTITY_TYPES["FifthDimensionalBeing"] = FifthDimensionalBeing

from typing import Dict, Any
from .entity import Entity

class NewEntityClass(Entity):
    def update(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        # Implement the update logic for the new entity
        self.age += 1
        self.properties["health"] -= 1
        return self.to_dict()

ENTITY_TYPES = {
    "NewEntityName": NewEntityClass
}