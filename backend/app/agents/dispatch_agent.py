from sqlalchemy.orm import Session
from app.core.shared_memory import SharedMemory
from app.core.logger import log_agent
from app.services.dispatch_service import DispatchService


class DispatchAgent:
    """Agent in charge of matching emergency response teams and transmitting alerts."""

    def __init__(self, dispatch_service: DispatchService):
        self.dispatch_service = dispatch_service

    def execute(self, shared_memory: SharedMemory, db: Session) -> SharedMemory:
        """Triggers incident dispatch workflows if the risk threshold is crossed."""
        risk = shared_memory.risk_assessment
        dispatch = shared_memory.dispatch_status
        entity = shared_memory.tracked_entity

        # Dispatch threshold is 80
        if risk.risk_score >= 80 and not dispatch.alert_sent:
            payload = self.dispatch_service.dispatch_nearest_patrol(
                db=db,
                risk_score=risk.risk_score,
                severity=risk.severity,
                last_known_camera=entity.last_seen_camera,
                timestamp=entity.timestamp
            )

            if payload:
                dispatch.patrol_unit_assigned = payload["nearest_patrol"]
                dispatch.eta_to_scene = int(payload["eta_minutes"] * 60)  # minutes to seconds
                dispatch.alert_sent = True

                log_agent("DispatchAgent", f"Patrol {dispatch.patrol_unit_assigned} alerted.")

        return shared_memory
