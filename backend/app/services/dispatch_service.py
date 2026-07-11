import uuid
import yaml
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.patrol import PatrolUnit
from app.models.alert import Alert
from app.core.logger import logger


class DispatchService:
    """Manages emergency services, selects available patrol units, and publishes

    both JSON and YAML incident reports.
    """

    def dispatch_nearest_patrol(
        self,
        db: Session,
        risk_score: float,
        severity: str,
        last_known_camera: str,
        timestamp: str
    ) -> Optional[Dict[str, Any]]:
        """Queries active patrol units, finds an available unit, and assigns it."""
        # Find nearest available patrol unit.
        # For simulation simplicity, we find the first available unit in DB.
        patrol_unit = db.query(PatrolUnit).filter(PatrolUnit.availability == True).first()

        assigned_id = "None"
        eta_minutes = 0.0

        if patrol_unit:
            patrol_unit.availability = False
            assigned_id = patrol_unit.patrol_id
            # Simulating travel time (roughly 3 minutes default or calculated)
            eta_minutes = 3.0
            db.commit()

        incident_id = str(uuid.uuid4())
        recommended_action = "Deploy rapid response unit for immediate physical search."

        # Required JSON payload schema
        json_payload = {
            "incident_id": incident_id,
            "risk_score": risk_score,
            "severity": severity,
            "recommended_action": recommended_action,
            "nearest_patrol": assigned_id,
            "eta_minutes": eta_minutes,
            "last_known_camera": last_known_camera,
            "alert_timestamp": timestamp
        }

        # Create database record
        alert_record = Alert(
            incident_id=incident_id,
            severity=severity,
            risk_score=risk_score,
            dispatched=True,
            recommended_action=recommended_action,
            nearest_patrol=assigned_id,
            eta_minutes=eta_minutes,
            last_known_camera=last_known_camera,
            alert_timestamp=timestamp,
            payload=json_payload
        )
        db.add(alert_record)
        db.commit()

        # Generate YAML representation
        yaml_payload = yaml.dump(json_payload, default_flow_style=False)

        # Output payload reports as requested
        print("\n=== SYSTEM ALERT DISPATCHED ===")
        print(f"JSON Payload:\n{json.dumps(json_payload, indent=2)}")
        print(f"YAML Payload:\n{yaml_payload}")
        print("===============================\n")

        return json_payload

    def get_dispatched_alerts(self, db: Session) -> list:
        return db.query(Alert).all()
