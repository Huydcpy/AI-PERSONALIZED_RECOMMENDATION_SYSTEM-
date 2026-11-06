"""Movie card rendering helpers."""

import streamlit as st

GENRES = (
    "unknown",
    "action",
    "adventure",
    "animation",
    "children",
    "comedy",
    "crime",
    "documentary",
    "drama",
    "fantasy",
    "film_noir",
    "horror",
    "musical",
    "mystery",
    "romance",
    "sci_fi",
    "thriller",
    "war",
    "western",
)


def format_genres(movie: dict) -> str:
    """Return a human-readable genre list from MovieLens flags."""
    genres = [
        genre.replace("_", " ").title()
        for genre in GENRES
        if genre != "unknown" and movie.get(genre) == 1
    ]
    return ", ".join(genres) if genres else "N/A"


def render_movie_card(
    movie: dict, score: float, reason: str | None = None
) -> None:
    """Render one recommendation card."""
    title = movie.get("title") or "Không rõ"
    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.caption(
            f"ID: {movie.get('movie_id', 'N/A')} | "
            f"Thể loại: {format_genres(movie)}"
        )
        st.metric("Điểm", f"{score:.3f}")
        if reason:
            st.info(f"Lý do: {reason}")
