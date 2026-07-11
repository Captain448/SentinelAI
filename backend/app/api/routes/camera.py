from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.api.dependencies import get_db
from app.orchestration.workflow import coordinator
from app.utils.validators import validate_camera_metadata
from app.models.patrol import PatrolUnit

router = APIRouter(prefix="/camera-feed", tags=["Camera Feed"])


class CameraEvent(BaseModel):
    camera_id: str
    timestamp: str
    metadata: Dict[str, Any] = {}


@router.post("")
def receive_camera_feed(event: CameraEvent, db: Session = Depends(get_db)):
    """Receives CCTV feed frame metadata and processes it through the safety network."""
    event_dict = event.model_dump()
    if not validate_camera_metadata(event_dict):
        raise HTTPException(status_code=400, detail="Invalid camera metadata.")

    # Process sighting through the multi-agent graph
    updated_state = coordinator.handle_sighting(
        db=db,
        camera_id=event.camera_id,
        timestamp=event.timestamp,
        metadata=event.metadata
    )

    return {
        "status": "PROCESSED",
        "state": updated_state.to_dict()
    }


@router.post("/check-timeouts")
def trigger_timeout_check(timestamp: str, db: Session = Depends(get_db)):
    """Manually checks for elapsed prediction timeouts at the specified timestamp."""
    coordinator.check_for_timeouts(db, timestamp)
    return {
        "status": "CHECKED",
        "state": coordinator.state_machine.state.to_dict()
    }
