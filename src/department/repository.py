from sqlalchemy import delete, literal, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.department.models import Department


class DepartmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        id: int,
        *,
        include_employees: bool = False,
        include_children: bool = False,
    ):
        query = select(Department).where(Department.id == id)

        if include_employees:
            query = query.options(selectinload(Department.employees))

        if include_children:
            query = query.options(selectinload(Department.children))

        result = await self.session.execute(query)
        return result.scalars().first()

    def add(self, department: Department):
        self.session.add(department)
        return department

    async def get_children(self, id: int, *, depth: int | None = None):
        recursive_cte = (
            select(Department.id, literal(1).label("depth"))
            .where(Department.parent_id == id)
            .cte(recursive=True)
        )

        union_query = select(
            Department.id, (recursive_cte.c.depth + 1).label("depth")
        ).join(Department, Department.parent_id == recursive_cte.c.id)

        if depth is not None:
            union_query = union_query.where(recursive_cte.c.depth < depth)

        recursive_cte = recursive_cte.union_all(union_query)

        query = select(Department).join(
            recursive_cte, Department.id == recursive_cte.c.id
        )

        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def check_is_child(self, id: int, new_parent_id: int | None):
        if new_parent_id is None:
            return False

        if id == new_parent_id:
            return True

        recursive_cte = (
            select(Department.id).where(Department.parent_id == id).cte(recursive=True)
        )

        recursive_cte = recursive_cte.union_all(
            select(Department.id).where(Department.parent_id == recursive_cte.c.id)
        )

        query = select(recursive_cte).where(recursive_cte.c.id == new_parent_id)
        result = await self.session.execute(query)

        return bool(result.scalars().first())

    async def reassign_parent(self, old_department_id: int, new_department_id: int):
        query = (
            update(Department)
            .where(Department.parent_id == old_department_id)
            .values(parent_id=new_department_id)
        )
        await self.session.execute(query)

    async def delete(self, id: int):
        query = delete(Department).where(Department.id == id)
        await self.session.execute(query)
