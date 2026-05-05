import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.utcnow(),
        server_default=func.utcnow(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.utcnow(),
        onupdate=func.utcnow(),
        server_default=func.utcnow(),
    )
