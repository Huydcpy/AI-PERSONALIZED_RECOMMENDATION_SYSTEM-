"""Chart helpers for the Streamlit app."""

import pandas as pd
import streamlit as st


def render_bar_chart(
    data: pd.DataFrame, x_col: str, y_col: str, title: str
) -> None:
    """Render a bar chart from a DataFrame."""
    st.subheader(title)
    st.bar_chart(data.set_index(x_col)[y_col])
