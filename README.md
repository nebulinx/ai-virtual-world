# The Virtual World Experiment

This experiment is designed to allow AI to design a virtual world autonomously. AI agents define challenges and build the world through continuous evolution. The system defines the world's physics, gravity, time flow, and other fundamental properties. Entities, anomalies, and emergent behaviors are created and evolved by AI agents. The experiment runs 24x7 using local models (qwen2.5-coder:7b and deepSeek-r1:7b) and autonomous agents. World state is continuously updated and publicly accessible via GitHub Pages.

## Architecture Overview

- **Multi-agent system** using LangGraph for orchestration
- **5 agents**: Planner, Developer, Applier, Tester, News Agent (3 LLM calls per cycle)
- **World engine** managing entities, physics, and events
- **Real-time 3D visualization** with Three.js
- **Autonomous code evolution**: generated code is applied to the repo via the Applier agent

## System Requirements

- **16GB RAM** / **8 cores** recommended
- Docker and Docker Compose
- Poetry (Python package manager)
- Ollama (for running local AI models)
- Git with SSH keys or GitHub token configured

## Setup Instructions

### 1. Clone Repository

```bash
git clone git@github.com:nebulinx/ai-virtual-world.git
cd ai-virtual-world
```

### 2. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Configure Git Credentials

Create a `.env` file or export environment variables:

```bash
export GIT_USER_NAME="Your Name"
export GIT_USER_EMAIL="your.email@example.com"
export GITHUB_TOKEN="your_github_token"  # Optional, if using token auth
```

Or create `.env` file:
```
GIT_USER_NAME=Your Name
GIT_USER_EMAIL=your.email@example.com
GITHUB_TOKEN=your_github_token
```

### 4. Run Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- Install Poetry if not present
- Install Python dependencies via Poetry
- Pull Ollama models
- Set up git configuration
- Create necessary directories

### 5. Start Docker Services

```bash
chmod +x scripts/docker-start.sh
./scripts/docker-start.sh
```

This will:
- Pull required Ollama models if not present
- Start backend and Ollama services in Docker
- Monitor service health

## Running the System

### Docker Deployment (Recommended)

```bash
./scripts/docker-start.sh
```

The system will:
- Start backend service (2GB RAM / 1 core)
- Start Ollama service (12GB RAM / 5 cores)
- Begin autonomous world evolution
- Commit changes following Conventional Commits

### Local Development (without Docker)

```bash
# Install dependencies
poetry install

# Activate environment
poetry shell

# Ensure Ollama is running
ollama serve

# Pull models
ollama pull qwen2.5-coder:7b
ollama pull deepseek-r1:7b

# Run backend (set PYTHONPATH so backend module resolves)
PYTHONPATH=. poetry run python backend/main.py
```

### Reset World and News

To reset world state and news feed to a blank state:

```bash
PYTHONPATH=. python -m backend.reset_world
```

## Agent Descriptions

### Planner
Single LLM call that outputs a challenge (1–2 sentences), implementation hint (entity/physics/event), and a short implementation plan. Replaces the former Product Manager + Developer planning step.

### Developer
Generates Python code from the Planner’s challenge and plan. Writes new entity classes, physics rules, or event logic. Code-only when used after Planner (no extra planning call).

### Applier
Writes the Developer’s generated code to the codebase using `CodeEvolution`: appends to `backend/world/entities.py`, `physics.py`, or `events.py` and registers new entities in `ENTITY_TYPES`. No LLM; applies code with backup and syntax validation.

### Tester
Validates world state (world.json schema, entity types) and runs basic syntax checks on generated code. No LLM.

### News Agent
Generates real-time news about world events. Outputs headline and body (validated; empty items are filtered out). Uses reasoning model (or single model when `OLLAMA_MODEL` is set).

## World Mechanics

