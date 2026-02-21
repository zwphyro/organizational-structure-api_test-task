from typing import Annotated
from fastapi import APIRouter, Depends, status

from src.department.schemas import (
    CreateDepartmentSchema,
    DepartmentSchema,
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
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPErrorSchema}},
)
async def create_department(
    new_department: CreateDepartmentSchema, service: ServiceDependency
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
    id: int, new_employee: CreateEmployeeSchema, service: ServiceDependency
):
    employee = await service.create_employee(
        id, new_employee.full_name, new_employee.position, new_employee.hired_at
    )
    return employee


@router.get("/{id}")
def get_department():
    pass


@router.patch(
    "/{id}",
    response_model=DepartmentSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPErrorSchema}},
)
async def move_department(
    id: int, new_department: MoveDepartmentSchema, service: ServiceDependency
):
    department = await service.move_department(
        id, new_department.name, new_department.parent_id
    )
    return department


@router.delete("/{id}")
def delete_department():
    pass
