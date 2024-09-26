import asyncio
import os
from datetime import datetime, date, timedelta

import pandas as pd
from httpx import AsyncClient

from src.models import SpimexTradingResults
from src.schemas import SpimexLastTradingDates
from src.utils.repository import SqlAlchemyRepository


class SpimexRepository(SqlAlchemyRepository):

    model = SpimexTradingResults

    async def get_trading(self, id) -> SpimexTradingResults | None:
        res = await self.get_by_id(id)
        return res

    async def get_last_trading_dates(self, days_num: int):
        res = await self.get_orderly_query_with_limit(self.model.date, days_num)
        return SpimexLastTradingDates(dates=res)

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
                    obj = SpimexTradingResults(
                        exchange_product_id=row["exchange_product_id"],
                        exchange_product_name=row["exchange_product_name"],
                        oil_id=row["exchange_product_id"][:4],
                        delivery_basis_id=row["exchange_product_id"][4:7],
                        delivery_basis_name=row["delivery_basis_name"],
                        delivery_type_id=row["exchange_product_id"][-1],
                        volume=row["volume"],
                        total=row["total"],
                        count=row["count"],
                        date=date,
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
