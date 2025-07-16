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

    TEMPLATE = """
    You are a literature analysis agent helping an EEG researcher. For the following paper, extract as much structured information as possible based on this JSON schema.

    If a field is not mentioned, leave it as an empty string.

    JSON Template:
    {
    "title": "{title}",
    "authors": "{authors}",
    "year": "{year}",

    "study": {
        "cohort": "",
        "EEG channels": "",
        "dual-layer EEG": "",
        "EEG system": "",
        "sampling frequency": "",
        "task": "",
        "secondary task": "",
        "EEG analysis software": ""
    },

    "preprocessing": {
        "channel rejection": "",
        "segment rejection": "",
        "downsampling" : "",
        "band-pass filter": "",
        "high-pass filter": "",
        "low-pass filter": "",
        "band-stop filter": "",
        "re-referencing": "",
        "line noise removal": "",
        "interpolation": "",
        "epoching": "",
        "ASR": "",
        "ICA": "",
        "dipfit": "",
        "ICLabel": "",
        "reject ICs segments": "",
        "select ICA weights": "",
        "IC clustering": ""
    },
    
    "processing": {
        "ERSP": "",
        "PSD": "",
        "corticomuscular coherence": "",
        "cortical connectivity": "",
        "fast fourier transform": "",
        "time frequency analysis": "",
        "frequency bands": ""      
    }
    }

    Paper Text:
    Title: {title}
    Authors: {authors}
    Year: {year}
    Abstract: {abstract}

    Please return the filled JSON only.
    """
    
    def summarize(self, papers):
        filled_jsons = []
        for paper in papers[:5]:
            title = paper.get("title", "")
            authors = ", ".join(paper.get("authors", []))
            year = paper.get("year", "")
            abstract = paper.get("abstract", "")

            prompt = TEMPLATE.format(title=title, authors=authors, year=year, abstract=abstract)

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 1024, "temperature": 0.3}
            }

            try:
                response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
                output = response.json()

                if isinstance(output, dict) and "error" in output:
                    filled_jsons.append({"error": output["error"]})
                else:
                    generated_text = output[0]["generated_text"]
                    try:
                        parsed = json.loads(generated_text)  # try parsing LLM response
                        filled_jsons.append(parsed)
                    except json.JSONDecodeError:
                        filled_jsons.append({"raw_response": generated_text})

            except Exception as e:
                filled_jsons.append({"error": str(e)})

        return filled_jsons

    def run(self, dataset_type, goal):
        query = f"{dataset_type} EEG {goal} preprocessing"
        papers = self.search(query)
        methods = self.extract_methods(papers)
        summary = self.summarize(methods)
        return summary, papers

