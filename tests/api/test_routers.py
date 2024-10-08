import pytest
from httpx import AsyncClient

from tests.conftest import TEST_SPIMEX_DATA


@pytest.mark.usefixtures("fastapi_cache")
@pytest.mark.asyncio
async def test_get_trading_days(api_client: AsyncClient):
    response = await api_client.get("api/v1/last-trading-days", params={"days": 6})

    data = response.json()
    print(data)
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
    api_client: AsyncClient, oil_id, delivery_type_id, delivery_basis_id, quantity
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
