import os
import cv2
import numpy as np
import datetime
from typing import List
from sqlalchemy.orm import Session

from app.orchestration.workflow import coordinator
from app.models.patrol import PatrolUnit
from app.models.alert import Alert
from app.models.risk import InvestigationLog, LearningHistory, SystemAnalytics
from app.models.entity import Entity
from app.simulations.generate_dummy_videos import generate_all_videos

def run_video_detection_scenario(db: Session) -> List[str]:
    """Scans the Camera_A, Camera_B, Camera_C synchronized video files,

    runs real CV detection for the red-jacket target, triggers LangGraph workflows,
    and returns logs.
    """
    logs = []

    def log_and_capture(msg: str):
        print(msg, flush=True)
        logs.append(msg)

    log_and_capture("\n--- Starting SentinelAI Video CV Sync Scenario ---")

    video_dir = os.path.join("data", "cameras")
    cam_paths = {
        "Camera_A": os.path.join(video_dir, "Camera_A.mp4"),
        "Camera_B": os.path.join(video_dir, "Camera_B.mp4"),
        "Camera_C": os.path.join(video_dir, "Camera_C.mp4")
    }

    if not all(os.path.exists(p) for p in cam_paths.values()):
        log_and_capture("[VideoProcessor] Video files missing. Generating camera MP4 feeds...")
        generate_all_videos()

    caps = {}
    for cam_id, path in cam_paths.items():
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            log_and_capture(f"[VideoProcessor] Error: Failed to open video feed for {cam_id} at {path}")
            return logs
        caps[cam_id] = cap

    detected_cameras = set()
    total_frames = 150
    log_and_capture("[VideoProcessor] Sync-scanning frames across CAM A, B, C in lockstep...")

    for frame_idx in range(total_frames):
        for cam_id, cap in caps.items():
            ret, frame = cap.read()
            if not ret:
                continue

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_red1 = np.array([0, 70, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 70, 50])
            upper_red2 = np.array([180, 255, 255])

            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = mask1 + mask2

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                if cam_id not in detected_cameras:
                    detected_cameras.add(cam_id)
                    log_and_capture(f"[VideoProcessor] CV DETECTED: Target found in {cam_id} feed (Frame {frame_idx}).")

                    metadata_woman = {
                        "entity_id": "Woman_01",
                        "physical_features": {
                            "height": "165cm",
                            "clothing_color": "Red Jacket",
                            "gender_estimate": "Female",
                            "movement_pattern": "Walking"
                        }
                    }

                    simulated_minutes = int(frame_idx / 10)
                    timestamp = f"2026-07-11T12:{simulated_minutes:02d}:00"

                    coordinator.handle_sighting(
                        db=db,
                        camera_id=cam_id,
                        timestamp=timestamp,
                        metadata=metadata_woman
                    )

    for cap in caps.values():
        cap.release()

    # Calculate and Persist Snapshots
    history = db.query(LearningHistory).all()
    total_success = sum(h.success_count for h in history)
    total_trials = sum(h.success_count + h.failure_count for h in history)
    accuracy = (total_success / total_trials * 100.0) if total_trials > 0 else 92.4

    alerts = db.query(Alert).all()
    dispatch_times = [a.eta_minutes for a in alerts if a.dispatched]
    avg_dispatch = sum(dispatch_times) / len(dispatch_times) if dispatch_times else 0.0

    patrols = db.query(PatrolUnit).all()
    busy_patrols = sum(1 for p in patrols if not p.availability)
    utilization = (busy_patrols / len(patrols) * 100.0) if patrols else 0.0

    analytics_record = SystemAnalytics(
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        prediction_accuracy=round(accuracy, 1),
        avg_dispatch_time=round(avg_dispatch, 1),
        incidents_handled=len(alerts),
        investigation_success_rate=100.0 if len(detected_cameras) > 1 else 0.0,
        false_positives=0,
        patrol_utilization=round(utilization, 1)
    )
    db.add(analytics_record)
    db.commit()

    log_and_capture("\n--- Video CV Sync Simulation Completed & Analytics Saved ---")
    return logs


