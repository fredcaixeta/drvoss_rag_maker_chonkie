# %%
import os
import sys
import time

import numpy as np
import json
import regex as re

from typing import Dict

# Pega o diretório atual do notebook
notebook_dir = os.getcwd() # ou os.path.dirname(__file__) se fosse um script .py

# Assume que 'src' está no mesmo nível do notebook ou um nível acima
# Ajuste '..' conforme a estrutura do seu projeto
project_root = os.path.abspath(os.path.join(notebook_dir, '..')) # Volta um diretório

# Se o 'src' estiver diretamente no mesmo nível do notebook:
# project_root = notebook_dir

# Adiciona o diretório raiz do projeto ao sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# %%
from src.interact_database_sql import get_all_days_content, insert_chunks_emb, retrieve_chunks_emb
from src.voyage_emb import get_voyage_embeddings, voyage_rerank

# INPUTS
# %%
json_file = r"C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\unit_qa.json"

with open(json_file, mode='r', encoding='utf-8') as jf:
    jsonfile: Dict = json.load(jf)

# %%
jsonfile = {"How does the doctor look like?":"Hair"}


# %%
def calculate_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calcula a similaridade de cosseno entre dois vetores."""
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0 # Evita divisão por zero
        
    return dot_product / (norm_vec1 * norm_vec2)

def semantic_search(query: str, indexed_chunks: list[dict], model = None, k = 10) -> list[dict]:
    """
    Realiza uma pesquisa de similaridade semântica.

    Args:
        query (str): A string de consulta.
        indexed_chunks (list[dict]): A lista de dicionários de chunks com embeddings.
        model: O modelo usado para gerar embeddings.

    Returns:
        list[dict]: Uma lista de dicionários de chunks, ordenados por similaridade
                    (maior primeiro), incluindo a pontuação de similaridade.
    """
    # 1. Gerar o embedding da consulta
    query_embedding = get_voyage_embeddings(query)
    #print(f"\nEmbedding da Consulta ('{query}'): {query_embedding}")

    results = []
    # 2. Calcular similaridade para cada chunk
    for item in indexed_chunks:
        chunk_text = item['chunk']
        chunk_embedding = item['embedding']
        
        # Certifique-se de que o embedding do chunk também é um array numpy
        # (se o seu modelo já retorna numpy arrays, isso pode ser redundante)
        if not isinstance(chunk_embedding, np.ndarray):
             chunk_embedding = np.array(chunk_embedding)

        similarity = calculate_cosine_similarity(query_embedding, chunk_embedding)
        
        results.append({
            'chunk': chunk_text,
            'similarity': similarity,
            'embedding': chunk_embedding # Opcional, para debug
        })
    
    # 3. Ordenar os resultados pela similaridade (decrescente)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return results[:k]

# %%
# --- Inicializa o cliente Gemini API ---
from src.classe_gemini import GeminiApiClient
# Certifique-se de que a variável de ambiente 'GOOGLE_API_KEY' está definida com sua chave de API
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente 'GOOGLE_API_KEY' não está definida.")
    
    gemini_client = GeminiApiClient(api_key=api_key)
except ValueError as e:
    print(f"Erro de configuração da API: {e}")
    exit() # Encerra o programa se a chave da API não estiver configurada


# %%
answers_dict = []
k = 30

chunks_emb = retrieve_chunks_emb()
for query, answer in jsonfile.items():
    reranked = []
    
    search_results = semantic_search(query, chunks_emb, k=k)
    txt_results = []
    
    for chunk in search_results:
        txt_results.append(chunk['chunk'])
    
    sorted_rows = voyage_rerank(
        query=query,
        documents=txt_results[:k]
        )    
    
    top_3 = sorted_rows[:10]  # Já está ordenado por relevance_score (maior para menor)
    
    # Extrair apenas o texto dos documentos
    top_3_texto = [doc for doc, score, index in top_3]
    
    for i, doc in enumerate(top_3_texto, 1):
        reranked.append(doc)
        
    # --- Chamada da API ---
    
    model_name = 'gemini-1.5-flash-8b' # Ou 'gemini-1.5-pro' se preferir um modelo mais potente

    prompt = f"""
        You are answering a question from a fantasy world in a travel log journey of Doctor Voss, a woman visiting the capital of Veridia.
        Question: {query}
        Here is the context to help you answer: {reranked}.
        Bring the answer **only**. Example: 'The Veridian's Skys were blue most days.'
        If you don't know the answer, respond: 'NTD' - meaning nothing to disclosure.
        If you are not sure, respond: 'NS' - meaning not sure.
        """
        
    prompt_parts = [
        {"text": f"{prompt}"}
    ]
    # Chama o método da classe GeminiApiClient
    response_data = gemini_client.generate_multimodal_content(model_name, prompt_parts)

    # Extrai o texto da resposta usando o método da classe
    generated_text = gemini_client.extract_text_from_response(response_data)

    if generated_text:
        print(f"********************************\nQuery: {query}")
        print(f"Gemini: {generated_text}")
        print(f"Actual Answer: {answer}")
        print("--------------------------------")
        
        answers_dict.append({
            'query': query,
            'llm_answer': generated_text,
            'actual_answer': answer
        })
    else:
        print("\nNão foi possível extrair texto da resposta do Gemini.")
    

# %%
# with open(r'C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\answers_dict.json', 'w', encoding='utf-8') as f:
#     json.dump(answers_dict, f, ensure_ascii=False, indent=4)


