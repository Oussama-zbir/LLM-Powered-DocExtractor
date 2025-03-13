from crawler import download_pdf
from pdf_utils import extract_text_from_pdf
from summarizer import load_llama_summarizer_chain, summarize_text
from report import save_report
from tqdm import tqdm
from config import logger

def process_pdf_files(pdf_links):
    summarizer_chain = load_llama_summarizer_chain()
    
    reports = {}
    for pdf_url in tqdm(pdf_links, desc="Traitement des PDF"):
        try:
            pdf_file = download_pdf(pdf_url)
            if not pdf_file:
                continue
                
            logger.info(f"Extraction du texte de {pdf_file}...")
            text = extract_text_from_pdf(pdf_file)
            
            if text.strip():
                logger.info(f"Génération du résumé pour {pdf_file}...")
                summary = summarize_text(text, summarizer_chain)
                summary_path = save_report(pdf_file, text, summary)
                reports[pdf_file] = {
                    "url": pdf_url,
                    "text_length": len(text),
                    "summary": summary,
                    "summary_path": summary_path
                }
            else:
                message = "Aucun texte n'a pu être extrait."
                reports[pdf_file] = {
                    "url": pdf_url,
                    "text_length": 0,
                    "summary": message,
                    "summary_path": None
                }
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {pdf_url}: {e}")
            reports[pdf_url] = {
                "url": pdf_url,
                "text_length": 0,
                "summary": f"Erreur: {str(e)}",
                "summary_path": None
            }
    
    return reports
