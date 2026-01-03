import streamlit as st
from streamlit_elements import elements, mui

from finance_daily.constants import DatasetName
from finance_daily.state import get_app_config
from finance_daily.utils import load_dataset


cfg = get_app_config()

st.title("Fundamentals")
st.caption("This page is under progress. Current view shows the raw fundamentals dataset.")
st.info("Under construction: next we’ll add per-ticker drilldowns, trends, and better valuation context.")

df = load_dataset(DatasetName.FACT_FUNDAMENTALS, config=cfg)
if df is None or df.empty:
    st.warning(
        "No local fundamentals dataset found yet. Click **Refresh data** on Overview, or ensure `DATA_DIR` is configured."
    )
else:
    df_view = df.copy()
    if "symbol" in df_view.columns:
        df_view = df_view.sort_values("symbol", ascending=True)

    cols = list(df_view.columns)
    rows = df_view.to_dict(orient="records")

    with elements("fundamentals_table"):
        mui.Card(
            variant="outlined",
            sx={"borderRadius": 3, "backgroundColor": "rgba(255,255,255,0.02)"},
            children=mui.CardContent(
                sx={"padding": "10px !important"},
                children=mui.TableContainer(
                    children=mui.Table(
                        size="small",
                        stickyHeader=True,
                        children=[
                            mui.TableHead(
                                children=mui.TableRow(
                                    children=[
                                        mui.TableCell(
                                            c,
                                            sx={
                                                "fontWeight": 750,
                                                "opacity": 0.9,
                                                "whiteSpace": "nowrap",
                                                "borderBottom": "1px solid rgba(255,255,255,0.08)",
                                            },
                                        )
                                        for c in cols
                                    ]
                                )
                            ),
                            mui.TableBody(
                                children=[
                                    mui.TableRow(
                                        key=f"fund_row_{i}",
                                        hover=True,
                                        sx={
                                            "&:last-child td, &:last-child th": {
                                                "borderBottom": 0
                                            }
                                        },
                                        children=[
                                            mui.TableCell(
                                                str(row.get(c, "—")),
                                                sx={
                                                    "borderBottom": "1px solid rgba(255,255,255,0.08)"
                                                },
                                            )
                                            for c in cols
                                        ],
                                    )
                                    for i, row in enumerate(rows)
                                ]
                            ),
                        ],
                    )
                ),
            ),
        )


