import sqlite3
import io
from PIL import Image

def retrieve_image_from_db(image_id: int = None, filename: str = None, db_name="imagens.db") -> Image.Image | None:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    if image_id:
        cursor.execute("SELECT dados_imagem FROM imagens WHERE id = ?", (image_id,))
    elif filename:
        cursor.execute("SELECT dados_imagem FROM imagens WHERE nome_arquivo = ?", (filename,))
    else:
        print("Forneça um ID ou um nome de arquivo para buscar a imagem.")
        return None

    result = cursor.fetchone()
    conn.close()

    if result:
        image_bytes = result[0]
        return Image.open(io.BytesIO(image_bytes))
    else:
        return None
    
def retrieve_image_bytes_from_db(image_id: int = None, filename: str = None, db_name=r"C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\imagens.db") -> bytes | None:
    """Busca os bytes brutos de uma imagem do banco de dados."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    if image_id:
        cursor.execute("SELECT dados_imagem FROM imagens WHERE id = ?", (image_id,))
    elif filename:
        cursor.execute("SELECT dados_imagem FROM imagens WHERE nome_arquivo = ?", (filename,))
    else:
        print("Forneça um ID ou um nome de arquivo para buscar a imagem.")
        conn.close()
        return None

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]  # Retorna diretamente os bytes
    else:
        return None