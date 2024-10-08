import pytest
from datetime import date
from httpx import AsyncClient

from tests.conftest import TEST_SPIMEX_DATA


class TestSpimexEndpoind:
    @pytest.mark.usefixtures("fastapi_cache")
    @pytest.mark.asyncio
    async def test_get_trading_days(self, api_client: AsyncClient):
        response = await api_client.get("api/v1/last-trading-days", params={"days": 6})

        data = response.json()
        assert response.status_code == 200
        assert len(data["dates"]) == 6

    @pytest.mark.usefixtures("fastapi_cache")
    @pytest.mark.parametrize(
        "oil_id, delivery_type_id, delivery_basis_id, quantity",
        [
            (None, None, None, 2),
            ("SIX", None, None, 1),
            (None, "D", None, 2),
            (None, None, "SEVEN", 1),
            ("FOUR", None, None, 0),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_trading_results(
        self,
        api_client: AsyncClient,
        oil_id,
        delivery_type_id,
        delivery_basis_id,
        quantity,
    ):
        response = await api_client.get(
            "api/v1/trading-results",
            params={
                "oil_id": oil_id,
                "delivery_type_id": delivery_type_id,
                "delivery_basis_id": delivery_basis_id,
            },
        )

        data = response.json()
        assert response.status_code == 200
        assert len(data["playload"]) == quantity

    @pytest.mark.usefixtures("fastapi_cache")
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "start, end, oil_id, delivery_type_id, delivery_basis_id, quantity",
        [
            (date(2024, 10, 1), date(2024, 10, 6), None, None, None, 7),
            (date(2024, 10, 1), date(2024, 10, 3), None, None, None, 3),
            (date(2024, 10, 1), date(2024, 10, 2), "ONE", None, None, 1),
            (date(2024, 10, 1), date(2024, 10, 6), "TWO", "B", "TWO", 1),
            (date(2024, 10, 1), date(2024, 10, 6), None, None, "THREE", 1),
            (date(2024, 10, 1), date(2024, 10, 6), "FOUR", "D", None, 1),
            (date(2024, 10, 3), date(2024, 10, 6), None, "D", None, 4),
            (date(2024, 10, 1), date(2024, 10, 6), None, None, "EIGHT", 0),
            (date(2024, 10, 6), date(2024, 10, 1), None, None, None, 0),
        ],
    )
    async def test_get_dynamics(
        self,
        api_client: AsyncClient,
        start,
        end,
        oil_id,
        delivery_type_id,
        delivery_basis_id,
        quantity,
    ):
        response = await api_client.get(
            "api/v1/dynamics",
            params={
                "start": start,
                "end": end,
                "oil_id": oil_id,
                "delivery_type_id": delivery_type_id,
                "delivery_basis_id": delivery_basis_id,
            },
        )

        data = response.json()
        assert response.status_code == 200

        assert len(data["playload"]) == quantity

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "id, status",
        [
            ("2ea8b7f5-fef5-4304-bcb3-119406210858", 200),
            ("b7817a5d-eba6-43ea-97d9-e93e7359e61a", 404),
        ],
    )
    async def test_get_spimex_trading_results(
        self, api_client: AsyncClient, id, status
    ):
        response = await api_client.get(f"api/v1/{id}")

        data = response.json()
        assert response.status_code == status
