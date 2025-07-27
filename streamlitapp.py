import streamlit as st
import requests
import xml.etree.ElementTree as ET
import re

st.title("🧠 Neurosift: Extract Methods Info from Open PMC Articles")

# ----------- Search Function -----------
def search_pmc_articles(keywords, max_results=5):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    # Use Entrez-compatible syntax: keyword1[Title/Abstract] AND keyword2[Title/Abstract]
    query_parts = [f"{word}[Title/Abstract]" for word in keywords.split()]
    query = " AND ".join(query_parts)

    params = {
        "db": "pmc",
        "term": query,
        "retmode": "xml",
        "retmax": max_results
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        # Check if result is valid XML
        if not response.content.strip().startswith(b"<?xml"):
            raise ValueError("Invalid response from NCBI")

        root = ET.fromstring(response.content)
        return [id_tag.text for id_tag in root.findall(".//Id")]
    except Exception as e:
        st.error(f"❌ Error fetching PMC articles: {e}")
        return []

# ----------- Fetch Full XML -----------
def fetch_article_xml(pmcid):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pmc",
        "id": pmcid,
        "retmode": "xml"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200 and resp.text.strip().startswith("<?xml"):
            return resp.text
    except:
        return None
    return None

# ----------- Extract Methods Section -----------
def extract_methods_text(xml_content):
    try:
        root = ET.fromstring(xml_content)
        methods_sections = []
        for sec in root.findall(".//sec"):
            title_elem = sec.find("title")
            if title_elem is not None and "method" in title_elem.text.lower():
                paragraphs = [p.text.strip() for p in sec.findall(".//p") if p.text]
                methods_sections.append("\n".join(paragraphs))
        return "\n\n".join(methods_sections) if methods_sections else None
    except ET.ParseError:
        return None

# ----------- Extract Structured Fields -----------
def extract_fields(text):
    def match(pattern):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1) if m else ""

    return {
        "Study cohort": match(r"cohort.*?(\d+[^.,;\n]*)"),
        "Participants": match(r"(\d+)\s+(participants|subjects)"),
        "EEG channels": match(r"(\d+)\s+(channels|electrodes)"),
        "Analysis software": match(r"(EEGLAB|MNE|BrainVision|FieldTrip|SPM|Python|Matlab)")
    }

# ----------- UI -----------
keywords = st.text_input("Enter keywords (e.g. EEG visual oddball):")

if st.button("Search & Extract"):
    if not keywords.strip():
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        st.info("🔍 Searching for articles...")
        pmc_ids = search_pmc_articles(keywords)

        if not pmc_ids:
            st.error("❌ No articles found.")
        else:
            results = []
            for pmc_id in pmc_ids:
                xml = fetch_article_xml(pmc_id)
                if not xml:
                    continue
                methods_text = extract_methods_text(xml)
                if not methods_text:
                    continue
                fields = extract_fields(methods_text)
                fields["PMCID"] = pmc_id
                results.append(fields)

            if results:
                st.success(f"✅ Found {len(results)} articles with extractable Methods sections.")
                st.dataframe(results)
            else:
                st.error("❌ No usable Methods sections found.")
