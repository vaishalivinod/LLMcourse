import streamlit as st
from agent import EEGReviewAgent

st.title("🧠 EEG Literature Review Agent")
api_key = st.secrets["HF_API_KEY"]

dataset_type = st.text_input("Dataset Type (e.g., visual oddball, P300)")
research_goal = st.text_input("Research Goal (e.g., event-related potentials)")

if st.button("Generate Preprocessing Summary"):
    agent = EEGReviewAgent(api_key)
    results = agent.run(dataset_type, research_goal)

    for res in results:
        st.subheader(res["title"])
        st.markdown(f"**Authors:** {', '.join(res['authors'])}")
        st.markdown(f"**Year:** {res['year']}")
        st.json(res)
