# %%
import requests
import os
from typing import List, Optional

def voyage_rerank(
    query: str,
    documents: List[str],
    model: str = "rerank-lite-1",
    api_key: Optional[str] = None):
    """
    Faz reranking de documentos com base em uma query usando a API da Voyage AI.

    Args:
        query (str): A query para reranking.
        documents (List[str]): Lista de documentos a serem reranqueados.
        model (str): Modelo de reranking a ser usado (e.g., 'rerank-lite-1').
        api_key (Optional[str]): Chave da API da Voyage AI. Se None, usa a variável de ambiente VOYAGE_API_KEY.

    Returns:
        List[Tuple[str, float, int]]: Lista de tuplas contendo (documento, score de relevância, índice original).
        Retorna uma lista vazia em caso de erro.

    Raises:
        ValueError: Se a chave da API não for fornecida ou se a entrada for inválida.
    """
    # Validar entradas
    if not query.strip():
        raise ValueError("A query não pode estar vazia.")
    if not documents:
        raise ValueError("A lista de documentos não pode estar vazia.")

    # Obter a chave da API
    if api_key is None:
        api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise ValueError("A chave da API da Voyage AI não foi fornecida. Defina a variável de ambiente VOYAGE_API_KEY ou passe api_key como argumento.")

    # Configurar a URL e os headers
    url = "https://api.voyageai.com/v1/rerank"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Configurar o corpo da requisição
    payload = {
        "query": query,
        "documents": documents,
        "model": model
    }

    try:
        # Fazer a requisição POST
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Levanta exceção para códigos de status 4xx/5xx

        # Extrair os dados da resposta
        data = response.json()
        rerank_results = data.get("data", [])

        # Associar scores e índices aos documentos originais
        results = [
            (documents[item["index"]], item["relevance_score"], item["index"])
            for item in rerank_results
        ]

        # Ordenar por relevance_score (maior para menor)
        results.sort(key=lambda x: x[1], reverse=True)

        return results

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao chamar a API da Voyage AI: {http_err}")
        print(f"Resposta: {response.text}")
        return []
    except requests.exceptions.RequestException as req_err:
        print(f"Erro de requisição ao chamar a API da Voyage AI: {req_err}")
        return []
    except (KeyError, IndexError) as parse_err:
        print(f"Erro ao processar a resposta da API: {parse_err}")
        return []

def get_voyage_embeddings(input_text: str, model: str = "voyage-3-large", api_key: Optional[str] = None) -> List[float]:
    """
    Obtém embeddings de uma string usando a API da Voyage AI.

    Args:
        input_text (str): Texto de entrada para gerar embeddings.
        model (str): Modelo da Voyage AI a ser usado (e.g., 'voyage-3', 'voyage-3-lite').
        api_key (Optional[str]): Chave da API da Voyage AI. Se None, usa a variável de ambiente VOYAGE_API_KEY.

    Returns:
        List[float]: Lista de embeddings para o texto de entrada.
        Retorna uma lista vazia em caso de erro.

    Raises:
        ValueError: Se a chave da API não for fornecida.
    """
    # Obter a chave da API
    if api_key is None:
        api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise ValueError("A chave da API da Voyage AI não foi fornecida. Defina a variável de ambiente VOYAGE_API_KEY ou passe api_key como argumento.")

    # Configurar a URL e os headers
    url = "https://api.voyageai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Configurar o corpo da requisição
    payload = {
        "input": [input_text],  # API aceita uma lista de textos
        "model": model
    }

    try:
        # Fazer a requisição POST
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Levanta exceção para códigos de status 4xx/5xx

        # Extrair os embeddings da resposta
        data = response.json()
        embeddings = data.get("data", [])[0].get("embedding", [])

        return embeddings

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao chamar a API da Voyage AI: {http_err}")
        print(f"Resposta: {response.text}")
        return []
    except requests.exceptions.RequestException as req_err:
        print(f"Erro de requisição ao chamar a API da Voyage AI: {req_err}")
        return []
    except (KeyError, IndexError) as parse_err:
        print(f"Erro ao processar a resposta da API: {parse_err}")
        return []

# Exemplo de uso
if __name__ == "__main__":
    # Exemplo de texto de entrada
    text = "Exemplo de texto em português para gerar embeddings."

    # Obter embeddings
    embeddings = get_voyage_embeddings(text)

    # Exibir o resultado
    if embeddings:
        print(f"Embeddings gerados ({len(embeddings)} dimensões):")
        print(embeddings[:10], "...")  # Mostra as primeiras 10 dimensões para brevidade
    else:
        print("Falha ao gerar embeddings.")


