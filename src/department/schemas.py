from datetime import datetime
from pydantic import BaseModel


class CreateDepartmentSchema(BaseModel):
    name: str
    parent_id: int | None


class MoveDepartmentSchema(BaseModel):
    name: str | None
    parent_id: int | None


class DepartmentSchema(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True
