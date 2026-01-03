from datetime import date as Date

import streamlit as st
from finance_daily.state import get_app_config, get_app_ctx
from finance_daily.utils import load_tickers
from finance_daily.components.ticker_series_chart import (
    TickerSeriesSpec,
    get_all_tickers_common_range,
    build_all_tickers_normalized_figure,
    build_single_ticker_figure,
)

ctx = get_app_ctx()
cfg = get_app_config()

st.title("Details")
st.caption(
    "Explore close prices by ticker, or compare all tickers normalized from a start date."
)

tickers = load_tickers(cfg)
symbols = tickers.to_symbols()

left, right = st.columns([0.62, 0.38], vertical_alignment="bottom")
with left:
    mode = st.selectbox(
        "Ticker",
        options=["All tickers"] + symbols,
        index=0,
        help="Choose All tickers for a normalized comparison, or pick one ticker for absolute prices.",
    )

spec = TickerSeriesSpec()

if mode == "All tickers":
    common_range, missing = get_all_tickers_common_range(
        data_dir=cfg.data_dir, symbols=symbols
    )

    if common_range is None:
        st.warning(
            "No common date range found across tickers (or missing local files)."
        )
        fig, _, _ = build_all_tickers_normalized_figure(
            data_dir=cfg.data_dir, symbols=symbols, start=Date.today(), spec=spec
        )
    else:
        min_d, max_d = common_range
        with right:
            start_date = st.date_input(
                "Start date (normalized)",
                value=min_d,
                min_value=min_d,
                max_value=max_d,
                help="All tickers are rebased to 0% on this date (or the next available trading day).",
                key="all_start_date",
            )

        fig, _, missing = build_all_tickers_normalized_figure(
            data_dir=cfg.data_dir, symbols=symbols, start=start_date, spec=spec
        )

    if missing:
        st.info(f"Missing local price files for: {', '.join(missing)}")

    st.plotly_chart(fig, width="content")
else:
    symbol = mode
    fig, date_range = build_single_ticker_figure(
        data_dir=cfg.data_dir, symbol=symbol, start=None, spec=spec
    )

    if date_range is None:
        st.warning(f"No local data found for {symbol}. Try refreshing datasets.")
        st.plotly_chart(fig, width="content")
    else:
        min_d, max_d = date_range
        with right:
            start_date = st.date_input(
                "Start date",
                value=min_d,
                min_value=min_d,
                max_value=max_d,
                help="Filter the chart to start at this date.",
                key="single_start_date",
            )

        fig, _ = build_single_ticker_figure(
            data_dir=cfg.data_dir, symbol=symbol, start=start_date, spec=spec
        )
        st.plotly_chart(fig, width="content")
