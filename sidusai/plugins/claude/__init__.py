import sidusai as sai
from typing import Optional, Dict, Any, List
import os

from .components import ClaudeClientComponent
from .skills import (
    create_message_skill,
    count_tokens_skill,
    create_batch_skill,
    list_models_skill,
    upload_file_skill
)

__claude_agent_name__ = 'claude_agent'

class ClaudePlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.skills = {}
        self.claude_client = None
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        print(f"Claude Plugin initialized with API key: {'✅' if self.api_key else '❌'}")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying Claude plugin to agent...")

        try:
            self.claude_client = ClaudeClientComponent(api_key=self.api_key)
            print("Claude client component created")

            def create_message_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['claude_client'] = self.claude_client
                    result = create_message_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def count_tokens_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['claude_client'] = self.claude_client
                    result = count_tokens_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def create_batch_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['claude_client'] = self.claude_client
                    result = create_batch_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def list_models_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['claude_client'] = self.claude_client
                    result = list_models_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def upload_file_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['claude_client'] = self.claude_client
                    result = upload_file_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            self.skills = {
                'create_message': create_message_wrapper,
                'count_tokens': count_tokens_wrapper,
                'create_batch': create_batch_wrapper,
                'list_models': list_models_wrapper,
                'upload_file': upload_file_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.claude_client = self.claude_client
            agent.claude_skills = self.skills

            print("Claude plugin applied successfully")

        except Exception as e:
            print(f"Error applying Claude plugin: {e}")
            import traceback
            traceback.print_exc()

class ClaudeAgent(sai.Agent):
    def __init__(self, name: str = __claude_agent_name__, api_key: Optional[str] = None):
        super().__init__()
        self._name = name
        self.api_key = api_key

        print(f"Creating Claude Agent '{name}'...")
        self.plugin = ClaudePlugin(api_key=api_key)
        self.plugin.apply_plugin(self)
        print(f"Claude Agent '{name}' created successfully")

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

    def create_message(self, prompt: str, model: str = 'claude-3-haiku-20240307', max_tokens: int = 1024, system: Optional[str] = None, temperature: float = 0.7, top_p: float = 1.0) -> Dict[str, Any]:
        context = {
            'prompt': prompt,
            'model': model,
            'max_tokens': max_tokens,
            'system': system,
            'temperature': temperature,
            'top_p': top_p,
            'skill_type': 'message'
        }

        if 'create_message' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_message'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def count_tokens(self, messages: List[Dict[str, Any]], model: str = 'claude-3-haiku-20240307') -> Dict[str, Any]:
        context = {
            'messages': messages,
            'model': model,
            'skill_type': 'count_tokens'
        }

        if 'count_tokens' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['count_tokens'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def create_batch(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        context = {
            'requests': requests,
            'skill_type': 'batch'
        }

        if 'create_batch' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_batch'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def list_models(self) -> Dict[str, Any]:
        context = {
            'skill_type': 'list_models'
        }

        if 'list_models' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['list_models'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def upload_file(self, file_path: str) -> Dict[str, Any]:
        context = {
            'file_path': file_path,
            'skill_type': 'upload_file'
        }

        if 'upload_file' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['upload_file'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

def create_claude_agent(api_key: Optional[str] = None) -> ClaudeAgent:
    return ClaudeAgent(api_key=api_key)

class SimpleClaudeClient:
    def __init__(self, api_key: Optional[str] = None):
        from .components import ClaudeClientComponent
        self.client = ClaudeClientComponent(api_key=api_key)

    def test_connection(self) -> bool:
        try:
            result = self.client.create_message("Hello", model="claude-3-haiku-20240307")
            return result.get('success', False)
        except:
            return False

    def chat(self, message: str, model: str = "claude-3-haiku-20240307") -> Dict[str, Any]:
        return self.client.create_message(message, model=model)

    def count_tokens(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.client.count_tokens(messages)

__all__ = [
    'ClaudePlugin',
    'ClaudeAgent',
    'SimpleClaudeClient',
    'create_claude_agent',
    'ClaudeClientComponent',
]
