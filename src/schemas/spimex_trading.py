from dataclasses import dataclass
from datetime import date, datetime

from fastapi import Query
from pydantic import BaseModel, Field


class TradingResultsSchema(BaseModel):
    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str
    volume: int = Field(ge=0)
    total: int = Field(ge=0)
    count: int = Field(ge=0)
    date: date
    created_on: datetime
    updated_on: datetime

    class Config:
        from_attributes = True


class LastTradingResultsDates(BaseModel):
    dates: list[date]


class TradingResultsList(BaseModel):
    playload: list[TradingResultsSchema]


@dataclass
class TradingFilters:
    oil_id: str | None = Query(None)
    delivery_type_id: str | None = Query(None)
    delivery_basis_id: str | None = Query(None)
