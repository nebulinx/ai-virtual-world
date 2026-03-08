"""Reset world.json and news.json to blank state. Run with: python -m backend.reset_world."""

import json
from datetime import datetime, timezone
from pathlib import Path

from backend.config import WORLD_JSON_PATH, NEWS_JSON_PATH, DIRECTION_JSON_PATH


def reset_world() -> None:
    """Overwrite world.json with blank schema (empty entities, events, anomalies)."""
    world_path = Path(WORLD_JSON_PATH)
    world_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "physics": {
            "gravity": {"default": -9.8, "zones": []},
            "timeFlow": {"default": 1.0, "zones": []},
            "dimensions": 4,
        },
        "entities": [],
        "terrain": {},
        "events": [],
        "anomalies": [],
        "evolution_log": [],
    }
    with open(world_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Reset {world_path}")


def reset_news() -> None:
    """Overwrite news.json with empty latest list."""
    news_path = Path(NEWS_JSON_PATH)
    news_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"latest": []}
    with open(news_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Reset {news_path}")


def reset_direction() -> None:
    """Overwrite direction.json with empty latest and history."""
    direction_path = Path(DIRECTION_JSON_PATH)
    direction_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"latest": None, "history": []}
    with open(direction_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Reset {direction_path}")


def main() -> None:
    reset_world()
    reset_news()
    reset_direction()
    print("Done. World, news, and direction are blank.")


if __name__ == "__main__":
    main()
