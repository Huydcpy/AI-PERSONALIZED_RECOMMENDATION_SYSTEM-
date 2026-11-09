import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="AI Movie Recommender", layout="wide")

from app.components.service import get_metrics

st.title("AI Personalized Recommendation System")
st.markdown(
    "Hệ thống gợi ý phim cá nhân hóa trên bộ dữ liệu MovieLens 100K."
)

st.subheader("Chức năng")
st.markdown(
    "- Pipeline dữ liệu: download, preprocess, split\n"
    "- 5 phương pháp gợi ý: Popularity (Bayesian average), Content-Based "
    "(thể loại), Item-Based CF (tương đồng item), SVD (latent factors), "
    "Hybrid (SVD + Item-CF + Content-Based)\n"
    "- 2 bảng đánh giá: Rating metrics (RMSE, MAE) và Ranking metrics "
    "(Precision@K, Recall@K, NDCG@K, Coverage@K)\n"
    "- Giao diện: nhiều trang Streamlit dùng chung service layer"
)

st.subheader("Dataset")
st.markdown(
    "- 100.000 ratings\n"
    "- 943 users\n"
    "- 1.682 movies\n"
    "- Train 80.000 / Test 20.000, split chuẩn u1"
)

st.subheader("Baseline metrics")
try:
    metrics = get_metrics()
except (OSError, ValueError, RuntimeError) as exc:
    st.error(f"Không thể khởi tạo service: {exc}")
    metrics = {}

rmse = metrics.get("rmse")
mae = metrics.get("mae")
if rmse is not None and mae is not None:
    col1, col2 = st.columns(2)
    col1.metric("RMSE", f"{float(rmse):.4f}")
    col2.metric("MAE", f"{float(mae):.4f}")
    st.caption(
        f"Test: {int(metrics.get('n_test', 0)):,} ratings | "
        f"Train: {int(metrics.get('train_size', 0)):,} ratings"
    )
else:
    st.warning(
        "Chưa có reports/metrics/baseline.json. "
        "Hãy chạy python scripts/run_baseline.py."
    )

st.sidebar.info(
    "Chọn trang trong sidebar để xem hồ sơ, gợi ý phim, phim tương tự, "
    "so sánh phương pháp và kết quả đánh giá."
)
