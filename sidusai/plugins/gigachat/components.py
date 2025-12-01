import requests
import json
#import ssl
import time
import uuid
import base64
#from urllib3.poolmanager import PoolManager
#from requests.adapters import HTTPAdapter
from sidusai.core.plugin import ChatAgentValue

__default_url__ = 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'
__auth_url__ = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'

__default_gigachat_model__ = 'GigaChat'
__default_max_tokens__ = 1024
__default_temperature__ = 0.7
__default_top_p__ = 0.9


#class GigaChatSSLAdapter(HTTPAdapter):
#    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
#        self.poolmanager = PoolManager(
#            num_pools=connections,
#            maxsize=maxsize,
#            block=block,
#            ssl_version=ssl.PROTOCOL_TLS,
#            cert_reqs=ssl.CERT_NONE,
#        )


class GigaChatResponse:
    def __init__(self, response: requests.Response):
        self.status_code = response.status_code
        self.last_message = None
        
        print(f"🔧 Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                obj = response.json()
                print("✅ Request successful")
                
                self.choices = obj.get('choices', [])
                if self.choices:
                    self.last_message = self.choices[0].get('message', {})
                    content = self.last_message.get('content', '')
                    print(f"🔧 Response content length: {len(content)} characters")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                self.last_message = None
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            if response.text:
                print(f"🔧 Response text: {response.text}")

    def is_successful(self):
        return self.status_code == 200 and self.last_message is not None


class GigaChatClientComponent:
    def __init__(self, client_id: str, client_secret: str, scope: str = "GIGACHAT_API_PERS", model_name: str = None, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.model_name = model_name if model_name is not None else __default_gigachat_model__
        self.params = kwargs

        self.access_token = None
        self.token_expires_at = 0

        self.session = requests.Session()
        #self.session.mount("https://", GigaChatSSLAdapter())
        
        print(f"🔧 GigaChat client initialized with OAuth")

    def _get_access_token(self) -> str:
        current_time = time.time()

        if self.access_token and current_time < self.token_expires_at:
            return self.access_token
        
        print("🔧 Requesting new OAuth token...")

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {self._encode_credentials()}',
            'RqUID': str(uuid.uuid4())
        }

        data = {
            'scope': self.scope
        }

        try:
            response = self.session.post(
                __auth_url__,
                headers = headers,
                data = data,
                timeout = 30,
                verify = False
            )
            
            print(f"🔧 OAuth response status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 1800)
                
                if self.access_token:
                    self.token_expires_at = current_time + expires_in - 60
                    
                    print("✅ OAuth token received successfully")
                    print(f"🔧 Token expires in: {expires_in} seconds")
                    return self.access_token
                else:
                    print("❌ No access_token in response")
                    print(f"🔧 Full response: {token_data}")
                    return None
            else:
                print(f"❌ Failed to get OAuth token: {response.status_code}")
                print(f"🔧 Response text: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ OAuth token request failed: {e}")
            return None

    def _encode_credentials(self) -> str:
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        print(f"🔧 Using Client ID: {self.client_id}")
        return encoded_credentials

    def request(self, chat: ChatAgentValue) -> GigaChatResponse:
        print("🔧 Starting GigaChat request...")

        access_token = self._get_access_token()
        if not access_token:
            print("❌ No valid access token available")
            mock_response = requests.Response()
            mock_response.status_code = 401
            return GigaChatResponse(mock_response)
        
        payload = self._build_payload(chat)
        headers = self._build_headers(access_token)

        print(f"🔧 Sending request to GigaChat API...")
        
        try:
            response = self.session.post(
                __default_url__, 
                headers=headers, 
                json=payload,
                timeout=30,
                verify=False
            )
            print(f"🔧 Request completed")
            return GigaChatResponse(response)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            mock_response = requests.Response()
            mock_response.status_code = 500
            return GigaChatResponse(mock_response)

    def _build_payload(self, chat: ChatAgentValue):
        messages = [{'role': v['role'], 'content': v['content']} for v in chat.messages]
        
        payload = {
            "messages": messages,
            "model": self.model_name,
            "max_tokens": self.params.get('max_tokens', __default_max_tokens__),
            "temperature": self.params.get('temperature', __default_temperature__),
            "top_p": self.params.get('top_p', __default_top_p__),
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return payload

    def _build_headers(self, access_token: str):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }