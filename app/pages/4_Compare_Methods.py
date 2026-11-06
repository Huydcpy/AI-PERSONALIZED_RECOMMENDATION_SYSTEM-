import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="So sánh phương pháp", layout="wide")

from app.components.movie_card import render_movie_card
from app.components.service import get_service

st.title("So sánh phương pháp")
st.caption("Item-CF, SVD và Hybrid: Day 3–4. Điểm hai phương pháp khác thang đo.")
try:
    service = get_service()
    users = service.list_users()
    if not users:
        st.warning("Chưa có dữ liệu. Hãy chạy data pipeline.")
        st.stop()
    user_id = st.selectbox("Chọn User ID", users)
    k = st.slider("Số lượng gợi ý", 5, 20, 10)
    for column, method in zip(st.columns(2), ("popularity", "content_based")):
        with column:
            st.subheader(method)
            recommendations = service.recommend(user_id, method=method, k=k)
            if not recommendations:
                st.info("Không có gợi ý phù hợp.")
            for rec in recommendations:
                render_movie_card(service.get_movie(rec.movie_id), rec.score, rec.reason, rec.method)
except (OSError, ValueError, RuntimeError) as exc:
    st.error(str(exc))
