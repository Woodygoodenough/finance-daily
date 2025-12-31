from dataclasses import dataclass
from datetime import datetime


@dataclass
class AppContext:
    test_str_1: str
    test_str_2: str
    lastest_data_date: datetime | None
    last_fetch_ok: bool | None = None
    last_fetch_error: str | None = None
    last_fetch_rows: int | None = None
