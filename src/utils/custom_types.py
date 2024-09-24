from datetime import datetime
from typing import Annotated
from uuid import uuid4, UUID

from sqlalchemy import DateTime, text
from sqlalchemy.orm import mapped_column


uuid_pk = Annotated[
    UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
]

dt_now_utc_sql = text("TIMEZONE('utc', now())")
created_on = Annotated[datetime, mapped_column(DateTime, server_default=dt_now_utc_sql)]
updated_on = Annotated[
    datetime,
    mapped_column(
        DateTime,
        server_default=dt_now_utc_sql,
        onupdate=dt_now_utc_sql,
    ),
]
