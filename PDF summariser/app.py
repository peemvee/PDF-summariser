import streamlit as st
import fitz  # PyMuPDF
from transformers import pipeline
from transformers import pipeline
def summarize_pdf(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    
    if len(text) > 1000:  # If the text is too long, use AI-based summarization
        summary = summarize_text(text)
    else:  # For shorter texts, use Sumy
        summary = summarize_text_sumy(text)

    return summary

def summarize_text(text, max_length=300):
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def summarize_text(text, max_length=300):
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

st.title("PDF Summarizer Tool")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    summary = summarize_pdf("temp.pdf")
    st.subheader("Summary:")
    st.write(summary)
