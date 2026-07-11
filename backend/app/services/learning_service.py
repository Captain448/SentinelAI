from sqlalchemy.orm import Session
from app.models.risk import LearningHistory
from app.core.logger import logger


class LearningService:
    """Updates camera transition probabilities based on successes and failures of predictions."""

    def record_outcome(self, db: Session, transition: str, success: bool) -> None:
        """Increments success or failure count for a transition, adjusting model weights."""
        record = db.query(LearningHistory).filter(LearningHistory.transition == transition).first()

        if not record:
            record = LearningHistory(
                transition=transition,
                success_count=1 if success else 0,
                failure_count=0 if success else 1
            )
            db.add(record)
        else:
            if success:
                record.success_count += 1
            else:
                record.failure_count += 1

        db.commit()
        db.refresh(record)
        logger.debug(
            f"Learning record updated for '{transition}': "
            f"success_count={record.success_count}, failure_count={record.failure_count}"
        )

    def calculate_transition_probability(
        self,
        db: Session,
        from_camera: str,
        to_camera: str,
        default_prob: float
    ) -> float:
        """Computes dynamic transition probability based on historical data using Laplace smoothing."""
        transition = f"{from_camera}->{to_camera}"
        record = db.query(LearningHistory).filter(LearningHistory.transition == transition).first()

        if not record:
            return default_prob

        total_trials = record.success_count + record.failure_count
        if total_trials == 0:
            return default_prob

        # Laplace smoothing (alpha = 1)
        prob = (record.success_count + 1) / (total_trials + 2)
        return round(prob, 2)
