import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

st.set_page_config(page_title="EEG PDF Analyzer", layout="wide")
st.title("🧠 Analyze EEG Methods from PDF Papers (Hugging Face Model)")

# Load HF model once
@st.cache_resource
def load_model():
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return pipe

llm = load_model()

# Questions to ask
QUESTIONS = {
    "Cohort": "What is the participant group in this study?",
    "Number of Participants": "How many participants are in the study?",
    "Number of EEG Electrodes": "How many EEG electrodes were recorded?",
    "Analysis Software": "Which EEG analysis software or toolbox was used?",
}

# File uploader
uploaded_files = st.file_uploader("📄 Upload up to 10 PDF articles", type="pdf", accept_multiple_files=True)

# PDF reading and methods extraction
def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

def extract_methods_section(text):
    match = re.search(r"\b(methods|materials and methods|methodology)\b", text, re.IGNORECASE)
    if not match:
        return ""
    start = match.start()
    # Try to find end of section
    end_match = re.search(r"\b(results|discussion|conclusion|references)\b", text[start:], re.IGNORECASE)
    end = start + end_match.start() if end_match else len(text)
    return text[start:end].strip()

def ask_questions_locally(text):
    responses = {}
    for key, question in QUESTIONS.items():
        prompt = f"[INST] Given the following Methods section from an EEG research paper:\n{text}\n\nQuestion: {question}\nAnswer: [/INST]"
        try:
            output = llm(prompt, max_new_tokens=200, temperature=0.2)
            answer = output[0]['generated_text'].split("[/INST]")[-1].strip()
            responses[key] = answer
        except Exception as e:
            responses[key] = f"Error: {e}"
    return responses

# Main logic
if uploaded_files:
    all_data = []

    for file in uploaded_files[:10]:
        with st.spinner(f"🔍 Processing {file.name}..."):
            try:
                text = extract_text_from_pdf(file)
                methods = extract_methods_section(text)

                if not methods:
                    st.warning(f"⚠️ Methods section not found in {file.name}")
                    continue

                result = ask_questions_locally(methods)
                result["Filename"] = file.name
                all_data.append(result)

            except Exception as e:
                st.error(f"❌ Error in {file.name}: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        df = df[["Filename"] + list(QUESTIONS.keys())]
        st.success("✅ Done! Here's your extracted data:")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "eeg_extraction_results.csv", "text/csv")
