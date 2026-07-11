from app.core.shared_memory import SharedMemory
from app.core.logger import log_agent
from app.services.risk_service import RiskService


class RiskAgent:
    """Agent in charge of evaluating behavioral and environmental hazard flags to output a risk score."""

    def __init__(self, risk_service: RiskService):
        self.risk_service = risk_service

    def execute(self, shared_memory: SharedMemory) -> SharedMemory:
        """Determines flags, evaluates multipliers, and commits risk assessment."""
        entity = shared_memory.tracked_entity
        prediction = shared_memory.prediction
        investigation = shared_memory.investigation
        risk = shared_memory.risk_assessment

        # Gather dynamic flags from state
        flags = list(risk.flags)

        if prediction.status == "MISSED" and "disappeared_from_expected_camera" not in flags:
            flags.append("disappeared_from_expected_camera")

        if len(investigation.blind_spots_checked) > 0 and "blind_spot_event" not in flags:
            flags.append("blind_spot_event")

        # Run risk calculations
        result = self.risk_service.calculate_risk(
            flags=flags,
            camera_id=entity.last_seen_camera,
            timestamp_str=entity.timestamp
        )

        # Update SharedMemory
        risk.risk_score = result["risk_score"]
        risk.severity = result["severity"]
        risk.flags = result["flags"]

        log_agent("RiskAgent", f"Risk score updated to {int(risk.risk_score)}.")

        return shared_memory
