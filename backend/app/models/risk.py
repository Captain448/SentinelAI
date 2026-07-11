from sqlalchemy import String, Integer, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class InvestigationLog(Base):
    __tablename__ = "investigation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    searched_camera: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[str] = mapped_column(String, nullable=False)
    result: Mapped[str] = mapped_column(String, nullable=False)  # SIGHTING_FOUND, EMPTY, ANOMALOUS


class LearningHistory(Base):
    __tablename__ = "learning_history"

    transition: Mapped[str] = mapped_column(String, primary_key=True)  # e.g., "Camera_A->Camera_B"
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)


class SystemAnalytics(Base):
    __tablename__ = "system_analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[str] = mapped_column(String, nullable=False)
    prediction_accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    avg_dispatch_time: Mapped[float] = mapped_column(Float, default=0.0)
    incidents_handled: Mapped[int] = mapped_column(Integer, default=0)
    investigation_success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    false_positives: Mapped[int] = mapped_column(Integer, default=0)
    patrol_utilization: Mapped[float] = mapped_column(Float, default=0.0)
