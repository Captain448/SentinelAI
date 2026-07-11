from sqlalchemy.orm import Session
from app.core.shared_memory import SharedMemory
from app.core.logger import log_agent
from app.core.constants import CAMERA_GRAPH
from app.services.learning_service import LearningService


class PredictionAgent:
    """Agent in charge of route predicting and path probability calculations."""

    def __init__(self, learning_service: LearningService):
        self.learning_service = learning_service

    def execute(self, shared_memory: SharedMemory, db: Session) -> SharedMemory:
        """Predicts the next expected camera location based on the current camera node."""
        current_cam = shared_memory.tracked_entity.last_seen_camera

        if not current_cam or current_cam not in CAMERA_GRAPH:
            # Clear or set to default if there is no adjacency mapping
            shared_memory.prediction.status = "PENDING"
            return shared_memory

        adjacency = CAMERA_GRAPH[current_cam]
        best_candidate = None
        best_prob = -1.0
        best_time = 0

        # Traverse neighbors and calculate probabilities dynamically
        for target, data in adjacency.items():
            prob = self.learning_service.calculate_transition_probability(
                db=db,
                from_camera=current_cam,
                to_camera=target,
                default_prob=data["transition_probability"]
            )
            if prob > best_prob:
                best_prob = prob
                best_candidate = target
                best_time = data["travel_time"]

        if best_candidate:
            # Update prediction states
            shared_memory.prediction.expected_next_camera = best_candidate
            shared_memory.prediction.eta_seconds = best_time
            shared_memory.prediction.confidence = best_prob
            shared_memory.prediction.status = "PENDING"

            log_agent("PredictionAgent", f"{best_candidate} predicted.")

        return shared_memory

    def handle_timeout(self, shared_memory: SharedMemory) -> SharedMemory:
        """Marks the prediction status as MISSED upon timeline expiration."""
        shared_memory.prediction.status = "MISSED"
        log_agent("PredictionAgent", "Timeout occurred.")
        return shared_memory
