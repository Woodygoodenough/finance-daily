import streamlit as st
from finance_daily.constants import (
    OVERVIEW_SCT,
    SERIES_SCT,
    SENTIMENT_SCT,
    FUNDAMENTALS_SCT,
)


overview_page = st.Page(OVERVIEW_SCT, title="Overview")
detail_page = st.Page(SERIES_SCT, title="Series")
sentiment_page = st.Page(SENTIMENT_SCT, title="Sentiment")
fundamentals_page = st.Page(FUNDAMENTALS_SCT, title="Fundamentals")

pg = st.navigation([overview_page, detail_page, sentiment_page, fundamentals_page])
st.set_page_config(page_title="Finance Assistant", page_icon=":material/edit:")
pg.run()
