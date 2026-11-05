import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from src.service.recommender_service import RecommenderService
from app.components.movie_card import render_movie_card

st.set_page_config(page_title="Recommendations", layout="wide")

@st.cache_resource
def get_service():
    return RecommenderService()

service = get_service()
st.title("🎯 Gợi ý Phim")

users = service.list_users()
user_id = st.selectbox("Chọn User ID:", users if users else [196])
method = st.selectbox("Phương pháp:", ["popularity"], help="Các phương pháp khác sẽ có từ Day 2/3")
k = st.slider("Số lượng gợi ý (K):", 5, 20, 10)
exclude_seen = st.checkbox("Loại bỏ phim đã xem", value=True)

if st.button("Lấy danh sách gợi ý"):
    recs = service.recommend(user_id, method=method, k=k, exclude_seen=exclude_seen)
    if not recs:
        st.warning("Không tìm thấy gợi ý phù hợp hoặc chưa có dữ liệu.")
    else:
        for rec in recs:
            render_movie_card(rec.movie_id, rec.title, rec.score, reason=rec.reason)
