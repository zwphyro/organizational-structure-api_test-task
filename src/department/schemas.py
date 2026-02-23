from datetime import datetime
from pydantic import BaseModel, Field, model_validator

from src.department.enums import DeleteModeEnum
from src.employee.schemas import EmployeeSchema


class CreateDepartmentSchema(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    parent_id: int | None = Field(default=None)


class MoveDepartmentSchema(BaseModel):
    name: str = Field(default=None)  # type: ignore[no-assignment-type]
    parent_id: int | None = Field(default=None)


class DeleteDepartmentSchema(BaseModel):
    mode: DeleteModeEnum
    reassign_to_department_id: int | None = Field(default=None)

    @model_validator(mode="after")
    def check_mode(self):
        mode = self.mode
        reassign_to_department_id = self.reassign_to_department_id

        if mode == DeleteModeEnum.REASSIGN and reassign_to_department_id is None:
            raise ValueError("reassign_to_department_id is required")

        if mode == DeleteModeEnum.CASCADE and reassign_to_department_id is not None:
            raise ValueError("reassign_to_department_id is not allowed")

        return self


class DepartmentSchema(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class DepartmentTreeSchema(BaseModel):
    department: DepartmentSchema
    employees: list[EmployeeSchema] = Field(exclude_if=lambda v: not v)
    children: list[DepartmentSchema]
