"""Cached service accessors for the Streamlit app."""

import streamlit as st

from src.service.recommender_service import RecommenderService


@st.cache_resource
def get_service() -> RecommenderService:
    """Return a cached RecommenderService instance."""
    return RecommenderService()


@st.cache_data(ttl=60)
def get_metrics() -> dict:
    """Return cached baseline metrics."""
    return get_service().get_baseline_metrics()


@st.cache_data(ttl=60)
def get_svd_metrics() -> dict:
    return get_service().get_svd_metrics()
