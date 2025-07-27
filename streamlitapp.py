import streamlit as st
import requests
import xml.etree.ElementTree as ET
import re

st.title("🧠 Neurosift: AI Agent for Method Extraction from PMC")

# --- Function to search PMC for open-access articles ---
def search_pmc_articles(keywords, max_results=5):
    query = "+AND+".join(keywords.split()) + "+AND+open+access[filter]"
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term={query}&retmode=xml&retmax={max_results}"
    resp = requests.get(url)

    if resp.status_code != 200 or not resp.text.startswith("<?xml"):
        st.error("❌ Failed to fetch search results.")
        return []

    root = ET.fromstring(resp.content)
    return [id_tag.text for id_tag in root.findall(".//Id")]

# --- Function to fetch article full-text XML ---
def fetch_article_xml(pmcid):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid}&retmode=xml"
    resp = requests.get(url)
    if resp.status_code != 200 or not resp.text.startswith("<?xml"):
        return None
    return resp.text

# --- Function to extract Methods section ---
def extract_methods_text(xml_content):
    try:
        root = ET.fromstring(xml_content)
        sections = []
        for sec in root.findall(".//sec"):
            title = sec.find("title")
            if title is not None and "method" in title.text.lower():
                paragraphs = [elem.text.strip() for elem in sec.findall(".//p") if elem.text]
                sections.append("\n".join(paragraphs))
        return "\n\n".join(sections) if sections else None
    except ET.ParseError:
        return None

# --- Function to extract fields from Methods ---
def extract_fields(text):
    def find(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else ""
    
    return {
        "Study cohort": find(r"(cohort|participants) (included|consisted of|comprised|were) ([^.]+)"),
        "Number of participants": find(r"(\d+)\s+(participants|subjects)"),
        "EEG channels": find(r"(\d+)\s+(EEG channels|electrodes)"),
        "Analysis package": find(r"(EEGLAB|MNE|BrainVision|FieldTrip|SPM|Python|Matlab)")
    }

# --- Streamlit interface ---
keywords = st.text_input("Enter keywords (e.g. EEG visual oddball):")

if st.button("Search"):
    if not keywords:
        st.warning("Please enter keywords.")
    else:
        st.info("🔍 Searching for open-access PMC articles...")
        ids = search_pmc_articles(keywords)

        if not ids:
            st.error("❌ No articles found.")
        else:
            data = []
            for pmcid in ids:
                xml = fetch_article_xml(pmcid)
                if not xml:
                    continue
                methods = extract_methods_text(xml)
                if not methods:
                    continue
                fields = extract_fields(methods)
                fields["PMCID"] = pmcid
                data.append(fields)

            if data:
                st.success(f"✅ Found {len(data)} articles with Methods sections.")
                st.dataframe(data)
            else:
                st.error("❌ No Methods sections found in full-text XML.")
