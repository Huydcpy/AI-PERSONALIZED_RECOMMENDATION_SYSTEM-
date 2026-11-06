import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from src.service.recommender_service import RecommenderService

st.set_page_config(page_title="User Profile", layout="wide")

@st.cache_resource
def get_service():
    return RecommenderService()

service = get_service()
st.title("👤 User Profile")

users = service.list_users()
if not users:
    st.warning("Chưa có dữ liệu người dùng.")
else:
    selected_user = st.selectbox("Chọn User ID:", users)
    profile = service.get_user_profile(selected_user)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tuổi", profile.get("age", "N/A"))
    col2.metric("Giới tính", profile.get("gender", "N/A"))
    col3.metric("Nghề nghiệp", profile.get("occupation", "N/A"))
    
    st.subheader("Bảng 10 rating gần nhất")
    st.dataframe(profile.get("recent_ratings", []))
