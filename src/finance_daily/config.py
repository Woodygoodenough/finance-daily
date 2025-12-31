from pathlib import Path
from enum import Enum
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings


class DatasetName(str, Enum):
    FACT_LATEST = "fact_latest_snapshot"
    """
    DIM_DATE = "dim_date"
    DIM_TICKER = "dim_ticker"
    FACT_PRICES = "fact_prices"
    FACT_FEATURES = "fact_features"
    ETL_METADATA = "etl_metadata"
    """


class AppConfig(BaseSettings):
    data_dir: Path = Field(..., env="DATA_DIR")
    data_src: HttpUrl = HttpUrl(
        "https://Woodygoodenough.github.io/finance-data-ETL/data"
    )
