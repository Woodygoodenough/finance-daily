import streamlit as st
from finance_daily.state import get_app_ctx

ctx = get_app_ctx()

st.title("Trending")
