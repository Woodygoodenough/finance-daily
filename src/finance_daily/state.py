from datetime import datetime
import streamlit as st
from finance_daily.context import AppContext
from finance_daily.config import AppConfig
from finance_daily.constants import DatasetName, ETLMetaFields
from finance_daily.utils import load_dataset
import pandas as pd

_CTX_KEY = "app_ctx"
_CONFIG_KEY = "config"


def get_app_ctx() -> AppContext:
    ctx = st.session_state.get(_CTX_KEY)
    if ctx is None:
        ctx = update_app_ctx()
    return ctx


def update_app_ctx() -> AppContext:
    etl_meta = _load_etl_meta(get_app_config())
    last_etl_timestamp = datetime.fromisoformat(
        etl_meta.loc[:, ETLMetaFields.LAST_ETL_TIMESTAMP.value].iloc[0]
    )
    last_etl_success = etl_meta.loc[:, ETLMetaFields.OVERALL_SUCCESS.value].iloc[0]
    ctx = AppContext(
        lastest_data_date=last_etl_timestamp,
        # later tries to fetch the metadata to understand if the data is up to date
        last_fetch_ok=last_etl_success == 1,
        last_fetch_error=None,
    )
    st.session_state[_CTX_KEY] = ctx
    return ctx


def _load_etl_meta(config: AppConfig) -> pd.DataFrame:
    return load_dataset(DatasetName.DIM_META, config=config)


def get_app_config() -> AppConfig:
    cfg = st.session_state.get(_CONFIG_KEY)
    if cfg is None:
        cfg = AppConfig()
        # optional: resolve to absolute path once
        # cfg.data_dir = cfg.data_dir.resolve()
        st.session_state[_CONFIG_KEY] = cfg
    return cfg
