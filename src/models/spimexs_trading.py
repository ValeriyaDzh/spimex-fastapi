from datetime import date

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped

from src.models import Base
from src.schemas import TradingResultsSchema
from src.utils.custom_types import uuid_pk, created_on, updated_on


class SpimexTradingResults(Base):

    __tablename__ = "spimex_trading_results"

    __table_args__ = (
        CheckConstraint("volume >= 0", name="check_volume_positive"),
        CheckConstraint("total >= 0", name="check_total_positive"),
        CheckConstraint("count >= 0", name="check_count_positive"),
    )

    id: Mapped[uuid_pk]
    exchange_product_id: Mapped[str]
    exchange_product_name: Mapped[str]
    oil_id: Mapped[str]
    delivery_basis_id: Mapped[str]
    delivery_basis_name: Mapped[str]
    delivery_type_id: Mapped[str]
    volume: Mapped[int]
    total: Mapped[int]
    count: Mapped[int]
    date: Mapped[date]
    created_on: Mapped[created_on]
    updated_on: Mapped[updated_on]

    def to_pydantic_schema(self) -> TradingResultsSchema:
        return TradingResultsSchema(**self.__dict__)
