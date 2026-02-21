from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.department.models import Department
from src.dependencies import DBDependency
from src.employee.models import Employee


class DepartmentService:
    session: AsyncSession

    def __init__(self, session: DBDependency):
        self.session = session

    async def create_department(self, name: str, parent_id: int | None):
        department = Department(name=name, parent_id=parent_id)

        self.session.add(department)
        await self.session.commit()

        return department

    async def create_employee(
        self, department_id, full_name: str, position: str, hired_at: datetime | None
    ):
        employee = Employee(
            department_id=department_id,
            full_name=full_name,
            position=position,
            hired_at=hired_at,
        )

        self.session.add(employee)
        await self.session.commit()

        return employee

    async def move_department(self, id: int, name: str | None, parent_id: int | None):
        department = await self.session.get(Department, id)
        if department is None:
            return None

        if name is not None:
            department.name = name

        if parent_id is not None:
            department.parent_id = parent_id

        await self.session.commit()
        return department

    # async def get_department(self, id: int, depth: int, include_employees: bool):
    #
