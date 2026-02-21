from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base, id, created_at


class Department(Base):
    id: Mapped[id]

    name: Mapped[str]
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"))

    created_at: Mapped[created_at]

    parent: Mapped["Department | None"] = relationship(
        back_populates="children", remote_side="Department.id"
    )
    children: Mapped[list["Department"]] = relationship(back_populates="parent")
    employees: Mapped[list["Employee"]] = relationship(back_populates="department")  # type: ignore[no-undefined-variable] # NOQA: F821
