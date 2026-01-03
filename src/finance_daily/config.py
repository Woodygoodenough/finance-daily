from pathlib import Path
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    data_dir: Path = Field(..., env="DATA_DIR")
    config_dir: Path = Field(..., env="CONFIG_DIR")
    data_src: HttpUrl = HttpUrl(
        "https://Woodygoodenough.github.io/finance-data-ETL/data"
    )
