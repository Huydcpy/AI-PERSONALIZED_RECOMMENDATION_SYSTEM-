import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from app.components.movie_card import render_movie_card
from src.service.recommender_service import RecommenderService

st.set_page_config(page_title="Recommendations", layout="wide")


@st.cache_resource
def get_service():
    return RecommenderService()


try:
    service = get_service()
    users = service.list_users()
except Exception as e:
    service = None
    users = []
    st.error(f"Không thể khởi tạo service hoặc tải dữ liệu: {e}")

st.title("🎯 Gợi ý Phim")

user_id = st.selectbox("Chọn User ID:", users if users else [196])

# "Popularity" -> method="popularity"
# "Content-Based" -> method="content_based"
METHOD_OPTIONS = {
    "Popularity": "popularity",
    "Content-Based": "content_based",
}
method_label = st.selectbox(
    "Phương pháp:", ["Popularity", "Content-Based"], index=0
)
method = METHOD_OPTIONS[method_label]

k = st.slider("Số lượng gợi ý (K):", 5, 20, 10)
exclude_seen = st.checkbox("Loại bỏ phim đã xem", value=True)

if st.button("Lấy danh sách gợi ý"):
    if service is None:
        st.error("Service chưa sẵn sàng (chưa có model/data). Vui lòng thử lại sau.")
    else:
        try:
            recs = service.recommend(
                user_id, method=method, k=k, exclude_seen=exclude_seen
            )
        except Exception as e:
            st.error(f"Lỗi khi lấy gợi ý: {e}")
        else:
            if not recs:
                st.warning("Không tìm thấy gợi ý phù hợp hoặc chưa có dữ liệu.")
            else:
                for rec in recs:
                    if isinstance(rec, dict):
                        movie_id = rec.get("movie_id")
                        title = rec.get("title", "")
                        score = rec.get("score", 0.0)
                        rec_method = rec.get("method", method)
                        reason = rec.get("reason")
                    else:
                        movie_id = rec.movie_id
                        title = rec.title
                        score = rec.score
                        rec_method = rec.method
                        reason = rec.reason

                    # Hiển thị đầy đủ method (card không có tham số method)
                    # và reason (nếu có) qua card.
                    st.caption(f"Phương pháp: {rec_method}")

                    if reason:
                        display_reason = (
                            f"Method: {rec_method} — {reason}"
                            if rec_method
                            else str(reason)
                        )
                    else:
                        display_reason = (
                            f"Method: {rec_method}" if rec_method else None
                        )

                    render_movie_card(
                        movie_id, title, score, reason=display_reason
                    )
