# The Virtual World Experiment

This experiment is designed to allow AI to design a virtual world autonomously. AI agents define challenges and build the world through continuous evolution. The system defines the world's physics, gravity, time flow, and other fundamental properties. Entities, anomalies, and emergent behaviors are created and evolved by AI agents. The experiment runs 24x7 using local models (qwen2.5-coder:7b and deepSeek-r1:7b) and autonomous agents. World state is continuously updated and publicly accessible via GitHub Pages.

## Architecture Overview

- **Multi-agent system** using LangGraph for orchestration
- **5 specialized agents**: Product Manager, Developer, Refactor, Tester, News Agent
- **World engine** managing entities, physics, and events
- **Real-time 3D visualization** with Three.js
- **Autonomous code evolution** and world state generation

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
- Pull quantized Ollama models (q8_0 versions for INT8)
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
ollama pull qwen2.5-coder:7b-q8_0
ollama pull deepseek-r1:7b-q8_0

# Run backend
poetry run python backend/main.py
```

## Agent Descriptions

### Product Manager
Defines challenges and goals for world evolution. Analyzes current world state and generates new objectives for other agents to implement.

### Developer
Implements new entities, physics rules, and world features. Receives challenges and writes Python code to extend the world simulation.

### Refactor
Optimizes code and improves existing implementations. Analyzes code quality and refactors for performance and readability.

### Tester
Validates world state integrity and code correctness. Ensures world.json is valid, checks for rendering errors, and validates entity data.

### News Agent
Generates real-time news about world events. Converts world events into natural language "alien news" descriptions.

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
- **Ollama Service**: 12GB RAM / 5 cores (for quantized 7B models)
- **Host System Buffer**: 2GB RAM / 2 cores (for OS and Docker overhead)

### Model Configuration

- **qwen2.5-coder:7b-q8_0** (~8GB): Code generation tasks (Developer, Refactor agents)
- **deepseek-r1:7b-q8_0** (~8GB): Reasoning tasks (Product Manager, News Agent, Tester)

INT8 quantization reduces memory from ~14GB (FP16) to ~8GB per model with minimal quality loss.

## 24x7 Operation

The system runs continuously with:
- **Never-ending agent loop**: LangGraph workflow cycles indefinitely
- **Continuous world evolution**: Agents modify world state and code
- **Automatic commits**: Changes committed following Conventional Commits
- **World state persistence**: History saved in `backend/data/history/`
- **Error recovery**: Resilient to failures with retry logic

## Contributing

### Submit Challenges

Submit challenges via GitHub Issues. The Product Manager agent will consider them for implementation.

### View World State

- **Live visualization**: https://nebulinx.github.io/ai-virtual-world/
- **World JSON**: https://raw.githubusercontent.com/nebulinx/ai-virtual-world/main/backend/data/world.json
- **News Feed**: https://raw.githubusercontent.com/nebulinx/ai-virtual-world/main/backend/data/news.json

### Understanding Autonomous Evolution

The system evolves autonomously:
1. Product Manager generates challenges
2. Developer implements solutions
3. Refactor optimizes code
4. Tester validates changes
5. News Agent reports events
6. Cycle repeats indefinitely

## Important Notes

- **Quantized models** (q8_0) are recommended for 16GB systems
- **Frontend polling** is set to 30 seconds to respect GitHub rate limits
- **Code evolution** includes safety checks - tester agent validates before commits
- **Git authentication** required: either SSH keys or GitHub token must be configured

## License

MIT License - See LICENSE file for details.
