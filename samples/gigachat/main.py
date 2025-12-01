import os
import sys
import base64
#import urllib3
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai as sai
import sidusai.plugins.gigachat as gc

api_key = os.environ.get('GIGACHAT_API_KEY')

try:
    decoded_credentials = base64.b64decode(api_key).decode('utf-8')
    client_id, client_secret = decoded_credentials.split(':', 1)
    
    print(f"🔧 Client ID: {client_id}")
    print(f"🔧 Client Secret: {client_secret[:10]}...")
    
except Exception as e:
    print(f"❌ Failed to decode API Key: {e}")
    print("💡 Make sure your API Key is in correct base64 format: client_id:client_secret")
    exit(1)

system_prompt = 'You are a helpful assistant'

print("🤖 Creating GigaChat agent...")
agent = gc.GigaChatSingleChatAgent(
    client_id=client_id,
    client_secret=client_secret,
    system_prompt=system_prompt,
    temperature=0.7,
    max_tokens=500,
)

def accept_response(value: sai.ChatAgentValue):
    message = value.last_content()
    print(f'🤖 Assistant: {message}')

if __name__ == '__main__':
    print("🔧 Building application...")
    agent.application_build()
    
    print("💬 Sending message to GigaChat...")
    agent.send_to_chat(
        message='What is the capital of Russia?',
        handler=accept_response
    )