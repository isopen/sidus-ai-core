import os
import sys

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai as sai
import sidusai.plugins.mistral as mistral

api_key = os.environ.get('MISTRAL_API_KEY')

if not api_key:
    print("❌ MISTRAL_API_KEY environment variable is not set")
    print("💡 Get your API key from: https://console.mistral.ai/api-keys/")
    exit(1)

print(f"🔧 API Key loaded (first 10 chars): {api_key[:10]}...")

system_prompt = 'You are a helpful assistant'

print("🤖 Creating Mistral agent...")
agent = mistral.MistralSingleChatAgent(
    api_key=api_key,
    system_prompt=system_prompt,
    temperature=0.7,
    max_tokens=50,
    model_name="open-mistral-7b"
)

def accept_response(value: sai.ChatAgentValue):
    message = value.last_content()
    print(f'🤖 Assistant: {message}')

if __name__ == '__main__':
    print("🔧 Building application...")
    agent.application_build()

    print("💬 Sending message to Mistral...")
    agent.send_to_chat(
        message='What is the capital of France?',
        handler=accept_response
    )
