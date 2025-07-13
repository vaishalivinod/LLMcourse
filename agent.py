import requests
import re
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    torch_dtype=torch.float16,
    device_map="auto"
)

class EEGReviewAgent:
    def __init__(self):
        self.papers = []

    def search(self, query):
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,abstract,url"
        response = requests.get(url)
        self.papers = response.json().get("data", [])
        return self.papers

    def extract_methods(self, papers):
        methods = []
        for p in papers:
            if "abstract" in p:
                text = p["abstract"]
                match = re.search(r"(methods?|procedure)[\s\S]+", text, re.IGNORECASE)
                if match:
                    methods.append(match.group(0))
                else:
                    methods.append(text)
        return methods

    def summarize(self, texts):
        prompt = "Summarize EEG preprocessing steps used in these abstracts:\n\n" + "\n\n".join(texts)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096).to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=300)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    def run(self, dataset_type, goal):
        query = f"{dataset_type} EEG {goal} preprocessing"
        papers = self.search(query)
        methods = self.extract_methods(papers)
        summary = self.summarize(methods)
        return summary, papers
