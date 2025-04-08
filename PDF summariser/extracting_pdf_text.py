import os
import sys
import fitz  # PyMuPDF
import pytesseract
import pdfplumber
import pandas as pd
from PIL import Image

# ✅ Set Tesseract OCR Path
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print("✅ Tesseract found, OCR is enabled.")
else:
    print("⚠️ WARNING: Tesseract not found! OCR functionality will be disabled.")
    print("Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")

# ✅ Set Input PDF File Path
PDF_FILE_PATH = r"C:\Users\phani\Documents\csp2\Concept cards - Retail and Commerce.pdf"

if not os.path.exists(PDF_FILE_PATH):
    print(f"❌ ERROR: File '{PDF_FILE_PATH}' not found!")
    sys.exit(1)

# ✅ Extract Text, Images, and Tables
print("\n📖 Extracting content from PDF...")
doc = fitz.open(PDF_FILE_PATH)
extracted_text = ""
image_count = 0
image_folder = "extracted_images"
os.makedirs(image_folder, exist_ok=True)

# 🔍 Extract Data Page by Page
for page_num in range(len(doc)):
    print(f"\n🔹 Processing Page {page_num + 1}...")
    page = doc[page_num]

    # 🔹 Extract Text
    text = page.get_text("text")  # Extract normal text
    if text.strip():
        extracted_text += f"\n=== Page {page_num + 1} ===\n{text}\n"
    else:
        print(f"🖼️ No direct text found on Page {page_num + 1}, running OCR...")

    # 🔹 Extract Images and Perform OCR
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        image_filename = os.path.join(image_folder, f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}")

        # Save the extracted image
        with open(image_filename, "wb") as img_file:
            img_file.write(image_bytes)

        print(f"🖼️ Extracted Image: {image_filename}")
        image_count += 1

        # ✅ Convert Image to Text Using OCR
        try:
            image = Image.open(image_filename)
            ocr_text = pytesseract.image_to_string(image, lang="eng")

            if ocr_text.strip():
                extracted_text += f"\n=== OCR Extracted from Image Page {page_num + 1}, Image {img_index + 1} ===\n{ocr_text}\n"
                print(f"📝 OCR Extracted Text:\n{ocr_text[:200]}...")  # Preview first 200 characters
            else:
                print(f"⚠️ OCR could not extract text from image on Page {page_num + 1}, Image {img_index + 1}.")

        except Exception as e:
            print(f"⚠️ OCR Error: {e}")

# 🔹 Extract Tables
print("\n📊 Extracting Tables...")
table_data = []
with pdfplumber.open(PDF_FILE_PATH) as pdf:
    for page_num, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for table_index, table in enumerate(tables):
            df = pd.DataFrame(table)
            table_data.append((page_num + 1, table_index + 1, df))
            print(f"📑 Extracted Table from Page {page_num + 1}, Table {table_index + 1}")

# 🔹 Save Extracted Data
text_output_path = "extracted_text.txt"
with open(text_output_path, "w", encoding="utf-8") as f:
    f.write(extracted_text)
print(f"\n✅ Text and OCR data saved to '{text_output_path}'")

if table_data:
    table_output_path = "extracted_tables.xlsx"
    with pd.ExcelWriter(table_output_path) as writer:
        for page_num, table_index, df in table_data:
            df.to_excel(writer, sheet_name=f"Page{page_num}_Table{table_index}", index=False)
    print(f"✅ Tables saved to '{table_output_path}'")

print(f"\n🎉 Extraction complete! {image_count} images, text, and tables extracted.")
