import sidusai as sai
from typing import Optional, Dict, Any, List
import os

from .components import TONAPIClient, TONWallet, TONToken, TONTransaction
from .skills import (
    get_ton_price_skill,
    get_wallet_balance_skill,
    get_wallet_transactions_skill,
    get_token_info_skill,
    get_jetton_holders_skill,
    get_nft_collection_skill,
    get_nft_item_skill,
    tonapi_chat_skill,
    TONDataValue,
    TONWalletValue,
    TONTokenValue
)

__tonapi_agent_name__ = 'tonapi_agent'

class TONAPIPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv('TONAPI_API_KEY')
        self.tonapi_client = None
        print(f"🔧 TON API Plugin initialized")

        if self.api_key and not os.getenv('TONAPI_API_KEY'):
            os.environ['TONAPI_API_KEY'] = self.api_key

    def apply_plugin(self, agent: sai.Agent):
        print("🔧 Applying TON API plugin to agent...")

        try:
            self.tonapi_client = TONAPIClient(api_key=self.api_key)

            if self.tonapi_client.test_connection():
                print("✅ TON API connection successful")
            else:
                print("⚠️ TON API connection issues - some features may not work")

            self.skills = {}

            def ton_price_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_ton_price_skill(context)
                return TONDataValue(result.value)

            def wallet_balance_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_wallet_balance_skill(context)
                return TONWalletValue(result.value)

            def wallet_transactions_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_wallet_transactions_skill(context)
                return TONDataValue(result.value)

            def token_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_token_info_skill(context)
                return TONTokenValue(result.value)

            def jetton_holders_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_jetton_holders_skill(context)
                return TONDataValue(result.value)

            def nft_collection_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_nft_collection_skill(context)
                return TONDataValue(result.value)

            def nft_item_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_nft_item_skill(context)
                return TONDataValue(result.value)

            def tonapi_chat_wrapper(chat_value: sai.ChatAgentValue) -> sai.ChatAgentValue:
                chat_value.context = {'tonapi_component': self.tonapi_client}
                return tonapi_chat_skill(chat_value)

            self.skills = {
                'get_ton_price': ton_price_wrapper,
                'get_wallet_balance': wallet_balance_wrapper,
                'get_wallet_transactions': wallet_transactions_wrapper,
                'get_token_info': token_info_wrapper,
                'get_jetton_holders': jetton_holders_wrapper,
                'get_nft_collection': nft_collection_wrapper,
                'get_nft_item': nft_item_wrapper,
                'tonapi_chat': tonapi_chat_wrapper
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name = skill_name)

            agent.tonapi_client = self.tonapi_client
            agent.tonapi_skills = self.skills

            print("✅ TON API plugin applied successfully")

        except Exception as e:
            print(f"❌ Error applying TON API plugin: {e}")
            import traceback
            traceback.print_exc()


class TONAPIAgent(sai.Agent):
    def __init__(self, api_key: Optional[str] = None, name: str = __tonapi_agent_name__):
        super().__init__()
        self._name = name

        print(f"🤖 Creating TON API Agent '{name}'...")
        self.plugin = TONAPIPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)

        print(f"✅ TON API Agent '{name}' created successfully")

    @property
    def name(self):
        """Get agent name"""
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        try:
            return sai.AgentValue(value = context)
        except TypeError:
            agent_value = sai.AgentValue()
            agent_value.value = context
            return agent_value

    def get_ton_price(self, currencies: List[str] = ["USD", "EUR", "RUB"]) -> Dict[str, Any]:
        context = {
            'currencies': currencies
        }

        if 'get_ton_price' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_ton_price'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_wallet_balance(self, wallet_address: str) -> Dict[str, Any]:
        context = {
            'wallet_address': wallet_address
        }

        if 'get_wallet_balance' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_wallet_balance'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_wallet_transactions(self, wallet_address: str, limit: int = 10) -> Dict[str, Any]:
        context = {
            'wallet_address': wallet_address,
            'limit': limit
        }

        if 'get_wallet_transactions' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_wallet_transactions'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_token_info(self, token_address: str) -> Dict[str, Any]:
        context = {
            'token_address': token_address
        }

        if 'get_token_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_token_info'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_jetton_holders(self, jetton_address: str, limit: int = 10) -> Dict[str, Any]:
        context = {
            'jetton_address': jetton_address,
            'limit': limit
        }

        if 'get_jetton_holders' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_jetton_holders'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_nft_collection(self, collection_address: str) -> Dict[str, Any]:
        context = {
            'collection_address': collection_address
        }

        if 'get_nft_collection' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_nft_collection'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_nft_item(self, nft_address: str) -> Dict[str, Any]:
        context = {
            'nft_address': nft_address
        }

        if 'get_nft_item' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_nft_item'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def chat(self, message: str) -> str:
        from sidusai.core.plugin import ChatAgentValue

        if 'tonapi_chat' not in self.plugin.skills:
            return "Chat skill not available"

        chat = ChatAgentValue()
        chat.append_user(message)
        chat.context = {'tonapi_component': self.plugin.tonapi_client}

        result = self.plugin.skills['tonapi_chat'](chat)

        if isinstance(result, ChatAgentValue) and result.messages:
            for msg in reversed(result.messages):
                if msg['role'] == 'assistant':
                    return msg['content']

        return "No response from agent"


def create_tonapi_agent(api_key: Optional[str] = None) -> TONAPIAgent:
    return TONAPIAgent(api_key = api_key)

class SimpleTONAPIClient:
    def __init__(self, api_key: Optional[str] = None):
        from .components import TONAPIClient

        actual_api_key = api_key or os.getenv('TONAPI_API_KEY')

        if actual_api_key and not os.getenv('TONAPI_API_KEY'):
            os.environ['TONAPI_API_KEY'] = actual_api_key

        self.client = TONAPIClient(api_key=actual_api_key)

    def get_ton_price(self, currencies: List[str] = ["USD", "EUR", "RUB"]) -> Dict[str, Any]:
        return self.client.get_ton_price(currencies)

    def get_wallet_balance(self, wallet_address: str) -> Dict[str, Any]:
        return self.client.get_wallet_balance(wallet_address)

    def get_wallet_transactions(self, wallet_address: str, limit: int = 10) -> Optional[list]:
        return self.client.get_wallet_transactions(wallet_address, limit)

    def get_token_info(self, token_address: str) -> Optional[Dict]:
        return self.client.get_token_info(token_address)

    def get_jetton_holders(self, jetton_address: str, limit: int = 10) -> Optional[list]:
        return self.client.get_jetton_holders(jetton_address, limit)

    def get_nft_collection(self, collection_address: str) -> Optional[Dict]:
        return self.client.get_nft_collection(collection_address)

    def get_nft_item(self, nft_address: str) -> Optional[Dict]:
        return self.client.get_nft_item(nft_address)

    def get_jetton_list(self, limit: int = 50, offset: int = 0) -> Optional[list]:
        return self.client.get_jetton_list(limit, offset)

    def get_nft_list(self, limit: int = 50, offset: int = 0) -> Optional[list]:
        return self.client.get_nft_list(limit, offset)

    def test_connection(self) -> bool:
        return self.client.test_connection()


__all__ = [
    'TONAPIPlugin',
    'TONAPIAgent',
    'SimpleTONAPIClient',
    'create_tonapi_agent',
    'TONAPIClient',
    'TONWallet',
    'TONToken',
    'TONTransaction',
]
