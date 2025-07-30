import os
import re
import torch
from dataclasses import dataclass
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer, GPT2Tokenizer, GPT2LMHeadModel, AutoModelForSeq2SeqLM, GPT2ForQuestionAnswering

# ============================ BioBERT  ============================ #
from transformers import pipeline

# Initialize the BioBERT model
biobert = pipeline('question-answering', model='trevorkwan/biomed_bert_squadv2')

def extract_parameters(context, prompts):
    '''
    Extracts parameters from a given text context using BioBERT and specified prompts.

    Args:
        context (str): The text context to process.
        prompts (dict): A dictionary of prompts to query.

    Returns:
        dict: A dictionary with prompt keys and extracted answers.
    '''
    results = {}
    for step, prompt in prompts.items():
        try:
            response = biobert(question=prompt, context=context)
            answer = response.get('answer', '').strip()
            if not answer or len(answer) < 3 or 'not mentioned' in answer.lower():
                answer = 'Not Mentioned'
            results[step] = answer
        except Exception as e:
            print(f'Error during processing | Step: {step} | Error: {e}')
            results[step] = 'Error during processing'
    return results




# ============================ GPT-2  ============================ #
@dataclass
class GPT2:
    model_name: str = "openai-community/gpt2"

    def __post_init__(self):
        """Loads GPT-2 model and tokenizer."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = GPT2ForQuestionAnswering.from_pretrained(self.model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token  # Avoid pad_token warning

    def extract_parameters(self, input_text: str) -> str:
        """Retrieve relevant methods and extract parameters using Flan-T5."""
    
        # Retrieve relevant context
        retrieved_context = self.retriever.retrieve(input_text, top_k=2)
        full_input = f"Context:\n{retrieved_context}\n\nInput:\n{input_text}"

        # Define the prompt explicitly
        prompt = f"""Extract EEG-related parameters from the given text.

        <instructions>
            - Extract only explicitly mentioned parameters.
            - Do NOT infer missing values.
            - Return a JSON-like format, strictly following the example.
            - If a parameter is missing, omit it (do not create empty placeholders).
        </instructions>

        <parameters>
            "num_channels": (number) The number of EEG channels.
            "prog_lang": (string) The programming language used.
            "artifact_correction": (string) The method used for artifact correction.
        </parameters>

        Example output:
        {{
            "num_channels": "12",
            "prog_lang": "Matlab",
            "artifact_correction": "AMICA"
        }}

        Now extract from the following:

        {full_input}
        """

        # Tokenize input text
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)

        # Generate response from model
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_length=256, repetition_penalty=1.2, no_repeat_ngram_size=3)

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


# ============================ Phi-1.5 Extractor ============================ #
@dataclass
class Phi15Extractor:
    model_name: str = "microsoft/phi-1_5"

    def __post_init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, torch_dtype=torch.float16, device_map="auto")

    def extract_info(self, text):
        """Extracts EEG parameters using Phi-1.5."""
        prompt = f"""
        Extract EEG parameters from the text:

        Text:
        {text}

        Answer in JSON format with these keys:
        - "num_channels"
        - "software_used"
        - "analysis_packages"
        - "bandpass_filters"
        - "artifact_correction"
        """
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to("cuda" if torch.cuda.is_available() else "cpu")
        output = self.model.generate(**inputs, max_new_tokens=300)
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)

        extracted_data = {"num_channels": "Not found", "software_used": "Not found",
                          "analysis_packages": "Not found", "bandpass_filters": "Not found",
                          "artifact_correction": "Not found"}

        for line in response.split("\n"):
            for key in extracted_data:
                if key in line:
                    extracted_data[key] = line.split(":")[-1].strip().strip('",')

        return extracted_data


# ============================ SmolLM Extractor ============================ #
@dataclass
class SmolLM:
    """Dataclass for SmolLM initialization with embedded prompt."""
    def __post_init__(self):
        self.model = SmolLM()
        self.prompt_template = """
        <purpose>
            Extract EEG-related parameters of interest from input text
        </purpose>
        <instructions>
            <instruction> Extract only explicitly mentioned parameters.</instruction>
            <instruction> If a parameter is missing, omit it.</instruction>
            <instruction> Return the output in strict JSON format.</instruction>
        </instructions>
        <parameters>
            {{ 
                "num_channels": "number",
                "prog_lang": "string",
                "artifact_correction": "string"
            }}
        </parameters>
        """
    
    def __call__(self, query_text):
        full_prompt = self.prompt_template + "\n" + query_text
        return self.model(full_prompt)
# ============================ TinyLlama ============================ #
@dataclass
class TinyLlama:
    model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

    def __post_init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, torch_dtype=torch.float16, device_map="auto")

    def extract_info(self, text):
        """Extracts EEG parameters using TinyLlama."""
        prompt = f"""
        You are an EEG research expert. Extract:

        - EEG Channels (e.g., 32, 64, 128)
        - Software used (MATLAB, Python, R)
        - Analysis packages (e.g., EEGLAB, MNE-Python, FieldTrip, Brainstorm)
        - Bandpass filters (e.g., 0.1–100 Hz, 1–40 Hz)
        - Artifact correction method (e.g., ICA, PCA)

        **Text:** 
        {text}

        Provide the extracted values in this format:
        EEG Channels: <value>
        Software: <value>
        Analysis Packages: <value>
        Bandpass Filters: <value>
        Artifact Correction: <value>
        """

        input_text = self.tokenizer.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False)
        inputs = self.tokenizer(input_text, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")

        with torch.no_grad():
            output = self.model.generate(**inputs, max_new_tokens=200, pad_token_id=self.tokenizer.eos_token_id)

        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return self.parse_response(response)

    def parse_response(self, response):
        """Parses the response to extract EEG parameters."""
        extracted_data = {"num_channels": "Not found", "software_used": "Not found",
                          "analysis_packages": "Not found", "bandpass_filters": "Not found",
                          "artifact_correction": "Not found"}

        for line in response.split("\n"):
            for key in extracted_data:
                if key.replace("_", " ") in line:
                    extracted_data[key] = line.split(":")[-1].strip()
        return extracted_data

# ============================ Flan-T5-Large ============================ #
CHECKPOINT_FLAN = "google/flan-t5-large"

@dataclass
class FlanT5:
    methods_dir: str  

    def __post_init__(self):
        """Initialize tokenizer, model, and document retriever."""
        self.tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT_FLAN)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(CHECKPOINT_FLAN)
        self.retriever = DocumentRetriever(self.methods_dir)  # Initialize retriever

    def extract_parameters(self, input_text: str) -> str:
        """Retrieve relevant methods and extract parameters using Flan-T5."""
    
        # Retrieve relevant context
        retrieved_context = self.retriever.retrieve(input_text, top_k=2)
        full_input = f"Context:\n{retrieved_context}\n\nInput:\n{input_text}"

        # Define the prompt explicitly
        prompt = f"""Extract EEG-related parameters from the given text.

        <instructions>
            - Extract only explicitly mentioned parameters.
            - Do NOT infer missing values.
            - Return a JSON-like format, strictly following the example.
            - If a parameter is missing, omit it (do not create empty placeholders).
        </instructions>

        <parameters>
            "num_channels": (number) The number of EEG channels.
            "prog_lang": (string) The programming language used.
            "artifact_correction": (string) The method used for artifact correction.
        </parameters>

        Example output:
        {{
            "num_channels": "12",
            "prog_lang": "Matlab",
            "artifact_correction": "AMICA"
        }}

        Now extract from the following:

        {full_input}
        """

        # Tokenize input text
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)

        # Generate response from model
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_length=256, repetition_penalty=1.2, no_repeat_ngram_size=3)

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
