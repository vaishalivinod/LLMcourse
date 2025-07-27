import streamlit as st
import requests
import xml.etree.ElementTree as ET
import re
from thefuzz import fuzz
from transformers import pipeline

st.set_page_config(page_title="AI Agent for Method Extraction", layout="wide")
st.title("🧠 AI Agent for Neuroscience Methods Extraction")

SIMILARITY_THRESHOLD = 65
METHODS_TITLES = {"methods", "materials and methods", "methodology", "experimental procedure"}

@st.cache_data
def get_mesh_terms(keyword):
    try:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=mesh&term={keyword}&retmode=xml"
        resp = requests.get(url, timeout=10)
        root = ET.fromstring(resp.content)
        qt = root.find('.//QueryTranslation')
        if qt is None:
            return []
        return re.findall(r'"([^"]+)"\[MeSH Terms\]', qt.text)[:5]
    except Exception as e:
        return []

def build_enhanced_query(keywords):
    parts = []
    for kw in keywords:
        mesh = get_mesh_terms(kw)
        terms = [f'"{kw}"[Title/Abstract]'] + [f'"{m}"[MeSH Terms]' for m in mesh]
        parts.append("(" + " OR ".join(terms) + ")")
    return " AND ".join(parts)

def search_pmc_by_keyword(keywords):
    query = build_enhanced_query(keywords)
    query += " AND open access[filter]"
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pmc&term={requests.utils.quote(query)}&retmode=xml&retmax=100"
    )
    resp = requests.get(url)
    
    # ✅ Check for errors
    if resp.status_code != 200:
        print(f"[ERROR] HTTP {resp.status_code}")
        return []

    if not resp.text.strip().startswith('<?xml'):
        print("[ERROR] Response is not valid XML.")
        print(resp.text[:200])  # Optional: show part of the response
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        print(f"[ERROR] XML parsing failed: {e}")
        return []

    ids = [id_tag.text for id_tag in root.findall('.//IdList/Id')]
    print(f"[search_pmc] PMC IDs found: {ids}")
    return ids


def fetch_full_text(pmc_id):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc_id}&retmode=xml"
    resp = requests.get(url)

    if resp.status_code != 200 or not resp.text.strip().startswith('<?xml'):
        print(f"[fetch_full_text] Failed for {pmc_id}: HTTP {resp.status_code}")
        return None

    return resp.text


def extract_methods_section(xml_content):
    try:
        root = ET.fromstring(xml_content)
        methods_sections = []
        for sec in root.findall(".//sec"):
            title_elem = sec.find("title")
            if title_elem is not None and title_elem.text:
                title = title_elem.text.strip()
                score = max(fuzz.ratio(title.lower(), mt) for mt in METHODS_TITLES)
                if score >= SIMILARITY_THRESHOLD:
                    section_text = extract_text_from_section(sec)
                    if section_text:
                        methods_sections.append(section_text)
        return "\n\n".join(methods_sections) if methods_sections else None
    except ET.ParseError:
        return None

def extract_text_from_section(section):
    lines = []
    for elem in section.iter():
        if elem.tag not in ("title", "sec"):
            if elem.text and elem.text.strip():
                lines.append(elem.text.strip())
            if elem.tail and elem.tail.strip():
                lines.append(elem.tail.strip())
    return "\n".join(lines).strip()

# QA Model for extraction
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

questions = {
    "Cohort": "What kind of participants were in the study?",
    "Participants": "How many participants were included?",
    "EEG Channels": "How many EEG channels were used?",
    "Analysis Tool": "What programming or software package was used for analysis?"
}

# --- Streamlit Interface ---
keywords = st.text_input("🔍 Enter keywords", value="EEG oddball")
if st.button("Run Agent"):
    with st.spinner("Running agent..."):
        ids = search_pmc_by_keyword(keywords.split())
        if not ids:
            st.warning("No open access articles found.")
        else:
            st.success(f"Found {len(ids)} articles.")
            data = []

            for pmc_id in ids:
                xml = fetch_full_text(pmc_id)
                if not xml:
                    continue
                methods = extract_methods_section(xml)
                if not methods:
                    continue
                row = {"PMC ID": pmc_id}
                for key, question in questions.items():
                    try:
                        answer = qa_pipeline(question=question, context=methods)
                        row[key] = answer["answer"]
                    except:
                        row[key] = "Not found"
                data.append(row)

            if data:
                st.dataframe(data)
            else:
                st.warning("Could not extract method sections.")
