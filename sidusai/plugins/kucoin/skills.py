from typing import Dict, Any
from datetime import datetime

class KuCoinDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

async def connect_skill(context: Dict[str, Any]) -> KuCoinDataValue:
    client = context.get('kucoin_client')
    trade_type = context.get('trade_type', 'SPOT')

    if not client:
        result = {"success": False, "error": "KuCoin client not available"}
        return KuCoinDataValue(result)

    try:
        connected = await client.connect(trade_type)

        if connected:
            status = client.get_connection_status()

            analysis_result = {
                "success": True,
                "connected": True,
                "trade_type": trade_type,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Connected to KuCoin {trade_type} WebSocket")

        else:
            analysis_result = {
                "success": False,
                "connected": False,
                "trade_type": trade_type,
                "error": "Failed to connect to WebSocket",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to connect to KuCoin {trade_type}")

        return KuCoinDataValue(analysis_result)

    except Exception as e:
        print(f"Error connecting: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to connect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KuCoinDataValue(analysis_result)

async def disconnect_skill(context: Dict[str, Any]) -> KuCoinDataValue:
    client = context.get('kucoin_client')

    if not client:
        result = {"success": False, "error": "KuCoin client not available"}
        return KuCoinDataValue(result)

    try:
        await client.disconnect()

        analysis_result = {
            "success": True,
            "disconnected": True,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Disconnected from KuCoin WebSocket")

        return KuCoinDataValue(analysis_result)

    except Exception as e:
        print(f"Error disconnecting: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to disconnect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KuCoinDataValue(analysis_result)

async def get_connections_skill(context: Dict[str, Any]) -> KuCoinDataValue:
    client = context.get('kucoin_client')

    if not client:
        result = {"success": False, "error": "KuCoin client not available"}
        return KuCoinDataValue(result)

    try:
        status = client.get_connection_status()

        total_subscriptions = len(status.get('subscriptions', []))

        analysis_result = {
            "success": True,
            "status": status,
            "summary": {
                "connected": status.get('connected', False),
                "total_subscriptions": total_subscriptions,
                "spot_connected": status.get('spot', {}).get('connected', False),
                "futures_connected": status.get('futures', {}).get('connected', False)
            },
            "timestamp": datetime.now().isoformat()
        }

        if status.get('connected'):
            print(f"✅ Connected to KuCoin")
            print(f"   Subscriptions: {total_subscriptions}")
        else:
            print(f"❌ Disconnected from KuCoin")

        return KuCoinDataValue(analysis_result)

    except Exception as e:
        print(f"Error getting connections: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to get connections: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KuCoinDataValue(analysis_result)

async def subscribe_ticker_skill(context: Dict[str, Any]) -> KuCoinDataValue:
    symbol = context.get('symbol')
    trade_type = context.get('trade_type', 'SPOT')
    client = context.get('kucoin_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return KuCoinDataValue(result)

    if not client:
        result = {"success": False, "error": "KuCoin client not available"}
        return KuCoinDataValue(result)

    try:
        message = {
            "action": "SUBSCRIBE",
            "channel": "ticker",
            "tradeType": trade_type,
            "symbol": symbol,
        }

        subscribed = await client.subscribe(trade_type, message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "trade_type": trade_type,
                "symbol": symbol.upper(),
                "channel": "ticker",
                "topic": f"ticker/{symbol.lower()}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to ticker: {symbol} ({trade_type})")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "trade_type": trade_type,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to ticker: {symbol}")

        return KuCoinDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to ticker: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KuCoinDataValue(analysis_result)

async def subscribe_kline_skill(context: Dict[str, Any]) -> KuCoinDataValue:
    symbol = context.get('symbol')
    interval = context.get('interval', '1min')
    trade_type = context.get('trade_type', 'SPOT')
    client = context.get('kucoin_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return KuCoinDataValue(result)

    if not client:
        result = {"success": False, "error": "KuCoin client not available"}
        return KuCoinDataValue(result)

    try:
        message = {
            "action": "SUBSCRIBE",
            "channel": "kline",
            "tradeType": trade_type,
            "symbol": symbol,
            "interval": interval
        }

        subscribed = await client.subscribe(trade_type, message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "trade_type": trade_type,
                "symbol": symbol.upper(),
                "channel": "kline",
                "interval": interval,
                "topic": f"kline/{symbol.lower()}/{interval}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to kline: {symbol} ({interval}, {trade_type})")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "trade_type": trade_type,
                "symbol": symbol,
                "interval": interval,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to kline: {symbol}")

        return KuCoinDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to kline: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KuCoinDataValue(analysis_result)

async def subscribe_orderbook_skill(context: Dict[str, Any]) -> KuCoinDataValue:
    symbol = context.get('symbol')
    depth = context.get('depth', '5')
    trade_type = context.get('trade_type', 'SPOT')
    rpi_filter = context.get('rpi_filter', 0)
    client = context.get('kucoin_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return KuCoinDataValue(result)

    if not client:
        result = {"success": False, "error": "KuCoin client not available"}
        return KuCoinDataValue(result)

    try:
        message = {
            "action": "SUBSCRIBE",
            "channel": "obu",
            "tradeType": trade_type,
            "symbol": symbol,
            "depth": depth,
            "rpiFilter": rpi_filter
        }

        subscribed = await client.subscribe(trade_type, message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "trade_type": trade_type,
                "symbol": symbol.upper(),
                "channel": "obu",
                "depth": depth,
                "rpi_filter": rpi_filter,
                "topic": f"orderbook/{symbol.lower()}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to orderbook: {symbol} (depth: {depth}, {trade_type})")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "trade_type": trade_type,
                "symbol": symbol,
                "depth": depth,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to orderbook: {symbol}")

        return KuCoinDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to orderbook: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KuCoinDataValue(analysis_result)

async def subscribe_trades_skill(context: Dict[str, Any]) -> KuCoinDataValue:
    symbol = context.get('symbol')
    trade_type = context.get('trade_type', 'SPOT')
    client = context.get('kucoin_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return KuCoinDataValue(result)

    if not client:
        result = {"success": False, "error": "KuCoin client not available"}
        return KuCoinDataValue(result)

    try:
        message = {
            "action": "SUBSCRIBE",
            "channel": "trade",
            "tradeType": trade_type,
            "symbol": symbol,
        }

        subscribed = await client.subscribe(trade_type, message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "trade_type": trade_type,
                "symbol": symbol.upper(),
                "channel": "trade",
                "topic": f"trade/{symbol.lower()}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to trades: {symbol} ({trade_type})")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "trade_type": trade_type,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to trades: {symbol}")

        return KuCoinDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to trades: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return KuCoinDataValue(analysis_result)
