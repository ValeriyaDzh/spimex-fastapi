import os
from datetime import date, datetime, timedelta

import pytest
import pandas as pd
from httpx import AsyncClient

from src.repositories import SpimexRepository
from src.utils.repository import SqlAlchemyRepository


class TestSpimexRepository:

    @pytest.mark.asyncio
    async def test_get_trading(self, mock_session, mocker):
        mocker.patch.object(
            SqlAlchemyRepository,
            "get_by_id",
            return_value="mocked_result",
        )

        repository = SpimexRepository(mock_session)

        result = await repository.get_trading(1)
        assert result == "mocked_result"

    @pytest.mark.asyncio
    async def test_get_last_trading_dates(self, mock_session, mocker):
        mocker.patch.object(
            SqlAlchemyRepository,
            "get_grouped_query_with_limit",
            return_value=["2024-10-04", "2024-10-03"],
        )

        repository = SpimexRepository(mock_session)

        result = await repository.get_last_trading_dates(2)
        assert result == ["2024-10-04", "2024-10-03"]

    @pytest.mark.asyncio
    async def test_get_dates(self, mock_session):
        test_day = datetime.now().date() - timedelta(3)

        repository = SpimexRepository(mock_session)
        dates = repository._get_dates(test_day)

        assert len(dates) == 3

    @pytest.mark.asyncio
    async def test_get_necessary_data(self, mocker, excel_file, mock_session):
        mocker.patch("pandas.read_excel", return_value=pd.read_excel(excel_file))

        repository = SpimexRepository(mock_session)
        df = repository._get_necessary_data("mocked_file.xlsx")

        assert df.shape == (4, 6)
        assert df["delivery_basis_name"].str.contains("TODEL").any() == False
        assert df.columns.tolist() == [
            "exchange_product_id",
            "exchange_product_name",
            "delivery_basis_name",
            "volume",
            "total",
            "count",
        ]
        assert df["volume"].dtype == int

    @pytest.mark.asyncio
    async def test_save_to_db(self, mocker, excel_file, test_session):
        mocker.patch(
            "src.repositories.spimex_trading.AsyncClient",
            return_value=mocker.AsyncMock(spec=AsyncClient),
        )
        mocker.patch.object(
            SpimexRepository, "_get_dates", return_value=[date(2024, 10, 7)]
        )
        mocker.patch.object(
            SpimexRepository, "_download_and_save", new_callable=mocker.AsyncMock
        )
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("pandas.read_excel", return_value=pd.read_excel(excel_file))
        mocker.patch("os.remove")

        repository = SpimexRepository(test_session)
        await repository.save_to_db(date(2024, 10, 7))
        os.remove.assert_called_once_with("2024-10-07_spimex_data.xls")
