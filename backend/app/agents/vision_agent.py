from typing import Dict, Any
from app.core.shared_memory import SharedMemory
from app.core.logger import log_agent
from app.services.vision_service import VisionService


class VisionAgent:
    """Agent in charge of processing incoming raw CCTV metadata feeds.

    Resolves features and publishes descriptors to shared memory.
    """

    def __init__(self, vision_service: VisionService):
        self.vision_service = vision_service

    def execute(self, shared_memory: SharedMemory, camera_id: str, timestamp: str, metadata: Dict[str, Any]) -> SharedMemory:
        """Parses camera event metadata, extracts descriptors, and initializes state."""
        processed = self.vision_service.process_frame_metadata(
            camera_id=camera_id,
            timestamp=timestamp,
            detected_entity_meta=metadata
        )

        if processed:
            # Update entity information in shared memory
            shared_memory.tracked_entity.id = processed["entity_id"]
            shared_memory.tracked_entity.last_seen_camera = processed["camera_id"]
            shared_memory.tracked_entity.timestamp = processed["timestamp"]

            features = processed["physical_features"]
            shared_memory.tracked_entity.physical_features.height = features["height"]
            shared_memory.tracked_entity.physical_features.clothing_color = features["clothing_color"]
            shared_memory.tracked_entity.physical_features.gender_estimate = features["gender_estimate"]
            shared_memory.tracked_entity.physical_features.movement_pattern = features["movement_pattern"]

            log_agent("VisionAgent", "Entity detected.")

        return shared_memory
