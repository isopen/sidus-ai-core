from typing import Dict, Any
from datetime import datetime

class BybitDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

async def connect_skill(context: Dict[str, Any]) -> BybitDataValue:
    stream_type = context.get('stream_type', 'spot')
    client = context.get('bybit_client')

    if not client:
        result = {"success": False, "error": "Bybit client not available"}
        return BybitDataValue(result)

    try:
        connected = await client.connect(stream_type)

        if connected:
            status = client.get_connection_status(stream_type)

            analysis_result = {
                "success": True,
                "connected": True,
                "stream_type": stream_type,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Connected to Bybit {stream_type} WebSocket")
            print(f"   URL: {status.get('url', 'N/A')}")

        else:
            analysis_result = {
                "success": False,
                "connected": False,
                "stream_type": stream_type,
                "error": "Failed to connect to WebSocket",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to connect to Bybit {stream_type}")

        return BybitDataValue(analysis_result)

    except Exception as e:
        print(f"Error connecting: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to connect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BybitDataValue(analysis_result)

async def disconnect_skill(context: Dict[str, Any]) -> BybitDataValue:
    stream_type = context.get('stream_type')
    client = context.get('bybit_client')

    if not client:
        result = {"success": False, "error": "Bybit client not available"}
        return BybitDataValue(result)

    try:
        await client.disconnect(stream_type)

        analysis_result = {
            "success": True,
            "disconnected": True,
            "stream_type": stream_type or "all",
            "timestamp": datetime.now().isoformat()
        }

        if stream_type:
            print(f"✅ Disconnected from Bybit {stream_type}")
        else:
            print(f"✅ Disconnected from all Bybit streams")

        return BybitDataValue(analysis_result)

    except Exception as e:
        print(f"Error disconnecting: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to disconnect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BybitDataValue(analysis_result)

async def get_connections_skill(context: Dict[str, Any]) -> BybitDataValue:
    stream_type = context.get('stream_type')
    client = context.get('bybit_client')

    if not client:
        result = {"success": False, "error": "Bybit client not available"}
        return BybitDataValue(result)

    try:
        status = client.get_connection_status(stream_type)

        connections_info = []
        if stream_type:
            connections_info.append(status)
        else:
            for st, conn_info in status.get('connections', {}).items():
                connections_info.append({
                    'stream_type': st,
                    **conn_info
                })

        total_connected = sum(1 for conn in connections_info if conn.get('connected', False))
        total_subscriptions = sum(len(conn.get('subscriptions', [])) for conn in connections_info)

        analysis_result = {
            "success": True,
            "connections": connections_info,
            "summary": {
                "total_connections": len(connections_info),
                "connected": total_connected,
                "disconnected": len(connections_info) - total_connected,
                "total_subscriptions": total_subscriptions
            },
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Connection status: {total_connected} connected")
        print(f"   Total subscriptions: {total_subscriptions}")

        for conn in connections_info:
            if conn.get('connected'):
                print(f"   {conn['stream_type']}: ✅ Connected ({len(conn.get('subscriptions', []))} subs)")
            else:
                print(f"   {conn['stream_type']}: ❌ Disconnected")

        return BybitDataValue(analysis_result)

    except Exception as e:
        print(f"Error getting connections: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to get connections: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BybitDataValue(analysis_result)

async def subscribe_ticker_skill(context: Dict[str, Any]) -> BybitDataValue:
    symbol = context.get('symbol')
    stream_type = context.get('stream_type', 'spot')
    client = context.get('bybit_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BybitDataValue(result)

    if not client:
        result = {"success": False, "error": "Bybit client not available"}
        return BybitDataValue(result)

    try:
        # Для Bybit V5 спотового рынка
        if stream_type == 'spot':
            topic = f"tickers.{symbol}"
        else:
            topic = "tickers"

        subscribed = await client.subscribe(stream_type, topic, None)  # Не добавляем символ повторно

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "stream_type": stream_type,
                "topic": topic,
                "symbol": symbol,
                "full_topic": topic,  # Уже содержит символ для spot
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to ticker: {symbol} on {stream_type} (topic: {topic})")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "stream_type": stream_type,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to ticker: {symbol}")

        return BybitDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to ticker: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BybitDataValue(analysis_result)

async def subscribe_kline_skill(context: Dict[str, Any]) -> BybitDataValue:
    symbol = context.get('symbol')
    interval = context.get('interval', '1')
    stream_type = context.get('stream_type', 'spot')
    client = context.get('bybit_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BybitDataValue(result)

    if not client:
        result = {"success": False, "error": "Bybit client not available"}
        return BybitDataValue(result)

    try:
        topic = f"kline.{interval}"
        subscribed = await client.subscribe(stream_type, topic, symbol)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "stream_type": stream_type,
                "topic": topic,
                "symbol": symbol,
                "interval": interval,
                "full_topic": f"{topic}.{symbol}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to kline: {symbol} ({interval}m) on {stream_type}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "stream_type": stream_type,
                "symbol": symbol,
                "interval": interval,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to kline: {symbol}")

        return BybitDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to kline: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BybitDataValue(analysis_result)

async def subscribe_orderbook_skill(context: Dict[str, Any]) -> BybitDataValue:
    symbol = context.get('symbol')
    depth = context.get('depth', '1')
    stream_type = context.get('stream_type', 'spot')
    client = context.get('bybit_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BybitDataValue(result)

    if not client:
        result = {"success": False, "error": "Bybit client not available"}
        return BybitDataValue(result)

    try:
        topic = f"orderbook.{depth}"
        subscribed = await client.subscribe(stream_type, topic, symbol)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "stream_type": stream_type,
                "topic": topic,
                "symbol": symbol,
                "depth": depth,
                "full_topic": f"{topic}.{symbol}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to orderbook: {symbol} (depth: {depth}) on {stream_type}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "stream_type": stream_type,
                "symbol": symbol,
                "depth": depth,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to orderbook: {symbol}")

        return BybitDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to orderbook: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BybitDataValue(analysis_result)

async def subscribe_trades_skill(context: Dict[str, Any]) -> BybitDataValue:
    symbol = context.get('symbol')
    stream_type = context.get('stream_type', 'spot')
    client = context.get('bybit_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BybitDataValue(result)

    if not client:
        result = {"success": False, "error": "Bybit client not available"}
        return BybitDataValue(result)

    try:
        topic = "publicTrade"
        subscribed = await client.subscribe(stream_type, topic, symbol)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "stream_type": stream_type,
                "topic": topic,
                "symbol": symbol,
                "full_topic": f"{topic}.{symbol}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to trades: {symbol} on {stream_type}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "stream_type": stream_type,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to trades: {symbol}")

        return BybitDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to trades: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BybitDataValue(analysis_result)
