import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Gợi ý phim", layout="wide")

from app.components.movie_card import render_movie_card
from app.components.service import get_service

st.title("Gợi ý phim")

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
method = st.selectbox(
    "Phương pháp",
    ["popularity"],
    help="Các phương pháp khác sẽ có từ Day 2/3.",
)
k = st.slider("Số lượng gợi ý", min_value=5, max_value=20, value=10)
exclude_seen = st.checkbox("Loại bỏ phim đã xem", value=True)

if st.button("Lấy gợi ý", type="primary"):
    try:
        recommendations = service.recommend(
            user_id=user_id,
            method=method,
            k=k,
            exclude_seen=exclude_seen,
        )
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
        st.stop()

    if not recommendations:
        st.warning("Không có gợi ý phù hợp.")
    else:
        for rec in recommendations:
            try:
                movie = service.get_movie(rec.movie_id)
            except (ValueError, RuntimeError):
                movie = {"movie_id": rec.movie_id, "title": rec.title}
            render_movie_card(movie, rec.score, rec.reason)
