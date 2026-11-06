import streamlit as st

st.set_page_config(page_title="So sánh phương pháp", layout="wide")

st.title("So sánh phương pháp")
st.info(
    "Trang này sẽ so sánh Content-Based, Item-CF, SVD và Hybrid từ Day 2-4."
)
st.markdown(
    "- Day 2: Content-Based Filtering\n"
    "- Day 3: Item-CF và ranking metrics\n"
    "- Day 4: SVD và Hybrid"
)
