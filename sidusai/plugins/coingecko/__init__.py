import sidusai as sai
from typing import Optional, Dict, Any
import os

from .components import CoingeckoClient, CryptoCurrency, CurrencyRate
from .skills import (
    get_crypto_price_skill,
    get_crypto_market_data_skill,
    convert_currency_skill,
    get_trending_cryptos_skill,
    get_historical_data_skill,
    get_currency_info_skill,
    coingecko_chat_skill,
    CryptoCurrencyValue,
    CurrencyConversionValue
)

__coingecko_agent_name__ = 'coingecko_agent'

class CoingeckoPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv('COINGECKO_API_KEY')
        self.coingecko_client = None
        print(f"🔧 Coingecko Plugin initialized")

        if self.api_key and not os.getenv('COINGECKO_API_KEY'):
            os.environ['COINGECKO_API_KEY'] = self.api_key

    def apply_plugin(self, agent: sai.Agent):
        print("🔧 Applying Coingecko plugin to agent...")

        try:
            self.coingecko_client = CoingeckoClient(api_key=self.api_key)

            if self.coingecko_client.test_connection():
                print("✅ CoinGecko API connection successful")
            else:
                print("⚠️ CoinGecko API connection issues - some features may not work")

            self.skills = {}

            def crypto_price_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coingecko_component'] = self.coingecko_client
                result = get_crypto_price_skill(context)
                return CryptoCurrencyValue(result.value)

            def crypto_market_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coingecko_component'] = self.coingecko_client
                result = get_crypto_market_data_skill(context)
                return CryptoCurrencyValue(result.value)

            def convert_currency_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coingecko_component'] = self.coingecko_client
                result = convert_currency_skill(context)
                return CurrencyConversionValue(result.value)

            def trending_cryptos_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coingecko_component'] = self.coingecko_client
                result = get_trending_cryptos_skill(context)
                return CryptoCurrencyValue(result.value)

            def historical_data_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coingecko_component'] = self.coingecko_client
                result = get_historical_data_skill(context)
                return CryptoCurrencyValue(result.value)

            def currency_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coingecko_component'] = self.coingecko_client
                result = get_currency_info_skill(context)
                return CryptoCurrencyValue(result.value)

            def coingecko_chat_wrapper(chat_value: sai.ChatAgentValue) -> sai.ChatAgentValue:
                chat_value.context = {'coingecko_component': self.coingecko_client}
                return coingecko_chat_skill(chat_value)

            self.skills = {
                'get_crypto_price': crypto_price_wrapper,
                'get_crypto_market_data': crypto_market_wrapper,
                'convert_currency': convert_currency_wrapper,
                'get_trending_cryptos': trending_cryptos_wrapper,
                'get_historical_data': historical_data_wrapper,
                'get_currency_info': currency_info_wrapper,
                'coingecko_chat': coingecko_chat_wrapper
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name = skill_name)

            agent.coingecko_client = self.coingecko_client
            agent.coingecko_skills = self.skills

            print("✅ Coingecko plugin applied successfully")

        except Exception as e:
            print(f"❌ Error applying Coingecko plugin: {e}")
            import traceback
            traceback.print_exc()


class CoingeckoAgent(sai.Agent):
    def __init__(self, api_key: Optional[str] = None, name: str = __coingecko_agent_name__):
        super().__init__()
        self._name = name

        print(f"🤖 Creating Coingecko Agent '{name}'...")
        self.plugin = CoingeckoPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)

        print(f"✅ Coingecko Agent '{name}' created successfully")

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

    def get_crypto_price(self, crypto_id: str, vs_currency: str = "usd") -> Dict[str, Any]:
        context = {
            'crypto_id': crypto_id,
            'vs_currency': vs_currency
        }

        if 'get_crypto_price' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_crypto_price'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_crypto_market_data(self, vs_currency: str = "usd", limit: int = 20) -> Dict[str, Any]:
        context = {
            'vs_currency': vs_currency,
            'limit': limit
        }

        if 'get_crypto_market_data' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_crypto_market_data'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        context = {
            'amount': amount,
            'from_currency': from_currency,
            'to_currency': to_currency
        }

        if 'convert_currency' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['convert_currency'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_trending_cryptos(self) -> Dict[str, Any]:
        context = {}

        if 'get_trending_cryptos' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_trending_cryptos'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_historical_data(self, crypto_id: str, days: int = 7, vs_currency: str = "usd") -> Dict[str, Any]:
        context = {
            'crypto_id': crypto_id,
            'days': days,
            'vs_currency': vs_currency
        }

        if 'get_historical_data' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_historical_data'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_currency_info(self, crypto_id: str) -> Dict[str, Any]:
        context = {
            'crypto_id': crypto_id
        }

        if 'get_currency_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_currency_info'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def chat(self, message: str) -> str:
        from sidusai.core.plugin import ChatAgentValue

        if 'coingecko_chat' not in self.plugin.skills:
            return "Chat skill not available"

        chat = ChatAgentValue()
        chat.append_user(message)
        chat.context = {'coingecko_component': self.plugin.coingecko_client}

        result = self.plugin.skills['coingecko_chat'](chat)

        if isinstance(result, ChatAgentValue) and result.messages:
            for msg in reversed(result.messages):
                if msg['role'] == 'assistant':
                    return msg['content']

        return "No response from agent"


def create_coingecko_agent(api_key: Optional[str] = None) -> CoingeckoAgent:
    return CoingeckoAgent(api_key = api_key)

class SimpleCoingeckoClient:
    def __init__(self, api_key: Optional[str] = None):
        from .components import CoingeckoClient

        actual_api_key = api_key or os.getenv('COINGECKO_API_KEY')

        if actual_api_key and not os.getenv('COINGECKO_API_KEY'):
            os.environ['COINGECKO_API_KEY'] = actual_api_key

        self.client = CoingeckoClient(api_key=actual_api_key)

    def get_crypto_price(self, crypto_id: str, vs_currency: str = "usd") -> Dict[str, Any]:
        return self.client.get_crypto_price(crypto_id, vs_currency)

    def get_crypto_market_data(self, vs_currency: str = "usd", limit: int = 20) -> Optional[list]:
        return self.client.get_crypto_market_data(vs_currency, limit)

    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Optional[Dict]:
        return self.client.convert_currency(amount, from_currency, to_currency)

    def get_trending_cryptos(self) -> Optional[list]:
        return self.client.get_trending_cryptos()

    def get_historical_data(self, crypto_id: str, vs_currency: str = "usd", days: int = 7) -> Optional[Dict]:
        return self.client.get_historical_data(crypto_id, vs_currency, days)

    def get_currency_info(self, crypto_id: str) -> Optional[Dict]:
        return self.client.get_currency_info(crypto_id)

    def get_supported_cryptocurrencies(self) -> Optional[list]:
        return self.client.get_supported_cryptocurrencies()

    def get_crypto_ohlc(self, crypto_id: str, vs_currency: str = "usd", days: int = 7) -> Optional[list]:
        return self.client.get_crypto_ohlc(crypto_id, vs_currency, days)

    def test_connection(self) -> bool:
        return self.client.test_connection()


__all__ = [
    'CoingeckoPlugin',
    'CoingeckoAgent',
    'SimpleCoingeckoClient',
    'create_coingecko_agent',
    'CoingeckoClient',
    'CryptoCurrency',
    'CurrencyRate',
]
