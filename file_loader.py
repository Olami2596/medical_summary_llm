from docx import Document as DocxDocument
from PIL import Image
import pytesseract
import fitz  # pymupdf
import tempfile
import os

def extract_text_from_pdf(uploaded_file):
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name
    doc = fitz.open(tmp_file_path)
    for page in doc:
        text += page.get_text() + "\f"
    doc.close()
    os.remove(tmp_file_path)
    return text

def extract_text_from_docx(uploaded_file):
    document = DocxDocument(uploaded_file)
    return "\n".join([p.text for p in document.paragraphs])

def extract_text_from_image(uploaded_file):
    image = Image.open(uploaded_file)
    return pytesseract.image_to_string(image)
