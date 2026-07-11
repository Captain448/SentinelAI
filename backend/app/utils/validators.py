from typing import Dict, Any, List


def validate_camera_metadata(data: Dict[str, Any]) -> bool:
    """Validates structure of incoming CCTV metadata payload."""
    required = ["camera_id", "timestamp"]
    for req in required:
        if req not in data:
            return False
    return True


def validate_risk_profile(risk_score: float, severity: str) -> bool:
    """Validates risk outputs against ranges."""
    if not (0.0 <= risk_score <= 100.0):
        return False
    valid_severities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    if severity not in valid_severities:
        return False
    return True
