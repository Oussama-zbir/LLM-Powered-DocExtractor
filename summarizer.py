import os
import torch
import re
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from langchain.llms import HuggingFacePipeline
from langchain import PromptTemplate, LLMChain
from nltk.tokenize import sent_tokenize
from config import logger

def load_llama_summarizer_chain():
    try:
        model_name = "meta-llama/Llama-3.1-8B"
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            token=os.environ.get("HUGGINGFACE_TOKEN"),
            trust_remote_code=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            token=os.environ.get("HUGGINGFACE_TOKEN"),
            device_map="cpu",
            torch_dtype=torch.float32,  
            trust_remote_code=True
        )
        hf_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=512,
            temperature=0.2,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        llm = HuggingFacePipeline(pipeline=hf_pipeline)
        prompt_template = """
<|begin_of_text|><|system|>
Tu es un assistant expert en synthèse de documents juridiques et financiers.
<|user|>
Voici un texte long extrait d'un document :

{text}

Merci de fournir un résumé concis et pertinent du texte ci-dessus.
<|assistant|>
"""
        prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        
        logger.info("Modèle LLaMA 3.1 chargé depuis Hugging Face avec succès")
        return llm_chain
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle LLaMA 3.1 depuis Hugging Face: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def process_llama_response(response):
    if "<|assistant|>" in response:
        response = response.split("<|assistant|>")[1]
    response = response.replace("<|end_of_text|>", "")
    return response.strip()

def smart_chunking(text, max_tokens=500):
    if not text:
        return []
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        if len(paragraph.split()) > max_tokens:
            sentences = sent_tokenize(paragraph)
            for sentence in sentences:
                if len(current_chunk.split()) + len(sentence.split()) <= max_tokens:
                    current_chunk += " " + sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
        elif len(current_chunk.split()) + len(paragraph.split()) <= max_tokens:
            current_chunk += "\n\n" + paragraph
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    logger.info(f"Texte découpé en {len(chunks)} chunks intelligents")
    return chunks

def summarize_text(text, summarizer_chain, max_length=150, min_length=40):
    if not text.strip():
        return "Aucun texte à résumer."
    
    if summarizer_chain is None:
        return "Modèle de summarization non disponible. Voici les 500 premiers caractères du texte:\n" + text[:500] + "..."
        
    chunks = smart_chunking(text)
    summaries = []
    
    from tqdm import tqdm
    for i, chunk in enumerate(tqdm(chunks, desc="Résumé des chunks")):
        try:
            if chunk.strip():
                if len(chunk.split()) < min_length:
                    summaries.append(chunk)
                    continue
                truncated_chunk = " ".join(chunk.split()[:1000])
                raw_summary = summarizer_chain.run(text=truncated_chunk)
                summary = process_llama_response(raw_summary)
                
                if summary and summary.strip():
                    summaries.append(summary.strip())
                    logger.info(f"Chunk {i+1}/{len(chunks)} résumé avec succès")
                else:
                    summaries.append(truncated_chunk[:200] + "... [Résumé automatique non disponible]")
                    logger.warning(f"Résumé vide pour le chunk {i+1}")
        except Exception as e:
            logger.error(f"Erreur lors de la summarization du chunk {i+1}: {e}")
            if len(chunk) > 200:
                summaries.append(chunk[:200] + "... [Résumé incomplet]")
            else:
                summaries.append(chunk)
    
    final_summary = "\n\n".join(summaries)
    return final_summary
