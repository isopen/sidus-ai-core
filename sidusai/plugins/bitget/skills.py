from typing import Dict, Any
from datetime import datetime

class BitgetDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

async def connect_skill(context: Dict[str, Any]) -> BitgetDataValue:
    client = context.get('bitget_client')

    if not client:
        result = {"success": False, "error": "Bitget client not available"}
        return BitgetDataValue(result)

    try:
        connected = await client.connect()

        if connected:
            status = client.get_connection_status()

            analysis_result = {
                "success": True,
                "connected": True,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Connected to Bitget WebSocket")

        else:
            analysis_result = {
                "success": False,
                "connected": False,
                "error": "Failed to connect to WebSocket",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to connect to Bitget")

        return BitgetDataValue(analysis_result)

    except Exception as e:
        print(f"Error connecting: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to connect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BitgetDataValue(analysis_result)

async def disconnect_skill(context: Dict[str, Any]) -> BitgetDataValue:
    client = context.get('bitget_client')

    if not client:
        result = {"success": False, "error": "Bitget client not available"}
        return BitgetDataValue(result)

    try:
        await client.disconnect()

        analysis_result = {
            "success": True,
            "disconnected": True,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Disconnected from Bitget WebSocket")

        return BitgetDataValue(analysis_result)

    except Exception as e:
        print(f"Error disconnecting: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to disconnect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BitgetDataValue(analysis_result)

async def get_connections_skill(context: Dict[str, Any]) -> BitgetDataValue:
    client = context.get('bitget_client')

    if not client:
        result = {"success": False, "error": "Bitget client not available"}
        return BitgetDataValue(result)

    try:
        status = client.get_connection_status()

        total_subscriptions = len(status.get('subscriptions', []))

        analysis_result = {
            "success": True,
            "status": status,
            "summary": {
                "connected": status.get('connected', False),
                "total_subscriptions": total_subscriptions
            },
            "timestamp": datetime.now().isoformat()
        }

        if status.get('connected'):
            print(f"✅ Connected to Bitget")
            print(f"   Subscriptions: {total_subscriptions}")
        else:
            print(f"❌ Disconnected from Bitget")

        return BitgetDataValue(analysis_result)

    except Exception as e:
        print(f"Error getting connections: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to get connections: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BitgetDataValue(analysis_result)

async def subscribe_ticker_skill(context: Dict[str, Any]) -> BitgetDataValue:
    symbol = context.get('symbol')
    inst_type = context.get('inst_type', 'SPOT')
    client = context.get('bitget_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BitgetDataValue(result)

    if not client:
        result = {"success": False, "error": "Bitget client not available"}
        return BitgetDataValue(result)

    try:
        channel = "ticker"
        subscribed = await client.subscribe(channel, symbol, inst_type)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "channel": channel,
                "symbol": symbol,
                "inst_type": inst_type,
                "full_topic": f"{channel}/{symbol}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to ticker: {symbol} ({inst_type})")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to ticker: {symbol}")

        return BitgetDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to ticker: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BitgetDataValue(analysis_result)

async def subscribe_kline_skill(context: Dict[str, Any]) -> BitgetDataValue:
    symbol = context.get('symbol')
    interval = context.get('interval', '1min')
    inst_type = context.get('inst_type', 'SPOT')
    client = context.get('bitget_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BitgetDataValue(result)

    if not client:
        result = {"success": False, "error": "Bitget client not available"}
        return BitgetDataValue(result)

    try:
        if interval == '1min':
            channel = "candle1m"
        elif interval == '5min':
            channel = "candle5m"
        elif interval == '15min':
            channel = "candle15m"
        elif interval == '1hour':
            channel = "candle1H"
        elif interval == '4hour':
            channel = "candle4H"
        elif interval == '1day':
            channel = "candle1D"
        else:
            channel = f"candle{interval}"

        subscribed = await client.subscribe(channel, symbol, inst_type)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "channel": channel,
                "symbol": symbol,
                "interval": interval,
                "inst_type": inst_type,
                "full_topic": f"{channel}/{symbol}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to candlestick: {symbol} ({interval}, {inst_type})")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "interval": interval,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to candlestick: {symbol}")

        return BitgetDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to candlestick: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BitgetDataValue(analysis_result)

async def subscribe_orderbook_skill(context: Dict[str, Any]) -> BitgetDataValue:
    symbol = context.get('symbol')
    depth = context.get('depth', '5')
    inst_type = context.get('inst_type', 'SPOT')
    client = context.get('bitget_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BitgetDataValue(result)

    if not client:
        result = {"success": False, "error": "Bitget client not available"}
        return BitgetDataValue(result)

    try:
        if depth == '5':
            channel = "books5"
        elif depth == '15':
            channel = "books15"
        else:
            channel = "books"

        subscribed = await client.subscribe(channel, symbol, inst_type)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "channel": channel,
                "symbol": symbol,
                "depth": depth,
                "inst_type": inst_type,
                "full_topic": f"{channel}/{symbol}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to orderbook: {symbol} (depth: {depth}, {inst_type})")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "depth": depth,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to orderbook: {symbol}")

        return BitgetDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to orderbook: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BitgetDataValue(analysis_result)

async def subscribe_trades_skill(context: Dict[str, Any]) -> BitgetDataValue:
    symbol = context.get('symbol')
    inst_type = context.get('inst_type', 'SPOT')
    client = context.get('bitget_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BitgetDataValue(result)

    if not client:
        result = {"success": False, "error": "Bitget client not available"}
        return BitgetDataValue(result)

    try:
        channel = "trade"
        subscribed = await client.subscribe(channel, symbol, inst_type)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "channel": channel,
                "symbol": symbol,
                "inst_type": inst_type,
                "full_topic": f"{channel}/{symbol}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to trades: {symbol} ({inst_type})")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to trades: {symbol}")

        return BitgetDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to trades: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BitgetDataValue(analysis_result)
