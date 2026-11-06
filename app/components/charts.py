import pandas as pd
import streamlit as st


def render_simple_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str):
    st.subheader(title)
    st.bar_chart(df.set_index(x_col)[y_col])
