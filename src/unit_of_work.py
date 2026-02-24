from typing import Type
from types import TracebackType
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.department.exceptions import DuplicateDepartmentNameError
from src.department.repository import DepartmentRepository
from src.employee.repository import EmployeeRepository
from src.exceptions import DatabaseError


class UnitOfWork:
    def __init__(self, session_pool: callable[[], AsyncSession]):
        self.session_pool = session_pool

    async def __aenter__(self):
        self.session = self.session_pool()
        self.departments = DepartmentRepository(self.session)
        self.employees = EmployeeRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if exc_type is not None:
            await self.rollback()
        await self.close()

    async def commit(self):
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.rollback()
            self._handle_integrity_error(e)

    async def flush(self):
        await self.session.flush()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()

    def _handle_integrity_error(self, e: IntegrityError):
        if "name_parent_id_unique" in str(e.orig):
            raise DuplicateDepartmentNameError(
                "Department with the same name already exists under the parent department"
            )

        raise DatabaseError(f"Integrity violation: {e}")
