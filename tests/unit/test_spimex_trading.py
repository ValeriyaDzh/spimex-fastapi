import pytest
from unittest.mock import AsyncMock
from src.repositories import SpimexRepository


class TestSpimexRepository:

    @pytest.mark.asyncio
    async def test_get_trading(mock_session, mocker):
        mocker.patch(
            "src.utils.repository.SqlAlchemyRepository.get_by_id",
            return_value="mocked_result",
        )

        repository = SpimexRepository(mock_session)

        result = await repository.get_trading(1)
        assert result == "mocked_result"

    @pytest.mark.asyncio
    async def test_get_last_trading_dates(mock_session, mocker):
        mocker.patch(
            "src.utils.repository.SqlAlchemyRepository.get_grouped_query_with_limit",
            return_value=["2024-10-04", "2024-10-03"],
        )

        repository = SpimexRepository(mock_session)

        result = await repository.get_last_trading_dates(2)
        assert result == ["2024-10-04", "2024-10-03"]
