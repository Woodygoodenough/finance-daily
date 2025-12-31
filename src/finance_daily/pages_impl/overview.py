from datetime import datetime
import streamlit as st

from finance_daily.state import get_app_ctx, get_app_config
from finance_daily.config import DatasetName
from finance_daily.services.data_fetch import fetch_and_store
from finance_daily.utils import load_dataset


ctx = get_app_ctx()
cfg = get_app_config()
snapshot_df = (
    load_dataset(DatasetName.FACT_LATEST, config=cfg)
    .loc[:, ["ticker", "last_close", "pct_1d"]]
    .assign(**{"pct_1d": lambda x: x["pct_1d"] * 100})
)


top_col_1, top_col_2 = st.columns(2)
with top_col_1:
    st.title("Overview")
    st.caption("Refresh the dataset and explore the latest snapshot.")

    refresh_clicked = st.button(
        "Refresh data",
        type="primary",
        width="content",
        help="Fetch the latest dataset from the configured remote source and store it locally.",
    )

    if refresh_clicked:
        with st.spinner("Fetching and storing datasets..."):
            result = fetch_and_store(cfg)

        ctx.lastest_data_date = datetime.now()
        ctx.last_fetch_ok = result.ok
        ctx.last_fetch_error = "\n".join(result.errors) if result.errors else None
        st.session_state["app_ctx"] = ctx

        if result.ok:
            st.success("Data refreshed successfully.")
        else:
            st.error("Refresh completed with errors.")

    st.metric(
        "Last refresh",
        value=(
            ctx.lastest_data_date.strftime("%Y-%m-%d %H:%M:%S")
            if ctx.lastest_data_date
            else "—"
        ),
    )

    st.metric(
        "Status",
        value=(
            "OK"
            if ctx.last_fetch_ok
            else ("—" if ctx.last_fetch_ok is None else "ERROR")
        ),
    )

    if ctx.last_fetch_error:
        with st.expander("Refresh errors", expanded=False):
            st.code(ctx.last_fetch_error)

    st.markdown("---")

with top_col_2:

    header_left, header_right = st.columns([1, 1], vertical_alignment="center")
    with header_left:
        st.subheader("Latest snapshot")

    if snapshot_df is None:
        st.warning(
            "No local dataset found yet. Click **Refresh data** to download it, or ensure `DATA_DIR` is configured."
        )
    else:
        st.dataframe(
            snapshot_df,
            column_config={
                "ticker": st.column_config.TextColumn(
                    label="Ticker",
                ),
                "last_close": st.column_config.NumberColumn(
                    label="Last close",
                ),
                "pct_1d": st.column_config.NumberColumn(
                    label="1 day change",
                    format="%.2f%%",
                ),
            },
            hide_index=True,
        )
