import streamlit as st
from finance_daily.context import AppContext
from finance_daily.config import AppConfig
from datetime import datetime

_CTX_KEY = "app_ctx"
_CONFIG_KEY = "config"


def get_app_ctx() -> AppContext:
    ctx = st.session_state.get(_CTX_KEY)
    if ctx is None:
        ctx = AppContext(
            lastest_data_date=datetime.now(),
            # later tries to fetch the metadata to understand if the data is up to date
            last_fetch_ok=True,
            last_fetch_error=None,
        )
        st.session_state[_CTX_KEY] = ctx
    return ctx


def get_app_config() -> AppConfig:
    cfg = st.session_state.get(_CONFIG_KEY)
    if cfg is None:
        cfg = AppConfig()
        # optional: resolve to absolute path once
        # cfg.data_dir = cfg.data_dir.resolve()
        st.session_state[_CONFIG_KEY] = cfg
    return cfg
