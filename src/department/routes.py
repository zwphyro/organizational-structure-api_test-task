from typing import Annotated
from fastapi import APIRouter, Depends, Query, status

from src.department.enums import DeleteModeEnum
from src.department.schemas import (
    CreateDepartmentSchema,
    DepartmentSchema,
    DepartmentTreeSchema,
    MoveDepartmentSchema,
)
from src.department.service import DepartmentService
from src.employee.schemas import CreateEmployeeSchema, EmployeeSchema
from src.schemas import HTTPErrorSchema

router = APIRouter()

ServiceDependency = Annotated[DepartmentService, Depends()]


@router.post(
    "/",
    response_model=DepartmentSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPErrorSchema},
        status.HTTP_409_CONFLICT: {"model": HTTPErrorSchema},
    },
)
async def create_department(
    service: ServiceDependency, new_department: CreateDepartmentSchema
):
    department = await service.create_department(
        new_department.name, new_department.parent_id
    )
    return department


@router.post(
    "/{id}/employees/",
    response_model=EmployeeSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPErrorSchema}},
)
async def create_employee(
    service: ServiceDependency, id: int, new_employee: CreateEmployeeSchema
):
    employee = await service.create_employee(
        id, new_employee.full_name, new_employee.position, new_employee.hired_at
    )
    return employee


@router.get("/{id}", response_model=DepartmentTreeSchema)
async def get_department(
    service: ServiceDependency,
    id: int,
    depth: int = Query(default=1, le=5),
    include_employees: bool = Query(default=True),
):
    department, employees, children = await service.get_department(
        id, depth, include_employees
    )

    return {
        "department": department,
        "employees": employees,
        "children": children,
    }


@router.patch(
    "/{id}",
    response_model=DepartmentSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPErrorSchema}},
)
async def move_department(
    service: ServiceDependency, id: int, new_department: MoveDepartmentSchema
):
    pass
    # department = await service.move_department(
    #     id, new_department.name, new_department.parent_id
    # )
    # return department


@router.delete("/{id}")
def delete_department(
    service: ServiceDependency,
    mode: DeleteModeEnum,
    reassign_to_department_id: int = Query(default=None),
):
    pass
