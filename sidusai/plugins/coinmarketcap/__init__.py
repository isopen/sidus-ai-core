import sidusai as sai
from typing import Optional, Dict, Any
import os

from .components import CoinMarketCapClient, CryptoCurrency, CurrencyConversion
from .skills import (
    get_crypto_price_skill,
    get_crypto_market_data_skill,
    convert_currency_skill,
    get_trending_cryptos_skill,
    get_historical_data_skill,
    get_currency_info_skill,
    get_global_metrics_skill,
    coinmarketcap_chat_skill,
    CryptoCurrencyValue,
    CurrencyConversionValue,
    GlobalMetricsValue
)

__coinmarketcap_agent_name__ = 'coinmarketcap_agent'

class CoinMarketCapPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv('COINMARKETCAP_API_KEY')
        self.coinmarketcap_client = None
        print(f"🔧 CoinMarketCap Plugin initialized")

        if self.api_key and not os.getenv('COINMARKETCAP_API_KEY'):
            os.environ['COINMARKETCAP_API_KEY'] = self.api_key

    def apply_plugin(self, agent: sai.Agent):
        print("🔧 Applying CoinMarketCap plugin to agent...")

        try:
            self.coinmarketcap_client = CoinMarketCapClient(api_key=self.api_key)

            if self.coinmarketcap_client.test_connection():
                print("✅ CoinMarketCap API connection successful")
            else:
                print("⚠️ CoinMarketCap API connection issues - some features may not work")

            self.skills = {}

            def crypto_price_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coinmarketcap_component'] = self.coinmarketcap_client
                result = get_crypto_price_skill(context)
                return CryptoCurrencyValue(result.value)

            def crypto_market_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coinmarketcap_component'] = self.coinmarketcap_client
                result = get_crypto_market_data_skill(context)
                return CryptoCurrencyValue(result.value)

            def convert_currency_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coinmarketcap_component'] = self.coinmarketcap_client
                result = convert_currency_skill(context)
                return CurrencyConversionValue(result.value)

            def trending_cryptos_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coinmarketcap_component'] = self.coinmarketcap_client
                result = get_trending_cryptos_skill(context)
                return CryptoCurrencyValue(result.value)

            def historical_data_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coinmarketcap_component'] = self.coinmarketcap_client
                result = get_historical_data_skill(context)
                return CryptoCurrencyValue(result.value)

            def currency_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coinmarketcap_component'] = self.coinmarketcap_client
                result = get_currency_info_skill(context)
                return CryptoCurrencyValue(result.value)

            def global_metrics_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['coinmarketcap_component'] = self.coinmarketcap_client
                result = get_global_metrics_skill(context)
                return GlobalMetricsValue(result.value)

            def coinmarketcap_chat_wrapper(chat_value: sai.ChatAgentValue) -> sai.ChatAgentValue:
                chat_value.context = {'coinmarketcap_component': self.coinmarketcap_client}
                return coinmarketcap_chat_skill(chat_value)

            self.skills = {
                'get_crypto_price': crypto_price_wrapper,
                'get_crypto_market_data': crypto_market_wrapper,
                'convert_currency': convert_currency_wrapper,
                'get_trending_cryptos': trending_cryptos_wrapper,
                'get_historical_data': historical_data_wrapper,
                'get_currency_info': currency_info_wrapper,
                'get_global_metrics': global_metrics_wrapper,
                'coinmarketcap_chat': coinmarketcap_chat_wrapper
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name = skill_name)

            agent.coinmarketcap_client = self.coinmarketcap_client
            agent.coinmarketcap_skills = self.skills

            print("✅ CoinMarketCap plugin applied successfully")

        except Exception as e:
            print(f"❌ Error applying CoinMarketCap plugin: {e}")
            import traceback
            traceback.print_exc()


