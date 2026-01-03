from typing import Dict, Any
from datetime import datetime

class KrakenDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

async def connect_skill(context: Dict[str, Any]) -> KrakenDataValue:
    client = context.get('kraken_client')

    if not client:
        result = {"success": False, "error": "Kraken client not available"}
        return KrakenDataValue(result)

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

        else:
            analysis_result = {
                "success": False,
                "connected": False,
                "error": "Failed to connect to WebSocket",
                "timestamp": datetime.now().isoformat()
            }

        return KrakenDataValue(analysis_result)

    except Exception as e:
        analysis_result = {
            "success": False,
            "error": f"Failed to connect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KrakenDataValue(analysis_result)

async def disconnect_skill(context: Dict[str, Any]) -> KrakenDataValue:
    client = context.get('kraken_client')

    if not client:
        result = {"success": False, "error": "Kraken client not available"}
        return KrakenDataValue(result)

    try:
        await client.disconnect()

        analysis_result = {
            "success": True,
            "disconnected": True,
            "timestamp": datetime.now().isoformat()
        }

        return KrakenDataValue(analysis_result)

    except Exception as e:
        analysis_result = {
            "success": False,
            "error": f"Failed to disconnect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KrakenDataValue(analysis_result)

async def get_connections_skill(context: Dict[str, Any]) -> KrakenDataValue:
    client = context.get('kraken_client')

    if not client:
        result = {"success": False, "error": "Kraken client not available"}
        return KrakenDataValue(result)

    try:
        status = client.get_connection_status()

        total_subscriptions = 0
        for channel, symbols in status.get('subscriptions', {}).items():
            total_subscriptions += len(symbols)

        analysis_result = {
            "success": True,
            "status": status,
            "summary": {
                "connected": status.get('connected', False),
                "total_subscriptions": total_subscriptions,
            },
            "timestamp": datetime.now().isoformat()
        }

        return KrakenDataValue(analysis_result)

    except Exception as e:
        analysis_result = {
            "success": False,
            "error": f"Failed to get connections: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KrakenDataValue(analysis_result)

async def subscribe_ticker_skill(context: Dict[str, Any]) -> KrakenDataValue:
    symbols = context.get('symbols', [])
    event_trigger = context.get('event_trigger', 'trades')
    snapshot = context.get('snapshot', True)
    client = context.get('kraken_client')

    if not symbols:
        result = {"success": False, "error": "Symbols are required"}
        return KrakenDataValue(result)

    if not client:
        result = {"success": False, "error": "Kraken client not available"}
        return KrakenDataValue(result)

    try:
        params = {
            "channel": "ticker",
            "symbol": symbols,
            "event_trigger": event_trigger,
            "snapshot": snapshot
        }

        subscribed = await client.subscribe("ticker", params)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "channel": "ticker",
                "symbols": symbols,
                "event_trigger": event_trigger,
                "snapshot": snapshot,
                "timestamp": datetime.now().isoformat()
            }

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbols": symbols,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }

        return KrakenDataValue(analysis_result)

    except Exception as e:
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KrakenDataValue(analysis_result)

async def unsubscribe_ticker_skill(context: Dict[str, Any]) -> KrakenDataValue:
    symbols = context.get('symbols', [])
    event_trigger = context.get('event_trigger', 'trades')
    client = context.get('kraken_client')

    if not symbols:
        result = {"success": False, "error": "Symbols are required"}
        return KrakenDataValue(result)

    if not client:
        result = {"success": False, "error": "Kraken client not available"}
        return KrakenDataValue(result)

    try:
        params = {
            "channel": "ticker",
            "symbol": symbols,
            "event_trigger": event_trigger
        }

        unsubscribed = await client.unsubscribe("ticker", params)

        if unsubscribed:
            analysis_result = {
                "success": True,
                "unsubscribed": True,
                "channel": "ticker",
                "symbols": symbols,
                "event_trigger": event_trigger,
                "timestamp": datetime.now().isoformat()
            }

        else:
            analysis_result = {
                "success": False,
                "unsubscribed": False,
                "symbols": symbols,
                "error": "Failed to unsubscribe",
                "timestamp": datetime.now().isoformat()
            }

        return KrakenDataValue(analysis_result)

    except Exception as e:
        analysis_result = {
            "success": False,
            "error": f"Failed to unsubscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KrakenDataValue(analysis_result)

async def subscribe_book_skill(context: Dict[str, Any]) -> KrakenDataValue:
    symbols = context.get('symbols', [])
    depth = context.get('depth', 10)
    snapshot = context.get('snapshot', True)
    client = context.get('kraken_client')

    if not symbols:
        result = {"success": False, "error": "Symbols are required"}
        return KrakenDataValue(result)

    if not client:
        result = {"success": False, "error": "Kraken client not available"}
        return KrakenDataValue(result)

    try:
        params = {
            "channel": "book",
            "symbol": symbols,
            "depth": depth,
            "snapshot": snapshot
        }

        subscribed = await client.subscribe("book", params)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "channel": "book",
                "symbols": symbols,
                "depth": depth,
                "snapshot": snapshot,
                "timestamp": datetime.now().isoformat()
            }

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbols": symbols,
                "depth": depth,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }

        return KrakenDataValue(analysis_result)

    except Exception as e:
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KrakenDataValue(analysis_result)

async def unsubscribe_book_skill(context: Dict[str, Any]) -> KrakenDataValue:
    symbols = context.get('symbols', [])
    depth = context.get('depth', 10)
    client = context.get('kraken_client')

    if not symbols:
        result = {"success": False, "error": "Symbols are required"}
        return KrakenDataValue(result)

    if not client:
        result = {"success": False, "error": "Kraken client not available"}
        return KrakenDataValue(result)

    try:
        params = {
            "channel": "book",
            "symbol": symbols,
            "depth": depth
        }

        unsubscribed = await client.unsubscribe("book", params)

        if unsubscribed:
            analysis_result = {
                "success": True,
                "unsubscribed": True,
                "channel": "book",
                "symbols": symbols,
                "depth": depth,
                "timestamp": datetime.now().isoformat()
            }

        else:
            analysis_result = {
                "success": False,
                "unsubscribed": False,
                "symbols": symbols,
                "depth": depth,
                "error": "Failed to unsubscribe",
                "timestamp": datetime.now().isoformat()
            }

        return KrakenDataValue(analysis_result)

    except Exception as e:
        analysis_result = {
            "success": False,
            "error": f"Failed to unsubscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KrakenDataValue(analysis_result)

async def subscribe_ohlc_skill(context: Dict[str, Any]) -> KrakenDataValue:
    symbols = context.get('symbols', [])
    interval = context.get('interval', 1)
    snapshot = context.get('snapshot', True)
    client = context.get('kraken_client')

    if not symbols:
        result = {"success": False, "error": "Symbols are required"}
        return KrakenDataValue(result)

    if not client:
        result = {"success": False, "error": "Kraken client not available"}
        return KrakenDataValue(result)

    try:
        valid_intervals = [1, 5, 15, 30, 60, 240, 1440, 10080, 21600]
        if interval not in valid_intervals:
            result = {"success": False, "error": f"Invalid interval. Valid intervals: {valid_intervals}"}
            return KrakenDataValue(result)

        params = {
            "channel": "ohlc",
            "symbol": symbols,
            "interval": interval,
            "snapshot": snapshot
        }

        subscribed = await client.subscribe("ohlc", params)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "channel": "ohlc",
                "symbols": symbols,
                "interval": interval,
                "snapshot": snapshot,
                "timestamp": datetime.now().isoformat()
            }

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbols": symbols,
                "interval": interval,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }

        return KrakenDataValue(analysis_result)

    except Exception as e:
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KrakenDataValue(analysis_result)

