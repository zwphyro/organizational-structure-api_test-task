from datetime import datetime
from sqlalchemy import literal, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.department.exceptions import DuplicateDepartmentNameError
from src.department.models import Department
from src.dependencies import DBDependency
from src.employee.models import Employee
from src.exceptions import NotFoundError


class DepartmentService:
    session: AsyncSession

    def __init__(self, session: DBDependency):
        self.session = session

    async def create_department(self, name: str, parent_id: int | None):
        if parent_id is not None:
            try:
                query = (
                    select(Department)
                    .where(Department.id == parent_id)
                    .options(selectinload(Department.children))
                )
                result = await self.session.execute(query)
                parent = result.scalars().one()
            except NoResultFound:
                raise NotFoundError("Parent department not found")

            if any(child.name == name for child in parent.children):
                raise DuplicateDepartmentNameError(
                    "Department with the same name already exists under the parent department"
                )

        department = Department(name=name, parent_id=parent_id)

        self.session.add(department)
        await self.session.commit()

        return department

    async def create_employee(
        self,
        department_id: int,
        full_name: str,
        position: str,
        hired_at: datetime | None,
    ):
        try:
            await self.session.get_one(Department, department_id)
        except NoResultFound:
            raise NotFoundError("Department not found")

        employee = Employee(
            department_id=department_id,
            full_name=full_name,
            position=position,
            hired_at=hired_at,
        )

        self.session.add(employee)
        await self.session.commit()

        return employee

    async def get_department(self, id: int, depth: int, include_employees: bool):
        try:
            query = select(Department).where(Department.id == id)

            if include_employees:
                query = query.options(selectinload(Department.employees))

            result = await self.session.execute(query)
            department = result.scalars().one()
        except NoResultFound:
            raise NotFoundError("Department not found")

        recursive_cte = (
            select(Department.id, literal(1).label("depth"))
            .where(Department.parent_id == id)
            .cte(recursive=True)
        )

        recursive_cte = recursive_cte.union_all(
            select(Department.id, (recursive_cte.c.depth + 1).label("depth"))
            .join(Department, Department.parent_id == recursive_cte.c.id)
            .where(recursive_cte.c.depth < depth)
        )

        query = select(Department).join(
            recursive_cte, Department.id == recursive_cte.c.id
        )

        result = await self.session.execute(query)
        children = result.scalars().unique().all()

        return department, department.employees if include_employees else [], children

    # async def move_department(self, id: int, name: str | None, parent_id: int | None):
    #     try:
    #         department = await self.session.get_one(Department, id)
    #     except NoResultFound:
    #         raise NotFoundError("Department not found")
    #
    #     if name is not None:
    #         department.name = name
    #
    #     if parent_id is not None:
    #         department.parent_id = parent_id
    #
    #     await self.session.commit()
    #     return department
