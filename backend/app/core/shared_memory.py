from typing import List, Optional
from pydantic import BaseModel, Field


class PhysicalFeatures(BaseModel):
    height: str = ""
    clothing_color: str = ""
    gender_estimate: str = ""
    movement_pattern: str = ""


class TrackedEntity(BaseModel):
    id: str = ""
    physical_features: PhysicalFeatures = Field(default_factory=PhysicalFeatures)
    last_seen_camera: str = ""
    timestamp: str = ""


class PredictionState(BaseModel):
    expected_next_camera: str = ""
    eta_seconds: int = 0
    confidence: float = 0.0
    status: str = "PENDING"  # PENDING, COMPLETED, MISSED


class InvestigationState(BaseModel):
    scanned_cameras: List[str] = Field(default_factory=list)
    blind_spots_checked: List[str] = Field(default_factory=list)
    sighting_found: bool = False


class RiskAssessment(BaseModel):
    risk_score: float = 0.0
    severity: str = ""  # LOW, MEDIUM, HIGH, CRITICAL
    flags: List[str] = Field(default_factory=list)


class DispatchStatus(BaseModel):
    patrol_unit_assigned: str = ""
    eta_to_scene: int = 0
    alert_sent: bool = False


class SharedMemory(BaseModel):
    tracked_entity: TrackedEntity = Field(default_factory=TrackedEntity)
    prediction: PredictionState = Field(default_factory=PredictionState)
    investigation: InvestigationState = Field(default_factory=InvestigationState)
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment)
    dispatch_status: DispatchStatus = Field(default_factory=DispatchStatus)

    def to_dict(self) -> dict:
        return self.model_dump()
