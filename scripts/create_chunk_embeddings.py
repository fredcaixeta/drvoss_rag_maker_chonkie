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
    
from src.interact_database_sql import get_all_days_content, insert_chunks_emb
from src.voyage_emb import get_voyage_embeddings, voyage_rerank

# 1. Recuperar apenas content_without_image e content_image_described para todos os registros
results = get_all_days_content(fields=['content_without_image', 'content_image_described'])

content = [result['content_image_described'] if result['content_image_described'] != "" else result['content_without_image'] for result in results]

# First import the chunker you want from Chonkie
from chonkie import SemanticChunker, RecursiveChunker

# Initialize the chunker
# chunker = RecursiveChunker()
chunker = SemanticChunker()

chunks = []
for day in content:
    # Chunk some text
    _chunks = chunker(day)

    # Access chunks
    for chunk in _chunks:
        #print(f"Chunk: {chunk.text}")
        chunks.append(chunk.text)   

old_size = 0
for chunk in chunks:
    new_size = len(chunk)
    if new_size > old_size:
        max_size = new_size
    else:
        max_size = old_size
        
print(f"Tamanho de caracteres maximo de um chunk: {max_size}")

chunks_emb: list[dict] = [{'chunk': chunk, 'embedding': ''} for chunk in chunks]

# # Make embeddings
for chunk in chunks_emb:
    # Get the chunk text to encode
    chunk_text = chunk['chunk']
    # Generate the embedding for this specific chunk
    # Note: model.encode usually takes a list of strings, even for a single string,
    # and returns a list of embeddings. So, we get the first (and only) embedding.
    
    # Model2Vec
    # embedding = model.encode(chunk_text)
    
    # Voyage
    embedding = get_voyage_embeddings(chunk_text)
    time.sleep(0.05)
    # Assign the generated embedding to the 'embedding' key
    chunk['embedding'] = embedding
    
# # Make sequences of token embeddings
# token_embeddings = model.encode_as_sequence(["It's dangerous to go alone!", "It's a secret to everybody."])

_ = insert_chunks_emb(chunks_emb=chunks_emb)

print("Dados salvos com sucesso no SQLite")