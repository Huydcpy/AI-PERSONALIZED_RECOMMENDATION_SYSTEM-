import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from src.service.recommender_service import RecommenderService

st.set_page_config(page_title="AI Movie Recommender", layout="wide")

@st.cache_resource
def get_service():
    return RecommenderService()

st.title("🎬 AI-Personalized Recommendation System")
st.markdown("### Welcome to Day 1 Baseline Recommender System")
st.info("Dự án xây dựng hệ thống gợi ý phim cá nhân hóa.")

try:
    service = get_service()
    metrics = service.get_baseline_metrics()
    if metrics:
        st.subheader("📊 Baseline Metrics")
        st.json(metrics)
    else:
        st.warning("Chưa tìm thấy reports/metrics/baseline.json. Vui lòng chạy baseline evaluation.")
except Exception as e:
    st.error(f"Lỗi khởi tạo Service: {e}")

st.sidebar.success("Chọn tính năng từ sidebar bên trái.")
