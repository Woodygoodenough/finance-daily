import streamlit as st
import pandas as pd
from finance_daily.config import DatasetName, AppConfig


@st.cache_data
def load_dataset(dsname: DatasetName, *, config: AppConfig) -> pd.DataFrame | None:
    file_name = f"{dsname.value}.csv"
    file_path = config.data_dir / file_name
    if not file_path.exists():
        return None
    return pd.read_csv(file_path)
