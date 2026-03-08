"""Configuration for AI Virtual World system."""

import os
from typing import Optional

# Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# Default: single model (qwen coder) for all agents. Set OLLAMA_MODEL to override; set to empty to use coder/reasoning split.
OLLAMA_CODER_MODEL = os.getenv("OLLAMA_CODER_MODEL", "qwen2.5-coder:7b")
OLLAMA_REASONING_MODEL = os.getenv("OLLAMA_REASONING_MODEL", "deepseek-r1:7b")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", OLLAMA_CODER_MODEL)

# Git configuration
GIT_USER_NAME = os.getenv("GIT_USER_NAME", "AI Virtual World")
GIT_USER_EMAIL = os.getenv("GIT_USER_EMAIL", "ai@virtualworld.local")
GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
GIT_REPO_URL = "git@github.com:nebulinx/ai-virtual-world.git"

# World state paths
WORLD_DATA_DIR = "backend/data"
WORLD_JSON_PATH = f"{WORLD_DATA_DIR}/world.json"
NEWS_JSON_PATH = f"{WORLD_DATA_DIR}/news.json"
DIRECTION_JSON_PATH = f"{WORLD_DATA_DIR}/direction.json"
HISTORY_DIR = f"{WORLD_DATA_DIR}/history"

# Agent loop configuration
AGENT_LOOP_INTERVAL = int(os.getenv("AGENT_LOOP_INTERVAL", "60"))  # seconds between cycles; 0 = no sleep (back-to-back)
COMMIT_INTERVAL = int(os.getenv("COMMIT_INTERVAL", "300"))  # seconds between commits (when not committing every cycle)
COMMIT_EVERY_CYCLE = os.getenv("COMMIT_EVERY_CYCLE", "true").lower() in ("1", "true", "yes")  # commit after each cycle with Planner summary as message

# Frontend configuration
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/nebulinx/ai-virtual-world/main"
WORLD_JSON_URL = f"{GITHUB_RAW_BASE}/{WORLD_JSON_PATH}"
NEWS_JSON_URL = f"{GITHUB_RAW_BASE}/{NEWS_JSON_PATH}"
DIRECTION_JSON_URL = f"{GITHUB_RAW_BASE}/{DIRECTION_JSON_PATH}"
