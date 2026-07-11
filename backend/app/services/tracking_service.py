from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.entity import Entity


class TrackingService:
    """Mock interface for ByteTrack and cross-camera Re-ID (FastReID).

    Manages trajectories and visual feature updates in the database.
    """

    def re_identify_entity(
        self,
        db: Session,
        entity_id: str,
        features: Dict[str, Any],
        camera_id: str,
        timestamp: str
    ) -> Entity:
        """Looks up existing tracking history or registers a new tracked entity."""
        entity = db.query(Entity).filter(Entity.entity_id == entity_id).first()

        if not entity:
            # Register new entity in database
            entity = Entity(
                entity_id=entity_id,
                descriptors=features,
                first_seen=timestamp,
                last_seen=timestamp,
                trajectory=[{"camera_id": camera_id, "timestamp": timestamp}]
            )
            db.add(entity)
        else:
            # Update existing entity
            entity.last_seen = timestamp

            # Update trajectory path if last step was not the same camera
            current_trajectory = list(entity.trajectory)
            if not current_trajectory or current_trajectory[-1]["camera_id"] != camera_id:
                current_trajectory.append({"camera_id": camera_id, "timestamp": timestamp})
                entity.trajectory = current_trajectory

            # Update descriptors if new visual features are resolved
            current_descriptors = dict(entity.descriptors)
            current_descriptors.update(features)
            entity.descriptors = current_descriptors

        db.commit()
        db.refresh(entity)
        return entity

    def get_trajectory(self, db: Session, entity_id: str) -> List[Dict[str, Any]]:
        entity = db.query(Entity).filter(Entity.entity_id == entity_id).first()
        return entity.trajectory if entity else []
