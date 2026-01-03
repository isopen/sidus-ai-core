import sidusai as sai
from typing import Dict, Any, Callable, List
import asyncio
import threading
import time
from .components import KrakenWebSocketClient
from .skills import (
    connect_skill,
    disconnect_skill,
    get_connections_skill,
    subscribe_ticker_skill,
    subscribe_book_skill,
    subscribe_ohlc_skill,
    subscribe_trade_skill,
    unsubscribe_ticker_skill,
    unsubscribe_book_skill,
    unsubscribe_ohlc_skill,
    unsubscribe_trade_skill
)

__kraken_agent_name__ = 'kraken_websocket_agent'

class KrakenPlugin(sai.AgentPlugin):
    def __init__(self):
        super().__init__()
        self.kraken_client = None
        self.callbacks = {}
        self.event_loop = None
        self.thread = None
        print(f"Kraken WebSocket Plugin initialized")

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
        print("Applying Kraken plugin to agent...")

        try:
            self.start_event_loop()

            def create_client():
                return KrakenWebSocketClient(loop=self.event_loop)

            self.kraken_client = self.run_coroutine_threadsafe(
                asyncio.to_thread(create_client)
            )

            print("Kraken WebSocket client component created")

            self.skills = {}

            def connect_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['kraken_client'] = self.kraken_client
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

                    context['kraken_client'] = self.kraken_client
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

                    context['kraken_client'] = self.kraken_client
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

                    context['kraken_client'] = self.kraken_client
                    result = self.run_coroutine_threadsafe(subscribe_ticker_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_book_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['kraken_client'] = self.kraken_client
                    result = self.run_coroutine_threadsafe(subscribe_book_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_ohlc_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['kraken_client'] = self.kraken_client
                    result = self.run_coroutine_threadsafe(subscribe_ohlc_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_trade_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['kraken_client'] = self.kraken_client
                    result = self.run_coroutine_threadsafe(subscribe_trade_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def unsubscribe_ticker_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['kraken_client'] = self.kraken_client
                    result = self.run_coroutine_threadsafe(unsubscribe_ticker_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def unsubscribe_book_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['kraken_client'] = self.kraken_client
                    result = self.run_coroutine_threadsafe(unsubscribe_book_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def unsubscribe_ohlc_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['kraken_client'] = self.kraken_client
                    result = self.run_coroutine_threadsafe(unsubscribe_ohlc_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def unsubscribe_trade_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['kraken_client'] = self.kraken_client
                    result = self.run_coroutine_threadsafe(unsubscribe_trade_skill(context))
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
                'subscribe_book': subscribe_book_wrapper,
                'subscribe_ohlc': subscribe_ohlc_wrapper,
                'subscribe_trade': subscribe_trade_wrapper,
                'unsubscribe_ticker': unsubscribe_ticker_wrapper,
                'unsubscribe_book': unsubscribe_book_wrapper,
                'unsubscribe_ohlc': unsubscribe_ohlc_wrapper,
                'unsubscribe_trade': unsubscribe_trade_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.kraken_client = self.kraken_client
            agent.kraken_skills = self.skills
            agent.kraken_callbacks = self.callbacks

            print("Kraken plugin applied successfully")

        except Exception as e:
            print(f"Error applying Kraken plugin: {e}")
            import traceback
            traceback.print_exc()

    def __del__(self):
        self.stop_event_loop()

class KrakenAgent(sai.Agent):
    def __init__(self, name: str = __kraken_agent_name__):
        super().__init__()
        self._name = name

        print(f"Creating Kraken Agent '{name}'...")
        self.plugin = KrakenPlugin()
        self.plugin.apply_plugin(self)
        print(f"Kraken Agent '{name}' created successfully")

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

    def subscribe_ticker(self, symbols: List[str], event_trigger: str = "trades", snapshot: bool = True) -> Dict[str, Any]:
        context = {
            'symbols': symbols,
            'event_trigger': event_trigger,
            'snapshot': snapshot
        }
        if 'subscribe_ticker' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_ticker'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def unsubscribe_ticker(self, symbols: List[str], event_trigger: str = "trades") -> Dict[str, Any]:
        context = {
            'symbols': symbols,
            'event_trigger': event_trigger
        }
        if 'unsubscribe_ticker' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['unsubscribe_ticker'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_book(self, symbols: List[str], depth: int = 10, snapshot: bool = True) -> Dict[str, Any]:
        context = {
            'symbols': symbols,
            'depth': depth,
            'snapshot': snapshot
        }
        if 'subscribe_book' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_book'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def unsubscribe_book(self, symbols: List[str], depth: int = 10) -> Dict[str, Any]:
        context = {
            'symbols': symbols,
            'depth': depth
        }
        if 'unsubscribe_book' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['unsubscribe_book'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_ohlc(self, symbols: List[str], interval: int = 1, snapshot: bool = True) -> Dict[str, Any]:
        context = {
            'symbols': symbols,
            'interval': interval,
            'snapshot': snapshot
        }
        if 'subscribe_ohlc' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_ohlc'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def unsubscribe_ohlc(self, symbols: List[str], interval: int = 1) -> Dict[str, Any]:
        context = {
            'symbols': symbols,
            'interval': interval
        }
        if 'unsubscribe_ohlc' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['unsubscribe_ohlc'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_trade(self, symbols: List[str], snapshot: bool = False) -> Dict[str, Any]:
        context = {
            'symbols': symbols,
            'snapshot': snapshot
        }
        if 'subscribe_trade' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_trade'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def unsubscribe_trade(self, symbols: List[str]) -> Dict[str, Any]:
        context = {
            'symbols': symbols
        }
        if 'unsubscribe_trade' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['unsubscribe_trade'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def register_callback(self, topic: str, callback: Callable):
        if not hasattr(self, 'kraken_callbacks'):
            self.kraken_callbacks = {}

        if topic not in self.kraken_callbacks:
            self.kraken_callbacks[topic] = []

        self.kraken_callbacks[topic].append(callback)

        if hasattr(self, 'plugin') and self.plugin.kraken_client:
            self.plugin.kraken_client.register_callback(topic, callback)

        print(f"Callback registered for topic: {topic}")

    def unregister_callback(self, topic: str, callback: Callable = None):
        if not hasattr(self, 'kraken_callbacks') or topic not in self.kraken_callbacks:
            return

        if callback is None:
            self.kraken_callbacks.pop(topic, None)
            if hasattr(self, 'plugin') and self.plugin.kraken_client:
                self.plugin.kraken_client.unregister_callback(topic)
            print(f"All callbacks removed for topic: {topic}")
        else:
            if callback in self.kraken_callbacks[topic]:
                self.kraken_callbacks[topic].remove(callback)
                if hasattr(self, 'plugin') and self.plugin.kraken_client:
                    self.plugin.kraken_client.unregister_callback(topic, callback)
                print(f"Callback removed for topic: {topic}")

def create_kraken_agent() -> KrakenAgent:
    return KrakenAgent()

class SimpleKrakenClient:
    def __init__(self):
        from .components import KrakenWebSocketClient
        self.client = KrakenWebSocketClient()

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
    'KrakenPlugin',
    'KrakenAgent',
    'SimpleKrakenClient',
    'create_kraken_agent',
    'KrakenWebSocketClient',
]
