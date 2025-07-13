import requests
import os

class EEGReviewAgent:
    def __init__(self):
        self.api_key = os.getenv("HF_API_KEY")
        self.model_id = "mistralai/Mistral-7B-Instruct-v0.2"
        self.endpoint = f"https://api-inference.huggingface.co/models/{self.model_id}"

    def search(self, query):
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,abstract,url"
        res = requests.get(url)
        return res.json().get("data", [])

    def extract_methods(self, papers):
        methods = []
        for p in papers:
            abstract = p.get("abstract", "")
            if abstract:  # Only add if not empty
                methods.append(str(abstract))
        return methods


    def summarize(self, texts):
        prompt = f"### Instruction:\nSummarize EEG preprocessing steps from these papers:\n\n" + "\n\n".join(texts) + "\n\n### Response:\n"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 512, "temperature": 0.7}
        }
        response = requests.post(self.endpoint, headers=headers, json=payload)
        output = response.json()

        if isinstance(output, dict) and "error" in output:
            return f"⚠️ Error from Hugging Face API: {output['error']}"

        return output[0]["generated_text"]

    def run(self, dataset_type, goal):
        query = f"{dataset_type} EEG {goal} preprocessing"
        papers = self.search(query)
        methods = self.extract_methods(papers)
        summary = self.summarize(methods)
        return summary, papers

