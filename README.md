# RAG

## Steps

### 1 - Ler o PDF com maker - https://github.com/datalab-to/marker

### 2 - Extrair Texto completo em MD & Imagens associadas (objetos PIL.Image.Image)

### 3 - Salvar em DB (SQLite) as imagens (imagens.db) & em um arquivo MD o texto (dr_voss_md.md)

Passos 1, 2 e 3 - scripts/try_maker.py

### 4 - Usar uma LLM para descrever a imagem & atribuir a descrição ao corpo do texto no md

### 5 - Salvar nova composição de descrição do md na table all_days do DB

Passos 4 e 5 - scripts/describe_images.py

### 6 - Fazer chunks referentes aos dias com Chonkie - https://github.com/chonkie-inc/chonkie

### 7 - Embedding & Reranker com Voyage 

### 8 - Endereçar à LLM os chunks e responder às perguntas

Passos 6, 7 e 8 - scripts/chunk_treat_v2.ipynb