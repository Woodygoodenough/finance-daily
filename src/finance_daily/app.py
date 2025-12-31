import streamlit as st
from finance_daily.constants import OVERVIEW_SCT, TRENDING_SCT


create_page = st.Page(OVERVIEW_SCT, title="Overview")
delete_page = st.Page(TRENDING_SCT, title="Trending")

pg = st.navigation([create_page, delete_page])
st.set_page_config(page_title="Finance Assistant", page_icon=":material/edit:")
pg.run()
