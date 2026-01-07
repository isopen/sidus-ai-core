import sidusai as sai
from typing import Optional, Dict, Any, List
import os

from .components import GeminiClientComponent
from .skills import (
    generate_text_skill,
    generate_content_skill,
    generate_image_skill,
    embed_content_skill,
    batch_embed_contents_skill,
    analyze_image_skill
)

__gemini_agent_name__ = 'gemini_agent'

class GeminiPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.gemini_client = None
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        print(f"Gemini Plugin initialized with API key: {'✅' if self.api_key else '❌'}")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying Gemini plugin to agent...")

        try:
            self.gemini_client = GeminiClientComponent(api_key=self.api_key)
            print("Gemini client component created")

            self.skills = {}

            def generate_text_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['gemini_client'] = self.gemini_client
                    result = generate_text_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def generate_content_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['gemini_client'] = self.gemini_client
                    result = generate_content_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def generate_image_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['gemini_client'] = self.gemini_client
                    result = generate_image_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def embed_content_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['gemini_client'] = self.gemini_client
                    result = embed_content_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def batch_embed_contents_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['gemini_client'] = self.gemini_client
                    result = batch_embed_contents_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def analyze_image_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['gemini_client'] = self.gemini_client
                    result = analyze_image_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            self.skills = {
                'generate_text': generate_text_wrapper,
                'generate_content': generate_content_wrapper,
                'generate_image': generate_image_wrapper,
                'embed_content': embed_content_wrapper,
                'batch_embed_contents': batch_embed_contents_wrapper,
                'analyze_image': analyze_image_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.gemini_client = self.gemini_client
            agent.gemini_skills = self.skills

            print("Gemini plugin applied successfully")

        except Exception as e:
            print(f"Error applying Gemini plugin: {e}")
            import traceback
            traceback.print_exc()

class GeminiAgent(sai.Agent):
    def __init__(self, name: str = __gemini_agent_name__, api_key: Optional[str] = None):
        super().__init__()
        self._name = name
        self.api_key = api_key

        print(f"Creating Gemini Agent '{name}'...")
        self.plugin = GeminiPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)
        print(f"Gemini Agent '{name}' created successfully")

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        try:
            agent_value = sai.AgentValue()
            agent_value.value = context
            return agent_value
        except Exception as e:
            print(f"Error creating AgentValue: {e}")
            agent_value = sai.AgentValue()
            setattr(agent_value, 'value', context)
            return agent_value

    def generate_text(self,
                     prompt: str,
                     model: str = 'gemini-3-flash-preview',
                     temperature: float = 0.7,
                     max_tokens: int = 1024) -> Dict[str, Any]:

        context = {
            'prompt': prompt,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'skill_type': 'text'
        }

        if 'generate_text' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['generate_text'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def generate_content(self,
                        contents: List[Dict[str, Any]],
                        model: str = 'gemini-3-flash-preview',
                        generation_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'contents': contents,
            'model': model,
            'generation_config': generation_config or {},
            'skill_type': 'content'
        }

        if 'generate_content' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['generate_content'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def generate_image(self,
                      prompt: str,
                      model: str = 'imagen-4.0-generate-001',
                      sample_count: int = 4,
                      parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'prompt': prompt,
            'model': model,
            'sample_count': sample_count,
            'parameters': parameters or {},
            'skill_type': 'image'
        }

        if 'generate_image' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['generate_image'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def embed_content(self,
                     text: str,
                     model: str = 'models/embedding-001') -> Dict[str, Any]:

        context = {
            'text': text,
            'model': model,
            'skill_type': 'embed'
        }

        if 'embed_content' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['embed_content'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def batch_embed_contents(self,
                            texts: List[str],
                            model: str = 'models/embedding-001') -> Dict[str, Any]:

        context = {
            'texts': texts,
            'model': model,
            'skill_type': 'batch_embed'
        }

        if 'batch_embed_contents' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['batch_embed_contents'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def analyze_image(self,
                     image_path: str,
                     prompt: str,
                     model: str = 'gemini-3-flash-preview',
                     temperature: float = 0.5,
                     thinking_budget: int = 0) -> Dict[str, Any]:

        context = {
            'image_path': image_path,
            'prompt': prompt,
            'model': model,
            'temperature': temperature,
            'thinking_budget': thinking_budget,
            'skill_type': 'image_analysis'
        }

        if 'analyze_image' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['analyze_image'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

def create_gemini_agent(api_key: Optional[str] = None) -> GeminiAgent:
    return GeminiAgent(api_key=api_key)

class SimpleGeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        from .components import GeminiClientComponent
        self.client = GeminiClientComponent(api_key=api_key)

    def test_connection(self) -> bool:
        try:
            result = self.client.generate_text("Hello", model="gemini-3-flash-preview")
            return result.get('success', False)
        except:
            return False

    def chat(self, message: str, model: str = "gemini-3-flash-preview") -> Dict[str, Any]:
        return self.client.generate_text(message, model=model)

    def embed_text(self, text: str) -> Dict[str, Any]:
        return self.client.embed_content(text)

__all__ = [
    'GeminiPlugin',
    'GeminiAgent',
    'SimpleGeminiClient',
    'create_gemini_agent',
    'GeminiClientComponent',
]
