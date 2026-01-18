from sidusai.core.plugin import ChatAgentValue
from sidusai.plugins.mistral.components import MistralClientComponent

def mistral_chat_transform_skill(value: ChatAgentValue, client: MistralClientComponent) -> ChatAgentValue:
    print("🔧 Starting mistral_chat_transform_skill...")

    response = client.request(value)
    print(f"🔧 Mistral response received, status: {response.status_code}")
    print(f"🔧 Model used: {response.model}")

    if response.last_message is not None and 'content' in response.last_message:
        content = response.last_message['content']
        print(f"🔧 Adding assistant content: {content}")
        value.append_assistant(content)

        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            print(f"🔧 Token usage - Prompt: {usage.get('prompt_tokens', 0)}, "
                  f"Completion: {usage.get('completion_tokens', 0)}, "
                  f"Total: {usage.get('total_tokens', 0)}")
    else:
        print("❌ No valid content in Mistral response")
        if response.choices:
            print(f"🔧 Choices available: {len(response.choices)}")
            for choice in response.choices:
                print(f"🔧 Choice message: {choice.get('message', {})}")

    print("🔧 Mistral skill execution completed")
    return value