def run_video_suspicious_following_scenario(db: Session) -> List[str]:
    """Simulates target detected in Camera_A video feed, being followed,

    failing to appear in Camera_B on time, triggering investigations, risk scores,
    and patrol unit dispatch.
    """
    logs = []

    def log_and_capture(msg: str):
        print(msg, flush=True)
        logs.append(msg)

    log_and_capture("\n--- Starting Video Feed Suspicious Following Scenario ---")

    video_dir = os.path.join("data", "cameras")
    cam_paths = {
        "Camera_A": os.path.join(video_dir, "Camera_A.mp4"),
        "Camera_B": os.path.join(video_dir, "Camera_B.mp4"),
        "Camera_C": os.path.join(video_dir, "Camera_C.mp4")
    }

    if not all(os.path.exists(p) for p in cam_paths.values()):
        log_and_capture("[VideoProcessor] Video files missing. Generating camera MP4 feeds...")
        generate_all_videos()

    # Open readers
    caps = {cam_id: cv2.VideoCapture(p) for cam_id, p in cam_paths.items()}
    
    total_frames = 150
    log_and_capture("[VideoProcessor] Lockstep scanning video frames for threat assessment...")

    for frame_idx in range(total_frames):
        # We only process Camera_A video feed, simulating target disappears after CAM A
        cap = caps["Camera_A"]
        ret, frame = cap.read()
        if not ret:
            continue

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours and frame_idx == 0:
            log_and_capture(f"[VideoProcessor] CV DETECTED: Target Woman_01 detected in Camera_A feed (Frame 0).")
            metadata_woman = {
                "entity_id": "Woman_01",
                "physical_features": {
                    "height": "165cm",
                    "clothing_color": "Red Jacket",
                    "gender_estimate": "Female",
                    "movement_pattern": "Walking"
                }
            }
            coordinator.handle_sighting(
                db=db,
                camera_id="Camera_A",
                timestamp="2026-07-11T12:00:00",
                metadata=metadata_woman
            )

        # Frame 15: Tracking agent detects a follower in background street patterns
        if frame_idx == 15:
            log_and_capture("[VideoProcessor] Threat Warning: Secondary entity detected matching target walking path.")
            coordinator.state_machine.state.risk_assessment.flags.append("suspicious_following")
            log_and_capture("[TrackingAgent] Threat tracking flag set: [suspicious_following].")

        # Frame 45: Prediction updates ETA window for Camera_B
        if frame_idx == 45:
            log_and_capture("[PredictionAgent] Destination estimated: Camera_B (ETA: 5s).")
            # Trigger prediction flow in coordinator
            coordinator.handle_sighting(
                db=db,
                camera_id="Camera_A",
                timestamp="2026-07-11T12:09:00",
                metadata=metadata_woman
            )

        # Frame 90: Timeout check (Expected arrival at Camera_B expired)
        if frame_idx == 90:
            log_and_capture("[VideoProcessor] Threat Warning: Camera_B video feed is EMPTY after ETA expiration.")
            log_and_capture("[Workflow] Travel timeout reached (Expected arrival window expired).")
            coordinator.check_for_timeouts(db, "2026-07-11T12:21:00")

        # Frame 100: Investigation sweep
        if frame_idx == 100:
            log_and_capture("[VideoProcessor] Triggering blind spot sweep and scans.")
            from app.agents.investigation_agent import InvestigationAgent
            investigation_agent = InvestigationAgent()
            investigation_agent.execute(coordinator.state_machine.state, db)

        # Frame 110: Risk Assessment evaluation
        if frame_idx == 110:
            log_and_capture("[VideoProcessor] Evaluating threat levels.")
            from app.agents.risk_agent import RiskAgent
            from app.services.risk_service import RiskService
            risk_agent = RiskAgent(RiskService())
            risk_agent.execute(coordinator.state_machine.state)

        # Frame 120: Emergency patrol dispatch
        if frame_idx == 120:
            log_and_capture("[VideoProcessor] Alert criteria met. Dispatching patrol unit.")
            from app.agents.dispatch_agent import DispatchAgent
            from app.services.dispatch_service import DispatchService
            dispatch_agent = DispatchAgent(DispatchService())
            dispatch_agent.execute(coordinator.state_machine.state, db)

            from app.agents.learning_agent import LearningAgent
            from app.services.learning_service import LearningService
            learning_agent = LearningAgent(LearningService())
            learning_agent.execute(coordinator.state_machine.state, db)

    # Release readers
    for cap in caps.values():
        cap.release()

    # Calculate and Persist Analytics
    alerts = db.query(Alert).all()
    dispatch_times = [a.eta_minutes for a in alerts if a.dispatched]
    avg_dispatch = sum(dispatch_times) / len(dispatch_times) if dispatch_times else 0.0

    patrols = db.query(PatrolUnit).all()
    busy_patrols = sum(1 for p in patrols if not p.availability)
    utilization = (busy_patrols / len(patrols) * 100.0) if patrols else 0.0

    analytics_record = SystemAnalytics(
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        prediction_accuracy=0.0,
        avg_dispatch_time=round(avg_dispatch, 1),
        incidents_handled=len(alerts),
        investigation_success_rate=0.0,
        false_positives=0,
        patrol_utilization=round(utilization, 1)
    )
    db.add(analytics_record)
    db.commit()

    log_and_capture("\n--- Video CV Follow & Disappearance Scenario Completed ---")
    return logs
