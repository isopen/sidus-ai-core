import sidusai as sai
from typing import Dict, Any, Callable
import asyncio
import threading
import time

from .components import BinanceWebSocketClient
from .skills import (
    connect_skill,
    disconnect_skill,
    get_connections_skill,
    subscribe_ticker_skill,
    subscribe_kline_skill,
    subscribe_orderbook_skill,
    subscribe_trades_skill,
    subscribe_mark_price_skill,
    subscribe_funding_rate_skill,
    subscribe_agg_trades_skill
)

__binance_agent_name__ = 'binance_websocket_agent'

class BinancePlugin(sai.AgentPlugin):
    def __init__(self):
        super().__init__()
        self.binance_client = None
        self.callbacks = {}
        self.event_loop = None
        self.thread = None
        print(f"Binance WebSocket Plugin initialized (Mainnet only)")

    def start_event_loop(self):
        if self.event_loop is not None:
            return

        def run_loop():
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            self.event_loop.run_forever()

        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()

        while self.event_loop is None:
            time.sleep(0.01)

        print("Event loop started in background thread")

    def stop_event_loop(self):
        if self.event_loop:
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
            if self.thread:
                self.thread.join(timeout=2)
            self.event_loop = None
            self.thread = None
            print("Event loop stopped")

    def run_coroutine_threadsafe(self, coro):
        if self.event_loop is None:
            self.start_event_loop()

        future = asyncio.run_coroutine_threadsafe(coro, self.event_loop)
        return future.result(timeout=10)

    def apply_plugin(self, agent: sai.Agent):
        print("Applying Binance plugin to agent...")

        try:
            self.start_event_loop()

            def create_client():
                return BinanceWebSocketClient(loop=self.event_loop)

            self.binance_client = self.run_coroutine_threadsafe(
                asyncio.to_thread(create_client)
            )

            print("Binance WebSocket client component created")

            self.skills = {}

            def connect_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['binance_client'] = self.binance_client
                    result = self.run_coroutine_threadsafe(connect_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def disconnect_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['binance_client'] = self.binance_client
                    result = self.run_coroutine_threadsafe(disconnect_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def get_connections_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['binance_client'] = self.binance_client
                    result = self.run_coroutine_threadsafe(get_connections_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_ticker_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['binance_client'] = self.binance_client
                    result = self.run_coroutine_threadsafe(subscribe_ticker_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_kline_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['binance_client'] = self.binance_client
                    result = self.run_coroutine_threadsafe(subscribe_kline_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_orderbook_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['binance_client'] = self.binance_client
                    result = self.run_coroutine_threadsafe(subscribe_orderbook_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_trades_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['binance_client'] = self.binance_client
                    result = self.run_coroutine_threadsafe(subscribe_trades_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_mark_price_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['binance_client'] = self.binance_client
                    result = self.run_coroutine_threadsafe(subscribe_mark_price_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_funding_rate_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['binance_client'] = self.binance_client
                    result = self.run_coroutine_threadsafe(subscribe_funding_rate_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_agg_trades_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['binance_client'] = self.binance_client
                    result = self.run_coroutine_threadsafe(subscribe_agg_trades_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            self.skills = {
                'connect': connect_wrapper,
                'disconnect': disconnect_wrapper,
                'get_connections': get_connections_wrapper,
                'subscribe_ticker': subscribe_ticker_wrapper,
                'subscribe_kline': subscribe_kline_wrapper,
                'subscribe_orderbook': subscribe_orderbook_wrapper,
                'subscribe_trades': subscribe_trades_wrapper,
                'subscribe_mark_price': subscribe_mark_price_wrapper,
                'subscribe_funding_rate': subscribe_funding_rate_wrapper,
                'subscribe_agg_trades': subscribe_agg_trades_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.binance_client = self.binance_client
            agent.binance_skills = self.skills
            agent.binance_callbacks = self.callbacks

            print("Binance plugin applied successfully")

        except Exception as e:
            print(f"Error applying Binance plugin: {e}")
            import traceback
            traceback.print_exc()

    def __del__(self):
        self.stop_event_loop()

class BinanceAgent(sai.Agent):
    def __init__(self, name: str = __binance_agent_name__):
        super().__init__()
        self._name = name

        print(f"Creating Binance Agent '{name}'...")
        self.plugin = BinancePlugin()
        self.plugin.apply_plugin(self)
        print(f"Binance Agent '{name}' created successfully")

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

    def connect(self) -> Dict[str, Any]:
        context = {}

        if 'connect' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['connect'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def disconnect(self) -> Dict[str, Any]:
        context = {}

        if 'disconnect' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['disconnect'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_connections(self) -> Dict[str, Any]:
        context = {}

        if 'get_connections' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_connections'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_ticker(self, symbol: str) -> Dict[str, Any]:
        context = {
            'symbol': symbol
        }

        if 'subscribe_ticker' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_ticker'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_kline(self, symbol: str, interval: str = '1m') -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'interval': interval
        }

        if 'subscribe_kline' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_kline'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_orderbook(self, symbol: str, level: str = '5') -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'level': level
        }

        if 'subscribe_orderbook' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_orderbook'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_trades(self, symbol: str) -> Dict[str, Any]:
        context = {
            'symbol': symbol
        }

        if 'subscribe_trades' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_trades'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_mark_price(self, symbol: str = None) -> Dict[str, Any]:
        context = {
            'symbol': symbol
        }

        if 'subscribe_mark_price' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_mark_price'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_funding_rate(self, symbol: str = None) -> Dict[str, Any]:
        context = {
            'symbol': symbol
        }

        if 'subscribe_funding_rate' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_funding_rate'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_agg_trades(self, symbol: str) -> Dict[str, Any]:
        context = {
            'symbol': symbol
        }

        if 'subscribe_agg_trades' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_agg_trades'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def register_callback(self, topic: str, callback: Callable):
        if not hasattr(self, 'binance_callbacks'):
            self.binance_callbacks = {}

        if topic not in self.binance_callbacks:
            self.binance_callbacks[topic] = []

        self.binance_callbacks[topic].append(callback)

        if hasattr(self, 'plugin') and self.plugin.binance_client:
            self.plugin.binance_client.register_callback(topic, callback)

        print(f"Callback registered for topic: {topic}")

    def unregister_callback(self, topic: str, callback: Callable = None):
        if not hasattr(self, 'binance_callbacks') or topic not in self.binance_callbacks:
            return

        if callback is None:
            self.binance_callbacks.pop(topic, None)
            if hasattr(self, 'plugin') and self.plugin.binance_client:
                self.plugin.binance_client.unregister_callback(topic)
            print(f"All callbacks removed for topic: {topic}")
        else:
            if callback in self.binance_callbacks[topic]:
                self.binance_callbacks[topic].remove(callback)
                if hasattr(self, 'plugin') and self.plugin.binance_client:
                    self.plugin.binance_client.unregister_callback(topic, callback)
                print(f"Callback removed for topic: {topic}")

def create_binance_agent() -> BinanceAgent:
    return BinanceAgent()

class SimpleBinanceClient:
    def __init__(self):
        from .components import BinanceWebSocketClient
        self.client = BinanceWebSocketClient()

    def connect(self) -> bool:
        try:
            return self.client.connect_sync()
        except:
            return False

    def disconnect(self):
        return self.client.disconnect_sync()

    def is_connected(self) -> bool:
        return self.client.is_connected()

__all__ = [
    'BinancePlugin',
    'BinanceAgent',
    'SimpleBinanceClient',
    'create_binance_agent',
    'BinanceWebSocketClient',
]
