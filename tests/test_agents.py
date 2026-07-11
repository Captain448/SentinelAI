import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.core.shared_memory import SharedMemory
from app.services.vision_service import VisionService
from app.services.tracking_service import TrackingService
from app.services.risk_service import RiskService
from app.services.dispatch_service import DispatchService
from app.services.learning_service import LearningService
from app.models.patrol import PatrolUnit

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_vision_service():
    service = VisionService()
    meta = {
        "entity_id": "test_entity",
        "physical_features": {
            "height": "180cm",
            "clothing_color": "Green Jacket",
            "gender_estimate": "Male",
            "movement_pattern": "Running"
        }
    }
    result = service.process_frame_metadata("Camera_A", "00:00", meta)
    assert result["entity_id"] == "test_entity"
    assert result["physical_features"]["clothing_color"] == "Green Jacket"


def test_tracking_service(db_session):
    service = TrackingService()
    features = {"height": "170cm", "clothing_color": "Black"}
    
    # First sighting
    entity = service.re_identify_entity(db_session, "entity_01", features, "Camera_A", "00:00")
    assert entity.entity_id == "entity_01"
    assert len(entity.trajectory) == 1
    assert entity.trajectory[0]["camera_id"] == "Camera_A"

    # Second sighting (different camera)
    entity = service.re_identify_entity(db_session, "entity_01", features, "Camera_B", "00:05")
    assert len(entity.trajectory) == 2
    assert entity.trajectory[1]["camera_id"] == "Camera_B"


def test_risk_service():
    service = RiskService()
    # Test case with suspicious following and missed predictions
    result = service.calculate_risk(
        flags=["suspicious_following", "disappeared_from_expected_camera"],
        camera_id="Camera_A",
        timestamp_str="12:00"
    )
    # suspicious following = 40, missed = 35 -> 75
    assert result["risk_score"] == 75.0
    assert result["severity"] == "MEDIUM"


def test_dispatch_service(db_session):
    # Pre-populate unit
    unit = PatrolUnit(patrol_id="Unit_99", location="Zone_A", availability=True)
    db_session.add(unit)
    db_session.commit()

    service = DispatchService()
    payload = service.dispatch_nearest_patrol(
        db=db_session,
        risk_score=85.0,
        severity="HIGH",
        last_known_camera="Camera_A",
        timestamp="00:30"
    )

    assert payload["nearest_patrol"] == "Unit_99"
    assert payload["risk_score"] == 85.0
    assert payload["alert_timestamp"] == "00:30"
