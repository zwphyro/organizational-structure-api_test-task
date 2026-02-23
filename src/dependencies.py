from typing import Annotated
from fastapi import Depends

from src.db import AsyncSessionLocal
from src.unit_of_work import UnitOfWork


async def get_uow():
    return UnitOfWork(AsyncSessionLocal)


UOWDependency = Annotated[UnitOfWork, Depends(get_uow)]
