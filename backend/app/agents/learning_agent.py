from sqlalchemy.orm import Session
from app.core.shared_memory import SharedMemory
from app.core.logger import log_agent
from app.services.learning_service import LearningService


class LearningAgent:
    """Agent in charge of feedback optimization and tuning transition weights."""

    def __init__(self, learning_service: LearningService):
        self.learning_service = learning_service

    def execute(self, shared_memory: SharedMemory, db: Session) -> SharedMemory:
        """Evaluates prediction success/failure and updates learning weights."""
        entity = shared_memory.tracked_entity
        prediction = shared_memory.prediction

        if not entity.id or not prediction.expected_next_camera:
            return shared_memory

        # Derive the transition path (e.g. from last_seen to expected target)
        from_cam = entity.last_seen_camera
        to_cam = prediction.expected_next_camera
        transition_path = f"{from_cam}->{to_cam}"

        # If status is COMPLETED or MISSED, record outcome
        if prediction.status in ["COMPLETED", "MISSED"]:
            success = (prediction.status == "COMPLETED")
            self.learning_service.record_outcome(
                db=db,
                transition=transition_path,
                success=success
            )
            log_agent("LearningAgent", "Transition weights updated.")

        return shared_memory
