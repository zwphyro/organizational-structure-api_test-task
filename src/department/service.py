from datetime import datetime

from src.department.exceptions import DepartmentCycleError, DuplicateDepartmentNameError
from src.department.models import Department
from src.dependencies import UOWDependency
from src.employee.models import Employee
from src.exceptions import NotFoundError


class DepartmentService:
    def __init__(self, uow: UOWDependency):
        self.uow = uow

    async def create_department(self, name: str, parent_id: int | None):
        async with self.uow:
            await self._check_department_name(name, parent_id)

            department = Department(name=name, parent_id=parent_id)

            self.uow.departments.add(department)
            await self.uow.commit()

        return department

    async def create_employee(
        self,
        department_id: int,
        full_name: str,
        position: str,
        hired_at: datetime | None,
    ):
        async with self.uow:
            department = await self.uow.departments.get_by_id(department_id)
            if department is None:
                raise NotFoundError("Department not found")

            employee = Employee(
                department_id=department_id,
                full_name=full_name,
                position=position,
                hired_at=hired_at,
            )

            self.uow.employees.add(employee)
            await self.uow.commit()

        return employee

    async def get_department(self, id: int, depth: int, include_employees: bool):
        async with self.uow:
            department = await self.uow.departments.get_by_id(
                id, include_employees=include_employees
            )
            if department is None:
                raise NotFoundError("Department not found")

            children = await self.uow.departments.get_children(id, depth)

        return department, department.employees if include_employees else [], children

    async def move_department(self, id: int, update_dict: dict):
        async with self.uow:
            department = await self.uow.departments.get_by_id(id)
            if department is None:
                raise NotFoundError("Department not found")

            if any(key in update_dict for key in ["parent_id", "name"]):
                parent_id = (
                    update_dict["parent_id"]
                    if "parent_id" in update_dict
                    else department.parent_id
                )
                name = update_dict["name"] if "name" in update_dict else department.name
                await self._check_department_name(name, parent_id)

            if "parent_id" in update_dict:
                new_parent_id = update_dict["parent_id"]
                if await self.uow.departments.check_is_child(id, new_parent_id):
                    raise DepartmentCycleError("Department cycle detected")

            for key, value in update_dict.items():
                setattr(department, key, value)

            await self.uow.commit()

        return department

    async def delete_department(self, id: int, reassign_to_department_id: int | None):
        is_reassign = reassign_to_department_id is not None
        async with self.uow:
            department = await self.uow.departments.get_by_id(
                id, include_children=is_reassign
            )
            if department is None:
                raise NotFoundError("Department not found")

            if is_reassign:
                reassign_to_department = await self.uow.departments.get_by_id(
                    reassign_to_department_id,
                    include_children=True,
                )
                if reassign_to_department is None:
                    raise NotFoundError("Reassign to department not found")

                new_department_children_names = {
                    child.name for child in reassign_to_department.children
                }
                if any(
                    child.name in new_department_children_names
                    for child in department.children
                ):
                    raise DuplicateDepartmentNameError(
                        "Department with the same name already exists under the new parent department"
                    )

                if await self.uow.departments.check_is_child(
                    id, reassign_to_department_id
                ):
                    raise DepartmentCycleError("Department cycle detected")

                await self.uow.departments.reassign_parent(
                    id, reassign_to_department_id
                )

                await self.uow.employees.reassign_department(
                    id, reassign_to_department_id
                )

            await self.uow.departments.delete(id)
            await self.uow.commit()

    async def _check_department_name(self, name: str, parent_id: int | None):
        if parent_id is None:
            return

        parent_department = await self.uow.departments.get_by_id(
            parent_id, include_children=True
        )

        if parent_department is None:
            raise NotFoundError("Parent department not found")

        if any(department.name == name for department in parent_department.children):
            raise DuplicateDepartmentNameError(
                "Department with the same name already exists under the parent department"
            )
