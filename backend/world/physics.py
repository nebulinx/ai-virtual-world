"""Alien physics rules and simulation."""

from typing import Dict, List, Any, Tuple
import math
import random


class PhysicsEngine:
    """Manages alien physics rules and simulation."""
    
    def __init__(self, world_state: Dict[str, Any]):
        self.world_state = world_state
        self.physics = world_state.get("physics", {})
    
    def get_gravity_at_position(self, position: Dict[str, float]) -> float:
        """Get gravity strength at a given position."""
        default_gravity = self.physics.get("gravity", {}).get("default", -9.8)
        zones = self.physics.get("gravity", {}).get("zones", [])
        
        for zone in zones:
            if self._point_in_zone(position, zone):
                return zone.get("gravity", default_gravity)
        
        return default_gravity
    
    def get_time_factor_at_position(self, position: Dict[str, float]) -> float:
        """Get time flow factor at a given position."""
        default_time = self.physics.get("timeFlow", {}).get("default", 1.0)
        zones = self.physics.get("timeFlow", {}).get("zones", [])
        
        for zone in zones:
            if self._point_in_zone(position, zone):
                return zone.get("time_factor", default_time)
        
        return default_time
    
    def _point_in_zone(self, position: Dict[str, float], zone: Dict[str, Any]) -> bool:
        """Check if point is within a physics zone."""
        zone_type = zone.get("type", "sphere")
        center = zone.get("center", {})
        radius = zone.get("radius", 10.0)
        
        if zone_type == "sphere":
            distance = self._distance(position, center)
            return distance <= radius
        elif zone_type == "box":
            # Check if point is in axis-aligned box
            return all(
                center.get(axis, 0) - radius <= position.get(axis, 0) <= center.get(axis, 0) + radius
                for axis in ["x", "y", "z"]
            )
        return False
    
    def _distance(self, pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
        """Calculate multi-dimensional distance."""
        dimensions = self.physics.get("dimensions", 4)
        squared_sum = 0.0
        
        for i in range(dimensions):
            axis = ["x", "y", "z", "w", "v", "u", "t", "s", "r", "q"][i]
            diff = pos1.get(axis, 0) - pos2.get(axis, 0)
            squared_sum += diff * diff
        
        return math.sqrt(squared_sum)
    
    def apply_physics_to_entity(self, entity: Dict[str, Any]) -> Dict[str, float]:
        """Apply physics rules to an entity position."""
        position = entity.get("position", {})
        entity_type = entity.get("type", "")
        
        # Get local physics
        gravity = self.get_gravity_at_position(position)
        time_factor = self.get_time_factor_at_position(position)
        
        # Apply gravity (negative gravity makes things float)
        velocity = entity.get("properties", {}).get("velocity", {})
        new_velocity = {}
        
        for axis in ["x", "y", "z"]:
            current_vel = velocity.get(axis, 0)
            # Gravity affects y-axis (up/down)
            if axis == "y":
                new_vel = current_vel + gravity * 0.1 * time_factor
            else:
                new_vel = current_vel * (1 - 0.01 * time_factor)  # Friction
            new_velocity[axis] = new_vel
        
        # Update position based on velocity
        new_position = {}
        for axis in ["x", "y", "z", "w"]:
            current_pos = position.get(axis, 0)
            vel = new_velocity.get(axis, 0)
            new_position[axis] = current_pos + vel * time_factor
        
        # Special physics for different entity types
        if entity_type == "EnergyVortex":
            # Vortex creates local gravity well
            vortex_gravity = entity.get("properties", {}).get("gravity_well", {}).get("strength", 0)
            if vortex_gravity != 0:
                # Pull nearby entities toward vortex
                pass  # Implemented in world engine
        
        return new_position
    
    def create_gravity_zone(self, center: Dict[str, float], radius: float, gravity: float) -> Dict[str, Any]:
        """Create a new gravity zone."""
        zone = {
            "type": "sphere",
            "center": center,
            "radius": radius,
            "gravity": gravity
        }
        return zone
    
    def create_time_zone(self, center: Dict[str, float], radius: float, time_factor: float) -> Dict[str, Any]:
        """Create a new time flow zone."""
        zone = {
            "type": "sphere",
            "center": center,
            "radius": radius,
            "time_factor": time_factor
        }
        return zone
