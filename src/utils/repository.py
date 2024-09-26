import logging
from typing import TYPE_CHECKING, TypeVar, Sequence, Any

from sqlalchemy import select, and_, desc, Column
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Base

if TYPE_CHECKING:
    from sqlalchemy.engine import Result

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

    async def get_by_id(self, entity_id: Any) -> T:
        result: Result = await self.session.execute(
            select(self.model).where(and_(self.model.id == entity_id))
        )
        return result.scalar_one_or_none()

    async def get_by_query_all(self, **kwargs: Any) -> Sequence[T]:
        query = select(self.model).filter_by(**kwargs)
        result: Result = await self.session.execute(query)
        return result.scalars().all()

    async def get_orderly_query_with_limit(self, column: Column, limit: int) -> list[T]:
        result: Result = await self.session.execute(
            select(column).group_by(column).order_by(desc(column)).limit(limit)
        )
        return result.scalars().all()
