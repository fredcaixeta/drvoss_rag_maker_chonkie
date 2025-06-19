import requests
import json
import os
from PIL import Image
import io
import base64

class GeminiApiClient:
    """
    Cliente para interagir com a Google AI Generative Language REST API.
    """
    def __init__(self, api_key: str, api_version: str = "v1beta"):
        if not api_key:
            raise ValueError("API Key não fornecida. Defina a variável de ambiente GOOGLE_API_KEY.")
        self.api_key = api_key
        self.base_url = f"https://generativelanguage.googleapis.com/{api_version}/models"

    def _make_request(self, model_name: str, endpoint: str, payload: dict) -> dict:
        """Método auxiliar para fazer chamadas POST para a API."""
        url = f"{self.base_url}/{model_name}:{endpoint}?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status() # Lança exceção para erros HTTP (4xx ou 5xx)

            if not response.text:
                print(f"Aviso: Resposta da API vazia para {url}")
                return {"error": "Resposta vazia da API", "status_code": response.status_code}
            try:
                return response.json()
            except json.JSONDecodeError:
                print(f"Erro: Não foi possível decodificar JSON da resposta. Status: {response.status_code}. Conteúdo: {response.text[:500]}...")
                return {"error": "Resposta inválida da API (não JSON)", "status_code": response.status_code, "content": response.text}

        except requests.exceptions.RequestException as e:
            print(f"Erro na chamada da API: {e}")
            error_details = {}
            if hasattr(e, 'response') and e.response is not None:
                error_details["status_code"] = e.response.status_code
                try:
                    error_details.update(e.response.json())
                except json.JSONDecodeError:
                    error_details["content"] = e.response.text
            return {"error": str(e), **error_details}

    def _image_to_base64(self, image_pil: Image.Image, format: str = "PNG") -> str:
        """Converte um objeto PIL.Image.Image para string base64."""
        byte_arr = io.BytesIO()
        # Certifique-se de que a imagem esteja em um formato suportado pela API
        # PNG é geralmente seguro e sem perdas
        image_pil.save(byte_arr, format=format)
        return base64.b64encode(byte_arr.getvalue()).decode('utf-8')

    def generate_multimodal_content(self, model_name: str, prompt_parts: list, generation_config: dict = None, safety_settings: list = None) -> dict:
        """
        Chama o endpoint generateContent para gerar texto com entrada multimodal (texto + imagem).
        'prompt_parts' deve ser uma lista de dicionários, onde cada dicionário
        representa uma 'part' com 'text' ou 'inlineData'.

        Exemplo de prompt_parts:
        [
            {"text": "Descreva esta imagem:"},
            {"inlineData": {"mimeType": "image/jpeg", "data": "BASE64_STRING_DA_IMAGEM"}},
            {"text": "E relacione-a com o seguinte texto:"},
            {"text": "O texto do documento..."}
        ]
        """
        if not isinstance(prompt_parts, list) or not all(isinstance(p, dict) and ("text" in p or "inlineData" in p) for p in prompt_parts):
            raise ValueError("prompt_parts deve ser uma lista de dicionários com chaves 'text' ou 'inlineData'.")

        payload = {
            "contents": [{"parts": prompt_parts}]
        }
        if generation_config:
            payload["generationConfig"] = generation_config
        if safety_settings:
            payload["safetySettings"] = safety_settings

        # Para modelos multimodais como gemini-1.5-pro, o endpoint é o mesmo 'generateContent'
        return self._make_request(model_name, "generateContent", payload)

    def extract_text_from_response(self, response_data: dict) -> str | None:
        """
        Extrai o texto gerado da resposta da API.
        Retorna o texto ou None se não encontrado ou se houve erro.
        """
        if not response_data or "error" in response_data:
            print(f"Erro na resposta da API: {response_data.get('error', 'Desconhecido')}")
            return None

        try:
            candidates = response_data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    # Assumindo que a resposta de texto gerada estará na primeira 'part'
                    # e que é um campo 'text'. Pode precisar de mais lógica se a resposta for complexa.
                    return parts[0].get("text")
            print("Aviso: Estrutura de resposta inesperada ou sem texto gerado.")
            return None
        except (AttributeError, IndexError, KeyError, TypeError) as e:
            print(f"Erro ao extrair texto da resposta: {e}")
            return None