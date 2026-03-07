"""Main entry point for AI Virtual World system."""

import time
import signal
import sys
from datetime import datetime
from backend.config import AGENT_LOOP_INTERVAL, COMMIT_INTERVAL
from backend.world.world_engine import WorldEngine
from backend.world.events import EventGenerator
from backend.ai.ollama_client import OllamaClient
from backend.workflow.agent_graph import AgentWorkflow
from backend.utils.git_utils import GitUtils


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
                
                # Update world state
                self.world_engine.save_world()
                
                # Commit periodically
                current_time = time.time()
                if current_time - self.last_commit_time >= COMMIT_INTERVAL:
                    print("Committing changes...")
                    success, message = self.git_utils.commit_and_push()
                    if success:
                        print(f"✓ {message}")
                        self.last_commit_time = current_time
                    else:
                        print(f"✗ Commit failed: {message}")
                
                print(f"Cycle {cycle_count} completed. Waiting {AGENT_LOOP_INTERVAL}s...")
                time.sleep(AGENT_LOOP_INTERVAL)
            
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                self.running = False
                break
            except Exception as e:
                print(f"Error in cycle {cycle_count}: {e}")
                import traceback
                traceback.print_exc()
                print("Continuing after error...")
                time.sleep(AGENT_LOOP_INTERVAL)
        
        print("\n" + "=" * 60)
        print("AI Virtual World - Shutting down")
        print("=" * 60)


if __name__ == "__main__":
    system = VirtualWorldSystem()
    system.run()
