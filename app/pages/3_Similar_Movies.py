import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from app.components.movie_card import render_movie_card
from src.service.recommender_service import RecommenderService

st.set_page_config(page_title="Similar Movies", layout="wide")

@st.cache_resource
def get_service():
    return RecommenderService()

try:
    service = get_service()
except Exception as e:
    service = None
    st.warning(f"Không thể khởi tạo service: {e}")

st.title("🔍 Phim Tương Tự")

movie_id = st.number_input("Nhập Movie ID:", min_value=1, value=1)
k = st.slider("Số lượng phim tương tự:", 5, 20, 10)

if st.button("Tìm phim tương tự"):
    if service is None:
        st.warning("Service chưa sẵn sàng. Vui lòng thử lại sau.")
    else:
        try:
            recs = service.similar_items(movie_id, k=k)
        except Exception as e:
            st.warning(
                f"Không tìm thấy phim tương tự cho Movie ID {movie_id}: {e}"
            )
        else:
            if not recs:
                st.warning(
                    f"Không tìm thấy phim tương tự cho Movie ID {movie_id}. "
                    "Vui lòng thử Movie ID khác."
                )
            else:
                for rec in recs:
                    if isinstance(rec, dict):
                        rec_movie_id = rec.get("movie_id")
                        title = rec.get("title", "")
                        score = rec.get("score", 0.0)
                        reason = rec.get("reason")
                        genres = rec.get("genres") or rec.get("genre") or ""
                    else:
                        rec_movie_id = rec.movie_id
                        title = rec.title
                        score = rec.score
                        reason = rec.reason
                        genres = getattr(rec, "genres", "") or getattr(rec, "genre", "") or ""

                    if reason:
                        raw_reason = str(reason).strip()
                        if raw_reason.startswith("Cùng thể loại"):
                            display_reason = raw_reason
                        else:
                            display_reason = f"Cùng thể loại: {raw_reason}"
                    elif genres:
                        display_reason = f"Cùng thể loại: {genres}"
                    else:
                        display_reason = "Cùng thể loại: ..."

                    render_movie_card(
                        rec_movie_id, title, score, genres=genres, reason=display_reason
                    )
