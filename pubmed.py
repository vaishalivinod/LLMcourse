import requests
import xml.etree.ElementTree as ET
import re
from thefuzz import fuzz

SIMILARITY_THRESHOLD = 65
METHODS_TITLES = {"methods", "materials and methods", "methodology", "experimental procedure"}

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
        print(f"[MeSH] Error: {e}")
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
    root = ET.fromstring(resp.content)
    ids = [id_tag.text for id_tag in root.findall('.//IdList/Id')]
    print(f"[search_pmc] PMC IDs found: {ids}")
    return ids

def fetch_full_text(pmc_id):
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        f"?db=pmc&id={pmc_id}&retmode=xml"
    )
    resp = requests.get(url)
    if resp.status_code != 200 or not resp.text.strip().startswith('<?xml'):
        print(f"[fetch_full_text_pmc] Bad XML or HTTP {resp.status_code} for {pmc_id}")
        return None
    return resp.text

def extract_methods_section(xml_content, verbose=False):
    try:
        root = ET.fromstring(xml_content)
        methods_sections = []  # ← This is the missing line

        for sec in root.findall(".//sec"):
            title_elem = sec.find("title")
            if title_elem is not None and title_elem.text:
                title = title_elem.text.strip()
                score = max(fuzz.ratio(title.lower(), mt) for mt in METHODS_TITLES)
                if verbose:
                    print(f"    Title: {title} | Match score: {score}")
                if score >= SIMILARITY_THRESHOLD:
                    section_text = extract_text_from_section(sec)
                    if section_text:
                        methods_sections.append(section_text)
            elif verbose:
                print("    [Skip] Section without title")

        return "\n\n".join(methods_sections) if methods_sections else None

    except ET.ParseError as e:
        if verbose:
            print(f"  XML parsing error: {e}")
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

def extract_metadata(root, pmc_id):
    pmid = root.findtext('.//article-id[@pub-id-type="pmid"]', default="")
    title = root.findtext('.//article-title', default="")
    authors = [" ".join(filter(None, [a.findtext('given-names',''), a.findtext('surname','')])) 
               for a in root.findall('.//contrib[@contrib-type="author"]')]
    year = root.findtext('.//pub-date/year','')
    return {"PMCID": pmc_id, "PMID": pmid, "title": title, "authors": authors, "year": year}
