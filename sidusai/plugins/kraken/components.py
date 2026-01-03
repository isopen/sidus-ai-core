import asyncio
import json
import websockets
import zlib
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import threading

class KrakenWebSocketClient:
    WS_BASE_URL = 'wss://ws.kraken.com/v2'

    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.connection = None
        self.connected = False
        self.subscriptions = {
            'ticker': [],
            'book': [],
            'ohlc': [],
            'trade': []
        }
        self.callbacks = {}
        self.websocket = None
        self.task = None
        self.heartbeat_task = None
        self.loop = loop or asyncio.new_event_loop()
        self.lock = threading.Lock()
        self.req_id_counter = 1
        self.running = True

        self.pending_subscriptions = {}
        self.pending_unsubscriptions = {}

    def _get_next_req_id(self) -> int:
        req_id = self.req_id_counter
        self.req_id_counter += 1
        return req_id

    async def _receive_messages(self):
        while self.running:
            try:
                message = await self.websocket.recv()

                try:
                    if isinstance(message, bytes):
                        try:
                            message = zlib.decompress(message).decode('utf-8')
                        except:
                            continue

                    data_obj = json.loads(message)

                    if isinstance(data_obj, dict) and data_obj.get('channel') == 'heartbeat':
                        pong_msg = {"method": "pong"}
                        await self.websocket.send(json.dumps(pong_msg))
                        continue

                    await self._handle_message(data_obj)
                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue

            except websockets.exceptions.ConnectionClosed:
                self.connected = False
                break
            except Exception:
                self.connected = False
                break

    def connect_sync(self) -> bool:
        future = asyncio.run_coroutine_threadsafe(self.connect(), self.loop)
        return future.result(timeout=10)

    async def connect(self) -> bool:
        if self.connected:
            return True

        try:
            self.websocket = await websockets.connect(
                self.WS_BASE_URL,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10,
                max_size=10 * 1024 * 1024,
                compression=None
            )

            self.connection = {
                'connected': True,
                'url': self.WS_BASE_URL,
                'connected_at': datetime.now().isoformat()
            }

            self.connected = True
            self.running = True
            self.task = asyncio.create_task(self._receive_messages())
            self.heartbeat_task = asyncio.create_task(self._send_heartbeats())

            return True

        except Exception:
            return False

    async def _send_heartbeats(self):
        while self.running and self.connected:
            try:
                await asyncio.sleep(15)
                if self.connected and self.websocket:
                    await self.websocket.ping()
            except:
                break

    def disconnect_sync(self):
        future = asyncio.run_coroutine_threadsafe(self.disconnect(), self.loop)
        return future.result(timeout=10)

    async def disconnect(self):
        if not self.connected:
            return

        self.running = False

        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass

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
        self.heartbeat_task = None

    def is_connected(self) -> bool:
        return self.connected

    async def _handle_message(self, data: Dict[str, Any]):
        try:
            channel = data.get('channel')
            msg_type = data.get('type')
            data_payload = data.get('data', [])

            if channel == 'heartbeat':
                return

            if channel and msg_type:
                if channel == 'ticker':
                    for ticker_data in data_payload:
                        symbol = ticker_data.get('symbol', '')
                        if symbol:
                            topic = f"ticker/{symbol}"
                            await self._process_and_notify(topic, {
                                'channel': channel,
                                'type': msg_type,
                                'data': data_payload,
                                'raw': data,
                                'timestamp': datetime.now().isoformat()
                            })

                elif channel == 'book':
                    for book_data in data_payload:
                        symbol = book_data.get('symbol', '')
                        if symbol:
                            topic = f"book/{symbol}"
                            await self._process_and_notify(topic, {
                                'channel': channel,
                                'type': msg_type,
                                'data': data_payload,
                                'raw': data,
                                'timestamp': datetime.now().isoformat()
                            })

                elif channel == 'ohlc':
                    for ohlc_data in data_payload:
                        symbol = ohlc_data.get('symbol', '')
                        if symbol:
                            interval = ohlc_data.get('interval', 1)
                            topic = f"ohlc/{symbol}/{interval}"
                            await self._process_and_notify(topic, {
                                'channel': channel,
                                'type': msg_type,
                                'data': data_payload,
                                'raw': data,
                                'timestamp': datetime.now().isoformat()
                            })

                elif channel == 'trade':
                    for trade_data in data_payload:
                        symbol = trade_data.get('symbol', '')
                        if symbol:
                            topic = f"trade/{symbol}"
                            await self._process_and_notify(topic, {
                                'channel': channel,
                                'type': msg_type,
                                'data': data_payload,
                                'raw': data,
                                'timestamp': datetime.now().isoformat()
                            })

            elif data.get('method') == 'subscribe':
                req_id = data.get('req_id', 0)
                success = data.get('success', False)

                if req_id in self.pending_subscriptions:
                    future = self.pending_subscriptions[req_id]
                    if not future.done():
                        if success:
                            symbols = data.get('symbol', [])
                            channel = data.get('channel', '')
                            if symbols and channel:
                                if channel not in self.subscriptions:
                                    self.subscriptions[channel] = []

                                for symbol in symbols:
                                    if symbol not in self.subscriptions[channel]:
                                        self.subscriptions[channel].append(symbol)

                            future.set_result(True)
                        else:
                            future.set_result(False)
                    del self.pending_subscriptions[req_id]

                topic = f"subscribe_ack/{req_id}"
                await self._process_and_notify(topic, data)

            elif data.get('method') == 'unsubscribe':
                req_id = data.get('req_id', 0)
                success = data.get('success', False)

                if req_id in self.pending_unsubscriptions:
                    future = self.pending_unsubscriptions[req_id]
                    if not future.done():
                        future.set_result(success)
                    del self.pending_unsubscriptions[req_id]

                topic = f"unsubscribe_ack/{req_id}"
                await self._process_and_notify(topic, data)

        except Exception:
            pass

    async def _process_and_notify(self, topic: str, data: Dict[str, Any]):
        if topic in self.callbacks:
            for callback in self.callbacks[topic]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception:
                    pass

    async def _send_message(self, message: Dict[str, Any]) -> Optional[int]:
        if not self.connected:
            return None

        try:
            req_id = self._get_next_req_id()
            message['req_id'] = req_id
            await self.websocket.send(json.dumps(message))
            return req_id
        except Exception:
            return None

    def subscribe_sync(self, channel: str, params: Dict[str, Any]) -> bool:
        future = asyncio.run_coroutine_threadsafe(
            self.subscribe(channel, params), 
            self.loop
        )
        return future.result(timeout=10)

    async def subscribe(self, channel: str, params: Dict[str, Any]) -> bool:
        message = {
            "method": "subscribe",
            "params": params
        }

        req_id = await self._send_message(message)
        if req_id is None:
            return False

        future = asyncio.Future()
        self.pending_subscriptions[req_id] = future

        try:
            success = await asyncio.wait_for(future, timeout=5.0)
            return success
        except asyncio.TimeoutError:
            if req_id in self.pending_subscriptions:
                del self.pending_subscriptions[req_id]
            return False

    def unsubscribe_sync(self, channel: str, params: Dict[str, Any]) -> bool:
        future = asyncio.run_coroutine_threadsafe(
            self.unsubscribe(channel, params), 
            self.loop
        )
        return future.result(timeout=10)

    async def unsubscribe(self, channel: str, params: Dict[str, Any]) -> bool:
        message = {
            "method": "unsubscribe",
            "params": params
        }

        req_id = await self._send_message(message)
        if req_id is None:
            return False

        future = asyncio.Future()
        self.pending_unsubscriptions[req_id] = future

        try:
            success = await asyncio.wait_for(future, timeout=5.0)
            if success:
                symbols = params.get('symbol', [])
                if symbols and channel in self.subscriptions:
                    for symbol in symbols:
                        if symbol in self.subscriptions[channel]:
                            self.subscriptions[channel].remove(symbol)
            return success
        except asyncio.TimeoutError:
            if req_id in self.pending_unsubscriptions:
                del self.pending_unsubscriptions[req_id]
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

    def get_subscriptions(self) -> Dict[str, List[str]]:
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
                'subscriptions': self.subscriptions
            }
