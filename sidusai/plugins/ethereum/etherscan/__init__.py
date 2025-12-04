import sidusai as sai
from typing import Optional, Dict, Any, List
import os

from .components import EtherscanClient, EthereumWallet, EthereumToken, EthereumTransaction
from .skills import (
    get_eth_price_skill,
    get_wallet_balance_skill,
    get_wallet_transactions_skill,
    get_gas_price_skill,
    EthereumDataValue,
    EthereumWalletValue,
    EthereumTokenValue
)

__etherscan_agent_name__ = 'etherscan_agent'

class EtherscanPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv('ETHERSCAN_API_KEY')
        self.etherscan_client = None
        print(f"🔧 Etherscan Plugin initialized")

        if self.api_key and not os.getenv('ETHERSCAN_API_KEY'):
            os.environ['ETHERSCAN_API_KEY'] = self.api_key

    def apply_plugin(self, agent: sai.Agent):
        print("🔧 Applying Etherscan plugin to agent...")

        try:
            self.etherscan_client = EtherscanClient(api_key = self.api_key)

            if self.etherscan_client.test_connection():
                print("✅ Etherscan API connection successful")
            else:
                print("⚠️ Etherscan API connection issues - some features may not work")

            self.skills = {}

            def eth_price_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['etherscan_component'] = self.etherscan_client
                result = get_eth_price_skill(context)
                return EthereumDataValue(result.value)

            def wallet_balance_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['etherscan_component'] = self.etherscan_client
                result = get_wallet_balance_skill(context)
                return EthereumWalletValue(result.value)

            def wallet_transactions_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['etherscan_component'] = self.etherscan_client
                result = get_wallet_transactions_skill(context)
                return EthereumDataValue(result.value)

            def gas_price_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['etherscan_component'] = self.etherscan_client
                result = get_gas_price_skill(context)
                return EthereumDataValue(result.value)

            self.skills = {
                'get_eth_price': eth_price_wrapper,
                'get_wallet_balance': wallet_balance_wrapper,
                'get_wallet_transactions': wallet_transactions_wrapper,
                'get_gas_price': gas_price_wrapper
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.etherscan_client = self.etherscan_client
            agent.etherscan_skills = self.skills

            print("✅ Etherscan plugin applied successfully")

        except Exception as e:
            print(f"❌ Error applying Etherscan plugin: {e}")
            import traceback
            traceback.print_exc()


class EtherscanAgent(sai.Agent):
    def __init__(self, api_key: Optional[str] = None, name: str = __etherscan_agent_name__):
        super().__init__()
        self._name = name

        print(f"🤖 Creating Etherscan Agent '{name}'...")
        self.plugin = EtherscanPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)

        print(f"✅ Etherscan Agent '{name}' created successfully")

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

    def get_eth_price(self) -> Dict[str, Any]:
        context = {}

        if 'get_eth_price' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_eth_price'](agent_value)
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

    def get_token_holders(self, token_address: str, limit: int = 10) -> Dict[str, Any]:
        context = {
            'token_address': token_address,
            'limit': limit
        }

        if 'get_token_holders' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_token_holders'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_gas_price(self) -> Dict[str, Any]:
        context = {}

        if 'get_gas_price' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_gas_price'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_eth_supply(self) -> Dict[str, Any]:
        context = {}

        if 'get_eth_supply' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_eth_supply'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_block_info(self, block_number: str = "latest") -> Dict[str, Any]:
        context = {
            'block_number': block_number
        }

        if 'get_block_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_block_info'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def chat(self, message: str) -> str:
        from sidusai.core.plugin import ChatAgentValue

        if 'etherscan_chat' not in self.plugin.skills:
            return "Chat skill not available"

        chat = ChatAgentValue()
        chat.append_user(message)
        chat.context = {'etherscan_component': self.plugin.etherscan_client}

        result = self.plugin.skills['etherscan_chat'](chat)

        if isinstance(result, ChatAgentValue) and result.messages:
            for msg in reversed(result.messages):
                if msg['role'] == 'assistant':
                    return msg['content']

        return "No response from agent"


def create_etherscan_agent(api_key: Optional[str] = None) -> EtherscanAgent:
    return EtherscanAgent(api_key=api_key)

class SimpleEtherscanClient:
    def __init__(self, api_key: Optional[str] = None):
        from .components import EtherscanClient

        actual_api_key = api_key or os.getenv('ETHERSCAN_API_KEY')

        if actual_api_key and not os.getenv('ETHERSCAN_API_KEY'):
            os.environ['ETHERSCAN_API_KEY'] = actual_api_key

        self.client = EtherscanClient(api_key = actual_api_key)

    def get_eth_price(self) -> Dict[str, Any]:
        return self.client.get_eth_price()

    def get_wallet_balance(self, wallet_address: str) -> Dict[str, Any]:
        return self.client.get_wallet_balance(wallet_address)

    def get_wallet_transactions(self, wallet_address: str, limit: int = 10) -> Optional[list]:
        return self.client.get_wallet_transactions(wallet_address, limit)

    def get_gas_price(self) -> Optional[Dict]:
        return self.client.get_gas_price()

    def test_connection(self) -> bool:
        return self.client.test_connection()


__all__ = [
    'EtherscanPlugin',
    'EtherscanAgent',
    'SimpleEtherscanClient',
    'create_etherscan_agent',
    'EtherscanClient',
    'EthereumWallet',
    'EthereumToken',
    'EthereumTransaction',
]
