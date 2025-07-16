# agent.py
from pubmed import search_pmc, fetch_article_xml, extract_methods_from_tree

class EEGReviewAgent:
    def __init__(self):
        self.memory = []

    def think(self, keywords):
        return f"Formulating query for keywords: {keywords}"

    def act(self, keywords):
        print("[Action] Searching PMC...")
        pmc_ids = search_pmc(keywords)
        print(f"[Observation] Found {len(pmc_ids)} articles.")
        return pmc_ids

    def observe(self, pmc_ids):
        extracted = []
        for pmc_id in pmc_ids:
            tree = fetch_article_xml(pmc_id)
            if tree is None:
                print(f"[Skip] No full text for {pmc_id}")
                continue
            methods_text = extract_methods_from_tree(tree)
            if not methods_text:
                print(f"[Skip] No methods section in {pmc_id}")
                continue
            extracted.append((pmc_id, methods_text))
        return extracted

    def run(self, keywords):
        print(self.think(keywords))
        ids = self.act(keywords)
        return self.observe(ids)
