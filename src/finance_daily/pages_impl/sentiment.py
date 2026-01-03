import streamlit as st

from finance_daily.constants import DatasetName
from finance_daily.components import NewsFeedSpec, df_to_news_items, render_news_feed
from finance_daily.state import get_app_config
from finance_daily.utils import load_dataset


cfg = get_app_config()

st.title("Sentiment analysis")
st.caption("Overall market/news sentiment based on recent headlines.")

news_df = load_dataset(DatasetName.FACT_NEWS_RAW, config=cfg)
if news_df is None:
    st.warning(
        "No local news dataset found yet. Click **Refresh data** on Overview, or ensure `DATA_DIR` is configured."
    )
else:
    items = df_to_news_items(news_df)
    scores = [it.sentiment_score for it in items if it.sentiment_score is not None]
    avg = (sum(scores) / len(scores)) if scores else None

    top_left, top_right = st.columns([0.55, 0.45], vertical_alignment="center")
    with top_left:
        st.metric(
            "Overall sentiment score", value=(f"{avg:+.3f}" if avg is not None else "—")
        )
    with top_right:
        st.caption(f"Articles scored: {len(scores)} / {len(items)}")

    spec = NewsFeedSpec(max_items=50, show_summaries=True)
    render_news_feed(items, spec=spec, key="sentiment_news", columns=2)