### Alien Physics
- **Non-Euclidean gravity**: Zones with different gravitational properties
- **Dimensional warping**: Multi-dimensional coordinate systems (4D+)
- **Energy fields**: Regions with special energy properties
- **Time flow manipulation**: Areas where time flows at different rates

### Stochastic Events
- **Gravity fluctuations**: Random changes in gravitational forces
- **Energy storms**: Temporary energy field disruptions
- **Temporal distortions**: Time flow anomalies
- **Dimensional rifts**: Portals between dimensions

### Entity Behaviors
- Entities have unique update logic and visual representations
- Entities interact with physics zones and events
- Emergent behaviors from agent-defined rules

## Deployment Guide

### GitHub Pages Setup

1. Go to repository Settings → Pages
2. Select Source: `docs/` folder
3. Frontend will be accessible at: `https://nebulinx.github.io/ai-virtual-world/`

### Resource Management

- **Backend Service**: 2GB RAM / 1 core (lightweight Python code)
- **Ollama Service**: 12GB RAM / 5 cores (for 7B models - loads one at a time)
- **Host System Buffer**: 2GB RAM / 2 cores (for OS and Docker overhead)

### Model Configuration

**Default: single model** – All agents use **qwen2.5-coder:7b** (no model switching, faster cycles).

To use a different single model:

```bash
export OLLAMA_MODEL=qwen2.5:7b   # or another model name
```

To use the coder/reasoning split again (qwen coder for code, deepseek-r1 for planning/news):

```bash
export OLLAMA_MODEL=   # empty = use OLLAMA_CODER_MODEL and OLLAMA_REASONING_MODEL
```

Override defaults via env:

- `OLLAMA_MODEL` – default is qwen2.5-coder:7b; set to another model or leave empty for split
- `OLLAMA_CODER_MODEL` – code tasks when using split (default: qwen2.5-coder:7b)
- `OLLAMA_REASONING_MODEL` – planning and news when using split (default: deepseek-r1:7b)

**Note:** 7B models use several GB. With single-model default, only one model is loaded.

## 24x7 Operation

The system runs continuously with:
- **Never-ending agent loop**: LangGraph workflow cycles indefinitely
- **Continuous world evolution**: Agents modify world state and code
- **Automatic commits**: Changes committed following Conventional Commits
- **World state persistence**: History saved in `backend/data/history/`
- **Error recovery**: Resilient to failures with retry logic

## Contributing

### Submit Challenges

Submit challenges via GitHub Issues. The Planner agent may take them into account when generating new challenges.

### View World State

- **Live visualization**: https://nebulinx.github.io/ai-virtual-world/
- **World JSON**: https://raw.githubusercontent.com/nebulinx/ai-virtual-world/main/backend/data/world.json
- **News Feed**: https://raw.githubusercontent.com/nebulinx/ai-virtual-world/main/backend/data/news.json

### Understanding Autonomous Evolution

The system evolves autonomously each cycle:
1. **Planner** – one LLM call: challenge + implementation hint + plan
2. **Developer** – one LLM call: generates code from the plan
3. **Applier** – writes code to entities.py / physics.py / events.py (and registers new entity types)
4. **Tester** – validates world state and code
5. **News Agent** – one LLM call: generates news headline and body
6. World state and news are saved; git commit/push runs on an interval
7. Cycle repeats indefinitely

## Important Notes

- **Model memory:** 7B models use several GB each. Use `OLLAMA_MODEL` for a single model to avoid switch latency.
- **Frontend polling** is set to 30 seconds to respect GitHub rate limits.
- **Code evolution:** Applier uses `CodeEvolution` (backup + syntax validation); Tester validates world and code before commits.
- **Git:** Repo root is detected from the backend path. For push: set `GITHUB_TOKEN` (HTTPS) or mount `~/.ssh` (SSH) in Docker.
- **Reset:** Run `python -m backend.reset_world` to reset world.json and news.json to a blank state.

## License

MIT License - See LICENSE file for details.
