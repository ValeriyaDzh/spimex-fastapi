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
        self.session.add_all(entities)
        await self.session.commit()

    async def get_by_id(self, entity_id: Any) -> T:
        result: Result = await self.session.execute(
            select(self.model).where(and_(self.model.id == entity_id))
        )
        return result.scalar_one_or_none()

    async def get_grouped_query_with_limit(
        self, column: Column, limit: int
    ) -> Sequence[T]:
        result: Result = await self.session.execute(
            select(column).group_by(column).order_by(desc(column)).limit(limit)
        )
        return result.scalars().all()

    async def get_orderly_query_with_limit(
        self, column: Column, limit: int
    ) -> Sequence[T]:
        result: Result = await self.session.execute(
            select(column).order_by(desc(column)).limit(limit)
        )
        return result.scalars().all()
