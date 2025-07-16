import requests
import xml.etree.ElementTree as ET
import re
from thefuzz import fuzz

# --- MeSH and Query Optimization ---
def get_mesh_terms(keyword):
    try:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=mesh&term={keyword}&retmode=xml"
        resp = requests.get(url, timeout=10)
        root = ET.fromstring(resp.content)
        qt = root.find('.//QueryTranslation')
        if qt is None:
            return []
        return re.findall(r'"([^"]+)"\\[MeSH Terms\\]', qt.text)[:5]
    except Exception as e:
        print(f"MeSH retrieval error: {e}")
        return []

def build_enhanced_query(keywords):
    query_parts = []
    for kw in keywords:
        terms = [f'"{kw}"[Title/Abstract]'] + [f'"{t}"[MeSH Terms]' for t in get_mesh_terms(kw)]
        query_parts.append(f"({' OR '.join(terms)})")
    return " AND ".join(query_parts)

# --- Search PMC for OA research articles ---
def search_pmc_by_keyword(keywords):
    try:
        query = build_enhanced_query(keywords)
        query += " AND open access[filter]"
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term={requests.utils.quote(query)}&retmode=xml&retmax=100"
        resp = requests.get(url)
        root = ET.fromstring(resp.content)
        return [id_tag.text for id_tag in root.findall('.//IdList/Id')]
    except Exception as e:
        print(f"Search error: {e}")
        return []

# --- Fetch full text of a PMC article ---
def fetch_full_text_pmc(pmc_id):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc_id}&retmode=xml"
    resp = requests.get(url)
    return resp.text if resp.status_code == 200 else None


# Acceptable section titles
METHODS_TITLES = {"methods", "materials and methods", "methodology", "method"}
SIMILARITY_THRESHOLD = 80

def is_methods_section(title):
    return any(fuzz.ratio(title.lower().strip(), ref) >= SIMILARITY_THRESHOLD for ref in METHODS_TITLES)

def extract_text_from_section(section):
    section_text = []
    for elem in section.iter():
        if elem.tag not in ["title", "sec"]:
            if elem.text and elem.text.strip():
                section_text.append(elem.text.strip())
            if elem.tail and elem.tail.strip():
                section_text.append(elem.tail.strip())
    return "\n".join(filter(None, section_text)).strip()

def extract_methods_from_xml(xml_string):
    try:
        root = ET.fromstring(xml_string)
        methods_texts = []

        for section in root.findall(".//sec"):
            title_elem = section.find("title")
            if title_elem is not None and is_methods_section(title_elem.text):
                text = extract_text_from_section(section)
                if text:
                    methods_texts.append(text)

        return "\n\n".join(methods_texts) if methods_texts else None
    except Exception as e:
        print(f"[Error] Failed to parse XML for methods: {e}")
        return None
