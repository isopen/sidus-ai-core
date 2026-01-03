import asyncio
import json
import websockets
from typing import Dict, Any, List, Callable
from datetime import datetime
import threading

class KuCoinWebSocketClient:
    WS_SPOT_URL = 'wss://x-push-spot.kucoin.com'
    WS_FUTURES_URL = 'wss://x-push-futures.kucoin.com'

    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.spot_connection = None
        self.futures_connection = None
        self.connected = False
        self.subscriptions = []
        self.callbacks = {}
        self.spot_websocket = None
        self.futures_websocket = None
        self.spot_task = None
        self.futures_task = None
        self.loop = loop or asyncio.new_event_loop()
        self.lock = threading.Lock()
        self.message_counter = 1

        print(f"KuCoin WebSocket Client initialized")

    def _get_ws_url(self, trade_type: str) -> str:
        if trade_type.upper() == "SPOT":
            return self.WS_SPOT_URL
        elif trade_type.upper() == "FUTURES":
            return self.WS_FUTURES_URL
        else:
            raise ValueError(f"Unsupported trade type: {trade_type}")

    def connect_sync(self, trade_type: str = "SPOT") -> bool:
        future = asyncio.run_coroutine_threadsafe(self.connect(trade_type), self.loop)
        return future.result(timeout=10)

    async def connect(self, trade_type: str = "SPOT") -> bool:
        try:
            url = self._get_ws_url(trade_type)
            print(f"Connecting to KuCoin {trade_type} at {url}...")

            websocket = await websockets.connect(
                url,
                ping_interval=180,
                ping_timeout=60,
                close_timeout=5,
                max_size=10 * 1024 * 1024
            )

            if trade_type.upper() == "SPOT":
                self.spot_connection = {
                    'connected': True,
                    'url': url,
                    'trade_type': 'SPOT',
                    'connected_at': datetime.now().isoformat()
                }
                self.spot_websocket = websocket
                self.spot_task = asyncio.create_task(self._receive_messages('SPOT'))
            else:
                self.futures_connection = {
                    'connected': True,
                    'url': url,
                    'trade_type': 'FUTURES',
                    'connected_at': datetime.now().isoformat()
                }
                self.futures_websocket = websocket
                self.futures_task = asyncio.create_task(self._receive_messages('FUTURES'))

            self.connected = True
            print(f"✅ Connected to KuCoin {trade_type} WebSocket")
            return True

        except Exception as e:
            print(f"❌ Failed to connect to KuCoin {trade_type}: {e}")
            return False

    def disconnect_sync(self):
        future = asyncio.run_coroutine_threadsafe(self.disconnect(), self.loop)
        return future.result(timeout=10)

    async def disconnect(self):
        try:
            if self.spot_websocket:
                await self.spot_websocket.close()
                self.spot_connection = None
                self.spot_websocket = None

            if self.futures_websocket:
                await self.futures_websocket.close()
                self.futures_connection = None
                self.futures_websocket = None

            if self.spot_task:
                self.spot_task.cancel()
                try:
                    await self.spot_task
                except asyncio.CancelledError:
                    pass

            if self.futures_task:
                self.futures_task.cancel()
                try:
                    await self.futures_task
                except asyncio.CancelledError:
                    pass

            self.connected = False
            self.subscriptions = []

            print("✅ Disconnected from KuCoin WebSocket")

        except Exception as e:
            print(f"Error disconnecting: {e}")

    def is_connected(self) -> bool:
        return self.connected

    async def _receive_messages(self, trade_type: str):
        websocket = self.spot_websocket if trade_type == "SPOT" else self.futures_websocket

        try:
            async for message in websocket:
                if not self.connected:
                    break

                try:
                    data_obj = json.loads(message)
                    await self._handle_message(data_obj, trade_type)
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {message[:100]}")
                except Exception as e:
                    print(f"Error processing message: {e}")

        except websockets.exceptions.ConnectionClosed:
            print(f"KuCoin {trade_type} WebSocket connection closed")
            if trade_type == "SPOT":
                self.spot_connection = None
            else:
                self.futures_connection = None
        except Exception as e:
            print(f"Error in {trade_type} receive loop: {e}")

    async def _handle_message(self, data: Dict[str, Any], trade_type: str):
        try:
            if 'T' in data:
                channel_type = data.get('T')
                push_data = data.get('d', {})
                push_type = data.get('t', '')
                depth_level = data.get('dp', '')
                symbol = push_data.get('s', '')

                if channel_type:
                    topic = None
                    processed_data = {
                        'trade_type': trade_type,
                        'channel_type': channel_type,
                        'push_type': push_type,
                        'depth_level': depth_level,
                        'symbol': symbol,
                        'data': push_data,
                        'raw': data,
                        'timestamp': datetime.now().isoformat()
                    }

                    if channel_type.startswith('obu.'):
                        event_type = 'orderbook'
                        topic = f"{event_type}/{symbol.lower()}" if symbol else f"{event_type}/all"
                    elif channel_type.startswith('trade.'):
                        event_type = 'trade'
                        topic = f"{event_type}/{symbol.lower()}" if symbol else f"{event_type}/all"
                    elif channel_type == 'ticker':
                        event_type = 'ticker'
                        topic = f"{event_type}/{symbol.lower()}" if symbol else f"{event_type}/all"
                    elif channel_type == 'kline':
                        event_type = 'kline'
                        interval = push_data.get('i', '')
                        topic = f"{event_type}/{symbol.lower()}/{interval}" if symbol else f"{event_type}/all"

                    if topic:
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

    def subscribe_sync(self, trade_type: str, message: Dict[str, Any]) -> bool:
        future = asyncio.run_coroutine_threadsafe(
            self.subscribe(trade_type, message), 
            self.loop
        )
        return future.result(timeout=10)

    async def subscribe(self, trade_type: str, message: Dict[str, Any]) -> bool:
        try:
            if trade_type.upper() == "SPOT":
                if not self.spot_websocket or not self.spot_connection:
                    await self.connect("SPOT")
                websocket = self.spot_websocket
            else:
                if not self.futures_websocket or not self.futures_connection:
                    await self.connect("FUTURES")
                websocket = self.futures_websocket

            message_id = str(self.message_counter)
            self.message_counter += 1
            message['id'] = message_id

            await websocket.send(json.dumps(message))

            stream_key = f"{trade_type}:{message.get('channel')}:{message.get('symbol', 'all')}"
            if stream_key not in self.subscriptions:
                self.subscriptions.append(stream_key)

            print(f"✅ Subscription sent: {message}")
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
        spot_status = self.spot_connection.copy() if self.spot_connection else {
            'connected': False,
            'trade_type': 'SPOT',
            'url': self.WS_SPOT_URL
        }

        futures_status = self.futures_connection.copy() if self.futures_connection else {
            'connected': False,
            'trade_type': 'FUTURES',
            'url': self.WS_FUTURES_URL
        }

        return {
            'connected': self.connected,
            'spot': spot_status,
            'futures': futures_status,
            'subscriptions': self.subscriptions
        }
