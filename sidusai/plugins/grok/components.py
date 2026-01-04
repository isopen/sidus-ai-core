import requests
import time
from typing import Optional, Dict, Any, List, Union

class GrokClientComponent:
    BASE_URL = "https://api.x.ai"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_delay = 0.2

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'SidusAI-Grok-Plugin/1.0'
        }

        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        self.session.headers.update(headers)

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        try:
            self.last_request_time = time.time()

            if method == "GET":
                response = self.session.get(url, params=params, timeout=60)
            elif method == "POST":
                response = self.session.post(url, json=data, params=params, timeout=60)
            elif method == "DELETE":
                response = self.session.delete(url, params=params, timeout=60)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 5
                time.sleep(wait_time)
                return self._request(method, endpoint, data, params)
            else:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', str(e))
                except:
                    error_msg = e.response.text[:200] if e.response.text else str(e)
                raise Exception(f"HTTP error {e.response.status_code}: {error_msg}")
        except requests.exceptions.Timeout:
            raise Exception("Request timeout. The server took too long to respond.")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def test_connection(self) -> bool:
        try:
            response = self._request("GET", "/v1/models")
            return "data" in response
        except Exception:
            return False

    def get_api_key_info(self) -> Dict[str, Any]:
        return self._request("GET", "/v1/api-key")

    def list_models(self) -> Dict[str, Any]:
        return self._request("GET", "/v1/models")

    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/models/{model_id}")

    def list_language_models(self) -> Dict[str, Any]:
        return self._request("GET", "/v1/language-models")

    def get_language_model_info(self, model_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/language-models/{model_id}")

    def list_image_generation_models(self) -> Dict[str, Any]:
        return self._request("GET", "/v1/image-generation-models")

    def get_image_generation_model_info(self, model_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/image-generation-models/{model_id}")

    def chat_completion(self,
                       model: str = "grok-4-0709",
                       messages: List[Dict[str, Any]] = None,
                       max_tokens: Optional[int] = None,
                       temperature: Optional[float] = None,
                       top_p: Optional[float] = None,
                       n: int = 1,
                       stream: bool = False,
                       tools: Optional[List[Dict]] = None,
                       tool_choice: Optional[Union[str, Dict]] = None) -> Dict[str, Any]:

        data = {
            "model": model,
            "messages": messages or [],
            "n": n,
            "stream": stream
        }

        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p
        if tools is not None:
            data["tools"] = tools
        if tool_choice is not None:
            data["tool_choice"] = tool_choice

        return self._request("POST", "/v1/chat/completions", data=data)

    def create_response(self,
                       model: str = "grok-4-0709",
                       input: Union[str, List[Dict[str, Any]]] = None,
                       max_output_tokens: Optional[int] = None,
                       temperature: Optional[float] = None,
                       top_p: Optional[float] = None,
                       store: bool = True,
                       tools: Optional[List[Dict]] = None,
                       tool_choice: Optional[Union[str, Dict]] = None) -> Dict[str, Any]:

        data = {
            "model": model,
            "store": store
        }

        if isinstance(input, str):
            data["input"] = input
        elif isinstance(input, list):
            data["input"] = input
        else:
            raise ValueError("Input must be either a string or a list of messages")

        if max_output_tokens is not None:
            data["max_output_tokens"] = max_output_tokens
        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p
        if tools is not None:
            data["tools"] = tools
        if tool_choice is not None:
            data["tool_choice"] = tool_choice

        return self._request("POST", "/v1/responses", data=data)

    def get_response(self, response_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/responses/{response_id}")

    def delete_response(self, response_id: str) -> Dict[str, Any]:
        return self._request("DELETE", f"/v1/responses/{response_id}")

    def anthropic_messages(self,
                          model: str = "grok-4-0709",
                          messages: List[Dict[str, Any]] = None,
                          max_tokens: int = 1024,
                          temperature: Optional[float] = None,
                          top_p: Optional[float] = None) -> Dict[str, Any]:

        data = {
            "model": model,
            "messages": messages or [],
            "max_tokens": max_tokens
        }

        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p

        return self._request("POST", "/v1/messages", data=data)

    def generate_image(self,
                      prompt: str,
                      model: str = "grok-2-image",
                      n: int = 1,
                      size: str = "1024x1024",
                      response_format: str = "url") -> Dict[str, Any]:

        data = {
            "prompt": prompt,
            "model": model,
            "n": n,
            "size": size,
            "response_format": response_format
        }

        return self._request("POST", "/v1/images/generations", data=data)

    def tokenize_text(self, text: str, model: str = "grok-4-0709") -> Dict[str, Any]:
        data = {
            "text": text,
            "model": model
        }

        return self._request("POST", "/v1/tokenize-text", data=data)

    def get_deferred_completion(self, request_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/chat/deferred-completion/{request_id}")

    def legacy_completion(self,
                         model: str = "grok-3",
                         prompt: str = "",
                         max_tokens: int = 16,
                         temperature: Optional[float] = None,
                         top_p: Optional[float] = None) -> Dict[str, Any]:

        data = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens
        }

        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p

        return self._request("POST", "/v1/completions", data=data)

    def anthropic_completion(self,
                            model: str = "grok-3",
                            prompt: str = "",
                            max_tokens_to_sample: int = 16,
                            temperature: Optional[float] = None,
                            top_p: Optional[float] = None) -> Dict[str, Any]:

        data = {
            "model": model,
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens_to_sample
        }

        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p

        return self._request("POST", "/v1/complete", data=data)
