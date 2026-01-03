import asyncio
import json
import websockets
from typing import Dict, Any, List, Callable
from datetime import datetime
import threading
import time

class BinanceWebSocketClient:
    WS_BASE_URL = 'wss://fstream.binance.com'

    def __init__(self, use_combined_stream: bool = False, loop: asyncio.AbstractEventLoop = None):
        self.use_combined_stream = use_combined_stream
        self.connection = None
        self.connected = False
        self.subscriptions = []
        self.callbacks = {}
        self.websocket = None
        self.task = None
        self.loop = loop or asyncio.new_event_loop()
        self.lock = threading.Lock()

        print(f"Binance WebSocket Client initialized")

    def _get_ws_url(self, streams: List[str] = None) -> str:
        if self.use_combined_stream and streams:
            streams_str = '/'.join(streams)
            return f"{self.WS_BASE_URL}/stream?streams={streams_str}"
        else:
            return f"{self.WS_BASE_URL}/ws"

    def connect_sync(self, streams: List[str] = None) -> bool:
        future = asyncio.run_coroutine_threadsafe(self.connect(streams), self.loop)
        return future.result(timeout=10)

    async def connect(self, streams: List[str] = None) -> bool:
        if self.connected:
            return True

        try:
            url = self._get_ws_url(streams)
            print(f"Connecting to {url}...")

            self.websocket = await websockets.connect(
                url,
                ping_interval=180,
                ping_timeout=60,
                close_timeout=5,
                max_size=10 * 1024 * 1024
            )

            self.connection = {
                'connected': True,
                'url': url,
                'connected_at': datetime.now().isoformat(),
                'use_combined_stream': self.use_combined_stream
            }

            self.connected = True
            self.subscriptions = streams or []

            self.task = asyncio.create_task(self._receive_messages())

            print(f"✅ Connected to Binance Futures WebSocket")
            return True

        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False

    def disconnect_sync(self):
        future = asyncio.run_coroutine_threadsafe(self.disconnect(), self.loop)
        return future.result(timeout=10)

    async def disconnect(self):
        if not self.connected:
            return

        try:
            await self.websocket.close()
        except:
            pass

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        self.connection = None
        self.connected = False
        self.websocket = None
        self.task = None
        self.subscriptions = []

        print("✅ Disconnected from Binance WebSocket")

    def is_connected(self) -> bool:
        return self.connected

    async def _receive_messages(self):
        try:
            async for message in self.websocket:
                if not self.connected:
                    break

                try:
                    data_obj = json.loads(message)
                    await self._handle_message(data_obj)
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"Error processing message: {e}")

        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            self.connected = False
        except Exception as e:
            print(f"Error in receive loop: {e}")
            self.connected = False

    async def _handle_message(self, data: Dict[str, Any]):
        try:
            if 'stream' in data:
                stream = data.get('stream')
                payload = data.get('data', {})

                if stream and 'e' in payload:
                    event_type = payload.get('e')
                    symbol = payload.get('s', '')

                    if event_type and symbol:
                        topic = f"{event_type.lower()}/{symbol.lower()}"
                        timestamp = payload.get('E', int(time.time() * 1000))
                        timestamp_readable = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

                        processed_data = {
                            'topic': topic,
                            'stream': stream,
                            'event_type': event_type,
                            'symbol': symbol,
                            'data': payload,
                            'timestamp': timestamp,
                            'timestamp_readable': timestamp_readable,
                            'raw': data
                        }

                        await self._notify_callbacks(topic, processed_data)
                return

            if 'e' in data:
                event_type = data.get('e')
                symbol = data.get('s', '')

                if event_type and symbol:
                    topic = f"{event_type.lower()}/{symbol.lower()}"
                    timestamp = data.get('E', int(time.time() * 1000))
                    timestamp_readable = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

                    processed_data = {
                        'topic': topic,
                        'event_type': event_type,
                        'symbol': symbol,
                        'data': data,
                        'timestamp': timestamp,
                        'timestamp_readable': timestamp_readable,
                        'raw': data
                    }

                    await self._notify_callbacks(topic, processed_data)

        except Exception as e:
            print(f"Handle message error: {e}")

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

    def subscribe_sync(self, streams: List[str]) -> bool:
        future = asyncio.run_coroutine_threadsafe(
            self.subscribe(streams), 
            self.loop
        )
        return future.result(timeout=10)

    async def subscribe(self, streams: List[str]) -> bool:
        if not self.connected:
            print("Not connected")
            return False

        try:
            if self.use_combined_stream:
                print(f"Already subscribed to streams via combined URL")
                return True

            subscribe_msg = {
                "method": "SUBSCRIBE",
                "params": streams,
                "id": 1
            }

            await self.websocket.send(json.dumps(subscribe_msg))

            for stream in streams:
                if stream not in self.subscriptions:
                    self.subscriptions.append(stream)

            print(f"✅ Subscription sent: {streams}")
            return True

        except Exception as e:
            print(f"Subscribe error: {e}")
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

    def get_subscriptions(self) -> List[str]:
        return self.subscriptions.copy()

    def get_connection_status(self) -> Dict[str, Any]:
        if self.connection:
            return {
                'connected': self.connected,
                'url': self.connection['url'],
                'use_combined_stream': self.connection['use_combined_stream'],
                'connected_at': self.connection['connected_at'],
                'subscriptions': self.subscriptions
            }
        else:
            return {
                'connected': False,
                'url': '',
                'use_combined_stream': False,
                'connected_at': '',
                'subscriptions': []
            }
