import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz 
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from PIL import Image
import io
import re
import torch
from transformers import pipeline
import nltk
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this if you need to restrict origins; "*" allows all origins.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


nltk.download('punkt')
nltk.download('stopwords')



def clean_text(text):
    # Remove header/footer markers and unwanted lines using regex.
    text = re.sub(r"(?m)^(===+.*?===+)\s*\n", " ", text)
    text = re.sub(r"(?m)^(-{3,}.*?-{3,})\s*\n", " ", text)
    # Remove extra whitespace and newlines.
    text = " ".join(text.split())
    return text

def chunk_text(text, max_tokens=512):
    """
    Splits text into smaller chunks based on sentences.
    Here we approximate token count by word count.
    """
    sentences = nltk.tokenize.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    current_length = 0
    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length <= max_tokens:
            current_chunk += " " + sentence
            current_length += sentence_length
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
            current_length = sentence_length
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Use a faster, distilled model that is often quicker on CPU.
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", framework="pt")

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return JSONResponse(content={"error": "Only PDF files are allowed"}, status_code=400)
    
    combined_text = ""
    file_bytes = await file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text("text").strip()
        if page_text:
            combined_text += f"\n=== Page {page_num + 1} Text ===\n" + page_text + "\n"
        else:
            combined_text += f"\n=== Page {page_num + 1} has no text, checking images ===\n"
        
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            ocr_text = pytesseract.image_to_string(image, lang="eng").strip()
            if ocr_text:
                combined_text += f"\n--- Image {img_index + 1} OCR ---\n" + ocr_text + "\n"
            else:
                combined_text += f"\n--- Image {img_index + 1} has no text ---\n"
    
    cleaned_text = clean_text(combined_text)
    chunks = chunk_text(cleaned_text, max_tokens=512)
    chunk_summaries = []
    
    # Adjust max_length and min_length to allow a longer summary per chunk.
    for chunk in chunks:
        try:
            summary_output = summarizer(chunk, max_length=300, min_length=100, do_sample=False)
            chunk_summary = summary_output[0]['summary_text']
            chunk_summaries.append(chunk_summary)
        except Exception as e:
            return JSONResponse(content={"error": f"Summarization error on a chunk: {str(e)}"}, status_code=500)
    
    # Combine all chunk summaries without re-summarizing.
    final_summary = " ".join(chunk_summaries)
    
    return {"filename": file.filename, "Summary": final_summary}

