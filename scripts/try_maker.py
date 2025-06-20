# %% [markdown]
# ## Usando maker para formar MD e extrair imagens

# %%
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

converter = PdfConverter(
    artifact_dict=create_model_dict(),
)
rendered = converter(r"C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\dr_voss_diary.pdf")
text, _, images = text_from_rendered(rendered) # _ = 'md'


# %%
full_output_path = r"C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\dr_voss_md.md"
try:
    with open(full_output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Texto salvo com sucesso em: {full_output_path}")
except IOError as e:
    print(f"Erro ao salvar o arquivo Markdown: {e}")

# %%
import sqlite3

def setup_database(db_name="imagens.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS imagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_arquivo TEXT NOT NULL,
            dados_imagem BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

setup_database() # Cria o banco de dados e a tabela

# %%
from PIL import Image
import io

def image_to_bytes(image_pil: Image.Image, format: str = "JPEG") -> bytes:
    """Converte um objeto PIL.Image.Image para bytes."""
    byte_arr = io.BytesIO()
    image_pil.save(byte_arr, format=format)
    return byte_arr.getvalue()

# Exemplo de uso:
# Digamos que 'minha_imagem_pil' é um dos valores do seu dicionário 'images'
# imagem_em_bytes = image_to_bytes(minha_imagem_pil, format="JPEG")

def store_images_in_db(images_dict: dict, db_name="imagens.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    for filename, image_pil in images_dict.items():
        # Converter a imagem para bytes (pode escolher PNG ou JPEG)
        image_bytes = image_to_bytes(image_pil, format="JPEG")

        try:
            cursor.execute(
                "INSERT INTO imagens (nome_arquivo, dados_imagem) VALUES (?, ?)",
                (filename, image_bytes)
            )
            print(f"Imagem '{filename}' inserida com sucesso.")
        except sqlite3.Error as e:
            print(f"Erro ao inserir a imagem '{filename}': {e}")

    conn.commit()
    conn.close()

# --- Como você usaria com seu dicionário 'images' ---
# Supondo que 'images' é o dicionário resultante do seu código Marker:
# images = {'_page_0_Picture_1.jpeg': <PIL.Image.Image object>, ...}
store_images_in_db(images)
