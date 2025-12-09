import sidusai as sai
from typing import Optional, Dict, Any, List

from .components import DogCEOClient
from .skills import (
    get_all_breeds_skill,
    get_random_dog_skill,
    get_breed_images_skill,
    get_sub_breeds_skill,
    dogceo_chat_skill,
    DogCEODataValue
)

__dogceo_agent_name__ = 'dogceo_agent'

class DogCEOPlugin(sai.AgentPlugin):
    def __init__(self):
        super().__init__()
        self.dog_client = None
        print(f"Dog CEO Plugin initialized")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying Dog CEO plugin to agent...")

        try:
            self.dog_client = DogCEOClient()

            if self.dog_client.test_connection():
                print("Dog CEO API connection successful")
            else:
                print("Dog CEO API connection issues - some features may not work")

            self.skills = {}

            def all_breeds_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['dog_component'] = self.dog_client
                result = get_all_breeds_skill(context)
                return DogCEODataValue(result.value)

            def random_dog_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['dog_component'] = self.dog_client
                result = get_random_dog_skill(context)
                return DogCEODataValue(result.value)

            def breed_images_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['dog_component'] = self.dog_client
                result = get_breed_images_skill(context)
                return DogCEODataValue(result.value)

            def sub_breeds_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['dog_component'] = self.dog_client
                result = get_sub_breeds_skill(context)
                return DogCEODataValue(result.value)

            def dogceo_chat_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value

                if isinstance(context, dict) and 'messages' in context:
                    chat_data = type('ChatData', (), {
                        'messages': context['messages'],
                        'context': {'dog_component': self.dog_client}
                    })
                    result = dogceo_chat_skill(chat_data)

                    if isinstance(result, dict) and 'messages' in result:
                        return DogCEODataValue({'messages': result['messages']})
                    elif isinstance(result, dict):
                        return DogCEODataValue(result)
                    else:
                        return DogCEODataValue({'error': 'Invalid chat response'})
                else:
                    return DogCEODataValue({'error': 'No messages provided'})

            self.skills = {
                'get_all_breeds': all_breeds_wrapper,
                'get_random_dog': random_dog_wrapper,
                'get_breed_images': breed_images_wrapper,
                'get_sub_breeds': sub_breeds_wrapper,
                'dogceo_chat': dogceo_chat_wrapper
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.dog_client = self.dog_client
            agent.dogceo_skills = self.skills

            print("Dog CEO plugin applied successfully")

        except Exception as e:
            print(f"Error applying Dog CEO plugin: {e}")
            import traceback
            traceback.print_exc()

class DogCEOAgent(sai.Agent):
    def __init__(self, name: str = __dogceo_agent_name__):
        super().__init__()
        self._name = name

        print(f"Creating Dog CEO Agent '{name}'...")
        self.plugin = DogCEOPlugin()
        self.plugin.apply_plugin(self)

        print(f"Dog CEO Agent '{name}' created successfully")

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        try:
            return sai.AgentValue(value=context)
        except TypeError:
            agent_value = sai.AgentValue()
            agent_value.value = context
            return agent_value

    def get_all_breeds(self) -> Dict[str, Any]:
        context = {}

        if 'get_all_breeds' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_all_breeds'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_random_dog(self, breed: Optional[str] = None, count: int = 1) -> Dict[str, Any]:
        context = {
            'breed': breed,
            'count': count
        }

        if 'get_random_dog' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_random_dog'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_breed_images(self, breed: str, count: int = 10) -> Dict[str, Any]:
        context = {
            'breed': breed,
            'count': count
        }

        if 'get_breed_images' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_breed_images'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_sub_breeds(self, breed: str) -> Dict[str, Any]:
        context = {
            'breed': breed
        }

        if 'get_sub_breeds' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_sub_breeds'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def chat(self, message: str) -> str:
        if 'dogceo_chat' not in self.plugin.skills:
            return "Chat skill not available"

        try:
            context = {
                'messages': [
                    {
                        'role': 'user',
                        'content': message
                    }
                ]
            }

            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['dogceo_chat'](agent_value)

            result_dict = result.value if hasattr(result, 'value') else result

            if isinstance(result_dict, dict):
                if 'messages' in result_dict:
                    messages = result_dict['messages']
                    if messages and len(messages) > 1:
                        last_message = messages[-1]
                        if isinstance(last_message, dict) and 'content' in last_message:
                            return last_message['content']

                if 'content' in result_dict:
                    return result_dict['content']

                if 'error' in result_dict:
                    return f"Error: {result_dict['error']}"

            return "No valid response"

        except Exception as e:
            print(f"Error in chat method: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"

def create_dogceo_agent() -> DogCEOAgent:
    return DogCEOAgent()

class SimpleDogCEOClient:
    def __init__(self):
        from .components import DogCEOClient
        self.client = DogCEOClient()

    def get_all_breeds(self) -> Dict[str, Any]:
        return self.client.get_all_breeds()

    def get_random_dog(self, breed: Optional[str] = None, count: int = 1) -> Dict[str, Any]:
        return self.client.get_random_dog(breed, count)

    def get_breed_images(self, breed: str, count: int = 10) -> List[str]:
        return self.client.get_breed_images(breed, count)

    def get_sub_breeds(self, breed: str) -> List[str]:
        return self.client.get_sub_breeds(breed)

    def test_connection(self) -> bool:
        return self.client.test_connection()

__all__ = [
    'DogCEOPlugin',
    'DogCEOAgent',
    'SimpleDogCEOClient',
    'create_dogceo_agent',
    'DogCEOClient',
]
