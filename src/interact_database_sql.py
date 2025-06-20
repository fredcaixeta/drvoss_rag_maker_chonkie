import sqlite3
import os

DB_PATH = r"C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\imagens.db"

def add_all_days_table(db_name: str = DB_PATH, days: list[dict] = None) -> None:
    # Conectar ao banco de dados SQLite (substitua 'database.db' pelo nome do seu banco)
    db_path = db_name  # Ajuste o caminho/nome do banco conforme necessário
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if days is not None:
        # Criar a tabela all_days
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS all_days (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT,
                month TEXT,
                year TEXT,
                title TEXT,
                content_raw TEXT,
                content_without_image TEXT,
                content_image_described TEXT,
                image TEXT,
                image_description TEXT
            )
        ''')

        # Inserir os dados na tabela all_days
        for day in days:
            cursor.execute('''
                INSERT INTO all_days (
                    day, month, year, title, content_raw,
                    content_without_image, content_image_described,
                    image, image_description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                day['day'],
                day['month'],
                day['year'],
                day['title'],
                day['content_raw'],
                day['content_without_image'],
                day['content_image_described'],
                day['image'],
                day['image_description']
            ))

        # Confirmar as alterações e fechar a conexão
        conn.commit()
        conn.close()

        print("Dados inseridos na tabela 'all_days' com sucesso!")
    else:
        print("Invalid Input")
        
def get_all_days_content(db_path = DB_PATH, fields=None, filters=None) -> list[dict] | list:
    """
    Acessa conteúdos da tabela all_days em um banco de dados SQLite.
    
    Parâmetros:
    - db_path (str): Caminho para o arquivo do banco de dados SQLite.
    - fields (list): Lista de campos a serem retornados (e.g., ['content_without_image', 'content_image_described']).
                     Se None, retorna todos os campos.
    - filters (dict): Dicionário com filtros para a consulta (e.g., {'day': '1', 'month': 'Frostfall'}).
                      Se None, retorna todos os registros.
    
    Retorna:
    - Lista de dicionários, onde cada dicionário contém os campos solicitados para uma entrada.
    """
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Definir os campos a serem selecionados
        if fields is None:
            fields = ['id', 'day', 'month', 'year', 'title', 'content_raw', 
                      'content_without_image', 'content_image_described', 'image', 'image_description']
        select_clause = ', '.join(fields)

        # Construir a consulta SQL
        query = f'SELECT {select_clause} FROM all_days'
        params = []

        # Adicionar filtros, se fornecidos
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            query += ' WHERE ' + ' AND '.join(conditions)

        # Executar a consulta
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Criar lista de dicionários com os resultados
        results = []
        for row in rows:
            result = {fields[i]: row[i] for i in range(len(fields))}
            results.append(result)

        # Fechar a conexão
        conn.close()

        return results

    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        return []
    
def get_image_description_from_db(filename: str = None, image_id: int = None, db_name: str = DB_PATH) -> str | None:
    """
    Busca a descrição da imagem gerada pelo Gemini no banco de dados SQLite.

    Args:
        filename (str, optional): O nome do arquivo da imagem. Use este OU image_id.
        image_id (int, optional): O ID da imagem no banco de dados. Use este OU filename.
        db_name (str): O caminho completo para o arquivo do banco de dados SQLite.

    Returns:
        str | None: A descrição da imagem se encontrada, ou None se não houver descrição
                    ou a imagem não for encontrada.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        query = "SELECT descricao_gemini FROM imagens WHERE "
        params = ()

        if image_id is not None:
            query += "id = ?"
            params = (image_id,)
        elif filename is not None:
            query += "nome_arquivo = ?"
            params = (filename,)
        else:
            print("Erro: Forneça um 'image_id' ou um 'filename' para buscar a descrição.")
            return None

        cursor.execute(query, params)
        result = cursor.fetchone()

        if result:
            # Retorna o valor da coluna 'descricao_gemini'
            return result[0]
        else:
            print(f"Aviso: Nenhuma descrição encontrada para a imagem com {('ID=' + str(image_id)) if image_id else ('filename=' + filename)}.")
            return None

    except sqlite3.Error as e:
        print(f"Erro no banco de dados ao buscar descrição: {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_descricao_gemini_column(db_name: str):
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Verifica se a coluna já existe para evitar erros
        cursor.execute("PRAGMA table_info(imagens)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "descricao_gemini" not in columns:
            cursor.execute("ALTER TABLE imagens ADD COLUMN descricao_gemini TEXT")
            conn.commit()
            print(f"Coluna 'descricao_gemini' adicionada com sucesso à tabela 'imagens' em {db_name}.")
        else:
            print(f"Coluna 'descricao_gemini' já existe na tabela 'imagens' em {db_name}.")
            
    except sqlite3.Error as e:
        print(f"Erro ao adicionar coluna 'descricao_gemini': {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            
def save_image_description_to_db(filename: str, description: str, db_name=r"C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\imagens.db") -> bool:
    """
    Salva a descrição gerada pelo Gemini no banco de dados SQLite para a imagem especificada.

    Args:
        filename (str): O nome do arquivo da imagem que servirá como chave para atualização.
        description (str): O texto descritivo gerado pela API do Gemini.
        db_name (str): O caminho completo para o arquivo do banco de dados SQLite.

    Returns:
        bool: True se a descrição foi salva com sucesso, False caso contrário.
    """
    add_descricao_gemini_column(db_name=db_name)
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Atualiza a coluna 'descricao_gemini' para a imagem correspondente ao nome do arquivo.
        # Certifique-se de que a coluna 'nome_arquivo' é única ou que você está
        # satisfeito em atualizar o primeiro registro encontrado.
        # Se você tiver um 'id' único para cada imagem, seria mais robusto
        # usar o 'id' para a atualização, mas estamos seguindo o 'filename'
        # como seu 'retrieve_image_bytes_from_db' original pode fazer.
        cursor.execute("UPDATE imagens SET descricao_gemini = ? WHERE nome_arquivo = ?", (description, filename))

        if cursor.rowcount > 0:
            conn.commit()  # Confirma a transação
            print(f"Sucesso: Descrição da imagem para '{filename}' salva no DB.")
            return True
        else:
            print(f"Aviso: Nenhuma imagem encontrada com o nome de arquivo '{filename}' para atualizar.")
            return False

    except sqlite3.Error as e:
        print(f"Erro no banco de dados ao salvar descrição para '{filename}': {e}")
        if conn:
            conn.rollback() # Reverte a transação em caso de erro
        return False
    finally:
        if conn:
            conn.close() # Garante que a conexão seja fechada
            
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
    
def non_described_images(db_name=r"C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\imagens.db"):
    """Busca todas as imagens que ainda não foram descritas."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Seleciona imagens que não têm descrição (NULL ou string vazia)
    cursor.execute("SELECT id, nome_arquivo FROM imagens WHERE descricao_gemini IS NULL OR descricao_gemini = ''")
    ids_images = cursor.fetchall()
    
    return ids_images
