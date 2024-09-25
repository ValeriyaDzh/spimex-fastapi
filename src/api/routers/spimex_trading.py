from datetime import date
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import UUID4

from src.repositories import SpimexRepository

from src.api.routers.dependensies import get_spimex_repository
from src.schemas import SpimexTradingResults

if TYPE_CHECKING:
    from src.repositories import SpimexRepository

router = APIRouter()


@router.get("/", status_code=200)
async def get_spimex_trading_results(
    date: date,
    spimex_repo: SpimexRepository = Depends(get_spimex_repository),
) -> None:

    return await spimex_repo.save_to_db(date)


@router.get("/{id}", status_code=200, response_model=SpimexTradingResults)
async def get_spimex_trading_results(
    id: UUID4,
    spimex_repo: SpimexRepository = Depends(get_spimex_repository),
) -> None:

    return await spimex_repo.get_trading(id)
