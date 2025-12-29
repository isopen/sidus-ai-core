import sidusai as sai
from typing import Optional, Dict, Any, List
from datetime import datetime
from .components import DYORComponents
from .skills import (
    get_jetton_analysis_skill,
    analyze_technical_skill,
    generate_report_skill,
    compare_jettons_skill
)

__dyor_agent_name__ = 'dyor_analysis_agent'

class DYORPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        self.dyor_client = None

    def apply_plugin(self, agent: sai.Agent):
        self.dyor_client = DYORComponents(api_key=self.api_key)

        self.skills = {}

        def analyze_jetton_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            context['dyor_client'] = self.dyor_client
            result = get_jetton_analysis_skill(context)
            return_value = sai.AgentValue()
            return_value.value = result
            return return_value

        def analyze_technical_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            context['dyor_client'] = self.dyor_client
            result = analyze_technical_skill(context)
            return_value = sai.AgentValue()
            return_value.value = result
            return return_value

        def generate_report_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            context['dyor_client'] = self.dyor_client
            result = generate_report_skill(context)
            return_value = sai.AgentValue()
            return_value.value = result
            return return_value

        def compare_jettons_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            context['dyor_client'] = self.dyor_client
            result = compare_jettons_skill(context)
            return_value = sai.AgentValue()
            return_value.value = result
            return return_value

        def get_jettons_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}

            result = self.dyor_client.get_jettons(
                sort=context.get('sort', 'createdAt'),
                order=context.get('order', 'asc'),
                currency=context.get('currency', 'ton'),
                limit=context.get('limit', 50),
                offset=context.get('offset', 0)
            )

            return_value = sai.AgentValue()
            return_value.value = {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat()
            } if result else {"success": False, "error": "Failed to fetch jettons"}
            return return_value

        def get_jetton_details_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}

            address = context.get('address')
            if not address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Address is required"}
                return return_value

            result = self.dyor_client.get_jetton(address)

            return_value = sai.AgentValue()
            return_value.value = {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat()
            } if result else {"success": False, "error": "Failed to fetch jetton"}
            return return_value

        def get_jetton_metrics_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}

            address = context.get('address')
            currency = context.get('currency', 'ton')

            if not address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Address is required"}
                return return_value

            result = self.dyor_client.get_jetton_metrics(address, currency)

            return_value = sai.AgentValue()
            return_value.value = {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat()
            } if result else {"success": False, "error": "Failed to fetch metrics"}
            return return_value

        self.skills = {
            'analyze_jetton': analyze_jetton_wrapper,
            'analyze_technical': analyze_technical_wrapper,
            'generate_report': generate_report_wrapper,
            'compare_jettons': compare_jettons_wrapper,
            'get_jettons': get_jettons_wrapper,
            'get_jetton': get_jetton_details_wrapper,
            'get_jetton_metrics': get_jetton_metrics_wrapper,
        }

        for skill_name, skill_func in self.skills.items():
            agent.add_skill(skill_func, name=skill_name)

        agent.dyor_client = self.dyor_client
        agent.dyor_skills = self.skills

class DYORAgent(sai.Agent):
    def __init__(self, api_key: Optional[str] = None, name: str = __dyor_agent_name__):
        super().__init__()
        self._name = name
        self.api_key = api_key

        self.plugin = DYORPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        agent_value = sai.AgentValue()
        agent_value.value = context
        return agent_value

    def get_jettons(self, 
                    sort: str = "createdAt",
                    order: str = "asc",
                    currency: str = "ton",
                    limit: int = 50,
                    offset: int = 0) -> Dict[str, Any]:

        context = {
            'sort': sort,
            'order': order,
            'currency': currency,
            'limit': limit,
            'offset': offset
        }

        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_jettons'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_jetton(self, address: str) -> Dict[str, Any]:
        context = {'address': address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_jetton'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_jetton_metrics(self, address: str, currency: str = "ton") -> Dict[str, Any]:
        context = {
            'address': address,
            'currency': currency
        }
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_jetton_metrics'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def analyze_jetton(self, address: str) -> Dict[str, Any]:
        context = {'address': address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['analyze_jetton'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def analyze_technical(self, address: str) -> Dict[str, Any]:
        context = {'address': address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['analyze_technical'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def generate_report(self, address: str) -> Dict[str, Any]:
        context = {'address': address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['generate_report'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def compare_jettons(self, addresses: List[str]) -> Dict[str, Any]:
        context = {'addresses': addresses}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['compare_jettons'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_jetton_price(self, address: str, currency: str = "ton") -> Dict[str, Any]:
        try:
            if self.plugin.dyor_client:
                result = self.plugin.dyor_client.get_jetton_price(address, currency)
                return {"success": True, "data": result}
            return {"success": False, "error": "Client not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_jetton_holders(self, address: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        try:
            if self.plugin.dyor_client:
                result = self.plugin.dyor_client.get_jetton_holders(address, limit, offset)
                return {"success": True, "data": result}
            return {"success": False, "error": "Client not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_jetton_transactions(self, address: str, exchange_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        try:
            if self.plugin.dyor_client:
                result = self.plugin.dyor_client.get_jetton_transactions(address, exchange_id, limit, offset)
                return {"success": True, "data": result}
            return {"success": False, "error": "Client not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_jetton_markets(self, address: str, exchange_id: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        try:
            if self.plugin.dyor_client:
                result = self.plugin.dyor_client.get_jetton_markets(address, exchange_id, limit, offset)
                return {"success": True, "data": result}
            return {"success": False, "error": "Client not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def create_dyor_agent(api_key: Optional[str] = None) -> DYORAgent:
    return DYORAgent(api_key=api_key)

__all__ = [
    'DYORPlugin',
    'DYORAgent',
    'create_dyor_agent',
    'DYORComponents',
]
