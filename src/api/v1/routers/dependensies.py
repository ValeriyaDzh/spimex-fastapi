from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.repositories import SpimexRepository


async def get_spimex_repository(session: AsyncSession = Depends(get_async_session)):
    """
    Provide a SpimexRepository instance.
    """
    return SpimexRepository(session=session)
