import streamlit as st

st.set_page_config(page_title="Compare Methods", layout="wide")

st.title("⚖️ So sánh phương pháp")

st.markdown("### Trạng thái các phương pháp gợi ý (Day 2)")

st.markdown(
    "- Popularity (Đã có - Day 1)\n"
    "- Content-Based (Đã có - Day 2)\n"
    "- Item-CF / SVD / Hybrid (Sẽ làm ở Day 3–4)"
)

st.success("Đã có: Popularity (Đã có - Day 1), Content-Based (Đã có - Day 2).")

st.info(
    "Item-CF / SVD / Hybrid (Sẽ làm ở Day 3–4) sẽ được bổ sung ở Day 3-4. "
    "Content-Based (Đã có - Day 2) là phương pháp mới được hỗ trợ trong Day 2."
)
