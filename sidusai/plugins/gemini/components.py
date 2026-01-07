import requests
import json
import time
import base64
from typing import Optional, Dict, Any, List
import os

class GeminiClientComponent:
    API_VERSION = "v1beta"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com"
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_delay = 0.5

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not provided and not found in environment")

        self.session.headers.update({
            'Content-Type': 'application/json',
            'x-goog-api-key': self.api_key
        })

        self.timeout = 30

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.API_VERSION}/{endpoint}"

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        try:
            self.last_request_time = time.time()

            if method == "POST":
                response = self.session.post(url, json=data, timeout=self.timeout)
            elif method == "GET":
                response = self.session.get(url, params=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()

            try:
                return response.json()
            except json.JSONDecodeError:
                return {"success": False, "error": "Invalid JSON response", "raw": response.text}

        except requests.exceptions.HTTPError as e:
            error_msg = e.response.text[:500] if e.response.text else str(e)
            return {"success": False, "error": f"HTTP error {e.response.status_code}: {error_msg}"}
        except Exception as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}

    def test_connection(self) -> bool:
        try:
            response = self.generate_text("Test", model="gemini-3-flash-preview")
            return response.get('success', False)
        except:
            return False

    def generate_text(self, prompt: str, model: str = 'gemini-3-flash-preview',
                     temperature: float = 0.7, max_tokens: int = 1024) -> Dict[str, Any]:

        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        response = self._request("POST", f"models/{model}:generateContent", data)
        response['success'] = 'candidates' in response
        return response

    def generate_content(self, contents: List[Dict[str, Any]],
                        model: str = 'gemini-3-flash-preview',
                        generation_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        data = {
            "contents": contents,
            "generationConfig": generation_config or {}
        }

        response = self._request("POST", f"models/{model}:generateContent", data)
        response['success'] = 'candidates' in response
        return response

    def generate_image(self, prompt: str, model: str = 'imagen-4.0-generate-001',
                  sample_count: int = 4, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        base_params = {
            "sampleCount": sample_count,
        }

        if parameters:
            filtered_params = {k: v for k, v in parameters.items() if k != 'negativePrompt'}
            base_params.update(filtered_params)

        data = {
            "instances": [{"prompt": prompt}],
            "parameters": base_params
        }

        response = self._request("POST", f"models/{model}:predict", data)
        response['success'] = 'predictions' in response
        return response

    def embed_content(self, text: str, model: str = 'gemini-embedding-001') -> Dict[str, Any]:

        data = {
            "model": model,
            "content": {
                "parts": [{"text": text}]
            }
        }

        response = self._request("POST", f"models/{model}:embedContent", data)
        response['success'] = 'embedding' in response
        return response

    def batch_embed_contents(self, texts: List[str],
                            model: str = 'gemini-embedding-001') -> Dict[str, Any]:

        requests_list = []
        for text in texts:
            requests_list.append({
                "model": f"models/{model}",
                "content": {
                    "parts": [{"text": text}]
                }
            })

        data = {"requests": requests_list}

        response = self._request("POST", f"models/{model}:batchEmbedContents", data)
        response['success'] = 'embeddings' in response
        return response

    def analyze_image(self, image_path: str, prompt: str,
                     model: str = 'gemini-3-flash-preview',
                     temperature: float = 0.5, thinking_budget: int = 0) -> Dict[str, Any]:

        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            mime_type = self._get_mime_type(image_path)

            data = {
                "contents": [{
                    "parts": [
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": image_data
                            }
                        },
                        {
                            "text": prompt
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 1000
                }
            }

            response = self._request("POST", f"models/{model}:generateContent", data)
            response['success'] = 'candidates' in response
            return response

        except Exception as e:
            return {"success": False, "error": f"Failed to process image: {str(e)}"}

    def _get_mime_type(self, filepath: str) -> str:
        ext = filepath.lower().split('.')[-1]

        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'webp': 'image/webp',
        }

        return mime_types.get(ext, 'application/octet-stream')
