import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.grok import create_grok_agent

def main():
    agent = create_grok_agent(api_key=os.environ.get('XAI_API_KEY'))

    print("Testing API connection...")
    if agent.test_connection():
        print("✅ Connected to Grok API")

        print("\nAvailable models:")
        result = agent.list_models()
        if result.get('success'):
            print(f"Total models: {result.get('total_models')}")

        print("\nChat completion example:")
        chat_result = agent.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"}
            ],
            model="grok-4-0709"
        )

        if chat_result.get('success'):
            response = chat_result['choices'][0]['content']
            print(f"Response: {response}")

    else:
        print("❌ Failed to connect to Grok API")

if __name__ == "__main__":
    main()
