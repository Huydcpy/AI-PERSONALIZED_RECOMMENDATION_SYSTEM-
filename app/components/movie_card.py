import streamlit as st


def render_movie_card(movie_id: int, title: str, score: float, genres: str = "", reason: str | None = None):
    with st.container(border=True):
        st.markdown(f"#### 🎬 {title}")
        st.caption(f"ID: {movie_id} | Thể loại: {genres if genres else 'N/A'}")
        st.metric("Score", f"{score:.3f}")
        if reason:
            st.info(f"💡 Lý do: {reason}")
