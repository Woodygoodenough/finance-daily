from enum import Enum
from pathlib import Path


# Enum
class DatasetName(str, Enum):
    FACT_LATEST = "fact_all_daily_snapshots.csv"
    FACT_NEWS_RAW = "fact_all_news_raw.csv"
    FACT_FUNDAMENTALS = "fact_equities_fundamentals.csv"
    DIM_META_GROUP1 = "dim_etl_meta_group_1.csv"
    DIM_META_GROUP2 = "dim_etl_meta_group_2.csv"
    """
    DIM_DATE = "dim_date"
    DIM_TICKER = "dim_ticker"
    FACT_PRICES = "fact_prices"
    FACT_FEATURES = "fact_features"
    ETL_METADATA = "etl_metadata"
    """


# per ticker dataset names
DAILY_RAW_T = "fact_all_daily_raw_{symbol}.csv"

# project structure
PAGES_DIR = "pages_impl"
OVERVIEW_SCT = Path(PAGES_DIR) / "overview.py"
SERIES_SCT = Path(PAGES_DIR) / "series.py"
SENTIMENT_SCT = Path(PAGES_DIR) / "sentiment.py"
FUNDAMENTALS_SCT = Path(PAGES_DIR) / "fundamentals.py"


# config file names
TICKERS_F = "tickers.yaml"


# ETL meta fields
class ETLMetaFields(str, Enum):
    OVERALL_SUCCESS = "overall_success"
    LAST_ETL_TIMESTAMP = "etl_timestamp"


# field names
class SnapshotFields(str, Enum):
    TICKER = "ticker"
    CLOSE = "close"
    PCT_1_DAY = "pct_1_day"
    PCT_1_WEEK = "pct_1_week"


class NewsFields(str, Enum):
    TITLE = "title"
    URL = "url"
    TIME_PUBLISHED = "time_published"
    SUMMARY = "summary"
    ICON = "icon"
    BANNER_IMAGE = "banner_image"
    OVERALL_SENTIMENT_SCORE = "overall_sentiment_score"
    OVERALL_SENTIMENT_LABEL = "overall_sentiment_label"
