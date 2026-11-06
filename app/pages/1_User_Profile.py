import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Hồ sơ người dùng", layout="wide")

import pandas as pd

from app.components.charts import render_bar_chart
from app.components.service import get_service

st.title("Hồ sơ người dùng")

try:
    service = get_service()
except (OSError, ValueError, RuntimeError) as exc:
    st.error(f"Không thể khởi tạo service: {exc}")
    st.stop()

users = service.list_users()
if not users:
    st.warning("Chưa có dữ liệu người dùng. Hãy chạy data pipeline trước.")
    st.stop()

user_id = st.selectbox("Chọn User ID", users)

try:
    profile = service.get_user_profile(user_id)
except (ValueError, RuntimeError) as exc:
    st.error(str(exc))
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Tuổi", profile.get("age", "N/A"))
col2.metric("Giới tính", profile.get("gender", "N/A"))
col3.metric("Nghề nghiệp", profile.get("occupation", "N/A"))

col4, col5 = st.columns(2)
col4.metric("Số rating", profile.get("n_ratings", 0))
avg_rating = profile.get("avg_rating")
col5.metric(
    "Rating trung bình",
    f"{float(avg_rating):.2f}" if avg_rating is not None else "N/A",
)

top_genres = profile.get("top_genres", [])
if top_genres:
    render_bar_chart(
        pd.DataFrame(top_genres),
        "genre",
        "count",
        "Số rating theo thể loại",
    )
else:
    st.info("Chưa có dữ liệu thể loại cho user này.")

st.subheader("10 rating gần nhất")
recent_ratings = profile.get("recent_ratings", [])
if recent_ratings:
    st.dataframe(
        pd.DataFrame(recent_ratings),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("User chưa có rating.")
