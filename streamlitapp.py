import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import PyPDF2
import tempfile

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
        text += page.extract_text() + "\n"
    return text

# Function to generate answer from model
def generate_answer(context, question):
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    outputs = model.generate(**inputs, max_new_tokens=100)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

# Streamlit UI
st.title("🧠 NeuroSift: Extracting methods from Scientific text")

uploaded_files = st.file_uploader("Upload up to 10 PDF articles", type=["pdf"], accept_multiple_files=True)
question = st.text_input("Enter your question (e.g. 'How many EEG channels were used?')")

if st.button("Run QA"):
    if not uploaded_files or not question:
        st.warning("Please upload PDFs and enter a question.")
    else:
        st.write("---")
        for file in uploaded_files:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(file.read())
                    tmp_path = tmp_file.name

                with open(tmp_path, 'rb') as f:
                    text = extract_text_from_pdf(f)
                
                truncated_text = text[:2000]  # Limit to first ~2K characters
                answer = generate_answer(truncated_text, question)

                st.subheader(f"📄 {file.name}")
                st.markdown(f"**Answer:** {answer}")
            except Exception as e:
                st.error(f"❌ Error processing {file.name}: {e}")