from uuid import UUID
import logging
from typing import TypeVar

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession


from src.models import Base

T = TypeVar("T", bound=Base)

logger = logging.getLogger(__name__)


class SqlAlchemyRepository:
    """
    Base repository providing generic database CRUD operations.
    """

    model: T

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_all(self, entities: list[T]) -> None:
        """
        Save a new entities in the database.

        :param entities: list of the new entities.
        """
        self.session.add_all(entities)
        await self.session.commit()

    async def get_by_id(self, entity_id: UUID) -> T:
        result = await self.session.execute(
            select(self.model).where(and_(self.model.id == entity_id))
        )
        return result.scalar_one_or_none()
