import logging
from typing import AsyncGenerator
from io import BytesIO

import pytest
import pandas as pd
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from tests.fake_data import TEST_SPIMEX_DATA, TEST_EXCEL_DATA
from src.database import get_async_session
from src.config import settings
from src.main import app
from src.models import Base, SpimexTradingResults

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


@pytest.fixture(scope="function", autouse=True)
def fastapi_cache():
    FastAPICache.init(InMemoryBackend())
    yield


@pytest.fixture(scope="function", autouse=True)
async def test_session():
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def mock_session(mocker):
    session = mocker.Mock(spec=AsyncSession)
    return session


client = TestClient(app)


@pytest.fixture(scope="session")
async def api_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as api_client:
        yield api_client


@pytest.fixture
def excel_file():
    df = pd.DataFrame(TEST_EXCEL_DATA)
    print(df)
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer) as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")

    return excel_buffer
