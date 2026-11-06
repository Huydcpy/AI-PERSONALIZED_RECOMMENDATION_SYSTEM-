import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Đánh giá mô hình", layout="wide")

from app.components.service import get_metrics

st.title("Đánh giá mô hình")

try:
    metrics = get_metrics()
except (OSError, ValueError, RuntimeError) as exc:
    st.error(f"Không thể đọc baseline metrics: {exc}")
    metrics = {}

if not metrics:
    st.warning(
        "Chưa có reports/metrics/baseline.json. "
        "Hãy chạy python scripts/run_baseline.py."
    )
else:
    col1, col2 = st.columns(2)
    rmse = metrics.get("rmse")
    mae = metrics.get("mae")
    col1.metric("RMSE", f"{float(rmse):.4f}" if rmse is not None else "N/A")
    col2.metric("MAE", f"{float(mae):.4f}" if mae is not None else "N/A")
    st.json(metrics)

st.caption(
    "Ranking metrics (Precision@K, Recall@K, NDCG@K) sẽ có ở Day 3."
)
