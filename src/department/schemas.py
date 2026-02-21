from datetime import datetime
from pydantic import BaseModel, Field


class CreateDepartmentSchema(BaseModel):
    name: str
    parent_id: int | None = Field(default=None)


class MoveDepartmentSchema(BaseModel):
    name: str | None = Field(default=None)
    parent_id: int | None = Field(default=None)


class DepartmentSchema(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True
