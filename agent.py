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

    def search_semantic_scholar(self, dataset_type, research_goal):
        query = f"{dataset_type} EEG {research_goal} preprocessing"
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,abstract,url"
        response = requests.get(url)
        self.papers = response.json().get("data", [])
        return self.papers

    def extract_methods_sections(self, papers):
        methods_sections = []
        for paper in papers:
            if "abstract" in paper:
                text = paper["abstract"]
                methods = self._extract_methods_from_text(text)
                if methods:
                    methods_sections.append(methods)
        return methods_sections

    def _extract_methods_from_text(self, text):
        pattern = re.compile(r"(methods?|methodology|procedure)\s*[:\n]", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return text[match.start():]
        return text  # fallback

    def summarize_preprocessing(self, methods_sections):
        combined_text = "\n\n".join(methods_sections)
        prompt = f"### Instruction:\nExtract and summarize the EEG preprocessing steps from these studies:\n\n{combined_text}\n\n### Response:"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096).to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=500)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    def run(self, dataset_type, research_goal):
        papers = self.search_semantic_scholar(dataset_type, research_goal)
        methods_texts = self.extract_methods_sections(papers)
        summary = self.summarize_preprocessing(methods_texts)
        return summary, papers
