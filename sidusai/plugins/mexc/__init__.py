import sidusai as sai
from typing import Dict, Any, Callable
import asyncio
import threading
import time

from .components import MEXCWebSocketClient
from .skills import (
    connect_skill,
    disconnect_skill,
    get_connections_skill,
    subscribe_tickers_skill,
    subscribe_ticker_skill,
    subscribe_deal_skill,
    subscribe_depth_skill,
    subscribe_depth_step_skill,
    subscribe_kline_skill,
    subscribe_funding_rate_skill,
    subscribe_index_price_skill,
    subscribe_fair_price_skill,
    subscribe_contract_skill,
    subscribe_event_contract_skill
)

__mexc_agent_name__ = 'mexc_websocket_agent'

class MEXCPlugin(sai.AgentPlugin):
    def __init__(self):
        super().__init__()
        self.mexc_client = None
        self.callbacks = {}
        self.event_loop = None
        self.thread = None
        print(f"MEXC WebSocket Plugin initialized (PERPETUAL futures)")

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
        print("Applying MEXC plugin to agent...")

        try:
            self.start_event_loop()

            def create_client():
                return MEXCWebSocketClient(loop=self.event_loop)

            self.mexc_client = self.run_coroutine_threadsafe(
                asyncio.to_thread(create_client)
            )

            print("MEXC WebSocket client component created")

            self.skills = {}

            def connect_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['mexc_client'] = self.mexc_client
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

                    context['mexc_client'] = self.mexc_client
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

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(get_connections_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_tickers_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(subscribe_tickers_skill(context))
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

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(subscribe_ticker_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_deal_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(subscribe_deal_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_depth_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(subscribe_depth_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_depth_step_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(subscribe_depth_step_skill(context))
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

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(subscribe_kline_skill(context))
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

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(subscribe_funding_rate_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_index_price_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(subscribe_index_price_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_fair_price_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(subscribe_fair_price_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_contract_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(subscribe_contract_skill(context))
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def subscribe_event_contract_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['mexc_client'] = self.mexc_client
                    result = self.run_coroutine_threadsafe(subscribe_event_contract_skill(context))
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
                'subscribe_tickers': subscribe_tickers_wrapper,
                'subscribe_ticker': subscribe_ticker_wrapper,
                'subscribe_deal': subscribe_deal_wrapper,
                'subscribe_depth': subscribe_depth_wrapper,
                'subscribe_depth_step': subscribe_depth_step_wrapper,
                'subscribe_kline': subscribe_kline_wrapper,
                'subscribe_funding_rate': subscribe_funding_rate_wrapper,
                'subscribe_index_price': subscribe_index_price_wrapper,
                'subscribe_fair_price': subscribe_fair_price_wrapper,
                'subscribe_contract': subscribe_contract_wrapper,
                'subscribe_event_contract': subscribe_event_contract_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.mexc_client = self.mexc_client
            agent.mexc_skills = self.skills
            agent.mexc_callbacks = self.callbacks

            print("MEXC plugin applied successfully")

        except Exception as e:
            print(f"Error applying MEXC plugin: {e}")
            import traceback
            traceback.print_exc()

    def __del__(self):
        self.stop_event_loop()

class MEXCAgent(sai.Agent):
    def __init__(self, name: str = __mexc_agent_name__):
        super().__init__()
        self._name = name

        print(f"Creating MEXC Agent '{name}'...")
        self.plugin = MEXCPlugin()
        self.plugin.apply_plugin(self)
        print(f"MEXC Agent '{name}' created successfully")

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

    def subscribe_tickers(self, gzip: bool = True) -> Dict[str, Any]:
        context = {
            'gzip': gzip
        }

        if 'subscribe_tickers' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_tickers'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_ticker(self, symbol: str, gzip: bool = True) -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'gzip': gzip
        }

        if 'subscribe_ticker' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_ticker'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_deal(self, symbol: str, gzip: bool = True, compress: bool = True) -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'gzip': gzip,
            'compress': compress
        }

        if 'subscribe_deal' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_deal'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_depth(self, symbol: str, gzip: bool = True) -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'gzip': gzip
        }

        if 'subscribe_depth' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_depth'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_depth_step(self, symbol: str, step: str, gzip: bool = True) -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'step': step,
            'gzip': gzip
        }

        if 'subscribe_depth_step' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_depth_step'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_kline(self, symbol: str, interval: str = 'Min1', gzip: bool = True) -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'interval': interval,
            'gzip': gzip
        }

        if 'subscribe_kline' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_kline'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_funding_rate(self, symbol: str, gzip: bool = True) -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'gzip': gzip
        }

        if 'subscribe_funding_rate' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_funding_rate'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_index_price(self, symbol: str, gzip: bool = True) -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'gzip': gzip
        }

        if 'subscribe_index_price' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_index_price'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_fair_price(self, symbol: str, gzip: bool = True) -> Dict[str, Any]:
        context = {
            'symbol': symbol,
            'gzip': gzip
        }

        if 'subscribe_fair_price' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_fair_price'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_contract(self, gzip: bool = True) -> Dict[str, Any]:
        context = {
            'gzip': gzip
        }

        if 'subscribe_contract' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_contract'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def subscribe_event_contract(self, gzip: bool = True) -> Dict[str, Any]:
        context = {
            'gzip': gzip
        }

        if 'subscribe_event_contract' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['subscribe_event_contract'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def register_callback(self, topic: str, callback: Callable):
        if not hasattr(self, 'mexc_callbacks'):
            self.mexc_callbacks = {}

        if topic not in self.mexc_callbacks:
            self.mexc_callbacks[topic] = []

        self.mexc_callbacks[topic].append(callback)

        if hasattr(self, 'plugin') and self.plugin.mexc_client:
            self.plugin.mexc_client.register_callback(topic, callback)

        print(f"Callback registered for topic: {topic}")

    def unregister_callback(self, topic: str, callback: Callable = None):
        if not hasattr(self, 'mexc_callbacks') or topic not in self.mexc_callbacks:
            return

        if callback is None:
            self.mexc_callbacks.pop(topic, None)
            if hasattr(self, 'plugin') and self.plugin.mexc_client:
                self.plugin.mexc_client.unregister_callback(topic)
            print(f"All callbacks removed for topic: {topic}")
        else:
            if callback in self.mexc_callbacks[topic]:
                self.mexc_callbacks[topic].remove(callback)
                if hasattr(self, 'plugin') and self.plugin.mexc_client:
                    self.plugin.mexc_client.unregister_callback(topic, callback)
                print(f"Callback removed for topic: {topic}")

def create_mexc_agent() -> MEXCAgent:
    return MEXCAgent()

class SimpleMEXCClient:
    def __init__(self):
        from .components import MEXCWebSocketClient
        self.client = MEXCWebSocketClient()

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
    'MEXCPlugin',
    'MEXCAgent',
    'SimpleMEXCClient',
    'create_mexc_agent',
    'MEXCWebSocketClient',
]
