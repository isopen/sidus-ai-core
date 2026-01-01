import asyncio
import json
import websockets
from typing import Dict, Any, List, Callable
from datetime import datetime
import threading
import time

class BybitWebSocketClient:
    STREAMS = {
        'spot': {
            'mainnet': 'wss://stream.bybit.com/v5/public/spot',
            'testnet': 'wss://stream-testnet.bybit.com/v5/public/spot'
        },
        'linear': {
            'mainnet': 'wss://stream.bybit.com/v5/public/linear',
            'testnet': 'wss://stream-testnet.bybit.com/v5/public/linear'
        },
        'inverse': {
            'mainnet': 'wss://stream.bybit.com/v5/public/inverse',
            'testnet': 'wss://stream-testnet.bybit.com/v5/public/inverse'
        },
        'spread': {
            'mainnet': 'wss://stream.bybit.com/v5/public/spread',
            'testnet': 'wss://stream-testnet.bybit.com/v5/public/spread'
        },
        'option': {
            'mainnet': 'wss://stream.bybit.com/v5/public/option',
            'testnet': 'wss://stream-testnet.bybit.com/v5/public/option'
        }
    }

    def __init__(self, testnet: bool = False, loop: asyncio.AbstractEventLoop = None):
        self.testnet = testnet
        self.connections = {}
        self.subscriptions = {}
        self.callbacks = {}
        self.websockets = {}
        self.tasks = {}
        self.loop = loop or asyncio.new_event_loop()
        self.lock = threading.Lock()
        self.reconnect_attempts = {}

        print(f"Bybit WebSocket Client initialized (testnet: {testnet})")

    def _get_ws_url(self, stream_type: str) -> str:
        if stream_type not in self.STREAMS:
            raise ValueError(f"Invalid stream type: {stream_type}")
        network = 'testnet' if self.testnet else 'mainnet'
        return self.STREAMS[stream_type][network]

    def connect_sync(self, stream_type: str = 'spot') -> bool:
        future = asyncio.run_coroutine_threadsafe(self.connect(stream_type), self.loop)
        return future.result(timeout=10)

    async def connect(self, stream_type: str = 'spot') -> bool:
        if stream_type in self.connections and self.connections[stream_type].get('connected', False):
            print(f"Already connected to {stream_type}")
            return True

        try:
            url = self._get_ws_url(stream_type)
            print(f"Connecting to {url}...")

            websocket = await websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5,
                max_size=10 * 1024 * 1024
            )

            self.websockets[stream_type] = websocket

            self.connections[stream_type] = {
                'connected': True,
                'url': url,
                'connected_at': datetime.now().isoformat(),
                'websocket': websocket
            }

            self.subscriptions[stream_type] = []
            self.reconnect_attempts[stream_type] = 0

            task = asyncio.create_task(self._receive_messages(stream_type))
            self.tasks[stream_type] = task

            print(f"✅ Connected to Bybit {stream_type} WebSocket")
            return True

        except Exception as e:
            print(f"❌ Failed to connect to {stream_type}: {e}")
            return False

    def disconnect_sync(self, stream_type: str = None):
        future = asyncio.run_coroutine_threadsafe(self.disconnect(stream_type), self.loop)
        return future.result(timeout=10)

    async def disconnect(self, stream_type: str = None):
        if stream_type is None:
            for st in list(self.connections.keys()):
                await self._disconnect_stream(st)
            print("Disconnected from all streams")
        elif stream_type in self.connections:
            await self._disconnect_stream(stream_type)
            print(f"Disconnected from {stream_type}")

    async def _disconnect_stream(self, stream_type: str):
        if stream_type in self.connections:
            try:
                if stream_type in self.websockets:
                    await self.websockets[stream_type].close()
            except:
                pass

            if stream_type in self.tasks:
                self.tasks[stream_type].cancel()
                try:
                    await self.tasks[stream_type]
                except asyncio.CancelledError:
                    pass
                del self.tasks[stream_type]

            self.connections.pop(stream_type, None)
            self.subscriptions.pop(stream_type, None)
            self.websockets.pop(stream_type, None)

    def is_connected(self, stream_type: str = 'spot') -> bool:
        return stream_type in self.connections and self.connections[stream_type].get('connected', False)

    async def _receive_messages(self, stream_type: str):
        try:
            websocket = self.websockets.get(stream_type)
            if not websocket:
                return

            async for message in websocket:
                if not self.connections.get(stream_type, {}).get('connected', False):
                    break

                try:
                    data_obj = json.loads(message)
                    await self._handle_message(stream_type, data_obj)
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"Error processing message: {e}")

            if stream_type in self.connections:
                self.connections[stream_type]['connected'] = False

        except websockets.exceptions.ConnectionClosed:
            print(f"WebSocket connection closed for {stream_type}")
            if stream_type in self.connections:
                self.connections[stream_type]['connected'] = False
        except Exception as e:
            print(f"Error in receive loop for {stream_type}: {e}")
            if stream_type in self.connections:
                self.connections[stream_type]['connected'] = False

    async def _handle_message(self, stream_type: str, data: Dict[str, Any]):
        try:
            topic = data.get('topic', '')
            if not topic:
                if 'success' in data:
                    print(f"Operation result: {data}")
                return

            if 'data' in data:
                message_data = data['data']
                timestamp = data.get('ts', int(time.time() * 1000))
                timestamp_readable = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                processed_data = {
                    'stream_type': stream_type,
                    'topic': topic,
                    'data': message_data,
                    'timestamp': timestamp,
                    'timestamp_readable': timestamp_readable,
                    'raw': data
                }

                await self._notify_callbacks(topic, processed_data)

        except Exception as e:
            print(f"Error handling message: {e}")

    async def _notify_callbacks(self, topic: str, data: Dict[str, Any]):
        if topic in self.callbacks:
            for callback in self.callbacks[topic]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    print(f"Error in callback for topic {topic}: {e}")

    def subscribe_sync(self, stream_type: str, topic: str, symbol: str = None) -> bool:
        future = asyncio.run_coroutine_threadsafe(self.subscribe(stream_type, topic, symbol), self.loop)
        return future.result(timeout=10)

    async def subscribe(self, stream_type: str, topic: str, symbol: str = None) -> bool:
        if not self.is_connected(stream_type):
            print(f"Not connected to {stream_type}")
            return False

        try:
            if symbol:
                full_topic = f"{topic}.{symbol}"
            else:
                full_topic = topic

            subscribe_msg = {
                "op": "subscribe",
                "args": [full_topic]
            }

            websocket = self.websockets.get(stream_type)
            if not websocket:
                return False

            await websocket.send(json.dumps(subscribe_msg))

            if stream_type not in self.subscriptions:
                self.subscriptions[stream_type] = []

            if full_topic not in self.subscriptions[stream_type]:
                self.subscriptions[stream_type].append(full_topic)

            print(f"✅ Subscription sent: {full_topic}")
            return True

        except Exception as e:
            print(f"Failed to subscribe to {topic}: {e}")
            return False

    def register_callback(self, topic: str, callback: Callable):
        with self.lock:
            if topic not in self.callbacks:
                self.callbacks[topic] = []

            if callback not in self.callbacks[topic]:
                self.callbacks[topic].append(callback)

    def unregister_callback(self, topic: str, callback: Callable = None):
        with self.lock:
            if topic in self.callbacks:
                if callback is None:
                    self.callbacks.pop(topic)
                elif callback in self.callbacks[topic]:
                    self.callbacks[topic].remove(callback)

    def get_subscriptions(self, stream_type: str = None) -> List[str]:
        if stream_type is None:
            all_subs = []
            for subs in self.subscriptions.values():
                all_subs.extend(subs)
            return all_subs
        else:
            return self.subscriptions.get(stream_type, [])

    def get_connection_status(self, stream_type: str = None) -> Dict[str, Any]:
        if stream_type is None:
            return {
                'connections': {
                    st: {
                        'connected': conn['connected'],
                        'url': conn['url'],
                        'connected_at': conn['connected_at'],
                        'subscriptions': self.subscriptions.get(st, [])
                    }
                    for st, conn in self.connections.items()
                }
            }
        elif stream_type in self.connections:
            conn = self.connections[stream_type]
            return {
                'stream_type': stream_type,
                'connected': conn['connected'],
                'url': conn['url'],
                'connected_at': conn['connected_at'],
                'subscriptions': self.subscriptions.get(stream_type, [])
            }
        else:
            return {
                'stream_type': stream_type,
                'connected': False,
                'url': '',
                'connected_at': '',
                'subscriptions': []
            }
