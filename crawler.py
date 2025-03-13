import os
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from config import BASE_URL, logger

def crawl_pdf_links(url, visited=None, max_depth=3, current_depth=0):
    if visited is None:
        visited = set()
    if url in visited or current_depth > max_depth:
        return []
    visited.add(url)
    
    pdf_links = []
    logger.info(f"Crawling: {url} (profondeur: {current_depth})")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de {url}: {e}")
        return pdf_links

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraction des liens PDF sur la page actuelle
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(url, href)
        if full_url.lower().endswith('.pdf'):
            pdf_links.append(full_url)

    # Suivre les liens internes à BASE_URL
    if current_depth < max_depth:
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)
            if full_url.startswith(BASE_URL) and full_url not in visited:
                pdf_links.extend(crawl_pdf_links(full_url, visited, max_depth, current_depth + 1))
    
    return list(set(pdf_links))

def download_pdf(pdf_url, download_folder="pdfs"):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        # Nettoyage du nom de fichier
        filename = os.path.basename(pdf_url)
        filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
        
        file_path = os.path.join(download_folder, filename)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"Téléchargé : {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de {pdf_url}: {e}")
        return None
