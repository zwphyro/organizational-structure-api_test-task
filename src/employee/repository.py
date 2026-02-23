from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.employee.models import Employee


class EmployeeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, employee: Employee):
        self.session.add(employee)
        return employee

    async def reassign_department(self, old_department_id: int, new_department_id: int):
        query = (
            update(Employee)
            .where(Employee.department_id == old_department_id)
            .values(department_id=new_department_id)
        )
        await self.session.execute(query)
