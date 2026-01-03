from dataclasses import dataclass
from datetime import datetime


@dataclass
class AppContext:
    lastest_data_date: datetime | None
    last_fetch_ok: bool | None = None
    last_fetch_error: str | None = None
