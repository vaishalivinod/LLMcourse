import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering

st.set_page_config(page_title="EEG Paper Analyzer (BioBERT)", layout="wide")
st.title("🧠 EEG Methods Extractor with BioBERT")

# Load BioBERT QA model
@st.cache_resource
def load_qa_pipeline():
    model_name = "dmis-lab/biobert-base-cased-v1.1"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    return pipeline("question-answering", model=model, tokenizer=tokenizer)

qa_pipeline = load_qa_pipeline()

QUESTIONS = {
    "Cohort": "What is the participant group in this study?",
    "Participants": "How many participants were included?",
    "EEG Channels": "How many EEG channels or electrodes were used?",
    "Software": "What software or toolbox was used to analyze EEG data?",
}

uploaded_files = st.file_uploader("📄 Upload up to 10 EEG-related PDF files", type="pdf", accept_multiple_files=True)

# Extract full text from PDF
def extract_text(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

# Try to extract methods section only
def extract_methods(text):
    match = re.search(r"(methods|materials and methods|methodology)", text, re.IGNORECASE)
    if not match:
        return text  # fallback to full text
    start = match.start()
    end_match = re.search(r"(results|discussion|conclusion|references)", text[start:], re.IGNORECASE)
    end = start + end_match.start() if end_match else len(text)
    return text[start:end]

# Ask QA questions using BioBERT
def ask_biobert_questions(context):
    result = {}
    for key, question in QUESTIONS.items():
        try:
            answer = qa_pipeline(question=question, context=context)
            result[key] = answer["answer"]
        except Exception as e:
            result[key] = f"Error: {e}"
    return result

# Run extraction
if uploaded_files:
    rows = []
    for file in uploaded_files:
        with st.spinner(f"Processing: {file.name}"):
            try:
                full_text = extract_text(file)
                methods_text = extract_methods(full_text)
                answers = ask_biobert_questions(methods_text)
                answers["Filename"] = file.name
                rows.append(answers)
            except Exception as e:
                st.error(f"❌ Error with {file.name}: {e}")

    if rows:
        df = pd.DataFrame(rows)
        df = df[["Filename"] + list(QUESTIONS.keys())]
        st.success("✅ Done!")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "results.csv", "text/csv")
