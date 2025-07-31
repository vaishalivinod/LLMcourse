import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import PyPDF2
import tempfile
import pandas as pd

# Load FLAN-T5 model and tokenizer
@st.cache_resource
def load_model():
    model_name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model()

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# Function to generate answer from model
def generate_answer(context, question):
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    outputs = model.generate(**inputs, max_new_tokens=100)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Streamlit App
st.title("🧠 NeuroSift: Extract Methods from Scientific PDFs")

uploaded_files = st.file_uploader("Upload up to 10 PDF articles", type=["pdf"], accept_multiple_files=True)

# Question entry section
st.subheader("Enter your questions")
if "question_count" not in st.session_state:
    st.session_state.question_count = 1

add_q = st.button("➕ Add another question")
remove_q = st.button("➖ Remove last question")

if add_q:
    st.session_state.question_count += 1
if remove_q and st.session_state.question_count > 1:
    st.session_state.question_count -= 1

question_inputs = []
for i in range(st.session_state.question_count):
    question = st.text_input(f"Question {i+1}", key=f"question_{i}")
    if question.strip():
        question_inputs.append(question.strip())

# Run QA
if st.button("Run QA"):
    if not uploaded_files or not question_inputs:
        st.warning("Please upload PDFs and enter at least one question.")
    else:
        results = []
        for file in uploaded_files:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(file.read())
                    tmp_path = tmp_file.name

                with open(tmp_path, 'rb') as f:
                    text = extract_text_from_pdf(f)

                truncated_text = text[:2000]
                row = {"PDF": file.name}
                for question in question_inputs:
                    answer = generate_answer(truncated_text, question)
                    row[question] = answer

                results.append(row)
            except Exception as e:
                st.error(f"❌ Error processing {file.name}: {e}")

        if results:
            st.subheader("📊 Answers Table")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
