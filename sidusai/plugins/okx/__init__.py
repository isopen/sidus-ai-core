import sidusai as sai
from typing import Optional, Dict, Any

from .components import OKXClientComponent
from .skills import (
    get_instruments_skill,
    get_server_time_skill,
    get_position_tiers_skill,
    get_insurance_fund_skill
)

__okx_agent_name__ = 'okx_public_agent'

class OKXPlugin(sai.AgentPlugin):
    def __init__(self):
        super().__init__()
        self.okx_client = None
        print(f"OKX Public Plugin initialized")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying OKX plugin to agent...")

        try:
            self.okx_client = OKXClientComponent()
            print("OKX client component created")

            self.skills = {}

            def get_instruments_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['okx_client'] = self.okx_client
                    result = get_instruments_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def get_server_time_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['okx_client'] = self.okx_client
                    result = get_server_time_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def get_position_tiers_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['okx_client'] = self.okx_client
                    result = get_position_tiers_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def get_insurance_fund_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['okx_client'] = self.okx_client
                    result = get_insurance_fund_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            self.skills = {
                'get_instruments': get_instruments_wrapper,
                'get_server_time': get_server_time_wrapper,
                'get_position_tiers': get_position_tiers_wrapper,
                'get_insurance_fund': get_insurance_fund_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.okx_client = self.okx_client
            agent.okx_skills = self.skills

            print("OKX plugin applied successfully")

        except Exception as e:
            print(f"Error applying OKX plugin: {e}")
            import traceback
            traceback.print_exc()

class OKXAgent(sai.Agent):
    def __init__(self, name: str = __okx_agent_name__):
        super().__init__()
        self._name = name

        print(f"Creating OKX Agent '{name}'...")
        self.plugin = OKXPlugin()
        self.plugin.apply_plugin(self)
        print(f"OKX Agent '{name}' created successfully")

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

    def get_instruments(self,
                       inst_type: str = 'SPOT',
                       uly: Optional[str] = None,
                       inst_family: Optional[str] = None,
                       inst_id: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'inst_type': inst_type,
            'uly': uly,
            'inst_family': inst_family,
            'inst_id': inst_id
        }

        if 'get_instruments' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_instruments'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_server_time(self) -> Dict[str, Any]:
        context = {}

        if 'get_server_time' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_server_time'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_position_tiers(self,
                          inst_type: str = 'SWAP',
                          uly: Optional[str] = None,
                          inst_family: Optional[str] = None,
                          inst_id: Optional[str] = None,
                          td_mode: str = 'cross') -> Dict[str, Any]:

        context = {
            'inst_type': inst_type,
            'uly': uly,
            'inst_family': inst_family,
            'inst_id': inst_id,
            'td_mode': td_mode
        }

        if 'get_position_tiers' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_position_tiers'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_insurance_fund(self,
                          inst_type: str = 'SWAP',
                          uly: Optional[str] = None,
                          inst_family: Optional[str] = None,
                          ccy: Optional[str] = None,
                          before: Optional[str] = None,
                          after: Optional[str] = None,
                          limit: str = '100') -> Dict[str, Any]:

        context = {
            'inst_type': inst_type,
            'uly': uly,
            'inst_family': inst_family,
            'ccy': ccy,
            'before': before,
            'after': after,
            'limit': limit
        }

        if 'get_insurance_fund' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_insurance_fund'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

def create_okx_agent() -> OKXAgent:
    return OKXAgent()

class SimpleOKXClient:
    def __init__(self):
        from .components import OKXClientComponent
        self.client = OKXClientComponent()

    def test_connection(self) -> bool:
        try:
            result = self.client.get_server_time()
            return result.get('code') == '0'
        except:
            return False

    def get_spot_instruments(self) -> Dict[str, Any]:
        return self.client.get_instruments(inst_type='SPOT')

    def get_server_time(self) -> Dict[str, Any]:
        return self.client.get_server_time()

__all__ = [
    'OKXPlugin',
    'OKXAgent',
    'SimpleOKXClient',
    'create_okx_agent',
    'OKXClientComponent',
]
