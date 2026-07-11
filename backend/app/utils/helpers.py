import uuid
from typing import Dict, Any


def generate_unique_id(prefix: str = "ID") -> str:
    """Generates a unique identifier string."""
    return f"{prefix}_{uuid.uuid4().hex[:8].upper()}"


def calculate_distance(pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
    """Calculates flat distance between two coordinates."""
    x1, y1 = pos1.get("x", 0.0), pos1.get("y", 0.0)
    x2, y2 = pos2.get("x", 0.0), pos2.get("y", 0.0)
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
