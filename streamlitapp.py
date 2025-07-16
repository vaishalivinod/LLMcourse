# streamlitapp.py
import streamlit as st
from agent import EEGReviewAgent

st.title("🧠 EEG Literature Review Agent")

keywords = st.text_input("Enter search keywords (comma-separated):", "EEG, deep learning")
agent = EEGReviewAgent()

if st.button("Run Agent"):
    with st.spinner("Running literature review..."):
        keyword_list = [kw.strip() for kw in keywords.split(",")]
        results = agent.run(keyword_list)

    st.success(f"Found {len(results)} papers with Methods sections.")
    for pmc_id, methods in results:
        st.subheader(f"PMC ID: {pmc_id}")
        st.text_area("Methods Section", methods, height=200)
