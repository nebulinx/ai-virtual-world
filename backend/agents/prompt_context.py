"""Shared context for agent prompts: schema, paths, entity contract. Keep DRY across agents."""

# Paths to world and code files (relative to project root)
WORLD_JSON_PATH = "backend/data/world.json"
NEWS_JSON_PATH = "backend/data/news.json"
ENTITIES_MODULE_PATH = "backend/world/entities.py"
PHYSICS_MODULE_PATH = "backend/world/physics.py"
EVENTS_MODULE_PATH = "backend/world/events.py"

# Known entity type names (must match ENTITY_TYPES in entities.py)
ENTITY_TYPES_LIST = [
    "EnergyVortex",
    "CrystalFormation",
    "TemporalAnomaly",
    "QuantumParticle",
]

WORLD_SCHEMA_SUMMARY = """World state (world.json) has:
- version, timestamp
- physics: gravity (default, zones), timeFlow (default, zones), dimensions (3-10)
- entities: array of { id, type, position {x,y,z,w}, properties?, age? }
- terrain: object
- events: array of event objects
- anomalies: array of anomaly objects
Entity required fields: id, type, position. Optional: properties, behavior, age."""

ENTITY_CONTRACT = """Every entity class must:
1. Inherit from Entity (from same module).
2. Implement update(self, world_state: Dict[str, Any]) -> Dict[str, Any].
3. Use to_dict() (inherited) for JSON; ensure position, properties, age are set.
4. Be registered in ENTITY_TYPES dict in the same file, e.g. ENTITY_TYPES["NewEntityName"] = NewEntityName."""
