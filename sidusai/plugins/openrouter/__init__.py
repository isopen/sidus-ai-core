import sidusai as sai
from typing import Optional, Dict, Any, List
import os

from .components import OpenRouterClient
from .skills import (
    get_available_models_skill,
    chat_completion_skill,
    text_completion_skill,
    get_model_info_skill,
    calculate_cost_skill,
    openrouter_chat_skill,
    OpenRouterDataValue,
    OpenRouterModelValue
)

__openrouter_agent_name__ = 'openrouter_agent'


class OpenRouterPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.openrouter_client = None
        print(f"🔧 OpenRouter Plugin initialized")

        if self.api_key and not os.getenv('OPENROUTER_API_KEY'):
            os.environ['OPENROUTER_API_KEY'] = self.api_key

    def apply_plugin(self, agent: sai.Agent):
        print("🔧 Applying OpenRouter plugin to agent...")

        try:
            self.openrouter_client = OpenRouterClient(api_key=self.api_key)

            if self.openrouter_client.test_connection():
                print("✅ OpenRouter connection successful")
            else:
                print("⚠️ OpenRouter connection issues - some features may not work")

            self.skills = {}

            def available_models_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openrouter_component'] = self.openrouter_client
                result = get_available_models_skill(context)
                return OpenRouterDataValue(result.value)

            def chat_completion_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openrouter_component'] = self.openrouter_client
                result = chat_completion_skill(context)
                return OpenRouterDataValue(result.value)

            def text_completion_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openrouter_component'] = self.openrouter_client
                result = text_completion_skill(context)
                return OpenRouterDataValue(result.value)

            def model_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openrouter_component'] = self.openrouter_client
                result = get_model_info_skill(context)
                return OpenRouterModelValue(result.value)

            def calculate_cost_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['openrouter_component'] = self.openrouter_client
                result = calculate_cost_skill(context)
                return OpenRouterDataValue(result.value)

            def openrouter_chat_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value

                if isinstance(context, dict) and 'messages' in context:
                    chat_data = type('ChatData', (), {
                        'messages': context['messages'],
                        'context': {'openrouter_component': self.openrouter_client}
                    })
                    result = openrouter_chat_skill(chat_data)

                    if isinstance(result, dict) and 'messages' in result:
                        return OpenRouterDataValue({'messages': result['messages']})
                    elif isinstance(result, dict):
                        return OpenRouterDataValue(result)
                    else:
                        return OpenRouterDataValue({'error': 'Invalid chat response'})
                else:
                    return OpenRouterDataValue({'error': 'No messages provided'})

            self.skills = {
                'get_available_models': available_models_wrapper,
                'chat_completion': chat_completion_wrapper,
                'text_completion': text_completion_wrapper,
                'get_model_info': model_info_wrapper,
                'calculate_cost': calculate_cost_wrapper,
                'openrouter_chat': openrouter_chat_wrapper
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.openrouter_client = self.openrouter_client
            agent.openrouter_skills = self.skills

            print("✅ OpenRouter plugin applied successfully")

        except Exception as e:
            print(f"❌ Error applying OpenRouter plugin: {e}")
            import traceback
            traceback.print_exc()


class OpenRouterAgent(sai.Agent):
    def __init__(self, api_key: Optional[str] = None, name: str = __openrouter_agent_name__):
        super().__init__()
        self._name = name

        print(f"🤖 Creating OpenRouter Agent '{name}'...")
        self.plugin = OpenRouterPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)

        print(f"✅ OpenRouter Agent '{name}' created successfully")

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

    def get_available_models(self, free_only: bool = True) -> Dict[str, Any]:
        context = {
            'free_only': free_only
        }

        if 'get_available_models' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_available_models'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "amazon/nova-2-lite-v1:free",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        context = {
            'messages': messages,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        if 'chat_completion' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['chat_completion'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def text_completion(
        self,
        prompt: str,
        model: str = "amazon/nova-2-lite-v1:free",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        context = {
            'prompt': prompt,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        if 'text_completion' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['text_completion'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        context = {
            'model_id': model_id
        }

        if 'get_model_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_model_info'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> Dict[str, Any]:
        context = {
            'model': model,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens
        }

        if 'calculate_cost' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['calculate_cost'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def chat(self, message: str) -> str:
        if 'openrouter_chat' not in self.plugin.skills:
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
            result = self.plugin.skills['openrouter_chat'](agent_value)

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
            print(f"❌ Error in chat method: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"


def create_openrouter_agent(api_key: Optional[str] = None) -> OpenRouterAgent:
    return OpenRouterAgent(api_key=api_key)


class SimpleOpenRouterClient:
    def __init__(self, api_key: Optional[str] = None):
        from .components import OpenRouterClient

        actual_api_key = api_key or os.getenv('OPENROUTER_API_KEY')

        if actual_api_key and not os.getenv('OPENROUTER_API_KEY'):
            os.environ['OPENROUTER_API_KEY'] = actual_api_key

        self.client = OpenRouterClient(api_key=actual_api_key)

    def get_available_models(self, free_only: bool = True) -> List[Dict[str, Any]]:
        return self.client.get_available_models(free_only)

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "amazon/nova-2-lite-v1:free",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        return self.client.chat_completion(messages, model, temperature, max_tokens)

    def text_completion(
        self,
        prompt: str,
        model: str = "amazon/nova-2-lite-v1:free",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        return self.client.chat_completion(
            [{"role": "user", "content": prompt}], 
            model, 
            temperature, 
            max_tokens
        )

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        return self.client.get_detailed_model_info(model_id)

    def calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> Dict[str, Any]:
        return self.client.calculate_usage_cost(model, prompt_tokens, completion_tokens)

    def test_connection(self) -> bool:
        return self.client.test_connection()


__all__ = [
    'OpenRouterPlugin',
    'OpenRouterAgent',
    'SimpleOpenRouterClient',
    'create_openrouter_agent',
    'OpenRouterClient',
]
