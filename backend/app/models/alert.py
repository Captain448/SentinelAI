from sqlalchemy import String, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    incident_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    dispatched: Mapped[bool] = mapped_column(Boolean, default=False)
    recommended_action: Mapped[str] = mapped_column(String, nullable=True)
    nearest_patrol: Mapped[str] = mapped_column(String, nullable=True)
    eta_minutes: Mapped[float] = mapped_column(Float, default=0.0)
    last_known_camera: Mapped[str] = mapped_column(String, nullable=True)
    alert_timestamp: Mapped[str] = mapped_column(String, nullable=False)
    # Extra payload containing full JSON / YAML details
    payload: Mapped[dict] = mapped_column(JSON, nullable=True)
