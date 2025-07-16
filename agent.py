# agent.py
import json
import requests
from pubmed import search_pubmed, fetch_full_text, get_metadata
from typing import List

class EEGReviewAgent:
    def __init__(self, api_key):
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def thought(self, dataset_type, research_goal):
        return f"Searching for EEG papers using '{dataset_type}' for goal '{research_goal}'"

    def action(self, dataset_type, research_goal, n=5):
        query = f"EEG AND {dataset_type} AND {research_goal} AND preprocessing"
        pmc_ids = search_pubmed(query, max_results=n)

        papers = []
        for pmc_id in pmc_ids:
            methods = fetch_full_text(pmc_id)
            if not methods:
                continue
            meta = get_metadata(pmc_id)
            meta["methods"] = methods
            papers.append(meta)
        return papers

    def observation(self, papers: List[dict]):
        filled = []
        for paper in papers:
            prompt = self.make_prompt(paper["methods"])
            response = self.query_llm(prompt)
            try:
                parsed = json.loads(response)
                parsed["title"] = paper.get("title", "")
                parsed["authors"] = paper.get("authors", [])
                parsed["year"] = paper.get("year", "")
                filled.append(parsed)
            except json.JSONDecodeError:
                print("Failed to parse JSON")
        return filled

    def run(self, dataset_type, research_goal):
        print(self.thought(dataset_type, research_goal))
        papers = self.action(dataset_type, research_goal)
        output = self.observation(papers)
        return output

    def make_prompt(self, method_text):
        return f"""Extract EEG preprocessing steps from the Methods section below.
Respond in this JSON format:

{{
  "study": {{
    "cohort": "", "EEG channels": "", "EEG system": "", "sampling frequency": "", "task": "", "EEG analysis software": ""
  }},
  "preprocessing": {{
    "channel rejection": "", "downsampling": "", "filtering": "", "re-referencing": "", "ICA": "", "epoching": "", "interpolation": ""
  }},
  "processing": {{
    "ERSP": "", "PSD": "", "time frequency analysis": "", "frequency bands": ""
  }}
}}

--- METHODS SECTION ---
{method_text}
"""

    def query_llm(self, prompt):
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"inputs": prompt, "parameters": {"temperature": 0.3}}
        )
        try:
            return response.json()[0]["generated_text"]
        except:
            return "Failed to parse LLM response"
