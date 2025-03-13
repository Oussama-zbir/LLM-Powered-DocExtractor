import os
import sys
import logging

# URL de base et paramètres
BASE_URL = "https://www.bkam.ma/Trouvez-l-information-concernant/Reglementation/Activite-des-etablissements-de-credit-et-assimiles/"
MAX_PDFS = 5

if sys.platform.startswith('win'):
    POPPLER_PATH = r"C:\Users\DELL XPS\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"
else:
    POPPLER_PATH = None

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("pdf_scraper.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
