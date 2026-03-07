"""File operation utilities."""

from pathlib import Path
from typing import List
import json


def ensure_directory(path: str) -> None:
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)


def read_json_file(file_path: str) -> dict:
    """Read JSON file."""
    path = Path(file_path)
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return {}


def write_json_file(file_path: str, data: dict) -> None:
    """Write JSON file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
