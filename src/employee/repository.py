from sqlalchemy.ext.asyncio import AsyncSession

from src.employee.models import Employee


class EmployeeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, employee: Employee):
        self.session.add(employee)
        return employee
