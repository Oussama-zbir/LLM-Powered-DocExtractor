import os
import re
from config import logger

def save_report(pdf_file, original_text, summary, output_folder="rapports"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    base_name = os.path.basename(pdf_file).replace(".pdf", "").replace(".PDF", "")
    base_name = re.sub(r'[\\/*?:"<>|]', "_", base_name)
    
    if original_text:
        original_path = os.path.join(output_folder, f"{base_name}_texte.txt")
        with open(original_path, 'w', encoding='utf-8') as f:
            f.write(original_text)
        logger.info(f"Texte original sauvegardé: {original_path}")
    
    summary_path = os.path.join(output_folder, f"{base_name}_resume.txt")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    logger.info(f"Résumé sauvegardé: {summary_path}")
    
    return summary_path
