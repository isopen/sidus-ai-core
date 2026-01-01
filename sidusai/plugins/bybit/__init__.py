import sidusai as sai
from typing import Dict, Any, Callable
import asyncio
import threading
import time

from .components import BybitWebSocketClient
from .skills import (
    connect_skill,
    disconnect_skill,
    get_connections_skill,
    subscribe_ticker_skill,
    subscribe_kline_skill,
    subscribe_orderbook_skill,
    subscribe_trades_skill
)

__bybit_agent_name__ = 'bybit_websocket_agent'

class BybitPlugin(sai.AgentPlugin):
    def __init__(self, testnet: bool = False):
        super().__init__()
        self.testnet = testnet
        self.bybit_client = None
        self.callbacks = {}
        self.event_loop = None
        self.thread = None
        print(f"Bybit WebSocket Plugin initialized (testnet: {testnet})")

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
        print("Applying Bybit plugin to agent...")

        try:
            self.start_event_loop()

            def create_client():
                return BybitWebSocketClient(testnet=self.testnet, loop=self.event_loop)

            self.bybit_client = self.run_coroutine_threadsafe(
                asyncio.to_thread(create_client)
            )

            print("Bybit WebSocket client component created")

            self.skills = {}

            def connect_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['bybit_client'] = self.bybit_client
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

                    context['bybit_client'] = self.bybit_client
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

                    context['bybit_client'] = self.bybit_client
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

                    context['bybit_client'] = self.bybit_client
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

                    context['bybit_client'] = self.bybit_client
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

                    context['bybit_client'] = self.bybit_client
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

                    context['bybit_client'] = self.bybit_client
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

            agent.bybit_client = self.bybit_client
            agent.bybit_skills = self.skills
            agent.bybit_callbacks = self.callbacks

            print("Bybit plugin applied successfully")

        except Exception as e:
            print(f"Error applying Bybit plugin: {e}")
            import traceback
            traceback.print_exc()

    def __del__(self):
        self.stop_event_loop()

class BybitAgent(sai.Agent):
    def __init__(self, testnet: bool = False, name: str = __bybit_agent_name__):
        super().__init__()
        self._name = name
        self.testnet = testnet

        print(f"Creating Bybit Agent '{name}'...")
        self.plugin = BybitPlugin(testnet=testnet)
        self.plugin.apply_plugin(self)
        print(f"Bybit Agent '{name}' created successfully")

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

    def connect(self, stream_type: str = 'spot') -> Dict[str, Any]:
        context = {
            'stream_type': stream_type
        }

        if 'connect' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['connect'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def disconnect(self, stream_type: str = None) -> Dict[str, Any]:
        context = {
            'stream_type': stream_type
        }

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

    def subscribe_ticker(self, symbol: str, stream_type: str = 'spot') -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'stream_type': stream_type
        }

        if 'subscribe_ticker' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_ticker'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_kline(self, symbol: str, interval: str = '1', stream_type: str = 'spot') -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'interval': interval,
            'stream_type': stream_type
        }

        if 'subscribe_kline' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_kline'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_orderbook(self, symbol: str, depth: str = '1', stream_type: str = 'spot') -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'depth': depth,
            'stream_type': stream_type
        }

        if 'subscribe_orderbook' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_orderbook'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_trades(self, symbol: str, stream_type: str = 'spot') -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'stream_type': stream_type
        }

        if 'subscribe_trades' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_trades'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def register_callback(self, topic: str, callback: Callable):
        if not hasattr(self, 'bybit_callbacks'):
            self.bybit_callbacks = {}

        if topic not in self.bybit_callbacks:
            self.bybit_callbacks[topic] = []

        self.bybit_callbacks[topic].append(callback)

        if hasattr(self, 'plugin') and self.plugin.bybit_client:
            self.plugin.bybit_client.register_callback(topic, callback)

        print(f"Callback registered for topic: {topic}")

    def unregister_callback(self, topic: str, callback: Callable = None):
        if not hasattr(self, 'bybit_callbacks') or topic not in self.bybit_callbacks:
            return

        if callback is None:
            self.bybit_callbacks.pop(topic, None)
            if hasattr(self, 'plugin') and self.plugin.bybit_client:
                self.plugin.bybit_client.unregister_callback(topic)
            print(f"All callbacks removed for topic: {topic}")
        else:
            if callback in self.bybit_callbacks[topic]:
                self.bybit_callbacks[topic].remove(callback)
                if hasattr(self, 'plugin') and self.plugin.bybit_client:
                    self.plugin.bybit_client.unregister_callback(topic, callback)
                print(f"Callback removed for topic: {topic}")

def create_bybit_agent(testnet: bool = False) -> BybitAgent:
    return BybitAgent(testnet=testnet)

class SimpleBybitClient:
    def __init__(self, testnet: bool = False):
        from .components import BybitWebSocketClient
        self.client = BybitWebSocketClient(testnet=testnet)

    def connect(self, stream_type: str = 'spot') -> bool:
        try:
            return self.client.connect_sync(stream_type)
        except:
            return False

    def disconnect(self, stream_type: str = None):
        return self.client.disconnect_sync(stream_type)

    def is_connected(self, stream_type: str = 'spot') -> bool:
        return self.client.is_connected(stream_type)

__all__ = [
    'BybitPlugin',
    'BybitAgent',
    'SimpleBybitClient',
    'create_bybit_agent',
    'BybitWebSocketClient',
]
