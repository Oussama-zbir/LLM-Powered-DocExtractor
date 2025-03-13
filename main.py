import sys
import nltk
from huggingface_hub import login
from config import BASE_URL, MAX_PDFS, POPPLER_PATH, logger
from crawler import crawl_pdf_links
from process_pdf import process_pdf_files

def main():
    # Authentification sur Hugging Face
    try:
        from os import environ
        token = environ.get("HUGGINGFACE_TOKEN")
        if not token:
            logger.error("HUGGINGFACE_TOKEN n'est pas défini. Vérifiez votre fichier .env.")
            return
        login(token=token)
    except Exception as e:
        logger.error(f"Erreur lors de l'authentification Hugging Face: {e}")
    
    # Téléchargement des ressources NLTK
    try:
        nltk.download('punkt')
        nltk.download('punkt_tab')
    except Exception as e:
        logger.warning(f"Impossible de télécharger les ressources NLTK: {e}")

    # Vérification des dépendances critiques
    missing_deps = []
    try:
        from google.protobuf import descriptor_pb2
    except ImportError:
        missing_deps.append("protobuf")
    try:
        import bitsandbytes
    except ImportError:
        missing_deps.append("bitsandbytes")
    try:
        import accelerate
    except ImportError:
        missing_deps.append("accelerate")
    
    if missing_deps:
        logger.error(f"Dépendances manquantes: {', '.join(missing_deps)}. Veuillez les installer avant de continuer.")
        logger.error("Commande d'installation: pip install " + " ".join(missing_deps))
        return

    if sys.platform.startswith('win') and not POPPLER_PATH:
        logger.warning("Le chemin vers Poppler n'est pas configuré. L'OCR pourrait ne pas fonctionner.")
        logger.warning("Téléchargez Poppler depuis https://github.com/oschwartz10612/poppler-windows/releases")
        logger.warning("Et définissez POPPLER_PATH dans config.py.")
    
    # Recherche des liens PDF
    logger.info("Recherche des liens PDF...")
    pdf_links = crawl_pdf_links(BASE_URL)
    logger.info(f"Nombre total de liens PDF trouvés : {len(pdf_links)}")
    
    pdf_links = pdf_links[:MAX_PDFS]
    logger.info(f"Traitement des {len(pdf_links)} premiers PDF pour le test.")
    
    # Traitement des PDF
    reports = process_pdf_files(pdf_links)
    
    logger.info("\n===== RÉSUMÉ DES RÉSULTATS =====")
    success_count = len([r for r in reports.values() if r["text_length"] > 0])
    logger.info(f"PDFs traités avec succès: {success_count}/{len(reports)}")
    
    for pdf_file, report_info in reports.items():
        logger.info(f"\nRapport pour {pdf_file}:")
        if report_info["text_length"] > 0:
            logger.info(f"- Longueur du texte extrait: {report_info['text_length']} caractères")
            logger.info(f"- Résumé sauvegardé dans: {report_info['summary_path']}")
            summary_preview = "\n".join(report_info["summary"].split("\n")[:3])
            logger.info(f"- Aperçu du résumé: {summary_preview}...")
        else:
            logger.info(f"- {report_info['summary']}")

if __name__ == "__main__":
    main()
