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

    last_etl_timestamp = _load_etl_meta(get_app_config())
    ctx = AppContext(
        lastest_data_date=last_etl_timestamp,
        # later tries to fetch the metadata to understand if the data is up to date
        last_fetch_ok=True,
        last_fetch_error=None,
    )
    st.session_state[_CTX_KEY] = ctx
    return ctx


def refresh_everything():
    # 1) Clear Streamlit caches (only if you use @st.cache_data / @st.cache_resource)
    try:
        st.cache_data.clear()
    except Exception:
        pass
    try:
        st.cache_resource.clear()
    except Exception:
        pass

    # 2) Clear your session_state context so it will be rebuilt
    st.session_state.pop(_CTX_KEY, None)

    # 3) Force rerun so UI immediately reflects new data
    st.rerun()


def _load_etl_meta(config: AppConfig) -> datetime:
    group1_df = load_dataset(DatasetName.DIM_META_GROUP1, config=config)
    group2_df = load_dataset(DatasetName.DIM_META_GROUP2, config=config)
    if (
        group1_df[ETLMetaFields.OVERALL_SUCCESS.value].iloc[0] == 1
        and group2_df[ETLMetaFields.OVERALL_SUCCESS.value].iloc[0] == 1
    ):
        return datetime.fromisoformat(
            group1_df[ETLMetaFields.LAST_ETL_TIMESTAMP.value].iloc[0]
        )
    raise ValueError("ETL workflow may have failed, please check the logs")


def get_app_config() -> AppConfig:
    cfg = st.session_state.get(_CONFIG_KEY)
    if cfg is None:
        cfg = AppConfig()
        # optional: resolve to absolute path once
        # cfg.data_dir = cfg.data_dir.resolve()
        st.session_state[_CONFIG_KEY] = cfg
    return cfg
