import sidusai as sai
from typing import Dict, Any, Callable
import asyncio
import threading
import time

from .components import KuCoinWebSocketClient
from .skills import (
    connect_skill,
    disconnect_skill,
    get_connections_skill,
    subscribe_ticker_skill,
    subscribe_kline_skill,
    subscribe_orderbook_skill,
    subscribe_trades_skill
)

__kucoin_agent_name__ = 'kucoin_websocket_agent'

class KuCoinPlugin(sai.AgentPlugin):
    def __init__(self):
        super().__init__()
        self.kucoin_client = None
        self.callbacks = {}
        self.event_loop = None
        self.thread = None
        print(f"KuCoin WebSocket Plugin initialized (SPOT and FUTURES)")

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
        print("Applying KuCoin plugin to agent...")

        try:
            self.start_event_loop()

            def create_client():
                return KuCoinWebSocketClient(loop=self.event_loop)

            self.kucoin_client = self.run_coroutine_threadsafe(
                asyncio.to_thread(create_client)
            )

            print("KuCoin WebSocket client component created")

            self.skills = {}

            def connect_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['kucoin_client'] = self.kucoin_client
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

                    context['kucoin_client'] = self.kucoin_client
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

                    context['kucoin_client'] = self.kucoin_client
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

                    context['kucoin_client'] = self.kucoin_client
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

                    context['kucoin_client'] = self.kucoin_client
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

                    context['kucoin_client'] = self.kucoin_client
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

                    context['kucoin_client'] = self.kucoin_client
                    result = self.run_coroutine_threadsafe(subscribe_trades_skill(context))
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
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.kucoin_client = self.kucoin_client
            agent.kucoin_skills = self.skills
            agent.kucoin_callbacks = self.callbacks

            print("KuCoin plugin applied successfully")

        except Exception as e:
            print(f"Error applying KuCoin plugin: {e}")
            import traceback
            traceback.print_exc()

    def __del__(self):
        self.stop_event_loop()

class KuCoinAgent(sai.Agent):
    def __init__(self, name: str = __kucoin_agent_name__):
        super().__init__()
        self._name = name

        print(f"Creating KuCoin Agent '{name}'...")
        self.plugin = KuCoinPlugin()
        self.plugin.apply_plugin(self)
        print(f"KuCoin Agent '{name}' created successfully")

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

    def connect(self, trade_type: str = "SPOT") -> Dict[str, Any]:
        context = {"trade_type": trade_type}

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

    def subscribe_ticker(self, symbol: str, trade_type: str = "SPOT") -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'trade_type': trade_type
        }

        if 'subscribe_ticker' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_ticker'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_kline(self, symbol: str, interval: str = '1min', trade_type: str = "SPOT") -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'interval': interval,
            'trade_type': trade_type
        }

        if 'subscribe_kline' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_kline'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_orderbook(self, symbol: str, depth: str = '5', trade_type: str = "SPOT", 
                          rpi_filter: int = 0) -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'depth': depth,
            'trade_type': trade_type,
            'rpi_filter': rpi_filter
        }

        if 'subscribe_orderbook' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_orderbook'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_trades(self, symbol: str, trade_type: str = "SPOT") -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'trade_type': trade_type
        }

        if 'subscribe_trades' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_trades'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def register_callback(self, topic: str, callback: Callable):
        if not hasattr(self, 'kucoin_callbacks'):
            self.kucoin_callbacks = {}

        if topic not in self.kucoin_callbacks:
            self.kucoin_callbacks[topic] = []

        self.kucoin_callbacks[topic].append(callback)

        if hasattr(self, 'plugin') and self.plugin.kucoin_client:
            self.plugin.kucoin_client.register_callback(topic, callback)

        print(f"Callback registered for topic: {topic}")

    def unregister_callback(self, topic: str, callback: Callable = None):
        if not hasattr(self, 'kucoin_callbacks') or topic not in self.kucoin_callbacks:
            return

        if callback is None:
            self.kucoin_callbacks.pop(topic, None)
            if hasattr(self, 'plugin') and self.plugin.kucoin_client:
                self.plugin.kucoin_client.unregister_callback(topic)
            print(f"All callbacks removed for topic: {topic}")
        else:
            if callback in self.kucoin_callbacks[topic]:
                self.kucoin_callbacks[topic].remove(callback)
                if hasattr(self, 'plugin') and self.plugin.kucoin_client:
                    self.plugin.kucoin_client.unregister_callback(topic, callback)
                print(f"Callback removed for topic: {topic}")

def create_kucoin_agent() -> KuCoinAgent:
    return KuCoinAgent()

class SimpleKuCoinClient:
    def __init__(self):
        from .components import KuCoinWebSocketClient
        self.client = KuCoinWebSocketClient()

    def connect(self, trade_type: str = "SPOT") -> bool:
        try:
            return self.client.connect_sync(trade_type)
        except:
            return False

    def disconnect(self):
        return self.client.disconnect_sync()

    def is_connected(self) -> bool:
        return self.client.is_connected()

__all__ = [
    'KuCoinPlugin',
    'KuCoinAgent',
    'SimpleKuCoinClient',
    'create_kucoin_agent',
    'KuCoinWebSocketClient',
]
