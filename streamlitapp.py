import streamlit as st
import requests
from transformers import pipeline

st.title("🧠 AI Agent for Method Extraction from PubMed")
st.markdown("Enter a neuroscience-related keyword to extract study details from PubMed abstracts.")

# Open-source LLM from HuggingFace (distilbart for QA)
extractor = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Function to search PubMed
def search_pubmed(keyword, max_results=5):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": keyword,
        "retmode": "json",
        "retmax": max_results
    }
    r = requests.get(search_url, params=search_params)
    r.raise_for_status()
    ids = r.json().get("esearchresult", {}).get("idlist", [])
    return ids

# Function to fetch abstract
def fetch_abstract(pubmed_id):
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": pubmed_id,
        "retmode": "xml"
    }
    r = requests.get(fetch_url, params=fetch_params)
    if r.status_code == 200:
        from xml.etree import ElementTree as ET
        tree = ET.fromstring(r.content)
        abstract = tree.findtext(".//AbstractText")
        return abstract
    return None

# Questions for the LLM
questions = {
    "Cohort": "What kind of participants or patient group was studied?",
    "Participants": "How many participants were in the study?",
    "EEG Channels": "How many EEG channels were used?",
    "Analysis Package": "What software or toolbox was used for EEG analysis?"
}

# Streamlit Input
keyword = st.text_input("🔎 Enter keyword(s):", value="EEG gait")

if st.button("Search and Extract"):
    with st.spinner("Searching and extracting..."):
        ids = search_pubmed(keyword)
        if not ids:
            st.warning("No articles found.")
        else:
            st.success(f"Found {len(ids)} articles. Extracting info...")

            results = []
            for pubmed_id in ids:
                abstract = fetch_abstract(pubmed_id)
                if not abstract:
                    continue
                row = {"PubMed ID": pubmed_id}
                for label, q in questions.items():
                    try:
                        answer = extractor(question=q, context=abstract)
                        row[label] = answer['answer']
                    except:
                        row[label] = "Not found"
                results.append(row)

            if results:
                st.dataframe(results)
            else:
                st.warning("No abstracts processed.")
