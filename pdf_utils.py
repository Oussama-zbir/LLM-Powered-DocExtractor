import re
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from config import POPPLER_PATH, logger

def extract_text_with_pdfplumber(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction avec pdfplumber de {pdf_path}: {e}")
    return text

def extract_text_with_ocr(pdf_path, dpi=300, languages='fra+ara+eng'):
    text = ""
    try:
        images = convert_from_path(pdf_path, dpi=dpi, poppler_path=POPPLER_PATH)
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image, lang=languages)
            if page_text:
                text += page_text + "\n"
            logger.info(f"OCR effectué sur la page {i+1}/{len(images)} de {pdf_path}")
    except Exception as e:
        logger.error(f"Erreur lors de l'OCR de {pdf_path}: {e}")
    return text

def extract_text_from_pdf(pdf_path):
    text = extract_text_with_pdfplumber(pdf_path)
    if len(text.strip()) < 100:
        logger.info(f"Peu de texte extrait avec pdfplumber, tentative avec OCR: {pdf_path}")
        text = extract_text_with_ocr(pdf_path)
    
    # Nettoyage du texte
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    if not text.strip():
        logger.warning(f"Aucun texte n'a pu être extrait de {pdf_path}")
    else:
        logger.info(f"Texte extrait avec succès: {len(text)} caractères")
    
    return text
