import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Phim tương tự", layout="wide")

from app.components.movie_card import render_movie_card
from app.components.service import get_service

st.title("Phim tương tự")
st.info(
    "Tìm phim tương tự theo thể loại. Phim không có tín hiệu dùng Popularity."
)

try:
    service = get_service()
except (OSError, ValueError, RuntimeError) as exc:
    st.error(f"Không thể khởi tạo service: {exc}")
    st.stop()

query = st.text_input("Tìm phim", placeholder="Ví dụ: Toy Story")
if not query.strip():
    st.caption("Nhập tên phim để tìm.")
    st.stop()

try:
    matches = service.search_movies(query, limit=50)
except (ValueError, RuntimeError) as exc:
    st.error(str(exc))
    st.stop()

if not matches:
    st.warning("Không tìm thấy phim phù hợp.")
    st.stop()

options = {
    f"{movie['title']} ({movie['movie_id']})": movie["movie_id"]
    for movie in matches
}
selected = st.selectbox("Chọn phim", list(options))
k = st.slider("Số lượng phim tương tự", min_value=5, max_value=20, value=10)

if st.button("Tìm phim tương tự", type="primary"):
    try:
        recommendations = service.similar_items(options[selected], k=k)
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
        st.stop()

    if not recommendations:
        st.warning("Không có phim tương tự.")
    else:
        for rec in recommendations:
            try:
                movie = service.get_movie(rec.movie_id)
            except (ValueError, RuntimeError):
                movie = {"movie_id": rec.movie_id, "title": rec.title}
            render_movie_card(movie, rec.score, rec.reason, rec.method)
