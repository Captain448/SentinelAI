from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class PatrolUnit(Base):
    __tablename__ = "patrol_units"

    patrol_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    location: Mapped[str] = mapped_column(String, nullable=False)  # Camera/Zone ID
    availability: Mapped[bool] = mapped_column(Boolean, default=True)
