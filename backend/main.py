"""Main entry point for AI Virtual World system."""

import json
import time
import signal
from pathlib import Path
from datetime import datetime, timezone
from backend.config import AGENT_LOOP_INTERVAL, COMMIT_INTERVAL, COMMIT_EVERY_CYCLE, DIRECTION_JSON_PATH
from backend.world.world_engine import WorldEngine
from backend.world.events import EventGenerator
from backend.world.schemas import validate_direction_json
from backend.ai.ollama_client import OllamaClient
from backend.workflow.agent_graph import AgentWorkflow
from backend.utils.git_utils import GitUtils

DIRECTION_HISTORY_CAP = 10


class VirtualWorldSystem:
    """Main system orchestrator."""
    
    def __init__(self):
        self.world_engine = WorldEngine()
        self.ollama = OllamaClient()
        self.workflow = AgentWorkflow(self.world_engine, self.ollama)
        self.git_utils = GitUtils()
        self.event_generator = EventGenerator(self.world_engine.get_world_state())
        self.running = True
        self.last_commit_time = time.time()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.running = False

    def _save_direction(self, final_state: dict) -> None:
        """Write planner output to direction.json for the Direction tab."""
        planner_result = (final_state.get("agent_results") or {}).get("planner") or {}
        challenge = (planner_result.get("challenge") or "").strip()
        plan = (planner_result.get("plan") or "").strip()
        impl_hint = (planner_result.get("implementation_hint") or "general").strip()
        summary = (planner_result.get("summary") or "").strip() or challenge.split(".")[0].strip() + "." if challenge else ""
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = {
            "timestamp": timestamp,
            "challenge": challenge or "No challenge recorded.",
            "plan": plan or "-",
            "implementation_hint": impl_hint,
            "summary": summary,
        }
        path = Path(DIRECTION_JSON_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"latest": None, "history": []}
        if path.exists():
            try:
                with open(path, "r") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        if data.get("latest"):
            data["history"] = (data.get("history") or []) + [data["latest"]]
        data["history"] = (data.get("history") or [])[-DIRECTION_HISTORY_CAP:]
        data["latest"] = entry
        if validate_direction_json(data):
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
    
    def run(self):
        """Run the never-ending agent loop."""
        print("=" * 60)
        print("AI Virtual World - Starting autonomous evolution")
        print("=" * 60)
        print(f"World state: {self.world_engine.world_path}")
        print(f"Ollama host: {self.ollama.base_url}")
        print(f"Agent loop interval: {AGENT_LOOP_INTERVAL}s")
        print(f"Commit interval: {COMMIT_INTERVAL}s")
        print("=" * 60)
        
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Cycle {cycle_count}")
                print("-" * 60)
                
                # Generate random events
                if cycle_count % 5 == 0:  # Every 5 cycles
                    event = self.event_generator.generate_event()
                    if event:
                        self.event_generator.apply_event_to_world(event, self.world_engine)
                        print(f"Event generated: {event.get('type', 'unknown')}")
                
                # Run agent workflow
                print("Running agent workflow...")
                final_state = self.workflow.run_cycle()
                
                # Persist planner direction for frontend
                self._save_direction(final_state)
                
                # Optional world tick: run entity updates so world state changes between cycles
                self.world_engine.run_entity_tick()
                
                # Spawn one instance when Applier added a new entity type
                applier_result = (final_state.get("agent_results") or {}).get("applier") or {}
                new_entity_type = applier_result.get("new_entity_type")
                if new_entity_type:
                    try:
                        from backend.world.entities import create_entity
                        import random
                        pos = {"x": random.uniform(-30, 30), "y": random.uniform(-30, 30), "z": random.uniform(-30, 30), "w": random.uniform(-5, 5)}
                        entity = create_entity(new_entity_type, f"entity_{len(self.world_engine.world_state['entities'])}", pos)
                        self.world_engine.add_entity(entity.to_dict())
                        print(f"Spawned new entity type: {new_entity_type}")
                    except Exception as e:
                        print(f"Could not spawn {new_entity_type}: {e}")
                
                # Per-cycle evolution log so every commit has a real world change (not just timestamp)
                summary = (final_state.get("agent_results") or {}).get("planner", {}).get("summary", "").strip()
                self.world_engine.append_evolution_entry(cycle_count, summary or f"Cycle {cycle_count}")
                self.world_engine.save_world()
                
                # Commit: every cycle (with Planner summary) or on interval
                current_time = time.time()
                commit_message = None
                if COMMIT_EVERY_CYCLE:
                    summary = (final_state.get("agent_results") or {}).get("planner", {}).get("summary", "").strip()
                    commit_message = f"feat(world): {summary}" if summary else None
                do_commit = COMMIT_EVERY_CYCLE or (current_time - self.last_commit_time >= COMMIT_INTERVAL)
                if do_commit:
                    print("Committing changes...")
                    success, message = self.git_utils.commit_and_push(commit_message)
                    if success:
                        print(f"✓ {message}")
                        self.last_commit_time = current_time
                    else:
                        print(f"✗ Commit/push failed: {message}")
                        print("  (In Docker: set GITHUB_TOKEN for HTTPS push, or mount ~/.ssh for SSH.)")
                
                if AGENT_LOOP_INTERVAL > 0:
                    print(f"Cycle {cycle_count} completed. Waiting {AGENT_LOOP_INTERVAL}s...")
                    time.sleep(AGENT_LOOP_INTERVAL)
                else:
                    print(f"Cycle {cycle_count} completed.")
            
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                self.running = False
                break
            except Exception as e:
                print(f"Error in cycle {cycle_count}: {e}")
                import traceback
                traceback.print_exc()
                print("Continuing after error...")
                if AGENT_LOOP_INTERVAL > 0:
                    time.sleep(AGENT_LOOP_INTERVAL)
        
        print("\n" + "=" * 60)
        print("AI Virtual World - Shutting down")
        print("=" * 60)


if __name__ == "__main__":
    system = VirtualWorldSystem()
    system.run()
