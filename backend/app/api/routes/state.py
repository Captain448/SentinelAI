from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import os
import cv2
from app.api.dependencies import get_db
from app.orchestration.workflow import coordinator
from app.models.alert import Alert
from app.models.patrol import PatrolUnit
from app.models.risk import InvestigationLog, LearningHistory, SystemAnalytics
from app.simulations.scenario_demo import run_simulation_scenario
from app.simulations.video_simulation import run_video_detection_scenario, run_video_suspicious_following_scenario

router = APIRouter(tags=["System State"])


@router.post("/simulate")
def run_simulation(scenario_type: str = "suspicious_following", db: Session = Depends(get_db)):
    """Triggers the specified SentinelAI simulation scenario."""
    # Reset coordinator state first to run clean simulation
    coordinator.state_machine.reset()

    # Clear and re-populate databases for clean run
    db.query(Alert).delete()
    db.query(InvestigationLog).delete()
    # Delete non-pre-populated patrols
    db.query(PatrolUnit).delete()

    # Prepopulate patrol units
    unit_12 = PatrolUnit(patrol_id="Unit_12", location="Zone_B", availability=True)
    unit_5 = PatrolUnit(patrol_id="Unit_5", location="Zone_C", availability=True)
    db.add_all([unit_12, unit_5])
    db.commit()

    # Run the simulation steps
    if scenario_type == "video_feed_sync":
        logs = run_video_detection_scenario(db)
    elif scenario_type == "video_feed_suspicious_following":
        logs = run_video_suspicious_following_scenario(db)
    else:
        logs = run_simulation_scenario(db, scenario_type)

    return {
        "status": "SIMULATION_COMPLETED",
        "logs": logs,
        "final_state": coordinator.state_machine.state.to_dict()
    }


@router.get("/state")
def get_current_state():
    """Returns the full centralized SharedMemory schema."""
    return coordinator.state_machine.state.to_dict()


@router.get("/state/snapshots")
def get_snapshots():
    """Returns historical state snapshots of transitions."""
    return coordinator.state_machine.get_snapshot_history()


@router.get("/state/audit")
def get_audit_logs():
    """Returns system level audit logs."""
    return coordinator.state_machine.get_audit_logs()


@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    """Fetches all dispatched alerts recorded in the database."""
    alerts = db.query(Alert).all()
    return [
        {
            "incident_id": a.incident_id,
            "severity": a.severity,
            "risk_score": a.risk_score,
            "dispatched": a.dispatched,
            "nearest_patrol": a.nearest_patrol,
            "last_known_camera": a.last_known_camera,
            "timestamp": a.alert_timestamp,
            "payload": a.payload
        }
        for a in alerts
    ]


@router.get("/risk")
def get_risk():
    """Returns risk assessment components from current state."""
    return coordinator.state_machine.state.risk_assessment.model_dump()


@router.get("/patrols")
def get_patrols(db: Session = Depends(get_db)):
    """Lists patrol units and their availability status."""
    patrols = db.query(PatrolUnit).all()
    return [
        {
            "patrol_id": p.patrol_id,
            "location": p.location,
            "availability": p.availability
        }
        for p in patrols
    ]


@router.get("/investigation")
def get_investigations(db: Session = Depends(get_db)):
    """Fetches the investigation logs of searched cameras and blind spots."""
    logs = db.query(InvestigationLog).all()
    return [
        {
            "id": l.id,
            "searched_camera": l.searched_camera,
            "timestamp": l.timestamp,
            "result": l.result
        }
        for l in logs
    ]


@router.get("/learning")
def get_learning(db: Session = Depends(get_db)):
    """Returns historical transition prediction metrics."""
    history = db.query(LearningHistory).all()
    return [
        {
            "transition": h.transition,
            "success_count": h.success_count,
            "failure_count": h.failure_count
        }
        for h in history
    ]


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """Retrieves all persisted analytics snapshots from the database."""
    records = db.query(SystemAnalytics).order_by(SystemAnalytics.id.desc()).all()
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "prediction_accuracy": r.prediction_accuracy,
            "avg_dispatch_time": r.avg_dispatch_time,
            "incidents_handled": r.incidents_handled,
            "investigation_success_rate": r.investigation_success_rate,
            "false_positives": r.false_positives,
            "patrol_utilization": r.patrol_utilization
        }
        for r in records
    ]


@router.get("/video_feed/{camera_id}")
def get_video_feed(camera_id: str):
    """Streams MJPEG frames from the specified camera MP4 file in a continuous loop."""
    video_path = f"data/cameras/{camera_id}.mp4"
    
    # Generate videos first if missing
    if not os.path.exists(video_path):
        from app.simulations.generate_dummy_videos import generate_all_videos
        generate_all_videos()
        
    def gen_frames():
        cap = cv2.VideoCapture(video_path)
        while True:
            success, frame = cap.read()
            if not success:
                # Restart from first frame for looping video feed
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
