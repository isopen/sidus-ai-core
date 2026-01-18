import requests
import json
from sidusai.core.plugin import ChatAgentValue

__default_mistral_model__ = 'open-mistral-7b'
__default_max_tokens__ = 1024
__default_temperature__ = 0.7
__default_top_p__ = 0.9
__default_base_url__ = 'https://api.mistral.ai/v1'

class MistralResponse:
    def __init__(self, response: requests.Response):
        self.status_code = response.status_code
        self.last_message = None

        print(f"🔧 Mistral Response status: {response.status_code}")

        if response.status_code == 200:
            try:
                obj = response.json()
                print("✅ Mistral request successful")

                self.choices = obj.get('choices', [])
                if self.choices:
                    self.last_message = self.choices[0].get('message', {})
                    content = self.last_message.get('content', '')
                    print(f"🔧 Mistral response content length: {len(content)} characters")

                self.id = obj.get('id')
                self.model = obj.get('model')
                self.usage = obj.get('usage', {})
                self.created = obj.get('created')

            except json.JSONDecodeError as e:
                print(f"❌ Mistral JSON decode error: {e}")
                self.last_message = None
        else:
            print(f"❌ Mistral request failed with status: {response.status_code}")
            if response.text:
                print(f"🔧 Mistral response text: {response.text}")

    def is_successful(self):
        return self.status_code == 200 and self.last_message is not None

    def get_tokens_usage(self):
        return self.usage

    def get_response_id(self):
        return self.id


class MistralClientComponent:
    def __init__(self, api_key: str, model_name: str = None, base_url: str = None, **kwargs):
        self.api_key = api_key
        self.model_name = model_name if model_name is not None else __default_mistral_model__
        self.base_url = base_url if base_url is not None else __default_base_url__
        self.params = kwargs

        self.session = requests.Session()

        print(f"🔧 Mistral client initialized with API Key")
        print(f"🔧 Model: {self.model_name}")
        print(f"🔧 Base URL: {self.base_url}")

    def request(self, chat: ChatAgentValue) -> MistralResponse:
        print("🔧 Starting Mistral request...")

        chat_endpoint = f"{self.base_url}/chat/completions"

        payload = self._build_payload(chat)
        headers = self._build_headers()

        print(f"🔧 Sending request to Mistral API...")
        print(f"🔧 Endpoint: {chat_endpoint}")

        try:
            response = self.session.post(
                chat_endpoint, 
                headers=headers, 
                json=payload,
                timeout=30
            )
            print(f"🔧 Mistral request completed")
            return MistralResponse(response)

        except requests.exceptions.RequestException as e:
            print(f"❌ Mistral request failed: {e}")
            mock_response = requests.Response()
            mock_response.status_code = 500
            return MistralResponse(mock_response)

    def _build_payload(self, chat: ChatAgentValue):
        messages = [{'role': v['role'], 'content': v['content']} for v in chat.messages]

        for msg in messages:
            if msg['role'] == 'assistant':
                msg['role'] = 'assistant'
            elif msg['role'] == 'user':
                msg['role'] = 'user'
            elif msg['role'] == 'system':
                msg['role'] = 'system'

        payload = {
            "messages": messages,
            "model": self.model_name,
            "max_tokens": self.params.get('max_tokens', __default_max_tokens__),
            "temperature": self.params.get('temperature', __default_temperature__),
            "top_p": self.params.get('top_p', __default_top_p__),
            "stream": False
        }

        extra_params = {}
        for key in ['frequency_penalty', 'presence_penalty', 'stop']:
            if key in self.params and self.params[key] is not None:
                extra_params[key] = self.params[key]

        if extra_params:
            payload.update(extra_params)

        payload = {k: v for k, v in payload.items() if v is not None}

        print(f"🔧 Payload model: {payload.get('model')}")
        print(f"🔧 Payload messages count: {len(payload.get('messages', []))}")

        return payload

    def _build_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }

    def get_available_models(self):
        try:
            models_endpoint = f"{self.base_url}/models"
            headers = self._build_headers()

            response = self.session.get(
                models_endpoint,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                models = response.json()
                print(f"🔧 Available Mistral models: {len(models.get('data', []))}")
                return models.get('data', [])
            else:
                print(f"❌ Failed to get models: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error getting models: {e}")
            return []

    def create_embedding(self, text: str, model: str = "mistral-embed"):
        try:
            embedding_endpoint = f"{self.base_url}/embeddings"
            headers = self._build_headers()

            payload = {
                "input": text,
                "model": model
            }

            response = self.session.post(
                embedding_endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Embedding created successfully")
                return result.get('data', [])
            else:
                print(f"❌ Failed to create embedding: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error creating embedding: {e}")
            return []
