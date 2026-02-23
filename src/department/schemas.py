from datetime import datetime
from fastapi import HTTPException, status
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
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="reassign_to_department_id is required for REASSIGN mode",
            )

        if mode == DeleteModeEnum.CASCADE and reassign_to_department_id is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="reassign_to_department_id is not allowed for CASCADE mode",
            )

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
    employees: list[EmployeeSchema] = Field(exclude_if=lambda v: v in None)
    children: list[DepartmentSchema]
