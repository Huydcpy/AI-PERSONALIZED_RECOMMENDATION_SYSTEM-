import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Đánh giá mô hình", layout="wide")

from app.components.service import get_metrics, get_service, get_svd_metrics

st.title("Đánh giá mô hình")

st.subheader("Rating Prediction")
try:
    baseline = get_metrics()
except (OSError, ValueError, RuntimeError) as exc:
    st.error(f"Không thể đọc baseline metrics: {exc}")
    baseline = {}

try:
    svd = get_svd_metrics()
except (OSError, ValueError, RuntimeError) as exc:
    st.error(f"Không thể đọc SVD metrics: {exc}")
    svd = {}

rating_rows = []
if baseline:
    rating_rows.append(
        {
            "Model": "Popularity",
            "RMSE": baseline.get("rmse"),
            "MAE": baseline.get("mae"),
            "Ghi chú": baseline.get("note", ""),
        }
    )
if svd:
    rating_rows.append(
        {
            "Model": "SVD",
            "RMSE": svd.get("rmse"),
            "MAE": svd.get("mae"),
            "Ghi chú": svd.get("note", ""),
        }
    )

if rating_rows:
    df = pd.DataFrame(rating_rows)
    for col in ("RMSE", "MAE"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    st.dataframe(df, use_container_width=True, hide_index=True)
elif not baseline:
    st.warning(
        "Chưa có reports/metrics/baseline.json. "
        "Hãy chạy python scripts/run_baseline.py."
    )

if not svd:
    st.warning(
        "Chưa có reports/metrics/svd.json. Hãy chạy python scripts/run_svd_eval.py."
    )

st.divider()

st.subheader("Ranking Evaluation")
try:
    service = get_service()
    ranking_metrics = service.get_ranking_metrics()
except (OSError, ValueError, RuntimeError) as exc:
    st.error(f"Không thể đọc ranking metrics: {exc}")
    ranking_metrics = {}

if not ranking_metrics:
    st.warning(
        "Chưa có reports/metrics/ranking.json. Hãy chạy python scripts/run_ranking_eval.py."
    )
else:
    config = ranking_metrics.get("config", {}) or {}
    col1, col2, col3 = st.columns(3)
    k_values = config.get("k_values", [])
    col1.metric("K values", ", ".join(str(k) for k in k_values) if k_values else "N/A")
    col2.metric("Threshold (relevance)", f"{config.get('relevance_threshold', 4.0)}")
    col3.metric("Số user đánh giá", f"{config.get('n_users_evaluated', 'N/A')}")
    if config:
        st.caption(f"Config: {config}")

    models_data = ranking_metrics.get("models", {}) or {}
    model_order = ["popularity", "content_based", "item_cf", "svd", "hybrid"]
    model_names = {
        "popularity": "Popularity",
        "content_based": "Content-Based",
        "item_cf": "Item-CF",
        "svd": "SVD",
        "hybrid": "Hybrid",
    }

    rows = []
    for model_key in model_order:
        m = models_data.get(model_key)
        if not m:
            continue
        rows.append(
            {
                "Model": model_names.get(model_key, model_key),
                "Precision@5": m.get("precision@5"),
                "Precision@10": m.get("precision@10"),
                "Recall@10": m.get("recall@10"),
                "NDCG@10": m.get("ndcg@10"),
                "Coverage@10": m.get("coverage@10"),
            }
        )

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Không có dữ liệu so sánh cho các model.")

    st.caption(
        "5 phương pháp; test set; relevance >= 4.0; không so sánh trực tiếp score"
    )
