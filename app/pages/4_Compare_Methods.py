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
    "So sánh 3 phương pháp: Popularity, Content-Based, Item-Based CF. "
    "Ghi chú: điểm số các phương pháp có thang đo khác nhau "
    "(Popularity dùng rating/count/Bayesian average, Content-Based dùng độ tương đồng cosine, Item-Based CF dùng điểm CF)."
)
try:
    service = get_service()
    users = service.list_users()
    if not users:
        st.warning("Chưa có dữ liệu. Hãy chạy data pipeline.")
        st.stop()
    user_id = st.selectbox("Chọn User ID", users)
    k = st.slider("Số lượng gợi ý", 5, 20, 10)
    cols = st.columns(3)
    methods = ("popularity", "content_based", "item_cf")
    method_names = {
        "popularity": "Popularity",
        "content_based": "Content-Based",
        "item_cf": "Item-Based CF",
    }
    for column, method in zip(cols, methods):
        with column:
            st.subheader(method_names[method])
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
                st.warning(str(exc))
except (OSError, ValueError, RuntimeError) as exc:
    st.error(str(exc))
