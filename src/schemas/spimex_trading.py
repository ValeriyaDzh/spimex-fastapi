from datetime import date, datetime

from pydantic import BaseModel, Field


class SpimexTradingResultsBase(BaseModel):
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


class SpimexTradingResults(SpimexTradingResultsBase):
    created_on: datetime
    updated_on: datetime


class SpimexLastTradingDates(BaseModel):
    dates: list[date]
