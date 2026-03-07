"""LangGraph state machine for agent orchestration."""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from backend.agents.product_manager import ProductManagerAgent
from backend.agents.developer import DeveloperAgent
from backend.agents.refactor import RefactorAgent
from backend.agents.tester import TesterAgent
from backend.agents.news_agent import NewsAgent
from backend.ai.ollama_client import OllamaClient
from backend.world.world_engine import WorldEngine


class AgentState(TypedDict):
    """State schema for agent workflow."""
    world_state: dict
    challenges: list
    code_changes: list
    news_items: list
    agent_results: dict
    current_agent: str


class AgentWorkflow:
    """LangGraph workflow for multi-agent orchestration."""
    
    def __init__(self, world_engine: WorldEngine, ollama_client: OllamaClient):
        self.world_engine = world_engine
        self.ollama = ollama_client
        
        # Initialize agents
        self.product_manager = ProductManagerAgent(ollama_client)
        self.developer = DeveloperAgent(ollama_client)
        self.refactor = RefactorAgent(ollama_client)
        self.tester = TesterAgent(ollama_client)
        self.news_agent = NewsAgent(ollama_client)
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph state machine."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("product_manager", self._product_manager_node)
        workflow.add_node("developer", self._developer_node)
        workflow.add_node("refactor", self._refactor_node)
        workflow.add_node("tester", self._tester_node)
        workflow.add_node("news_agent", self._news_agent_node)
        
        # Set entry point
        workflow.set_entry_point("product_manager")
        
        # Add edges
        workflow.add_edge("product_manager", "developer")
        workflow.add_edge("developer", "refactor")
        workflow.add_edge("refactor", "tester")
        workflow.add_edge("tester", "news_agent")
        workflow.add_edge("news_agent", END)
        
        return workflow.compile()
    
    def _product_manager_node(self, state: AgentState) -> AgentState:
        """Product Manager agent node."""
        context = {
            "world_state": state.get("world_state", self.world_engine.get_world_state())
        }
        result = self.product_manager.execute(context)
        state["challenges"] = state.get("challenges", []) + [result.get("challenge", "")]
        state["agent_results"] = state.get("agent_results", {})
        state["agent_results"]["product_manager"] = result
        state["current_agent"] = "product_manager"
        return state
    
    def _developer_node(self, state: AgentState) -> AgentState:
        """Developer agent node."""
        context = {
            "world_state": state.get("world_state", self.world_engine.get_world_state()),
            "challenge": state.get("challenges", [""])[-1] if state.get("challenges") else ""
        }
        result = self.developer.execute(context)
        state["code_changes"] = state.get("code_changes", []) + [result]
        state["agent_results"] = state.get("agent_results", {})
        state["agent_results"]["developer"] = result
        state["current_agent"] = "developer"
        return state
    
    def _refactor_node(self, state: AgentState) -> AgentState:
        """Refactor agent node."""
        context = {
            "world_state": state.get("world_state", self.world_engine.get_world_state()),
            "code_changes": state.get("code_changes", [])
        }
        result = self.refactor.execute(context)
        state["agent_results"] = state.get("agent_results", {})
        state["agent_results"]["refactor"] = result
        state["current_agent"] = "refactor"
        return state
    
    def _tester_node(self, state: AgentState) -> AgentState:
        """Tester agent node."""
        context = {
            "world_state": state.get("world_state", self.world_engine.get_world_state()),
            "code_changes": state.get("code_changes", [])
        }
        result = self.tester.execute(context)
        state["agent_results"] = state.get("agent_results", {})
        state["agent_results"]["tester"] = result
        state["current_agent"] = "tester"
        return state
    
    def _news_agent_node(self, state: AgentState) -> AgentState:
        """News agent node."""
        context = {
            "world_state": state.get("world_state", self.world_engine.get_world_state())
        }
        result = self.news_agent.execute(context)
        state["news_items"] = state.get("news_items", []) + result.get("news_items", [])
        state["agent_results"] = state.get("agent_results", {})
        state["agent_results"]["news_agent"] = result
        state["current_agent"] = "news_agent"
        return state
    
    def run_cycle(self) -> AgentState:
        """Run one complete agent cycle."""
        initial_state: AgentState = {
            "world_state": self.world_engine.get_world_state(),
            "challenges": [],
            "code_changes": [],
            "news_items": [],
            "agent_results": {},
            "current_agent": ""
        }
        
        final_state = self.graph.invoke(initial_state)
        return final_state
