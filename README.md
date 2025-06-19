# RAG

## Steps

### 1 - Ler o PDF com maker - https://github.com/datalab-to/marker

### 2 - Extrair Texto completo em MD & Imagens associadas (objetos PIL.Image.Image)

### 3 - Salvar em DB (SQLite) as imagens (imagens.db) & em um arquivo MD o texto (dr_voss_md.md)

### 4 - Usar um LLM para descrever a imagem & atribuir a descrição ao corpo do texto no md

### 5 - 