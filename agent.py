from pubmed import search_pmc_by_keyword, fetch_full_text_pmc, extract_methods_section, extract_metadata
from parser import LLMParser
import xml.etree.ElementTree as ET

class EEGReviewAgent:
    def __init__(self, hf_api_key):
        self.parser = LLMParser(hf_api_key)

    def run(self, keywords):
        pmc_ids = search_pmc_by_keyword(keywords)
        results = []
        for pmc in pmc_ids[:10]:
            xml = fetch_full_text_pmc(pmc)
            if not xml: continue
            methods = extract_methods_section(xml)
            if not methods: continue
            root = ET.fromstring(xml)
            meta = extract_metadata(root, pmc)
            record = self.parser.parse_methods(meta, methods)
            if record:
                results.append(record)
        return results