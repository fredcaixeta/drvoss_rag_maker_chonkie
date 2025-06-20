# %% [markdown]
# # Objetivo:
# 
# Entregar a LLM as imagens para serem descritas, com o contexto do dia onde se encontra a imagem
# 
# ## Passo a Passo:
# 
# ## 1 - Separar todos os dias do texto
# ## 2 - Encontrar os dias que contem imagens
# ## 3 - Salvar na table all_days no DB o dicionario completo

# %%
import os
import sys
import time

import regex as re

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
from PIL import Image
import io
import base64

from src.classe_gemini import GeminiApiClient
from src.retrieve_img import retrieve_image_bytes_from_db
from src.interact_database_sql import save_image_description_to_db, get_image_description_from_db, non_described_images, add_all_days_table

import sqlite3

# %% [markdown]
# ### 1 - Separar todos os chunks do texto

# %%
# Regex para encontrar as linhas que começam com o padrão de data

diary_text_path = r"C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\dr_voss_md.md"

with open(diary_text_path, 'r', encoding='utf-8') as md:
    diary_text = md.read()

# %%
date_pattern = r"(\d{1,2})(?:st|nd|rd|th)? Day of ([A-Za-z]+) (18\d{2}) - ([A-Za-z\s]+)"
image_pattern = r"!\[\]\((_page_\d+_Picture_\d+\.jpeg)\)"

matches = [(match, match.start()) for match in re.finditer(date_pattern, diary_text)]

all_days = []
for i, (match, start_pos) in enumerate(matches):
    # Extract date components and title
    day, month, year, title = match.groups()
    # Determine the end position (next match's start or end of text)
    end_pos = matches[i + 1][1] if i + 1 < len(matches) else len(diary_text)
    # Get the content including the date line
    content = diary_text[start_pos:end_pos].strip()
    
    # Extrair nomes das imagens, se houver
    image_names = [match.group(1) for match in re.finditer(image_pattern, content)]
    # Usar o primeiro nome de imagem encontrado ou uma string vazia se não houver
    image = image_names[0] if image_names else ""
    
    all_days.append({
        'day': day,
        'month': month,
        'year': year,
        'title': title.strip(),
        'content_raw': content,
        'content_without_image': content.replace(image, "").replace("[]()",""),
        'content_image_described': "",
        'image': image,
        'image_description': "",
        'chunks': []
    })

# %% [markdown]
# ### 2 - Encontrar os chunks que contém imagens

# %%
# Filter chunks that contain the image 'jpeg' in their content
image_chunks = [
    chunk for chunk in all_days
    if chunk['image'] != ""
]

# %% [markdown]
# Encontrar as imagens do DB

# %%
id_image = non_described_images()
n_d_images = [item[1] for item in id_image]

# %%
image_chunks_to_process = []
for image in n_d_images:
    for chunk in image_chunks:
        if image in chunk['image']:
            image_chunks_to_process.append(chunk)

# %%
# --- Inicializa o cliente Gemini API ---
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
# --- Busca dos bytes da imagem no DB ---
for _image in image_chunks_to_process:
    image_name = _image.get("image")
    image_bytes = retrieve_image_bytes_from_db(filename=image_name)

    if image_bytes:
        # --- Codifica os bytes da imagem para Base64 ---
        # A classe GeminiApiClient espera a imagem em formato base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # --- Prepara os dados para a API Gemini (usando a estrutura esperada pela classe) ---
        image_part = {
            "inlineData": {
                "mimeType": "image/jpeg", # Confirme que este é o tipo MIME correto da sua imagem
                "data": base64_image
            }
        }
        
    # --- Chamada da API ---
    model_name = 'gemini-1.5-pro' # Ou 'gemini-1.5-pro' se preferir um modelo mais potente
    
    chunk_description = _image.get('content_without_image')
    
    prompt = f"""
    You are describing a image from a fantasy world in a travel log journey of Doctor Voss, a woman visiting the capital of Veridia.
    Here is the context of the image: {chunk_description}.
    
    Describe **only** the image. Bring **only the description**. Be concise - 300 characters max.
    If the doctor is on the image, describe her looks, skin color, appearence and others with great details.
    """
    
    prompt_parts = [
        {"text": f"{prompt}"},
        image_part
    ]

    print(f"Enviando imagem do banco de dados para a API Gemini (modelo: {model_name})...")

    # Chama o método da classe GeminiApiClient
    response_data = gemini_client.generate_multimodal_content(model_name, prompt_parts)

    print("\n--- Resposta Bruta da API Gemini ---")
    print(response_data) # Para ver a estrutura completa da resposta
    print("-----------------------------------")

    # Extrai o texto da resposta usando o método da classe
    time.sleep(3) # time for the response
    generated_text = gemini_client.extract_text_from_response(response_data)

    if generated_text:
        print("\n--- Texto Descritivo do Gemini ---")
        print(generated_text)
        print("---------------------------------")
    else:
        print("\nNão foi possível extrair texto da resposta do Gemini.")
        
    _ = save_image_description_to_db(filename=image_name, description=generated_text)


# %% [markdown]
# ## Salvar descrições do dicionário ao DB

# %%
for day in all_days:
    if day['image'] != "":
        day['image_description'] = get_image_description_from_db(filename=day['image'])

# %%
for day in all_days:
    if day['image'] != "":
        day['content_image_described'] = day['content_raw'].replace("![]("+day['image']+")", "Picture - " + day['image_description'])

# %%
add_all_days_table(days=all_days)


