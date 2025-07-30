import streamlit as st
from utils.article_fetcher import search_pmc_by_keyword, fetch_full_text_pmc, read_txt_files
from utils.saveas import save_xml, save_csv
from utils.log_search import keywords_to_ids
from utils.methodstext import extract_methods
from utils.llm import extract_parameters
from utils.config import dir_fulltexts, dir_log_results, dir_researcharticles, dir_methods
from utils.prompts import study_prompts, gait_eeg_prompts
from utils.article_fetcher import filter_research_articles
import pandas as pd

st.set_page_config(page_title="EEG Agent", layout="wide")
st.title("🧠 AI Agent for EEG Literature Extraction")

keywords = st.text_input("Enter keywords (separated by commas)", "Mobile-EEG, Gait")

if st.button("Run Extraction"):
    keywords_list = [k.strip() for k in keywords.split(",")]
    log_file_path = dir_log_results / "keyword_overview.txt"

    with st.spinner("🔍 Searching PMC for articles..."):
        pmc_ids = search_pmc_by_keyword(keywords_list)
    
    if not pmc_ids:
        st.error("No PMC articles found.")
        st.stop()

    st.success(f"✅ Found {len(pmc_ids)} articles.")

    with st.spinner("📥 Downloading full text XMLs..."):
        for pmc_id in pmc_ids:
            full_text = fetch_full_text_pmc(pmc_id)
            if full_text:
                save_xml(pmc_id, full_text, dir_fulltexts)

    with st.spinner("🧪 Filtering research articles..."):
        filter_research_articles(dir_fulltexts, dir_researcharticles)

    with st.spinner("✂️ Extracting methods sections..."):
        extract_methods(input_folder=dir_researcharticles, output_folder=dir_methods)

    with st.spinner("🧠 Extracting study and preprocessing parameters..."):
        txt_files = read_txt_files(dir_methods)
        results = {}

        for file, context in txt_files.items():
            if context.strip():
                file_results = {}
                file_results.update(extract_parameters(context, study_prompts))
                file_results.update(extract_parameters(context, gait_eeg_prompts))
                results[file] = file_results

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(results, orient='index')
    st.success("✅ Extraction completed.")

    st.dataframe(df)

    # Optional save to download
    save_csv(results, "preprocessing_gaiteeg.csv")
    st.download_button("⬇️ Download CSV", data=df.to_csv(), file_name="results.csv", mime="text/csv")
