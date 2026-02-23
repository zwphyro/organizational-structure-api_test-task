from typing import Annotated
from fastapi import Depends

from src.unit_of_work import UnitOfWork


async def get_uow():
    return UnitOfWork()


UOWDependency = Annotated[UnitOfWork, Depends(get_uow)]
