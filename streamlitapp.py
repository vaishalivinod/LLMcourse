import streamlit as st
from agent import retrieve_methods_sections
from parser import LLMParser

# Page config
st.set_page_config(page_title="EEG Agent", layout="wide")

st.title("🧠 EEG AI Agent - Visual Oddball Analyzer")
st.markdown("Analyze EEG preprocessing methods using an autonomous LLM agent.")

# Input
keywords = st.text_input("Enter search keywords (comma-separated):", "EEG, visual oddball")

if st.button("Run Agent"):
    with st.spinner("Running agent... please wait."):
        # Run retrieval
        kw_list = [k.strip() for k in keywords.split(",")]
        raw_results = retrieve_methods_sections(kw_list)

        if not raw_results:
            st.warning("No methods sections were extracted.")
        else:
            # Load parser
            parser = LLMParser(st.secrets["HF_API_KEY"])
            for pmc_id, method_text in raw_results.items():
                st.subheader(f"📄 PMC ID: {pmc_id}")

                # Fake metadata (for demo)
                metadata = {
                    "PMCID": pmc_id,
                    "PMID": "",
                    "title": f"EEG Study {pmc_id}",
                    "authors": "Unknown",
                    "year": "Unknown"
                }

                parsed = parser.parse_methods(metadata, method_text)
                if parsed:
                    st.json(parsed)
                else:
                    st.error("Failed to parse methods with LLM.")
