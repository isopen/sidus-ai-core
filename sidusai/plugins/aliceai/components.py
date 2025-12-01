import requests
import json
from sidusai.core.plugin import ChatAgentValue

__default_url__ = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

__default_yandex_model__ = 'yandexgpt-lite/latest'
__default_max_tokens__ = 1024
__default_temperature__ = 0.7

class AliceAIResponse:
    def __init__(self, response: requests.Response):
        self.status_code = response.status_code
        self.last_message = None

        print(f"🔧 Response status: {response.status_code}")

        if response.status_code == 200:
            try:
                obj = response.json()
                print("✅ Request successful")

                # Yandex GPT формат ответа
                result = obj.get('result', {})
                alternatives = result.get('alternatives', [])
                if alternatives:
                    self.last_message = alternatives[0].get('message', {})
                    content = self.last_message.get('text', '')
                    print(f"🔧 Response content length: {len(content)} characters")
                    print(f"🔧 Response content: {content}")
                else:
                    print(f"🔧 No alternatives in response: {obj}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"🔧 Response text: {response.text}")
                self.last_message = None
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            if response.text:
                print(f"🔧 Response text: {response.text}")

    def is_successful(self):
        return self.status_code == 200 and self.last_message is not None

class AliceAIClientComponent:
    def __init__(self, api_key: str, folder_id: str, model_name: str = None, **kwargs):
        self.api_key = api_key
        self.folder_id = folder_id
        self.model_name = model_name if model_name is not None else __default_yandex_model__
        self.params = kwargs

        # Создаем сессию
        self.session = requests.Session()

        print(f"🔧 Alice AI (Yandex GPT) client initialized")
        print(f"🔧 Model: {self.model_name}")
        print(f"🔧 Folder ID: {self.folder_id}")

    def request(self, chat: ChatAgentValue) -> AliceAIResponse:
        print("🔧 Starting Alice AI request...")

        payload = self._build_payload(chat)
        headers = self._build_headers()

        print(f"🔧 Sending request to Yandex GPT API...")
        print(f"🔧 Payload preview: {json.dumps(payload, ensure_ascii=False)[:200]}...")

        try:
            response = self.session.post(
                __default_url__, 
                headers=headers, 
                json=payload,
                timeout=30
            )
            print(f"🔧 Request completed in {response.elapsed.total_seconds():.2f} seconds")
            return AliceAIResponse(response)

        except requests.exceptions.Timeout:
            print(f"❌ Request timeout (30 seconds)")
            mock_response = requests.Response()
            mock_response.status_code = 408
            return AliceAIResponse(mock_response)
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            mock_response = requests.Response()
            mock_response.status_code = 500
            return AliceAIResponse(mock_response)

    def _build_payload(self, chat: ChatAgentValue):
        messages = []
        for msg in chat.messages:
            role = 'user' if msg['role'] == 'user' else 'assistant'
            messages.append({
                'role': role,
                'text': msg['content']
            })

        payload = {
            "modelUri": f"gpt://{self.folder_id}/{self.model_name}",
            "completionOptions": {
                "temperature": self.params.get('temperature', __default_temperature__),
                "maxTokens": str(self.params.get('max_tokens', __default_max_tokens__))
            },
            "messages": messages
        }

        return payload

    def _build_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Api-Key {self.api_key}'
        }
