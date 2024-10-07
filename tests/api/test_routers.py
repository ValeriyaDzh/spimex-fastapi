import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from fastapi_cache.decorator import cache


@pytest.mark.asyncio
async def test_get_trading_days(mocker, api_client: AsyncClient):
    response = await api_client.get("api/v1/last-trading-days", params={"days": 6})

    data = response.json()
    assert response.status_code == 200
    assert len(data["dates"]) == 6