class CoinMarketCapAgent(sai.Agent):
    def __init__(self, api_key: Optional[str] = None, name: str = __coinmarketcap_agent_name__):
        super().__init__()
        self._name = name

        print(f"🤖 Creating CoinMarketCap Agent '{name}'...")
        self.plugin = CoinMarketCapPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)

        print(f"✅ CoinMarketCap Agent '{name}' created successfully")

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

    def get_crypto_price(self, symbol: str, convert: str = "USD") -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'convert': convert
        }

        if 'get_crypto_price' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_crypto_price'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_crypto_market_data(self, limit: int = 20, convert: str = "USD") -> Dict[str, Any]:
        context = {
            'limit': limit,
            'convert': convert
        }

        if 'get_crypto_market_data' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_crypto_market_data'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def convert_currency(self, amount: float, symbol: str, convert: str) -> Dict[str, Any]:
        context = {
            'amount': amount,
            'symbol': symbol,
            'convert': convert
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

    def get_historical_data(self, symbol: str, time_period: str = "7d", convert: str = "USD") -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'time_period': time_period,
            'convert': convert
        }

        if 'get_historical_data' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_historical_data'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_currency_info(self, symbol: str) -> Dict[str, Any]:
        context = {
            'symbol': symbol
        }

        if 'get_currency_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_currency_info'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_global_metrics(self, convert: str = "USD") -> Dict[str, Any]:
        context = {
            'convert': convert
        }

        if 'get_global_metrics' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_global_metrics'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def chat(self, message: str) -> str:
        from sidusai.core.plugin import ChatAgentValue

        if 'coinmarketcap_chat' not in self.plugin.skills:
            return "Chat skill not available"

        chat = ChatAgentValue()
        chat.append_user(message)
        chat.context = {'coinmarketcap_component': self.plugin.coinmarketcap_client}

        result = self.plugin.skills['coinmarketcap_chat'](chat)

        if isinstance(result, ChatAgentValue) and result.messages:
            for msg in reversed(result.messages):
                if msg['role'] == 'assistant':
                    return msg['content']

        return "No response from agent"


def create_coinmarketcap_agent(api_key: Optional[str] = None) -> CoinMarketCapAgent:
    return CoinMarketCapAgent(api_key = api_key)

class SimpleCoinMarketCapClient:
    def __init__(self, api_key: Optional[str] = None):
        from .components import CoinMarketCapClient

        actual_api_key = api_key or os.getenv('COINMARKETCAP_API_KEY')

        if actual_api_key and not os.getenv('COINMARKETCAP_API_KEY'):
            os.environ['COINMARKETCAP_API_KEY'] = actual_api_key

        self.client = CoinMarketCapClient(api_key=actual_api_key)

    def get_crypto_price(self, symbol: str, convert: str = "USD") -> Dict[str, Any]:
        return self.client.get_crypto_price(symbol, convert)

    def get_crypto_market_data(self, limit: int = 20, convert: str = "USD") -> Optional[list]:
        return self.client.get_crypto_market_data(limit, convert)

    def convert_currency(self, amount: float, symbol: str, convert: str) -> Optional[Dict]:
        return self.client.convert_currency(amount, symbol, convert)

    def get_trending_cryptos(self) -> Optional[list]:
        return self.client.get_trending_cryptos()

    def get_historical_data(self, symbol: str, time_period: str = "7d", convert: str = "USD") -> Optional[Dict]:
        return self.client.get_historical_data(symbol, time_period, convert)

    def get_currency_info(self, symbol: str) -> Optional[Dict]:
        return self.client.get_currency_info(symbol)

    def get_global_metrics(self, convert: str = "USD") -> Optional[Dict]:
        return self.client.get_global_metrics(convert)

    def get_listings_latest(self, limit: int = 100, convert: str = "USD") -> Optional[list]:
        return self.client.get_listings_latest(limit, convert)

    def get_crypto_map(self) -> Optional[list]:
        return self.client.get_crypto_map()

    def test_connection(self) -> bool:
        return self.client.test_connection()


__all__ = [
    'CoinMarketCapPlugin',
    'CoinMarketCapAgent',
    'SimpleCoinMarketCapClient',
    'create_coinmarketcap_agent',
    'CoinMarketCapClient',
    'CryptoCurrency',
    'CurrencyConversion',
]