async def unsubscribe_ohlc_skill(context: Dict[str, Any]) -> KrakenDataValue:
    symbols = context.get('symbols', [])
    interval = context.get('interval', 1)
    client = context.get('kraken_client')

    if not symbols:
        result = {"success": False, "error": "Symbols are required"}
        return KrakenDataValue(result)

    if not client:
        result = {"success": False, "error": "Kraken client not available"}
        return KrakenDataValue(result)

    try:
        params = {
            "channel": "ohlc",
            "symbol": symbols,
            "interval": interval
        }

        unsubscribed = await client.unsubscribe("ohlc", params)

        if unsubscribed:
            analysis_result = {
                "success": True,
                "unsubscribed": True,
                "channel": "ohlc",
                "symbols": symbols,
                "interval": interval,
                "timestamp": datetime.now().isoformat()
            }

        else:
            analysis_result = {
                "success": False,
                "unsubscribed": False,
                "symbols": symbols,
                "interval": interval,
                "error": "Failed to unsubscribe",
                "timestamp": datetime.now().isoformat()
            }

        return KrakenDataValue(analysis_result)

    except Exception as e:
        analysis_result = {
            "success": False,
            "error": f"Failed to unsubscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KrakenDataValue(analysis_result)

async def subscribe_trade_skill(context: Dict[str, Any]) -> KrakenDataValue:
    symbols = context.get('symbols', [])
    snapshot = context.get('snapshot', False)
    client = context.get('kraken_client')

    if not symbols:
        result = {"success": False, "error": "Symbols are required"}
        return KrakenDataValue(result)

    if not client:
        result = {"success": False, "error": "Kraken client not available"}
        return KrakenDataValue(result)

    try:
        params = {
            "channel": "trade",
            "symbol": symbols,
            "snapshot": snapshot
        }

        subscribed = await client.subscribe("trade", params)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "channel": "trade",
                "symbols": symbols,
                "snapshot": snapshot,
                "timestamp": datetime.now().isoformat()
            }

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbols": symbols,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }

        return KrakenDataValue(analysis_result)

    except Exception as e:
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KrakenDataValue(analysis_result)

async def unsubscribe_trade_skill(context: Dict[str, Any]) -> KrakenDataValue:
    symbols = context.get('symbols', [])
    client = context.get('kraken_client')

    if not symbols:
        result = {"success": False, "error": "Symbols are required"}
        return KrakenDataValue(result)

    if not client:
        result = {"success": False, "error": "Kraken client not available"}
        return KrakenDataValue(result)

    try:
        params = {
            "channel": "trade",
            "symbol": symbols
        }

        unsubscribed = await client.unsubscribe("trade", params)

        if unsubscribed:
            analysis_result = {
                "success": True,
                "unsubscribed": True,
                "channel": "trade",
                "symbols": symbols,
                "timestamp": datetime.now().isoformat()
            }

        else:
            analysis_result = {
                "success": False,
                "unsubscribed": False,
                "symbols": symbols,
                "error": "Failed to unsubscribe",
                "timestamp": datetime.now().isoformat()
            }

        return KrakenDataValue(analysis_result)

    except Exception as e:
        analysis_result = {
            "success": False,
            "error": f"Failed to unsubscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KrakenDataValue(analysis_result)
