from sqlalchemy.orm import Session
from app.core.shared_memory import SharedMemory
from app.core.logger import log_agent
from app.core.constants import CAMERA_GRAPH
from app.models.risk import InvestigationLog


class InvestigationAgent:
    """Agent in charge of scanning secondary network cameras and blind spots on miss detection."""

    def execute(self, shared_memory: SharedMemory, db: Session) -> SharedMemory:
        """Triggered when predictions are missed.

        Initiates a sweep across connected nodes.
        """
        expected_cam = shared_memory.prediction.expected_next_camera

        if not expected_cam:
            return shared_memory

        log_agent("InvestigationAgent", "Blind spot search started.")

        scanned = [expected_cam]
        blind_spots = []

        # Find connected camera nodes and blind spots (up to 2 hops for expanded radius)
        queue = [expected_cam]
        visited = {expected_cam}
        
        for _ in range(2):
            next_queue = []
            for node in queue:
                if node in CAMERA_GRAPH:
                    for neighbor in CAMERA_GRAPH[node].keys():
                        if neighbor not in visited:
                            visited.add(neighbor)
                            next_queue.append(neighbor)
                            if "Blind_Spot" in neighbor:
                                blind_spots.append(neighbor)
                            else:
                                scanned.append(neighbor)
            queue = next_queue

        # Update SharedMemory
        shared_memory.investigation.scanned_cameras = scanned
        shared_memory.investigation.blind_spots_checked = blind_spots
        shared_memory.investigation.sighting_found = False

        # Record logs in Database
        timestamp = shared_memory.tracked_entity.timestamp
        for cam in scanned:
            log_entry = InvestigationLog(
                searched_camera=cam,
                timestamp=timestamp,
                result="EMPTY"
            )
            db.add(log_entry)

        for bs in blind_spots:
            log_entry = InvestigationLog(
                searched_camera=bs,
                timestamp=timestamp,
                result="EMPTY"
            )
            db.add(log_entry)

        db.commit()
        return shared_memory
