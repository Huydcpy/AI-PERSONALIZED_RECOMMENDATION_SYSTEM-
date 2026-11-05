import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from src.service.recommender_service import RecommenderService

st.set_page_config(page_title="Evaluation", layout="wide")

@st.cache_resource
def get_service():
    return RecommenderService()

service = get_service()
st.title("📈 Đánh giá mô hình (Baseline Metrics)")

metrics = service.get_baseline_metrics()
if metrics:
    st.json(metrics)
else:
    st.warning("Chưa có báo cáo reports/metrics/baseline.json. Ranking metrics sẽ bổ sung ở Day 3.")
