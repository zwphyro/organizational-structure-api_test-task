from abc import ABC, abstractmethod
from typing import Optional, Type
from types import TracebackType
from sqlalchemy.exc import IntegrityError

from src.db import AsyncSessionLocal
from src.department.exceptions import DuplicateDepartmentNameError
from src.department.repository import DepartmentRepository
from src.employee.repository import EmployeeRepository
from src.exceptions import DatabaseError


class IUnitOfWork(ABC):
    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        if exc_type is not None:
            await self.rollback()
        await self.close()

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def flush(self): ...

    @abstractmethod
    async def rollback(self): ...

    @abstractmethod
    async def close(self): ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_pool = AsyncSessionLocal

    async def __aenter__(self):
        self.session = self.session_pool()
        self.departments = DepartmentRepository(self.session)
        self.employees = EmployeeRepository(self.session)
        return await super().__aenter__()

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
