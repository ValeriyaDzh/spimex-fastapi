import asyncio
import os
from datetime import datetime, date, timedelta
from typing import TYPE_CHECKING

import pandas as pd
from fastapi import Query
from sqlalchemy import select, and_
from httpx import AsyncClient

from src.models import SpimexTradingResults
from src.schemas import TradingFilters
from src.utils.repository import SqlAlchemyRepository

if TYPE_CHECKING:
    from collections.abc import Sequence


class SpimexRepository(SqlAlchemyRepository):

    model = SpimexTradingResults

    async def get_trading(self, id) -> SpimexTradingResults | None:
        res = await self.get_by_id(id)
        return res

    async def get_last_trading_dates(self, days_num: int):
        res = await self.get_grouped_query_with_limit(self.model.date, days_num)
        return res

    async def get_trading_results(self, filters: TradingFilters) -> list[dict]:
        last_trading_date = await self.get_orderly_query_with_limit(self.model.date, 1)
        if last_trading_date is None:
            return []

        query = select(self.model).where(self.model.date == last_trading_date[0])
        query = await self.__apply_filters(query, filters)

        return await self.__execute_and_fetch(
            query.limit(filters.limit).offset(filters.offset)
        )

    async def get_dynamics(
        self, start_date: date, end_date: date, filters: TradingFilters
    ) -> list[dict]:
        query = select(self.model).where(
            and_(self.model.date >= start_date, self.model.date <= end_date)
        )

        query = await self.__apply_filters(query, filters)

        return await self.__execute_and_fetch(
            query.limit(filters.limit).offset(filters.offset)
        )

    async def __apply_filters(self, query: Query, filters: TradingFilters) -> Query:
        # uses_filters = (oil_id, delivery_type_id, delivery_basis_id)
        if filters.oil_id:
            query = query.filter(self.model.oil_id == filters.oil_id)

        if filters.delivery_type_id:
            query = query.filter(
                self.model.delivery_type_id == filters.delivery_type_id
            )

        if filters.delivery_basis_id:
            query = query.where(
                self.model.delivery_basis_id == filters.delivery_basis_id
            )

        return query

    async def __execute_and_fetch(self, query: Query) -> list[dict]:
        res = await self.session.execute(query.order_by(self.model.created_on.desc()))
        results: Sequence[self.model] = res.scalars().all()
        return [trading.to_pydantic_schema() for trading in results]

    async def save_to_db(self, date: date) -> None:
        dates = self.__get_dates(date)
        try:
            async with AsyncClient() as client:
                tasks = [self.__download_and_save(date, client) for date in dates]
                await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error while download: {e}!")

        for date in dates:
            if os.path.exists(f"{date}_spimex_data.xls"):
                prepared_obj = []
                df_data = self.__get_necessary_data(f"{date}_spimex_data.xls")
                for _, row in df_data.iterrows():
                    obj = self.model(
                        **row.to_dict()
                        | {
                            "oil_id": row["exchange_product_id"][:4],
                            "delivery_basis_id": row["exchange_product_id"][4:7],
                            "delivery_type_id": row["exchange_product_id"][-1],
                            "date": date,
                        }
                    )
                    prepared_obj.append(obj)
                await self.save_all(prepared_obj)
                os.remove(f"{date}_spimex_data.xls")

    def __get_dates(self, date: date) -> list[date]:
        dates = []
        today = datetime.now().date()
        while date != today:
            dates.append(today)
            today -= timedelta(days=1)
        return dates

    async def __download_and_save(self, date: datetime, client: AsyncClient) -> None:
        url = f"https://spimex.com/upload/reports/oil_xls/oil_xls_{date.strftime('%Y%m%d')}162000.xls"
        response = await client.get(url=url, timeout=5)
        if response.status_code == 200:
            with open(f"{date}_spimex_data.xls", "wb") as file:
                file.write(response.content)

    def __get_necessary_data(self, file: str) -> pd.DataFrame:
        columns_names = [
            "exchange_product_id",
            "exchange_product_name",
            "delivery_basis_name",
            "volume",
            "total",
            "count",
        ]

        columns_types = {
            "exchange_product_id": str,
            "exchange_product_name": str,
            "delivery_basis_name": str,
            "volume": int,
            "total": int,
            "count": int,
        }
        df = pd.read_excel(file, sheet_name=0, header=6)
        df[df.columns[-1]] = pd.to_numeric(df[df.columns[-1]], errors="coerce")
        df = df[df[df.columns[-1]] > 0]
        df = df.iloc[:-2, [1, 2, 3, 4, 5, -1]]
        df.columns = columns_names
        df = df.astype(columns_types)

        return df
