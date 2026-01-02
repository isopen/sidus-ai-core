import asyncio
import json
import websockets
from typing import Dict, Any, List, Callable
from datetime import datetime
import threading
import time

class BitgetWebSocketClient:
    WS_URL = 'wss://ws.bitget.com/v2/ws/public'

    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.connection = None
        self.connected = False
        self.subscriptions = []
        self.callbacks = {}
        self.websocket = None
        self.task = None
        self.loop = loop or asyncio.new_event_loop()
        self.lock = threading.Lock()

    def connect_sync(self) -> bool:
        future = asyncio.run_coroutine_threadsafe(self.connect(), self.loop)
        return future.result(timeout=10)

    async def connect(self) -> bool:
        if self.connected:
            return True

        try:
            self.websocket = await websockets.connect(
                self.WS_URL,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5
            )

            self.connection = {
                'connected': True,
                'url': self.WS_URL,
                'connected_at': datetime.now().isoformat()
            }

            self.connected = True
            self.subscriptions = []

            self.task = asyncio.create_task(self._receive_messages())

            return True

        except Exception as e:
            print(f"Connect error: {e}")
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
            except:
                pass

        self.connection = None
        self.connected = False
        self.websocket = None
        self.task = None
        self.subscriptions = []

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
                except:
                    pass

        except:
            self.connected = False

    async def _handle_message(self, data: Dict[str, Any]):
        try:
            if 'event' in data:
                event = data.get('event')
                code = data.get('code')

                if event == 'subscribe' and (code is None or code == '0'):
                    arg = data.get('arg', {})
                    channel = arg.get('channel')
                    inst_id = arg.get('instId')
                    if channel and inst_id:
                        topic = f"{channel}/{inst_id}"
                        print(f"✅ Subscription confirmed: {topic}")
                elif event == 'unsubscribe' and (code is None or code == '0'):
                    print("✅ Unsubscription confirmed")
                elif code and code != '0':
                    print(f"❌ Error {code}: {data.get('msg')}")
                return

            if 'arg' in data and 'data' in data:
                arg = data.get('arg', {})
                channel = arg.get('channel')
                inst_id = arg.get('instId')

                if channel and inst_id:
                    topic = f"{channel}/{inst_id}"
                    message_data = data.get('data')
                    timestamp = data.get('ts', int(time.time() * 1000))
                    timestamp_readable = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

                    processed_data = {
                        'topic': topic,
                        'channel': channel,
                        'symbol': inst_id,
                        'data': message_data,
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
                except:
                    pass

    def subscribe_sync(self, channel: str, inst_id: str, inst_type: str = 'SPOT') -> bool:
        future = asyncio.run_coroutine_threadsafe(
            self.subscribe(channel, inst_id, inst_type), 
            self.loop
        )
        return future.result(timeout=10)

    async def subscribe(self, channel: str, inst_id: str, inst_type: str = 'SPOT') -> bool:
        if not self.connected:
            print("Not connected")
            return False

        try:
            subscribe_msg = {
                "op": "subscribe",
                "args": [{
                    "instType": inst_type,
                    "channel": channel,
                    "instId": inst_id
                }]
            }

            await self.websocket.send(json.dumps(subscribe_msg))

            topic = f"{channel}/{inst_id}"

            if topic not in self.subscriptions:
                self.subscriptions.append(topic)

            print(f"✅ Subscription sent: {topic} ({inst_type})")
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
                'connected_at': self.connection['connected_at'],
                'subscriptions': self.subscriptions
            }
        else:
            return {
                'connected': False,
                'url': '',
                'connected_at': '',
                'subscriptions': []
            }
