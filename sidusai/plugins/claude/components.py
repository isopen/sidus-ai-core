import requests
import json
import time
import base64
from typing import Optional, Dict, Any, List
import os

class ClaudeClientComponent:
    API_VERSION = "2023-06-01"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.base_url = "https://api.anthropic.com"
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_delay = 0.5

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not provided and not found in environment")

        self.session.headers.update({
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': self.API_VERSION
        })

        self.timeout = 30

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, beta_header: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/{endpoint}"

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        try:
            self.last_request_time = time.time()

            headers = self.session.headers.copy()
            if beta_header:
                headers['anthropic-beta'] = beta_header

            if method == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
            elif method == "GET":
                response = self.session.get(url, headers=headers, timeout=self.timeout)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()

            try:
                return response.json()
            except json.JSONDecodeError:
                return {"success": False, "error": "Invalid JSON response", "raw": response.text}

        except requests.exceptions.HTTPError as e:
            error_msg = e.response.text if e.response.text else str(e)
            return {"success": False, "error": f"HTTP error {e.response.status_code}: {error_msg}"}
        except Exception as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}

    def test_connection(self) -> bool:
        try:
            response = self.create_message("Test", model="claude-3-haiku-20240307")
            return response.get('success', False)
        except:
            return False

    def create_message(self, prompt: str, model: str = 'claude-3-haiku-20240307', max_tokens: int = 1024, system: Optional[str] = None, temperature: float = 0.7, top_p: float = 1.0) -> Dict[str, Any]:
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        if system:
            data["system"] = system

        if temperature != 0.7:
            data["temperature"] = temperature

        if top_p != 1.0:
            data["top_p"] = top_p

        response = self._request("POST", "messages", data)
        response['success'] = 'content' in response
        return response

    def count_tokens(self, messages: List[Dict[str, Any]], model: str = 'claude-3-haiku-20240307') -> Dict[str, Any]:
        data = {
            "model": model,
            "messages": messages
        }

        response = self._request("POST", "messages/count_tokens", data)
        response['success'] = 'input_tokens' in response
        return response

    def create_batch(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        data = {
            "requests": requests
        }

        response = self._request("POST", "messages/batches", data)
        response['success'] = 'id' in response
        return response

    def get_batch(self, batch_id: str) -> Dict[str, Any]:
        response = self._request("GET", f"messages/batches/{batch_id}")
        response['success'] = 'id' in response
        return response

    def list_batches(self) -> Dict[str, Any]:
        response = self._request("GET", "messages/batches")
        response['success'] = 'data' in response
        return response

    def cancel_batch(self, batch_id: str) -> Dict[str, Any]:
        response = self._request("POST", f"messages/batches/{batch_id}/cancel")
        response['success'] = 'id' in response
        return response

    def delete_batch(self, batch_id: str) -> Dict[str, Any]:
        response = self._request("DELETE", f"messages/batches/{batch_id}")
        response['success'] = 'type' in response and response['type'] == 'message_batch_deleted'
        return response

    def list_models(self) -> Dict[str, Any]:
        response = self._request("GET", "models")
        response['success'] = 'data' in response
        return response

    def get_model(self, model_id: str) -> Dict[str, Any]:
        response = self._request("GET", f"models/{model_id}")
        response['success'] = 'id' in response
        return response

    def upload_file(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()

            filename = os.path.basename(file_path)

            files = {
                'file': (filename, file_data)
            }

            headers = {
                'x-api-key': self.api_key,
                'anthropic-version': self.API_VERSION,
                'anthropic-beta': 'files-api-2025-04-14'
            }

            url = f"{self.base_url}/v1/files"
            response = requests.post(url, files=files, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            result['success'] = True
            return result

        except Exception as e:
            return {"success": False, "error": f"Failed to upload file: {str(e)}"}

    def list_files(self) -> Dict[str, Any]:
        response = self._request("GET", "files", beta_header='files-api-2025-04-14')
        response['success'] = 'data' in response
        return response

    def get_file_content(self, file_id: str) -> Dict[str, Any]:
        response = self._request("GET", f"files/{file_id}/content", beta_header='files-api-2025-04-14')
        response['success'] = True
        return response

    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        response = self._request("GET", f"files/{file_id}", beta_header='files-api-2025-04-14')
        response['success'] = 'id' in response
        return response

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        response = self._request("DELETE", f"files/{file_id}", beta_header='files-api-2025-04-14')
        response['success'] = 'type' in response and response['type'] == 'file_deleted'
        return response
