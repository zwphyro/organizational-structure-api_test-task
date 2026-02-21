from datetime import datetime
from pydantic import BaseModel, Field


class CreateDepartmentSchema(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    parent_id: int | None = Field(default=None)


class MoveDepartmentSchema(BaseModel):
    name: str = Field(default=None)  # type: ignore[no-assignment-type]
    parent_id: int | None = Field(default=None)


class DepartmentSchema(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True
