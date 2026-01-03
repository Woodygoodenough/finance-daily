from __future__ import annotations

from dataclasses import dataclass
from datetime import date as Date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


@dataclass(frozen=True)
class TickerSeriesSpec:
    height: int = 520
    template: str = "plotly_dark"


def _daily_raw_path(data_dir: Path, symbol: str) -> Path:
    return data_dir / f"fact_all_daily_raw_{symbol.upper()}.csv"


@st.cache_data(show_spinner=False)
def load_close_series(data_dir: Path, symbol: str) -> pd.DataFrame | None:
    """Load a single ticker close series from the local raw CSV."""
    path = _daily_raw_path(data_dir, symbol)
    if not path.exists():
        return None

    df = pd.read_csv(path)
    if df.empty or "date" not in df.columns or "close" not in df.columns:
        return None

    out = df.loc[:, ["date", "close"]].copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.dropna(subset=["date", "close"]).sort_values("date", ascending=True)
    out["close"] = pd.to_numeric(out["close"], errors="coerce")
    out = out.dropna(subset=["close"])
    return out.reset_index(drop=True)


def _common_date_range(
    series_by_symbol: dict[str, pd.DataFrame],
) -> tuple[pd.Timestamp, pd.Timestamp] | None:
    if not series_by_symbol:
        return None
    mins = [df["date"].min() for df in series_by_symbol.values() if not df.empty]
    maxs = [df["date"].max() for df in series_by_symbol.values() if not df.empty]
    if not mins or not maxs:
        return None
    common_start = max(mins)
    common_end = min(maxs)
    if pd.isna(common_start) or pd.isna(common_end) or common_start > common_end:
        return None
    return common_start, common_end


def get_all_tickers_common_range(
    *,
    data_dir: Path,
    symbols: list[str],
) -> tuple[tuple[Date, Date] | None, list[str]]:
    """Return (common_date_range, missing_symbols) for locally available tickers."""
    series_by_symbol: dict[str, pd.DataFrame] = {}
    missing: list[str] = []
    for sym in symbols:
        s = load_close_series(data_dir, sym)
        if s is None or s.empty:
            missing.append(sym)
            continue
        series_by_symbol[sym] = s

    common = _common_date_range(series_by_symbol)
    if common is None:
        return None, missing
    common_start, common_end = common
    return (common_start.date(), common_end.date()), missing


def build_all_tickers_normalized_figure(
    *,
    data_dir: Path,
    symbols: list[str],
    start: Date,
    spec: TickerSeriesSpec = TickerSeriesSpec(),
) -> tuple[px.line, tuple[Date, Date] | None, list[str]]:
    """Build a % change chart for all tickers, normalized to the selected start date.

    Returns (fig, (min_date, max_date), missing_symbols).
    """
    series_by_symbol: dict[str, pd.DataFrame] = {}
    missing: list[str] = []
    for sym in symbols:
        s = load_close_series(data_dir, sym)
        if s is None or s.empty:
            missing.append(sym)
            continue
        series_by_symbol[sym] = s

    common = _common_date_range(series_by_symbol)
    if common is None:
        fig = px.line(template=spec.template, height=spec.height)
        fig.update_layout(
            title="No data available",
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        return fig, None, missing

    common_start, common_end = common
    min_date, max_date = common_start.date(), common_end.date()

    start_ts = pd.Timestamp(start)
    if start_ts < common_start:
        start_ts = common_start
    if start_ts > common_end:
        start_ts = common_end

    rows: list[pd.DataFrame] = []
    for sym, df in series_by_symbol.items():
        dfv = df[(df["date"] >= common_start) & (df["date"] <= common_end)].copy()
        dfv = dfv[dfv["date"] >= start_ts].copy()
        if dfv.empty:
            continue
        base = dfv.iloc[0]["close"]
        if base == 0 or pd.isna(base):
            continue
        dfv["ticker"] = sym
        dfv["pct_from_start"] = (dfv["close"] / base - 1.0) * 100.0
        rows.append(dfv.loc[:, ["date", "ticker", "pct_from_start"]])

    plot_df = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    fig = px.line(
        plot_df,
        x="date",
        y="pct_from_start",
        color="ticker",
        template=spec.template,
        height=spec.height,
        title="All tickers — % change since start",
    )
    fig.update_traces(mode="lines")
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="% from start",
        margin=dict(l=10, r=10, t=50, b=10),
        legend_title_text="",
    )
    fig.update_yaxes(ticksuffix="%")
    return fig, (min_date, max_date), missing


def build_single_ticker_figure(
    *,
    data_dir: Path,
    symbol: str,
    start: Date | None = None,
    spec: TickerSeriesSpec = TickerSeriesSpec(),
) -> tuple[px.line, tuple[Date, Date] | None]:
    """Build an absolute close price chart for a single ticker."""
    df = load_close_series(data_dir, symbol)
    if df is None or df.empty:
        fig = px.line(template=spec.template, height=spec.height)
        fig.update_layout(
            title=f"{symbol} — no local data found",
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        return fig, None

    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    if start is not None:
        start_ts = pd.Timestamp(start)
        df = df[df["date"] >= start_ts]

    fig = px.line(
        df,
        x="date",
        y="close",
        template=spec.template,
        height=spec.height,
        title=f"{symbol} — close price",
    )
    fig.update_traces(mode="lines")
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Close",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig, (min_date, max_date)
