import streamlit as st

from finance_daily.state import (
    get_app_ctx,
    get_app_config,
    update_app_ctx,
    refresh_everything,
)
from finance_daily.constants import DatasetName, SnapshotFields
from finance_daily.components import SnapshotTableSpec, render_snapshot_table
from finance_daily.components import NewsFeedSpec, df_to_news_items, render_news_feed
from finance_daily.utils import load_dataset


ctx = get_app_ctx()
cfg = get_app_config()
snapshot_df = load_dataset(DatasetName.FACT_LATEST, config=cfg)

# --- TOP ROW ---
# Best practice for "wider" widgets in Streamlit: give them more layout space via column ratios.
top_col_1, top_col_2 = st.columns([0.42, 0.58])
# --- Overall Status ---
with top_col_1:
    st.title("Overview")
    st.caption("Refresh the dataset and explore the latest snapshot.")

    # placeholder for now
    refresh_clicked = st.button(
        "Refresh data",
        type="primary",
        width="content",
        help="Reload the metadata from the database.",
    )

    if refresh_clicked:
        refresh_everything()

    st.metric(
        "Last refresh",
        value=(
            ctx.lastest_data_date.strftime("%Y-%m-%d %H:%M")
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

# --- Snapshot Table ---
with top_col_2:
    header_left, header_right = st.columns([1, 1], vertical_alignment="center")
    with header_left:
        st.subheader("Latest snapshot")

    if snapshot_df is None:
        st.warning(
            "No local dataset found yet. Click **Refresh data** to download it, or ensure `DATA_DIR` is configured."
        )
    else:
        render_snapshot_table(
            snapshot_df,
            spec=SnapshotTableSpec(
                max_rows=50,
                sort_by=SnapshotFields.TICKER.value,
                percent_is_fraction=True,
            ),
        )
st.markdown("---")

# --- BOTTOM ROW ---
# News feed
news_df = load_dataset(DatasetName.FACT_NEWS_RAW, config=cfg)

st.subheader("News feed")
if news_df is None:
    st.warning(
        "No local news dataset found yet. Click **Refresh data** to download it, or ensure `DATA_DIR` is configured."
    )
else:
    spec = NewsFeedSpec(max_items=5, show_summaries=True)
    items = df_to_news_items(news_df)
    render_news_feed(items, spec=spec)
