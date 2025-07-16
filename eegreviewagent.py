import os
from pathlib import Path
from pubmed import search_pmc_by_keyword, fetch_full_text_pmc
import xml.etree.ElementTree as ET

def extract_methods_from_xml(xml_content):
    try:
        root = ET.fromstring(xml_content)

        # First, try sec-type='methods'
        methods_sections = root.findall(".//sec[@sec-type='methods']")
        if not methods_sections:
            # Fallback to title='Methods'
            methods_sections = [sec for sec in root.findall(".//sec") if sec.findtext("title", "").strip().lower() == "methods"]

        if not methods_sections:
            return None

        text_parts = []
        for sec in methods_sections:
            for elem in sec.iter():
                if elem.tag not in ['sec', 'title']:
                    if elem.text and elem.text.strip():
                        text_parts.append(elem.text.strip())
                    if elem.tail and elem.tail.strip():
                        text_parts.append(elem.tail.strip())

        return "\n".join(text_parts)

    except Exception as e:
        print(f"[Error] Failed to parse XML: {e}")
        return None

def main():
    # --- Step 1: Define research topic ---
    keywords = ["EEG", "visual oddball"]
    print(f"Formulating query for keywords: {keywords}")

    # --- Step 2: Search PMC ---
    print("[Action] Searching PMC...")
    pmc_ids = search_pmc_by_keyword(keywords)

    if not pmc_ids:
        print("[Observation] No articles found.")
        return

    print(f"[Observation] Found {len(pmc_ids)} articles.")

    # --- Step 3: Fetch and parse articles ---
    extracted_methods = {}
    for pmc_id in pmc_ids[:10]:  # Limit for testing
        print(f"\n[Action] Fetching full text for PMC ID: {pmc_id}")
        xml_content = fetch_full_text_pmc(pmc_id)

        if not xml_content:
            print(f"[Skip] No full text for {pmc_id}")
            continue

        print(f"[Action] Extracting methods for PMC ID: {pmc_id}")
        methods_text = extract_methods_from_xml(xml_content)

        if methods_text:
            extracted_methods[pmc_id] = methods_text
            print(f"[✓] Extracted methods for {pmc_id}")
        else:
            print(f"[Skip] No methods section in {pmc_id}")

    # --- Step 4: Display results ---
    print("\n\n--- Extracted Methods Sections ---")
    for pmc_id, text in extracted_methods.items():
        print(f"\n PMCID: {pmc_id}\n{text[:1000]}...\n")

if __name__ == "__main__":
    main()
