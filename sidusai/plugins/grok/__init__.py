import sidusai as sai
from typing import Optional, Dict, Any, List, Union
import os

from .components import GrokClientComponent
from .skills import (
    get_api_info_skill,
    list_models_skill,
    chat_completion_skill,
    create_response_skill,
    generate_image_skill,
    analyze_model_capabilities_skill,
    tokenize_text_skill
)

__grok_agent_name__ = 'grok_ai_agent'

class GrokPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.environ.get('XAI_API_KEY')
        self.grok_client = None

    def apply_plugin(self, agent: sai.Agent):
        try:
            self.grok_client = GrokClientComponent(self.api_key)

            self.skills = {}

            skill_wrappers = {
                'get_api_info': get_api_info_skill,
                'list_models': list_models_skill,
                'chat_completion': chat_completion_skill,
                'create_response': create_response_skill,
                'generate_image': generate_image_skill,
                'analyze_model_capabilities': analyze_model_capabilities_skill,
                'tokenize_text': tokenize_text_skill
            }

            for skill_name, skill_func in skill_wrappers.items():
                def create_wrapper(func):
                    def wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                        try:
                            context = {}
                            if hasattr(agent_value, 'value'):
                                context = agent_value.value
                            elif isinstance(agent_value, dict):
                                context = agent_value

                            context['grok_client'] = self.grok_client
                            result = func(context)
                            return_value = sai.AgentValue()
                            return_value.value = result.value
                            return return_value
                        except Exception as e:
                            error_value = sai.AgentValue()
                            error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                            return error_value
                    return wrapper

                self.skills[skill_name] = create_wrapper(skill_func)

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.grok_client = self.grok_client
            agent.grok_skills = self.skills

        except Exception as e:
            import traceback
            traceback.print_exc()

class GrokAgent(sai.Agent):
    def __init__(self, name: str = __grok_agent_name__, api_key: Optional[str] = None):
        super().__init__()
        self._name = name
        self._api_key = api_key or os.environ.get('XAI_API_KEY')

        self.plugin = GrokPlugin(self._api_key)
        self.plugin.apply_plugin(self)

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        try:
            agent_value = sai.AgentValue()
            agent_value.value = context
            return agent_value
        except Exception as e:
            agent_value = sai.AgentValue()
            setattr(agent_value, 'value', context)
            return agent_value

    def get_api_info(self) -> Dict[str, Any]:
        context = {}

        if 'get_api_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_api_info'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def list_models(self, model_type: str = 'all') -> Dict[str, Any]:
        context = {
            'model_type': model_type
        }

        if 'list_models' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['list_models'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def chat_completion(self,
                       messages: List[Dict[str, Any]],
                       model: str = "grok-4-0709",
                       max_tokens: Optional[int] = None,
                       temperature: Optional[float] = None,
                       tools: Optional[List[Dict]] = None,
                       tool_choice: Optional[Union[str, Dict]] = None) -> Dict[str, Any]:

        context = {
            'messages': messages,
            'model': model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'tools': tools,
            'tool_choice': tool_choice
        }

        if 'chat_completion' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['chat_completion'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def create_response(self,
                       input_data: Union[str, List[Dict[str, Any]]],
                       model: str = "grok-4-0709",
                       max_output_tokens: Optional[int] = None,
                       temperature: Optional[float] = None,
                       store: bool = True,
                       tools: Optional[List[Dict]] = None,
                       tool_choice: Optional[Union[str, Dict]] = None) -> Dict[str, Any]:

        context = {
            'input': input_data,
            'model': model,
            'max_output_tokens': max_output_tokens,
            'temperature': temperature,
            'store': store,
            'tools': tools,
            'tool_choice': tool_choice
        }

        if 'create_response' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_response'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def generate_image(self,
                      prompt: str,
                      model: str = "grok-2-image",
                      n: int = 1,
                      size: str = "1024x1024") -> Dict[str, Any]:

        context = {
            'prompt': prompt,
            'model': model,
            'n': n,
            'size': size
        }

        if 'generate_image' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['generate_image'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def analyze_model_capabilities(self, model_id: str = "grok-4-0709") -> Dict[str, Any]:
        context = {
            'model_id': model_id
        }

        if 'analyze_model_capabilities' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['analyze_model_capabilities'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def tokenize_text(self, text: str, model: str = "grok-4-0709") -> Dict[str, Any]:
        context = {
            'text': text,
            'model': model
        }

        if 'tokenize_text' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['tokenize_text'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def test_connection(self) -> bool:
        try:
            return self.grok_client.test_connection()
        except:
            return False

def create_grok_agent(api_key: Optional[str] = None) -> GrokAgent:
    return GrokAgent(api_key=api_key)

class SimpleGrokClient:
    def __init__(self, api_key: Optional[str] = None):
        from .components import GrokClientComponent
        self.client = GrokClientComponent(api_key)

    def test_connection(self) -> bool:
        try:
            return self.client.test_connection()
        except:
            return False

    def quick_chat(self, message: str, model: str = "grok-4-0709") -> Dict[str, Any]:
        return self.client.chat_completion(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ]
        )

__all__ = [
    'GrokPlugin',
    'GrokAgent',
    'SimpleGrokClient',
    'create_grok_agent',
    'GrokClientComponent',
]
