"""JSON schemas for world state validation."""

from typing import Dict, List, Any
import json

WORLD_SCHEMA = {
    "type": "object",
    "required": ["version", "timestamp", "physics", "entities"],
    "properties": {
        "version": {"type": "string"},
        "timestamp": {"type": "string"},
        "physics": {
            "type": "object",
            "properties": {
                "gravity": {"type": "object"},
                "timeFlow": {"type": "object"},
                "dimensions": {"type": "integer", "minimum": 3, "maximum": 10}
            }
        },
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "type", "position"],
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string"},
                    "position": {"type": "object"},
                    "properties": {"type": "object"},
                    "behavior": {"type": "string"}
                }
            }
        },
        "terrain": {"type": "object"},
        "events": {"type": "array"},
        "anomalies": {"type": "array"}
    }
}

NEWS_SCHEMA = {
    "type": "object",
    "required": ["latest"],
    "properties": {
        "latest": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["timestamp", "headline", "body", "category"],
                "properties": {
                    "timestamp": {"type": "string"},
                    "headline": {"type": "string"},
                    "body": {"type": "string"},
                    "category": {"type": "string", "enum": ["physics", "entity", "anomaly"]}
                }
            }
        }
    }
}

DIRECTION_ENTRY_SCHEMA = {
    "type": "object",
    "required": ["timestamp", "challenge", "plan", "implementation_hint"],
    "properties": {
        "timestamp": {"type": "string"},
        "challenge": {"type": "string"},
        "plan": {"type": "string"},
        "implementation_hint": {"type": "string"},
        "summary": {"type": "string"},
    },
}

DIRECTION_SCHEMA = {
    "type": "object",
    "required": ["history"],
    "properties": {
        "latest": {
            "oneOf": [{"type": "null"}, DIRECTION_ENTRY_SCHEMA],
        },
        "history": {
            "type": "array",
            "items": DIRECTION_ENTRY_SCHEMA,
        },
    },
}


def validate_world_json(data: Dict[str, Any]) -> bool:
    """Validate world.json structure."""
    try:
        import jsonschema
        jsonschema.validate(instance=data, schema=WORLD_SCHEMA)
        return True
    except (jsonschema.ValidationError, ImportError):
        return False


def validate_news_json(data: Dict[str, Any]) -> bool:
    """Validate news.json structure."""
    try:
        import jsonschema
        jsonschema.validate(instance=data, schema=NEWS_SCHEMA)
        return True
    except (jsonschema.ValidationError, ImportError):
        return False


def validate_direction_json(data: Dict[str, Any]) -> bool:
    """Validate direction.json structure."""
    try:
        import jsonschema
        jsonschema.validate(instance=data, schema=DIRECTION_SCHEMA)
        return True
    except (jsonschema.ValidationError, ImportError):
        return False
