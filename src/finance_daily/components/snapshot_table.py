from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st
from streamlit_elements import elements, mui

from finance_daily.constants import SnapshotFields


@dataclass(frozen=True)
class SnapshotTableSpec:
    max_rows: int = 25
    sort_by: str = SnapshotFields.TICKER.value
    ascending: bool = True
    percent_is_fraction: bool = True  # e.g. 0.0123 means 1.23%
    key: str = "snapshot_table"


CARD_SX = {
    "borderRadius": 3,
    "backgroundColor": "rgba(255,255,255,0.02)",
    "width": "100%",
}
CELL_SX = {"borderBottom": "1px solid rgba(255,255,255,0.08)"}
HEAD_CELL_SX = {
    **CELL_SX,
    "fontWeight": 750,
    "opacity": 0.9,
    "whiteSpace": "nowrap",
}


def _fmt_price(x) -> str:
    try:
        return f"{float(x):,.2f}"
    except Exception:
        return "—"


def _fmt_pct(x, *, percent_is_fraction: bool) -> tuple[str, str]:
    """Return (label, chip_color) for a percentage value."""
    try:
        v = float(x)
    except Exception:
        return ("—", "default")

    if percent_is_fraction:
        v *= 100.0

    label = f"{v:+.2f}%"
    if v > 0:
        return (label, "success")
    if v < 0:
        return (label, "error")
    return (label, "default")


def render_snapshot_table(
    df: pd.DataFrame, *, spec: SnapshotTableSpec = SnapshotTableSpec()
) -> None:
    """Render a compact snapshot table using Material UI (no dataframes)."""
    if df is None or df.empty:
        st.info("No data to display.")
        return

    df_view = df.copy()
    if spec.sort_by in df_view.columns:
        df_view = df_view.sort_values(spec.sort_by, ascending=spec.ascending)
    df_view = df_view.head(spec.max_rows).reset_index(drop=True)

    ticker_col = SnapshotFields.TICKER.value
    close_col = SnapshotFields.CLOSE.value
    pct_1d_col = SnapshotFields.PCT_1_DAY.value
    pct_1w_col = SnapshotFields.PCT_1_WEEK.value

    with elements(spec.key):
        mui.Card(
            variant="outlined",
            sx=CARD_SX,
            children=mui.CardContent(
                sx={"padding": "10px !important"},
                children=mui.TableContainer(
                    sx={"width": "100%"},
                    children=mui.Table(
                        size="small",
                        stickyHeader=True,
                        children=[
                            mui.TableHead(
                                children=mui.TableRow(
                                    children=[
                                        mui.TableCell("Ticker", sx=HEAD_CELL_SX),
                                        mui.TableCell(
                                            "Price",
                                            align="right",
                                            sx=HEAD_CELL_SX,
                                        ),
                                        mui.TableCell(
                                            "1D", align="right", sx=HEAD_CELL_SX
                                        ),
                                        mui.TableCell(
                                            "1W", align="right", sx=HEAD_CELL_SX
                                        ),
                                    ]
                                )
                            ),
                            mui.TableBody(
                                children=[
                                    mui.TableRow(
                                        key=f"{spec.key}_row_{i}",
                                        hover=True,
                                        sx={
                                            "&:last-child td, &:last-child th": {
                                                "borderBottom": 0
                                            }
                                        },
                                        children=[
                                            mui.TableCell(
                                                str(row.get(ticker_col, "")),
                                                sx=CELL_SX,
                                            ),
                                            mui.TableCell(
                                                _fmt_price(row.get(close_col)),
                                                align="right",
                                                sx=CELL_SX,
                                            ),
                                            mui.TableCell(
                                                align="right",
                                                sx=CELL_SX,
                                                children=(
                                                    lambda t: mui.Chip(
                                                        label=t[0],
                                                        color=t[1],
                                                        size="small",
                                                        variant="outlined",
                                                    )
                                                )(
                                                    _fmt_pct(
                                                        row.get(pct_1d_col),
                                                        percent_is_fraction=spec.percent_is_fraction,
                                                    )
                                                ),
                                            ),
                                            mui.TableCell(
                                                align="right",
                                                sx=CELL_SX,
                                                children=(
                                                    lambda t: mui.Chip(
                                                        label=t[0],
                                                        color=t[1],
                                                        size="small",
                                                        variant="outlined",
                                                    )
                                                )(
                                                    _fmt_pct(
                                                        row.get(pct_1w_col),
                                                        percent_is_fraction=spec.percent_is_fraction,
                                                    )
                                                ),
                                            ),
                                        ],
                                    )
                                    for i, (_, row) in enumerate(df_view.iterrows())
                                ]
                            ),
                        ],
                    ),
                ),
            ),
        )


# Back-compat name (older code used AgGrid)
def render_snapshot_grid(
    df: pd.DataFrame, *, spec: SnapshotTableSpec = SnapshotTableSpec(), **_
) -> None:
    render_snapshot_table(df, spec=spec)
