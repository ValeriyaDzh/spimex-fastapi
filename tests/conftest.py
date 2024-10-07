import logging
from datetime import date
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.database import get_async_session
from src.config import settings
from src.main import app
from src.models import Base, SpimexTradingResults
from src.utils.redis import init_redis_cache

logger = logging.getLogger(__name__)


engine_test = create_async_engine(
    settings.db.URL.get_secret_value(), poolclass=NullPool
)

async_session_maker = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope="session", autouse=True)
async def prepare_db():
    assert settings.db.MODE == "TEST"
    init_redis_cache()
    logger.info(f"Preparing database...: {settings.db.URL.get_secret_value()}")
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database table created successfully.")

    async with async_session_maker() as session:
        for data in TEST_SPIMEX_DATA:
            try:
                logger.info(f"Inserting test data {data}...")
                add_data = SpimexTradingResults(**data)
                session.add(add_data)
                await session.commit()
                logger.debug(f"Test data inserted successfully.")
            except Exception as e:
                logger.error(f"Error inserting test: {e}")
                await session.rollback()
                logger.info("Rolled back transaction.")
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully.")

    yield

    logger.info("Deleting database...")
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Database tables delete successfully.")


TEST_SPIMEX_DATA = [
    {
        "id": "2ea8b7f5-fef5-4304-bcb3-119406210858",
        "exchange_product_id": "TEST_ONE",
        "exchange_product_name": "SOME_PRODUCT_1",
        "oil_id": "ONE",
        "delivery_basis_id": "ONE",
        "delivery_basis_name": "SOME_NAME_1",
        "delivery_type_id": "A",
        "volume": 100,
        "total": 1,
        "count": 1,
        "date": date(2024, 10, 1),
    },
    {
        "id": "b7817a5d-eba6-41ea-97d9-e93e7359e61a",
        "exchange_product_id": "TEST_TWO",
        "exchange_product_name": "SOME_PRODUCT_2",
        "oil_id": "TWO",
        "delivery_basis_id": "TWO",
        "delivery_basis_name": "SOME_NAME_2",
        "delivery_type_id": "B",
        "volume": 200,
        "total": 2,
        "count": 2,
        "date": date(2024, 10, 2),
    },
    {
        "id": "00569ac2-6337-4ce9-b19e-879c8c6c0102",
        "exchange_product_id": "TEST_THREE",
        "exchange_product_name": "SOME_PRODUCT_3",
        "oil_id": "THREE",
        "delivery_basis_id": "THREE",
        "delivery_basis_name": "SOME_NAME_3",
        "delivery_type_id": "C",
        "volume": 300,
        "total": 3,
        "count": 3,
        "date": date(2024, 10, 3),
    },
    {
        "id": "e662b31b-2137-4ca0-8b01-85f6a7f24ece",
        "exchange_product_id": "TEST_FOUR",
        "exchange_product_name": "SOME_PRODUCT_4",
        "oil_id": "FOUR",
        "delivery_basis_id": "FOUR",
        "delivery_basis_name": "SOME_NAME_4",
        "delivery_type_id": "D",
        "volume": 400,
        "total": 4,
        "count": 4,
        "date": date(2024, 10, 4),
    },
    {
        "id": "1d16ade7-f9c9-4730-b27f-cae5a0aea0b1",
        "exchange_product_id": "TEST_FIVE",
        "exchange_product_name": "SOME_PRODUCT_5",
        "oil_id": "FIVE",
        "delivery_basis_id": "FIVE",
        "delivery_basis_name": "SOME_NAME_5",
        "delivery_type_id": "D",
        "volume": 500,
        "total": 5,
        "count": 5,
        "date": date(2024, 10, 5),
    },
    {
        "id": "e4aef022-1ed9-4ad3-8a15-77dab9353fed",
        "exchange_product_id": "TEST_SIX",
        "exchange_product_name": "SOME_PRODUCT_6",
        "oil_id": "SIX",
        "delivery_basis_id": "SIX",
        "delivery_basis_name": "SOME_NAME_6",
        "delivery_type_id": "D",
        "volume": 600,
        "total": 6,
        "count": 6,
        "date": date(2024, 10, 6),
    },
]


client = TestClient(app)


@pytest.fixture(scope="session")
async def api_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as api_client:
        yield api_client
