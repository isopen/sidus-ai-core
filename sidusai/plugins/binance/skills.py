from typing import Dict, Any
from datetime import datetime

class BinanceDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

async def connect_skill(context: Dict[str, Any]) -> BinanceDataValue:
    client = context.get('binance_client')

    if not client:
        result = {"success": False, "error": "Binance client not available"}
        return BinanceDataValue(result)

    try:
        streams = context.get('streams', [])
        connected = await client.connect(streams)

        if connected:
            status = client.get_connection_status()

            analysis_result = {
                "success": True,
                "connected": True,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Connected to Binance WebSocket")

        else:
            analysis_result = {
                "success": False,
                "connected": False,
                "error": "Failed to connect to WebSocket",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to connect to Binance")

        return BinanceDataValue(analysis_result)

    except Exception as e:
        print(f"Error connecting: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to connect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BinanceDataValue(analysis_result)

async def disconnect_skill(context: Dict[str, Any]) -> BinanceDataValue:
    client = context.get('binance_client')

    if not client:
        result = {"success": False, "error": "Binance client not available"}
        return BinanceDataValue(result)

    try:
        await client.disconnect()

        analysis_result = {
            "success": True,
            "disconnected": True,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Disconnected from Binance WebSocket")

        return BinanceDataValue(analysis_result)

    except Exception as e:
        print(f"Error disconnecting: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to disconnect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BinanceDataValue(analysis_result)

async def get_connections_skill(context: Dict[str, Any]) -> BinanceDataValue:
    client = context.get('binance_client')

    if not client:
        result = {"success": False, "error": "Binance client not available"}
        return BinanceDataValue(result)

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
            print(f"✅ Connected to Binance")
            print(f"   Subscriptions: {total_subscriptions}")
        else:
            print(f"❌ Disconnected from Binance")

        return BinanceDataValue(analysis_result)

    except Exception as e:
        print(f"Error getting connections: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to get connections: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BinanceDataValue(analysis_result)

async def subscribe_ticker_skill(context: Dict[str, Any]) -> BinanceDataValue:
    symbol = context.get('symbol')
    client = context.get('binance_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BinanceDataValue(result)

    if not client:
        result = {"success": False, "error": "Binance client not available"}
        return BinanceDataValue(result)

    try:
        streams = [f"{symbol.lower()}@ticker"]
        subscribed = await client.subscribe(streams)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "streams": streams,
                "topic": f"24hrticker/{symbol.lower()}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to ticker: {symbol}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to ticker: {symbol}")

        return BinanceDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to ticker: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BinanceDataValue(analysis_result)

async def subscribe_kline_skill(context: Dict[str, Any]) -> BinanceDataValue:
    symbol = context.get('symbol')
    interval = context.get('interval', '1m')
    client = context.get('binance_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BinanceDataValue(result)

    if not client:
        result = {"success": False, "error": "Binance client not available"}
        return BinanceDataValue(result)

    try:
        streams = [f"{symbol.lower()}@kline_{interval}"]
        subscribed = await client.subscribe(streams)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "interval": interval,
                "streams": streams,
                "topic": f"kline/{symbol.lower()}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to kline: {symbol} ({interval})")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "interval": interval,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to kline: {symbol}")

        return BinanceDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to kline: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BinanceDataValue(analysis_result)

async def subscribe_orderbook_skill(context: Dict[str, Any]) -> BinanceDataValue:
    symbol = context.get('symbol')
    level = context.get('level', '5')
    client = context.get('binance_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BinanceDataValue(result)

    if not client:
        result = {"success": False, "error": "Binance client not available"}
        return BinanceDataValue(result)

    try:
        if level == '5':
            stream_name = f"{symbol.lower()}@depth5"
        elif level == '10':
            stream_name = f"{symbol.lower()}@depth10"
        elif level == '20':
            stream_name = f"{symbol.lower()}@depth20"
        else:
            stream_name = f"{symbol.lower()}@depth"

        streams = [stream_name]
        subscribed = await client.subscribe(streams)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "level": level,
                "streams": streams,
                "topic": f"depthupdate/{symbol.lower()}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to orderbook: {symbol} (level: {level})")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "level": level,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to orderbook: {symbol}")

        return BinanceDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to orderbook: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BinanceDataValue(analysis_result)

async def subscribe_trades_skill(context: Dict[str, Any]) -> BinanceDataValue:
    symbol = context.get('symbol')
    client = context.get('binance_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BinanceDataValue(result)

    if not client:
        result = {"success": False, "error": "Binance client not available"}
        return BinanceDataValue(result)

    try:
        streams = [f"{symbol.lower()}@trade"]
        subscribed = await client.subscribe(streams)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "streams": streams,
                "topic": f"trade/{symbol.lower()}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to trades: {symbol}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to trades: {symbol}")

        return BinanceDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to trades: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BinanceDataValue(analysis_result)

async def subscribe_mark_price_skill(context: Dict[str, Any]) -> BinanceDataValue:
    symbol = context.get('symbol')
    client = context.get('binance_client')

    if not client:
        result = {"success": False, "error": "Binance client not available"}
        return BinanceDataValue(result)

    try:
        if symbol:
            streams = [f"{symbol.lower()}@markPrice"]
        else:
            streams = ["!markPrice@arr"]

        subscribed = await client.subscribe(streams)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "streams": streams,
                "timestamp": datetime.now().isoformat()
            }

            if symbol:
                analysis_result["symbol"] = symbol.upper()
                analysis_result["topic"] = f"markpriceupdate/{symbol.lower()}"
                print(f"✅ Subscribed to mark price: {symbol}")
            else:
                analysis_result["topic"] = "markpriceupdate/all"
                print(f"✅ Subscribed to all mark prices")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to mark price")

        return BinanceDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to mark price: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BinanceDataValue(analysis_result)

async def subscribe_funding_rate_skill(context: Dict[str, Any]) -> BinanceDataValue:
    symbol = context.get('symbol')
    client = context.get('binance_client')

    if not client:
        result = {"success": False, "error": "Binance client not available"}
        return BinanceDataValue(result)

    try:
        if symbol:
            streams = [f"{symbol.lower()}@markPrice"]
        else:
            streams = ["!markPrice@arr"]

        subscribed = await client.subscribe(streams)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "streams": streams,
                "timestamp": datetime.now().isoformat()
            }

            if symbol:
                analysis_result["symbol"] = symbol.upper()
                analysis_result["topic"] = f"fundingrate/{symbol.lower()}"
                print(f"✅ Subscribed to funding rate: {symbol}")
            else:
                analysis_result["topic"] = "fundingrate/all"
                print(f"✅ Subscribed to all funding rates")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to funding rate")

        return BinanceDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to funding rate: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BinanceDataValue(analysis_result)

async def subscribe_agg_trades_skill(context: Dict[str, Any]) -> BinanceDataValue:
    symbol = context.get('symbol')
    client = context.get('binance_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return BinanceDataValue(result)

    if not client:
        result = {"success": False, "error": "Binance client not available"}
        return BinanceDataValue(result)

    try:
        streams = [f"{symbol.lower()}@aggTrade"]
        subscribed = await client.subscribe(streams)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "streams": streams,
                "topic": f"aggtrade/{symbol.lower()}",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to agg trades: {symbol}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to agg trades: {symbol}")

        return BinanceDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to agg trades: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return BinanceDataValue(analysis_result)
