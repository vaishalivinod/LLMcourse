import streamlit as st
from agent import EEGReviewAgent

st.set_page_config(page_title="EEG Preprocessing Literature Agent", layout="wide")

st.title("🧠 EEG Literature Review Agent")
st.markdown("This agent helps you identify typical EEG preprocessing pipelines from the literature based on your dataset and objective.")

# Step 1: Collect inputs
dataset_type = st.text_input("Describe your EEG dataset", placeholder="e.g., visual oddball")
research_goal = st.text_input("What EEG feature are you analyzing?", placeholder="e.g., P300")

run_button = st.button("Run Literature Review")

# Step 2: Run agent
if run_button and dataset_type and research_goal:
    with st.spinner("Thinking... 🧠 Searching the literature and analyzing papers..."):
        agent = EEGReviewAgent()
        summary, raw_papers = agent.run(dataset_type, research_goal)

        st.subheader("📋 Suggested Preprocessing Pipeline")
        st.markdown(summary)

        st.subheader("📚 Papers Used")
        for paper in raw_papers:
            st.markdown(f"- [{paper['title']}]({paper['url']})")

