from sidusai.core.plugin import ChatAgentValue
from sidusai.plugins.gigachat.components import GigaChatClientComponent


def gc_chat_transform_skill(value: ChatAgentValue, client: GigaChatClientComponent) -> ChatAgentValue:
    print("🔧 Starting gc_chat_transform_skill...")
    
    response = client.request(value)
    print(f"🔧 Response received, status: {response.status_code}")
    print(f"🔧 Last message: {response.last_message}")
    
    if response.last_message is not None and 'content' in response.last_message:
        content = response.last_message['content']
        print(f"🔧 Adding assistant content: {content}")
        value.append_assistant(content)
    else:
        print("❌ No valid content in response")

    print("🔧 Skill execution completed")
    return value