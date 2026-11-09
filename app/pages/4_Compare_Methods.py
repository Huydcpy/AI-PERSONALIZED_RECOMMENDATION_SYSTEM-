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
st.caption(
    "Ghi chú thang đo: Popularity dùng count/rating; "
    "Content-Based dùng cosine [0,1]; "
    "Item-CF/SVD dùng rating [1,5]; "
    "Hybrid dùng blended score [0,1]."
)

try:
    service = get_service()
    users = service.list_users()
except (OSError, ValueError, RuntimeError) as exc:
    st.error(f"Không thể khởi tạo service: {exc}")
    st.stop()

if not users:
    st.warning("Chưa có dữ liệu. Hãy chạy data pipeline.")
    st.stop()

user_id = st.selectbox("Chọn User ID", users)
k = st.slider("Số lượng gợi ý", 5, 20, 10)

methods = [
    ("popularity", "Popularity"),
    ("content_based", "Content-Based"),
    ("item_cf", "Item-CF"),
    ("svd", "SVD"),
    ("hybrid", "Hybrid"),
]
tabs = st.tabs([name for _, name in methods])

for (method, name), tab in zip(methods, tabs):
    with tab:
        try:
            recommendations = service.recommend(user_id, method=method, k=k)
            if not recommendations:
                st.info("Không có gợi ý phù hợp.")
            else:
                for rec in recommendations:
                    try:
                        movie = service.get_movie(rec.movie_id)
                    except (ValueError, RuntimeError):
                        movie = {"movie_id": rec.movie_id, "title": rec.title}
                    render_movie_card(movie, rec.score, rec.reason, rec.method)
        except (ValueError, RuntimeError) as exc:
            st.warning(f"{name}: {exc}")
