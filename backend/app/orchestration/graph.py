from typing import TypedDict, Dict, Any
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END

# Import shared models and agent classes
from app.core.shared_memory import SharedMemory
from app.agents.vision_agent import VisionAgent
from app.agents.tracking_agent import TrackingAgent
from app.agents.prediction_agent import PredictionAgent
from app.agents.investigation_agent import InvestigationAgent
from app.agents.risk_agent import RiskAgent
from app.agents.dispatch_agent import DispatchAgent
from app.agents.learning_agent import LearningAgent

# Import services
from app.services.vision_service import VisionService
from app.services.tracking_service import TrackingService
from app.services.risk_service import RiskService
from app.services.dispatch_service import DispatchService
from app.services.learning_service import LearningService


# Define the state schema for LangGraph
class AgentState(TypedDict):
    shared_memory: SharedMemory
    camera_id: str
    timestamp: str
    metadata: Dict[str, Any]
    db: Session
    event_type: str  # "sighting" or "timeout"


# Initialize services
vision_service = VisionService()
tracking_service = TrackingService()
risk_service = RiskService()
dispatch_service = DispatchService()
learning_service = LearningService()

# Initialize Agents
vision_agent = VisionAgent(vision_service)
tracking_agent = TrackingAgent(tracking_service)
prediction_agent = PredictionAgent(learning_service)
investigation_agent = InvestigationAgent()
risk_agent = RiskAgent(risk_service)
dispatch_agent = DispatchAgent(dispatch_service)
learning_agent = LearningAgent(learning_service)


# Define nodes
def vision_node(state: AgentState) -> AgentState:
    state["shared_memory"] = vision_agent.execute(
        shared_memory=state["shared_memory"],
        camera_id=state["camera_id"],
        timestamp=state["timestamp"],
        metadata=state["metadata"]
    )
    return state


def tracking_node(state: AgentState) -> AgentState:
    state["shared_memory"] = tracking_agent.execute(
        shared_memory=state["shared_memory"],
        db=state["db"]
    )
    return state


def prediction_node(state: AgentState) -> AgentState:
    state["shared_memory"] = prediction_agent.execute(
        shared_memory=state["shared_memory"],
        db=state["db"]
    )
    return state


def prediction_timeout_node(state: AgentState) -> AgentState:
    state["shared_memory"] = prediction_agent.handle_timeout(
        shared_memory=state["shared_memory"]
    )
    return state


def investigation_node(state: AgentState) -> AgentState:
    state["shared_memory"] = investigation_agent.execute(
        shared_memory=state["shared_memory"],
        db=state["db"]
    )
    return state


def risk_node(state: AgentState) -> AgentState:
    state["shared_memory"] = risk_agent.execute(
        shared_memory=state["shared_memory"]
    )
    return state


def dispatch_node(state: AgentState) -> AgentState:
    state["shared_memory"] = dispatch_agent.execute(
        shared_memory=state["shared_memory"],
        db=state["db"]
    )
    return state


def learning_node(state: AgentState) -> AgentState:
    state["shared_memory"] = learning_agent.execute(
        shared_memory=state["shared_memory"],
        db=state["db"]
    )
    return state


# Entry node to route events
def entry_node(state: AgentState) -> AgentState:
    return state

# Build the StateGraph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("entry", entry_node)
workflow.add_node("vision", vision_node)
workflow.add_node("tracking", tracking_node)
workflow.add_node("prediction", prediction_node)
workflow.add_node("prediction_timeout", prediction_timeout_node)
workflow.add_node("investigation", investigation_node)
workflow.add_node("risk", risk_node)
workflow.add_node("dispatch", dispatch_node)
workflow.add_node("learning", learning_node)

# Set entry point
workflow.set_entry_point("entry")

# Route event types from entry
def route_entry(state: AgentState) -> str:
    et = state.get("event_type")
    if et == "timeout":
        return "prediction_timeout"
    elif et == "investigation":
        return "investigation"
    elif et == "risk":
        return "risk"
    elif et == "dispatch":
        return "dispatch"
    elif et == "learning":
        return "learning"
    return "vision"

workflow.add_conditional_edges(
    "entry",
    route_entry,
    {
        "vision": "vision",
        "prediction_timeout": "prediction_timeout",
        "investigation": "investigation",
        "risk": "risk",
        "dispatch": "dispatch",
        "learning": "learning"
    }
)

# Define regular edges
workflow.add_edge("vision", "tracking")
workflow.add_edge("tracking", "prediction")
workflow.add_edge("prediction", END)
workflow.add_edge("prediction_timeout", END)
workflow.add_edge("investigation", END)
workflow.add_edge("risk", END)
workflow.add_edge("dispatch", END)
workflow.add_edge("learning", END)

# Compile LangGraph app
app_graph = workflow.compile()
