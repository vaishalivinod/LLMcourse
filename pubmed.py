# pubmed.py
import requests
from xml.etree import ElementTree as ET

NCBI_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
PMC_OA_BASE = "https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi"

def search_pubmed(query, max_results=5):
    params = {
        "db": "pmc",
        "retmax": max_results,
        "term": query,
        "retmode": "json"
    }
    response = requests.get(NCBI_API + "esearch.fcgi", params=params)
    tree = ET.fromstring(response.text)
    pmc_ids = [id_elem.text for id_elem in tree.findall(".//Id")]
    return pmc_ids

def fetch_full_text(pmc_id):
    params = {
        "verb": "GetRecord",
        "identifier": f'oai:pubmedcentral.nih.gov:{pmc_id}',
        "metadataPrefix": "pmc"
    }
    response = requests.get(PMC_OA_BASE, params=params)
    if response.status_code != 200:
        return None

    try:
        tree = ET.fromstring(response.text)
        ns = {'pmc': 'http://www.openarchives.org/OAI/2.0/'}
        methods_section = []

        for sec in tree.findall(".//sec"):
            title_elem = sec.find("title")
            if title_elem is not None and "method" in title_elem.text.lower():
                methods_section.append(ET.tostring(sec, encoding="unicode"))
        
        return methods_section[0] if methods_section else None
    except Exception as e:
        print("Error parsing PMC:", e)
        return None

def get_metadata(pmc_id):
    params = {
        "db": "pmc",
        "id": pmc_id,
        "retmode": "xml"
    }
    response = requests.get(NCBI_API + "efetch.fcgi", params=params)
    try:
        tree = ET.fromstring(response.text)
        article = tree.find(".//article-title")
        authors = [a.findtext("fore-name", "") + " " + a.findtext("last-name", "") 
                   for a in tree.findall(".//contrib[@contrib-type='author']")]
        year = tree.findtext(".//pub-date/year")
        return {
            "title": article.text if article is not None else "Untitled",
            "authors": authors,
            "year": year,
        }
    except:
        return {}
