import asyncio
import json
import websockets
from typing import Dict, Any, List, Callable
from datetime import datetime
import threading

class MEXCWebSocketClient:
    WS_URL = 'wss://contract.mexc.com/edge'

    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.connection = None
        self.websocket = None
        self.connected = False
        self.subscriptions = []
        self.callbacks = {}
        self.task = None
        self.loop = loop or asyncio.new_event_loop()
        self.lock = threading.Lock()
        self.message_counter = 1

        print(f"MEXC WebSocket Client initialized")

    def connect_sync(self) -> bool:
        future = asyncio.run_coroutine_threadsafe(self.connect(), self.loop)
        return future.result(timeout=10)

    async def connect(self) -> bool:
        try:
            print(f"Connecting to MEXC Futures at {self.WS_URL}...")

            self.websocket = await websockets.connect(
                self.WS_URL,
                ping_interval=180,
                ping_timeout=60,
                close_timeout=5,
                max_size=10 * 1024 * 1024
            )

            self.connection = {
                'connected': True,
                'url': self.WS_URL,
                'trade_type': 'PERPETUAL',
                'connected_at': datetime.now().isoformat()
            }

            self.task = asyncio.create_task(self._receive_messages())
            self.connected = True

            print(f"✅ Connected to MEXC Futures WebSocket")
            return True

        except Exception as e:
            print(f"❌ Failed to connect to MEXC: {e}")
            return False

    def disconnect_sync(self):
        future = asyncio.run_coroutine_threadsafe(self.disconnect(), self.loop)
        return future.result(timeout=10)

    async def disconnect(self):
        try:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None

            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass

            self.connection = None
            self.connected = False
            self.subscriptions = []

            print("✅ Disconnected from MEXC WebSocket")

        except Exception as e:
            print(f"Error disconnecting: {e}")

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
                    print(f"Invalid JSON received: {message[:100]}")
                except Exception as e:
                    print(f"Error processing message: {e}")

        except websockets.exceptions.ConnectionClosed:
            print(f"MEXC WebSocket connection closed")
            self.connection = None
        except Exception as e:
            print(f"Error in receive loop: {e}")

    async def _handle_message(self, data: Dict[str, Any]):
        try:
            channel = data.get('channel')
            symbol = data.get('symbol')

            if not channel:
                return

            processed_data = {
                'channel': channel,
                'symbol': symbol,
                'data': data.get('data'),
                'raw': data,
                'timestamp': datetime.now().isoformat()
            }

            topic = None

            if channel == 'push.tickers':
                topic = f"tickers/all"
            elif channel == 'push.ticker':
                topic = f"ticker/{symbol.lower()}" if symbol else "ticker/all"
            elif channel == 'push.deal':
                topic = f"deal/{symbol.lower()}" if symbol else "deal/all"
            elif channel == 'push.depth':
                topic = f"depth/{symbol.lower()}" if symbol else "depth/all"
            elif channel == 'push.depth.step':
                topic = f"depth_step/{symbol.lower()}" if symbol else "depth_step/all"
            elif channel == 'push.kline':
                topic = f"kline/{symbol.lower()}" if symbol else "kline/all"
            elif channel == 'push.funding.rate':
                topic = f"funding_rate/{symbol.lower()}" if symbol else "funding_rate/all"
            elif channel == 'push.index.price':
                topic = f"index_price/{symbol.lower()}" if symbol else "index_price/all"
            elif channel == 'push.fair.price':
                topic = f"fair_price/{symbol.lower()}" if symbol else "fair_price/all"
            elif channel == 'push.contract':
                topic = f"contract/{symbol.lower()}" if symbol else "contract/all"
            elif channel == 'push.event.contract':
                topic = f"event_contract/{symbol.lower()}" if symbol else "event_contract/all"

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

    def subscribe_sync(self, message: Dict[str, Any]) -> bool:
        future = asyncio.run_coroutine_threadsafe(
            self.subscribe(message), 
            self.loop
        )
        return future.result(timeout=10)

    async def subscribe(self, message: Dict[str, Any]) -> bool:
        try:
            if not self.websocket or not self.connection:
                await self.connect()

            message_id = str(self.message_counter)
            self.message_counter += 1

            await self.websocket.send(json.dumps(message))

            method = message.get('method', '')
            symbol = message.get('param', {}).get('symbol', 'all')
            channel_key = f"{method}:{symbol}"

            if channel_key not in self.subscriptions:
                self.subscriptions.append(channel_key)

            print(f"✅ Subscription sent: {message}")
            return True

        except Exception as e:
            print(f"Subscribe error: {e}")
            return False

    def unsubscribe_sync(self, message: Dict[str, Any]) -> bool:
        future = asyncio.run_coroutine_threadsafe(
            self.unsubscribe(message), 
            self.loop
        )
        return future.result(timeout=10)

    async def unsubscribe(self, message: Dict[str, Any]) -> bool:
        try:
            if not self.websocket or not self.connection:
                return False

            message_id = str(self.message_counter)
            self.message_counter += 1

            await self.websocket.send(json.dumps(message))

            # Удаляем из списка подписок
            method = message.get('method', '')
            symbol = message.get('param', {}).get('symbol', 'all')
            channel_key = f"{method}:{symbol}"

            if channel_key in self.subscriptions:
                self.subscriptions.remove(channel_key)

            print(f"✅ Unsubscription sent: {message}")
            return True

        except Exception as e:
            print(f"Unsubscribe error: {e}")
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
        connection_status = self.connection.copy() if self.connection else {
            'connected': False,
            'trade_type': 'PERPETUAL',
            'url': self.WS_URL
        }

        return {
            'connected': self.connected,
            'connection': connection_status,
            'subscriptions': self.subscriptions
        }
