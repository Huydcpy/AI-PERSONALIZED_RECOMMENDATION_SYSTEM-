import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from src.service.recommender_service import RecommenderService
from app.components.movie_card import render_movie_card

st.set_page_config(page_title="Similar Movies", layout="wide")

@st.cache_resource
def get_service():
    return RecommenderService()

service = get_service()
st.title("🔍 Phim Tương Tự")
st.info("📌 Day 1 Fallback: Đang hiển thị danh sách phim phổ biến. Content-Based Recommender sẽ thay thế ở Day 2.")

movie_id = st.number_input("Nhập Movie ID:", min_value=1, value=1)
k = st.slider("Số lượng phim tương tự:", 5, 20, 10)

if st.button("Tìm phim tương tự"):
    recs = service.similar_items(movie_id, k=k)
    for rec in recs:
        render_movie_card(rec.movie_id, rec.title, rec.score)
