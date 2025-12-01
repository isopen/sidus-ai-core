import os
import sys
#import time

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai as sai
import sidusai.plugins.aliceai as aliceai

api_key = os.getenv('YANDEX_API_KEY')
folder_id = os.getenv('YANDEX_FOLDER_ID')

if not api_key or not folder_id:
    print("❌ YANDEX_API_KEY or YANDEX_FOLDER_ID not found")
    print("💡 Get them from: https://console.cloud.yandex.ru/")
    print("💡 Set with:")
    print("   export YANDEX_API_KEY='your_api_key_here'")
    print("   export YANDEX_FOLDER_ID='your_folder_id_here'")
    exit(1)

print(f"🔧 API Key: {api_key[:20]}...")
print(f"🔧 Folder ID: {folder_id}")

system_prompt = "You are a helpful assistant"

print("🤖 Creating Alice AI agent...")
try:
    agent = aliceai.AliceAISingleChatAgent(
        api_key = api_key,
        folder_id = folder_id,
        system_prompt = system_prompt,
        temperature = 0.7,
        max_tokens = 30,
        model_name='yandexgpt-lite/latest'
    )
    print("✅ Agent created successfully")
except Exception as e:
    print(f"❌ Failed to create agent: {e}")
    exit(1)

def accept_response(value: sai.ChatAgentValue):
    print(f"🔧 Handler called with {len(value.messages)} messages")
    message = value.last_content()
    print(f'🤖 Alice AI: {message}')

if __name__ == '__main__':
    print("🔧 Building application...")
    try:
        agent.application_build()
        print("✅ Application built successfully")
    except Exception as e:
        print(f"❌ Failed to build application: {e}")
        exit(1)

    print("💬 Sending message to Alice AI...")
    try:
        agent.send_to_chat(
            message='Reply simply OK if you received this message',
            handler=accept_response
        )
        print("✅ Message sent to chat")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        exit(1)

    #print("⏳ Waiting for response...")
    #for i in range(30):
    #    print(f"⏳ {30-i} seconds remaining...")
    #    time.sleep(1)
