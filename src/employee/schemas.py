from datetime import datetime
from pydantic import BaseModel, Field


class CreateEmployeeSchema(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=200)
    hired_at: datetime | None = Field(default=None)


class EmployeeSchema(BaseModel):
    id: int

    department_id: int
    full_name: str
    position: str
    hired_at: datetime | None

    created_at: datetime

    class Config:
        from_attributes = True
