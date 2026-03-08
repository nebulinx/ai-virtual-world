"""Tester agent - validates world state and code integrity."""

from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.agents.prompt_context import WORLD_SCHEMA_SUMMARY, ENTITY_TYPES_LIST
from backend.ai.ollama_client import OllamaClient
from backend.world.schemas import validate_world_json, validate_news_json
import json
from pathlib import Path


class TesterAgent(BaseAgent):
    """Verifies world state integrity and code correctness."""
    
    def __init__(self, ollama_client: OllamaClient):
        super().__init__("Tester", ollama_client)
    
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze world state and code for validation."""
        world_state = context.get("world_state", {})
        code_changes = context.get("code_changes", [])
        
        world_valid = validate_world_json(world_state)
        issues = []
        
        if not world_valid:
            issues.append("World JSON schema validation failed")
        
        entities = world_state.get("entities", [])
        for entity in entities:
            if "id" not in entity or "type" not in entity:
                issues.append(f"Entity missing required fields: {entity}")
            if "position" not in entity:
                issues.append(f"Entity {entity.get('id')} missing position")
            etype = entity.get("type")
            if etype and etype not in ENTITY_TYPES_LIST:
                issues.append(f"Entity type '{etype}' not in ENTITY_TYPES registry (known: {ENTITY_TYPES_LIST})")
        
        physics = world_state.get("physics", {})
        if "dimensions" not in physics:
            issues.append("Physics missing dimensions")
        
        code_issues = []
        if code_changes:
            for change in code_changes:
                if "code" in change:
                    try:
                        compile(change["code"], "<string>", "exec")
                    except SyntaxError as e:
                        code_issues.append(f"Syntax error in code: {e}")
        
        return {
            "world_valid": world_valid,
            "issues": issues,
            "code_issues": code_issues,
            "entity_count": len(entities),
            "validation_passed": len(issues) == 0 and len(code_issues) == 0
        }
    
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run validation tests."""
        thoughts = context.get("thoughts", {})
        validation_passed = thoughts.get("validation_passed", False)
        issues = thoughts.get("issues", [])
        code_issues = thoughts.get("code_issues", [])
        
        if validation_passed:
            return {
                "status": "success",
                "agent": self.name,
                "validation": "passed",
                "message": "All validations passed",
                "next_agent": "news_agent"
            }
        else:
            return {
                "status": "warning",
                "agent": self.name,
                "validation": "failed",
                "issues": issues + code_issues,
                "message": f"Found {len(issues + code_issues)} issues",
                "next_agent": "news_agent"  # Continue anyway, but log issues
            }
    
    def validate_world_file(self, file_path: str) -> bool:
        """Validate world.json file."""
        path = Path(file_path)
        if not path.exists():
            return False
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return validate_world_json(data)
        except (json.JSONDecodeError, IOError):
            return False
    
    def validate_news_file(self, file_path: str) -> bool:
        """Validate news.json file."""
        path = Path(file_path)
        if not path.exists():
            return False
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return validate_news_json(data)
        except (json.JSONDecodeError, IOError):
            return False
