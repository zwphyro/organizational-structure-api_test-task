from datetime import datetime
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base, id, created_at


class Employee(Base):
    id: Mapped[id]

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    full_name: Mapped[str]
    position: Mapped[str]
    hired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[created_at]

    department: Mapped["Department"] = relationship(back_populates="employees")  # type: ignore[no-undefined-variable] # NOQA: F821
