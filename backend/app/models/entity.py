from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Entity(Base):
    __tablename__ = "entities"

    entity_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    # Store descriptors dictionary: physical features, movement patterns, gender, etc.
    descriptors: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    first_seen: Mapped[str] = mapped_column(String, nullable=False)
    last_seen: Mapped[str] = mapped_column(String, nullable=False)
    trajectory: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # Camera trace path
