import datetime
from typing import Dict, Any, List
from app.core.constants import HIGH_CRIME_AREAS


class RiskService:
    """Calculates dynamically adjusted risk levels for tracked entities in the city."""

    def calculate_risk(
        self,
        flags: List[str],
        camera_id: str,
        timestamp_str: str,
        failed_reid_count: int = 0,
        missing_duration_seconds: float = 0.0
    ) -> Dict[str, Any]:
        """Calculates risk score (0-100) and maps to appropriate severity.

        Factors:
        - suspicious_follower_detected (flag) -> +40
        - missed_expected_camera (flag) -> +35
        - blind_spot_disappearance (flag) -> +20
        - high_crime_area -> +10
        - failed_reid -> +10 per occurrence
        - missing_duration -> +2 per 5 seconds missing
        - night-time multiplier -> x1.2 (applied to final score)
        """
        score = 0.0

        # Flag factors
        if "suspicious_following" in flags:
            score += 40.0
        if "disappeared_from_expected_camera" in flags:
            score += 35.0
        if "blind_spot_event" in flags:
            score += 10.0

        # Crime zone factor
        if camera_id in HIGH_CRIME_AREAS:
            score += 10.0

        # Re-id failures factor
        score += failed_reid_count * 10.0

        # Missing duration factor
        if missing_duration_seconds > 0:
            score += (missing_duration_seconds / 5.0) * 2.0

        # Night-time multiplier
        is_night = False
        try:
            # Assume time format e.g. "00:04" or "2026-07-11T00:04:00"
            # We can extract hours
            time_part = timestamp_str.split("T")[-1] if "T" in timestamp_str else timestamp_str
            hour = int(time_part.split(":")[0])
            if hour >= 20 or hour <= 6:
                is_night = True
        except Exception:
            # Fallback if parsing fails, assume day-time
            pass

        if is_night:
            score *= 1.2

        # Clamp score between 0 and 100
        score = min(max(score, 0.0), 100.0)

        # Map to severity levels
        if score >= 90:
            severity = "CRITICAL"
        elif score >= 80:
            severity = "HIGH"
        elif score >= 50:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        return {
            "risk_score": round(score, 2),
            "severity": severity,
            "flags": flags
        }
