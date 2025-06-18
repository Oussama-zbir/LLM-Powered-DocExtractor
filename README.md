# PDF Scraper et Summarizer

Ce projet permet de crawler une page web pour extraire des liens vers des fichiers PDF, de télécharger ces fichiers, d'en extraire le texte (via pdfplumber ou OCR) et de générer un résumé concis grâce au modèle LLaMA 3.1 via Hugging Face et LangChain.

## Structure du projet


SCRAPLAMA/
config.py # Configuration globale (constantes, logging, etc.)

crawler.py # Fonctions de crawling et téléchargement des PDF

pdf_utils.py # Extraction du texte des PDF (pdfplumber et OCR)

summarizer.py # Chargement du modèle LLaMA et génération du résumé

report.py # Sauvegarde des rapports (texte et résumé)

process_pdf.py # Orchestration du traitement complet des PDF

main.py # Point d'entrée de l’application

requirements.txt # Liste des dépendances

.env # Variables d’environnement (ex. HUGGINGFACE_TOKEN)

README.md # Documentation du projet

## Installation

1. Clonez ce dépôt.
2. Créez un environnement virtuel et activez-le.
3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
4. Configurez le fichier .env avec votre token Hugging Face.
