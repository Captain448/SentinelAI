import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.shared_memory import SharedMemory
from app.core.state_machine import StateMachine
from app.core.constants import TIMEOUT_GRACE_PERIOD
from app.orchestration.graph import app_graph, AgentState
from app.core.logger import logger


class WorkflowCoordinator:
    """Manages overall event coordination, time tracking, state snapshots, and agent graphs."""

    def __init__(self):
        self.state_machine = StateMachine()
        self.event_listeners: List[Any] = []

    def handle_sighting(
        self,
        db: Session,
        camera_id: str,
        timestamp: str,
        metadata: Dict[str, Any]
    ) -> SharedMemory:
        """Processes a sighting event (CCTV metadata packet) through the multi-agent graph."""
        shared_memory = self.state_machine.state

        # Check if this is the expected next camera (prediction success)
        prediction = shared_memory.prediction
        if prediction.status == "PENDING" and prediction.expected_next_camera == camera_id:
            # Mark prediction status as COMPLETED
            prediction.status = "COMPLETED"
            logger.info(f"[Workflow] Entity appeared at expected {camera_id}. Prediction COMPLETED.")

        # Construct AgentState input for LangGraph
        inputs: AgentState = {
            "shared_memory": shared_memory,
            "camera_id": camera_id,
            "timestamp": timestamp,
            "metadata": metadata,
            "db": db,
            "event_type": "sighting"
        }

        # Run LangGraph pipeline
        result = app_graph.invoke(inputs)

        # Sync result back to central state machine
        self.state_machine.state = result["shared_memory"]
        self.state_machine.create_snapshot(f"Sighting at {camera_id}")

        return self.state_machine.state

    def check_for_timeouts(self, db: Session, current_time_str: str) -> None:
        """Checks if expected entity arrival time has expired and executes alert flows."""
        shared_memory = self.state_machine.state
        prediction = shared_memory.prediction

        if prediction.status != "PENDING":
            return

        entity = shared_memory.tracked_entity
        if not entity.timestamp:
            return

        # Calculate time elapsed since last seen
        try:
            # Parse timestamps
            last_time_part = ":".join(entity.timestamp.split("T")[-1].split(":")[:2])
            curr_time_part = ":".join(current_time_str.split("T")[-1].split(":")[:2])
            fmt = "%H:%M"
            t_last = datetime.datetime.strptime(last_time_part, fmt)
            t_curr = datetime.datetime.strptime(curr_time_part, fmt)

            elapsed_seconds = (t_curr - t_last).total_seconds()
            timeout_threshold = prediction.eta_seconds + TIMEOUT_GRACE_PERIOD

            if elapsed_seconds >= timeout_threshold:
                # Mark as MISSED and run investigation flow via LangGraph
                logger.warning(
                    f"[Workflow] Timeout occurred. Elapsed: {elapsed_seconds}s, "
                    f"Threshold: {timeout_threshold}s (ETA: {prediction.eta_seconds}s + Grace: {TIMEOUT_GRACE_PERIOD}s)"
                )

                inputs: AgentState = {
                    "shared_memory": shared_memory,
                    "camera_id": entity.last_seen_camera,
                    "timestamp": current_time_str,
                    "metadata": {},
                    "db": db,
                    "event_type": "timeout"
                }

                # Start the LangGraph workflow directly from prediction_timeout node
                # For this, we compile and invoke from prediction_timeout node onwards.
                # Since app_graph compiled the whole flow, we can invoke it with PENDING set to MISSED
                # which will trigger conditional edges or we manually change status and run graph nodes.
                # In graph.py, prediction_timeout node handles the timeout.
                # We can call the compiled graph directly. If we set state to MISSED beforehand,
                # the routing in the graph can execute the remaining agents.
                shared_memory.prediction.status = "MISSED"

                # Invoke the graph starting with the updated state
                result = app_graph.invoke(inputs)

                # Sync state back to state machine
                self.state_machine.state = result["shared_memory"]
                self.state_machine.create_snapshot("Prediction Timeout Fired")

        except Exception as e:
            logger.error(f"[Workflow] Error parsing timestamp for timeout checks: {e}")


# Initialize central coordinator instance
coordinator = WorkflowCoordinator()
