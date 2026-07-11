from sqlalchemy.orm import Session
from app.core.shared_memory import SharedMemory
from app.core.logger import log_agent
from app.services.tracking_service import TrackingService


class TrackingAgent:
    """Agent in charge of maintaining continuous entity histories and resolving trajectories."""

    def __init__(self, tracking_service: TrackingService):
        self.tracking_service = tracking_service

    def execute(self, shared_memory: SharedMemory, db: Session) -> SharedMemory:
        """Looks up historical identifiers, writes trajectory path and updates database."""
        entity = shared_memory.tracked_entity

        if entity.id:
            # Re-identify and commit trajectory updates to database
            self.tracking_service.re_identify_entity(
                db=db,
                entity_id=entity.id,
                features=entity.physical_features.model_dump(),
                camera_id=entity.last_seen_camera,
                timestamp=entity.timestamp
            )
            log_agent("TrackingAgent", "Entity trajectory updated.")

        return shared_memory
