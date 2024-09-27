from datetime import date
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import UUID4

from src.repositories import SpimexRepository

from src.api.v1.routers.dependensies import get_spimex_repository
from src.schemas import (
    TradingResultsSchema,
    LastTradingResultsDates,
    TradingResultsList,
    TradingFilters,
)

if TYPE_CHECKING:
    from src.repositories import SpimexRepository

router = APIRouter()


@router.get("/", status_code=200)
async def get_spimex_trading_results(
    date: date,
    spimex_repo: SpimexRepository = Depends(get_spimex_repository),
) -> None:

    return await spimex_repo.save_to_db(date)


@router.get(
    "/last-trading-days", status_code=200, response_model=LastTradingResultsDates
)
async def get_trading_days(
    days: int,
    spimex_repo: SpimexRepository = Depends(get_spimex_repository),
) -> None:
    result = await spimex_repo.get_last_trading_dates(days)
    return LastTradingResultsDates(dates=result)


@router.get("/trading-results", status_code=200, response_model=TradingResultsList)
async def get_trading_results(
    sp_filters: TradingFilters = Depends(TradingFilters),
    spimex_repo: SpimexRepository = Depends(get_spimex_repository),
) -> None:
    result = await spimex_repo.get_trading_results(sp_filters)
    return TradingResultsList(playload=result)


@router.get("/dynamics", status_code=200, response_model=TradingResultsList)
async def get_dynamics(
    start: date,
    end: date,
    sp_filters: TradingFilters = Depends(TradingFilters),
    spimex_repo: SpimexRepository = Depends(get_spimex_repository),
) -> None:
    result = await spimex_repo.get_dynamics(
        start_date=start, end_date=end, filters=sp_filters
    )
    return TradingResultsList(playload=result)


@router.get("/{id}", status_code=200, response_model=TradingResultsSchema)
async def get_spimex_trading_results(
    id: UUID4,
    spimex_repo: SpimexRepository = Depends(get_spimex_repository),
) -> None:

    return await spimex_repo.get_trading(id)
