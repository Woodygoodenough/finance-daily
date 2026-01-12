import streamlit as st
from pathlib import Path
import yaml
import pandas as pd
from finance_daily.config import AppConfig
from finance_daily.shared_types import ETLTickers, Ticker
from finance_daily.constants import TICKERS_F, DatasetName


@st.cache_data(ttl=300)
def load_dataset(dsname: DatasetName, *, config: AppConfig) -> pd.DataFrame | None:
    file_path = config.data_dir / dsname.value
    if not file_path.exists():
        return None
    return pd.read_csv(file_path)


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    return config


def load_tickers(config: AppConfig) -> ETLTickers:
    tickers_raw = load_yaml(config.config_dir / TICKERS_F)
    tickers_dict = {}
    for group_name, group_tickers in tickers_raw.items():
        tickers_dict[group_name] = [
            Ticker(symbol=ticker["symbol"].strip().upper(), name=ticker["name"])
            for ticker in group_tickers
        ]
    return ETLTickers(tickers_dict=tickers_dict)
