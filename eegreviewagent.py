import os
import xml.etree.ElementTree as ET
from pubmed import search_pmc_by_keyword fetch_full_text, extract_metadata, extract_methods_section
from parser import LLMParser

class EEGReviewAgent:
    def __init__(self, hf_api_key):
        self.hf_api_key = hf_api_key
        self.parser = LLMParser(hf_api_key)

    def run(self, keywords):
        results = {}
        print(f"Formulating query for keywords: {keywords}")
        pmc_ids = search_pmc_by_keyword(keywords)
        print(f"[search_pmc] PMC IDs found: {pmc_ids}")

        for pmc_id in pmc_ids:
            print(f"\nFetching PMC ID: {pmc_id}")
            xml = fetch_full_text(pmc_id)
            if not xml:
                print(f"  [Skip] No full text for {pmc_id}")
                continue

            methods_text = extract_methods_section(xml, verbose=True)
            if not methods_text:
                print(f"  [Skip] No methods section found in {pmc_id}")
                continue

            root = ET.fromstring(xml)
            metadata = extract_metadata(root, pmc_id)

            # Parse methods with LLMParser
            print(f"  Parsing methods section with LLM parser...")
            parsed_data = self.parser.parse_methods(metadata, methods_text)

            if parsed_data:
                results[pmc_id] = parsed_data
            else:
                print(f"  [Warning] LLM parser returned empty or invalid data for {pmc_id}")

        return results


if __name__ == "__main__":
    hf_api_key = os.getenv("HF_API_KEY") or input("Enter your Hugging Face API key: ")
    agent = EEGReviewAgent(hf_api_key)

    keywords = ["EEG", "visual oddball"]
    records = agent.run(keywords)

    if not records:
        print("\nNo methods sections extracted.")
    else:
        print("\n--- Extracted Preprocessing Info ---")
        import json
        print(json.dumps(records, indent=2))
