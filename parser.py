import os
import requests
import re
import json

# JSON schema template for EEG preprocessing
JSON_TEMPLATE = {
    "PMCID": "",
    "PMID": "",
    "title": "",
    "authors": "",
    "year": "",
    "study": {
        "cohort": "", "EEG channels": "", "dual-layer EEG": "",
        "EEG system": "", "sampling frequency": "", "task": "",
        "secondary task": "", "EEG analysis software": ""
    },
    "preprocessing": {
        "channel rejection": "", "segment rejection": "", "downsampling": "",
        "band-pass filter": "", "high-pass filter": "", "low-pass filter": "",
        "band-stop filter": "", "re-referencing": "", "line noise removal": "",
        "interpolation": "", "epoching": "", "ASR": "", "ICA": "",
        "dipfit": "", "ICLabel": "", "reject ICs segments": "",
        "select ICA weights": "", "IC clustering": ""
    },
    "processing": {
        "ERSP": "", "PSD": "", "corticomuscular coherence": "",
        "cortical connectivity": "", "fast fourier transform": "",
        "time frequency analysis": "", "frequency bands": "",
        "IC clustering": ""
    }
}

class LLMParser:
    def __init__(self, hf_api_key, model_id="mistralai/Mistral-7B-Instruct-v0.1"):
        self.endpoint = f"https://api-inference.huggingface.co/models/{model_id}"
        self.headers = {"Authorization": f"Bearer {hf_api_key}"}

    def parse_methods(self, metadata: dict, methods_text: str) -> dict:
        prompt = f"""
You are an EEG preprocessing extraction assistant. Given the following metadata and Methods section, return an exact JSON matching the schema below. If a field isn't present, leave it as an empty string.

Schema:
{json.dumps(JSON_TEMPLATE, indent=2)}

Article Metadata:
PMCID: {metadata.get('PMCID','')}
PMID: {metadata.get('PMID','')}
title: {metadata.get('title','')}
authors: {metadata.get('authors','')}
year: {metadata.get('year','')}

Methods Section:
{methods_text}

Return ONLY valid JSON following the schema.
"""
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 512, "temperature": 0.1},
            "options": {"wait_for_model": True}
        }
        resp = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=60)
        try:
            out = resp.json()
            if isinstance(out, dict) and "error" in out:
                raise ValueError(out["error"])

            text = out[0]["generated_text"]

            # Extract JSON from text (attempt to find {...} block)
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if not json_match:
                print("LLM parse error: No JSON found in response")
                return {}

            json_text = json_match.group(0)
            return json.loads(json_text)

        except Exception as e:
            print("LLM parse error:", e)
            return {}
