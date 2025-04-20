import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import fitz
import pytesseract
from PIL import Image
import io
import re
import nltk
from transformers import pipeline

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- restore your Tesseract path for Windows ---
# point this to where you installed Tesseract‑OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

nltk.download('punkt')
nltk.download('stopwords')

def clean_text(text):
    text = re.sub(r"(?m)^(===+.*?===+)\s*\n", " ", text)
    text = re.sub(r"(?m)^(-{3,}.*?-{3,})\s*\n", " ", text)
    return " ".join(text.split())

def chunk_text(text, max_tokens=512):
    sentences = nltk.tokenize.sent_tokenize(text)
    chunks, current, length = [], "", 0
    for s in sentences:
        l = len(s.split())
        if length + l <= max_tokens:
            current += " " + s
            length += l
        else:
            if current:
                chunks.append(current.strip())
            current, length = s, l
    if current:
        chunks.append(current.strip())
    return chunks

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    framework="pt"
)

@app.post("/upload-pdf/")
async def upload_pdf(
    file: UploadFile = File(...),
    word_limit: int      = Form(90),
    tone: str            = Form("Professional")
):
    if file.content_type != "application/pdf":
        return JSONResponse({"error":"Only PDFs allowed"}, status_code=400)

    data = await file.read()
    doc  = fitz.open(stream=data, filetype="pdf")
    combined = ""

    for i in range(len(doc)):
        page = doc[i]
        txt  = page.get_text("text").strip()
        combined += f"\n=== Page {i+1} ===\n{txt}\n" if txt else f"\n=== Page {i+1} has no text ===\n"
        for imgx, img in enumerate(page.get_images(full=True)):
            base   = doc.extract_image(img[0])
            img_b  = base["image"]
            pil_img= Image.open(io.BytesIO(img_b))
            ocr    = pytesseract.image_to_string(pil_img).strip()
            combined += f"\n--- Image {imgx+1} OCR ---\n{ocr}\n" if ocr else f"\n--- Image {imgx+1} no text ---\n"

    cleaned = clean_text(combined)
    chunks  = chunk_text(cleaned, max_tokens=512)
    summaries = []

    for chunk in chunks:
        prompt = (
            f"Summarize in a {tone.lower()} tone, "
            f"about {word_limit} words:\n\n{chunk}"
        )
        try:
            out = summarizer(
                prompt,
                max_length=word_limit+20,
                min_length=int(word_limit*0.5),
                do_sample=False
            )
            summaries.append(out[0]['summary_text'])
        except Exception as e:
            return JSONResponse({"error":f"Summarization error: {e}"}, status_code=500)

    final = " ".join(summaries)
    return {"filename": file.filename, "Summary": final}
