"""Applier agent - writes generated code to the codebase using CodeEvolution."""

import re
from pathlib import Path
from typing import Dict, Any

from backend.agents.base_agent import BaseAgent
from backend.agents.prompt_context import (
    ENTITIES_MODULE_PATH,
    PHYSICS_MODULE_PATH,
    EVENTS_MODULE_PATH,
)
from backend.ai.code_evolution import CodeEvolution


# Paths relative to project root (cwd when running from repo root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class ApplierAgent(BaseAgent):
    """Applies developer-generated code to the correct file."""

    def __init__(self):
        super().__init__("Applier", None)
        self.code_evolution = CodeEvolution()

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Determine target file and extract code to apply."""
        code_changes = context.get("code_changes", [])
        if not code_changes:
            return {"target_file": None, "code": "", "implementation_type": "general", "apply": False}
        last = code_changes[-1]
        code = (last.get("code") or "").strip()
        impl_type = last.get("implementation_type", "general")
        if not code:
            return {"target_file": None, "code": "", "implementation_type": impl_type, "apply": False}
        if impl_type == "entity":
            target = PROJECT_ROOT / ENTITIES_MODULE_PATH
        elif impl_type == "physics":
            target = PROJECT_ROOT / PHYSICS_MODULE_PATH
        elif impl_type == "event":
            target = PROJECT_ROOT / EVENTS_MODULE_PATH
        else:
            target = PROJECT_ROOT / ENTITIES_MODULE_PATH
        return {
            "target_file": str(target),
            "code": code,
            "implementation_type": impl_type,
            "apply": True,
        }

    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Inject code into target file; for entities, register in ENTITY_TYPES."""
        target_file = context.get("target_file")
        code = context.get("code", "")
        impl_type = context.get("implementation_type", "general")
        apply = context.get("apply", False)

        if not apply or not target_file or not code:
            return {
                "status": "skipped",
                "agent": self.name,
                "applied": False,
                "message": "No code to apply",
                "next_agent": "refactor",
            }

        # Strip markdown code fences if present
        code = re.sub(r"^```(?:\w*)\n?", "", code)
        code = re.sub(r"\n?```\s*$", "", code)
        code = code.strip()

        # For entities: separate class code from ENTITY_TYPES line
        entity_types_line = None
        if impl_type == "entity":
            match = re.search(r'\n\s*ENTITY_TYPES\s*\[\s*["\'](\w+)["\']\s*\]\s*=\s*\1\s*', code)
            if match:
                entity_types_line = match.group(0).strip()
                code = code[: match.start()].strip()
            # Extract class name for later registration if not in ENTITY_TYPES line
            class_match = re.search(r"class\s+(\w+)\s*\(\s*Entity\s*\)", code)
            class_name = class_match.group(1) if class_match else None

        ok, msg = self.code_evolution.inject_code(
            target_file,
            code,
            location="end",
        )
        if not ok:
            return {
                "status": "error",
                "agent": self.name,
                "applied": False,
                "file": target_file,
                "error": msg,
                "next_agent": "refactor",
            }

        # For entities, add ENTITY_TYPES entry if we have it
        if impl_type == "entity" and (entity_types_line or class_name):
            path = Path(target_file)
            if path.exists():
                text = path.read_text()
                if entity_types_line:
                    # Parse ENTITY_TYPES["X"] = X
                    m = re.search(r'ENTITY_TYPES\s*\[\s*["\'](\w+)["\']\s*\]\s*=\s*(\w+)', entity_types_line)
                    if m:
                        key, val = m.group(1), m.group(2)
                        entry_line = f'    "{key}": {val}'
                    else:
                        entry_line = None
                elif class_name:
                    entry_line = f'    "{class_name}": {class_name}'
                else:
                    entry_line = None
                if entry_line:
                    # Add new entry to ENTITY_TYPES: find the block and insert after last entry
                    block_match = re.search(
                        r"(ENTITY_TYPES\s*=\s*\{)(.*?)(\n\s*\})(\s*\n(?:def |\Z))",
                        text,
                        re.DOTALL,
                    )
                    if block_match:
                        block_content = block_match.group(2)
                        closing_brace = block_match.group(3)
                        rest = block_match.group(4)
                        last_entry_match = re.search(
                            r"(\s*\"[A-Za-z0-9_]+\":\s*[A-Za-z0-9_]+)\s*,?\s*$",
                            block_content,
                            re.MULTILINE,
                        )
                        if last_entry_match:
                            last_line = last_entry_match.group(1).rstrip().rstrip(",")
                            new_block = (
                                block_content[: last_entry_match.start()]
                                + last_line
                                + ",\n    "
                                + entry_line.strip()
                                + "\n"
                            )
                            new_text = text.replace(
                                block_match.group(0),
                                block_match.group(1) + new_block + closing_brace + rest,
                            )
                            path.write_text(new_text)

        return {
            "status": "success",
            "agent": self.name,
            "applied": True,
            "file": target_file,
            "message": msg,
            "next_agent": "refactor",
        }
