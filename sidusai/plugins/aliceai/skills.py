from sidusai.core.plugin import ChatAgentValue

def create_aliceai_skill(component):
    def aliceai_chat_transform_skill(chat: ChatAgentValue) -> ChatAgentValue:
        print("🔧 Starting aliceai_chat_transform_skill...")

        if component is None:
            print("❌ Alice AI component is None")
            chat.append_assistant("Component not initialized")
            return chat

        try:
            print(f"🔧 Using component for request")
            response = component.request(chat)
            print(f"🔧 Response status: {response.status_code}")

            if response.is_successful():
                assistant_content = response.last_message.get('text', '')
                if assistant_content:
                    chat.append_assistant(assistant_content)
                    print(f"🔧 Added response: {assistant_content[:100]}...")
                else:
                    chat.append_assistant("Empty response from API")
            else:
                chat.append_assistant(f"API Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
            chat.append_assistant(f"Error: {str(e)}")

        print("🔧 Skill completed")
        return chat

    return aliceai_chat_transform_skill
