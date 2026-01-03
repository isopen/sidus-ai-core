from typing import Dict, Any
from datetime import datetime

class MEXCDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

async def connect_skill(context: Dict[str, Any]) -> MEXCDataValue:
    client = context.get('mexc_client')

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        connected = await client.connect()

        if connected:
            status = client.get_connection_status()

            analysis_result = {
                "success": True,
                "connected": True,
                "trade_type": "PERPETUAL",
                "status": status,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Connected to MEXC Futures WebSocket")

        else:
            analysis_result = {
                "success": False,
                "connected": False,
                "error": "Failed to connect to WebSocket",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to connect to MEXC")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error connecting: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to connect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def disconnect_skill(context: Dict[str, Any]) -> MEXCDataValue:
    client = context.get('mexc_client')

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        await client.disconnect()

        analysis_result = {
            "success": True,
            "disconnected": True,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Disconnected from MEXC WebSocket")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error disconnecting: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to disconnect: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def get_connections_skill(context: Dict[str, Any]) -> MEXCDataValue:
    client = context.get('mexc_client')

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        status = client.get_connection_status()

        total_subscriptions = len(status.get('subscriptions', []))

        analysis_result = {
            "success": True,
            "status": status,
            "summary": {
                "connected": status.get('connected', False),
                "total_subscriptions": total_subscriptions,
                "connection_type": status.get('connection', {}).get('trade_type', 'PERPETUAL')
            },
            "timestamp": datetime.now().isoformat()
        }

        if status.get('connected'):
            print(f"✅ Connected to MEXC")
            print(f"   Subscriptions: {total_subscriptions}")
        else:
            print(f"❌ Disconnected from MEXC")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error getting connections: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to get connections: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def subscribe_tickers_skill(context: Dict[str, Any]) -> MEXCDataValue:
    gzip = context.get('gzip', True)
    client = context.get('mexc_client')

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        message = {
            "method": "sub.tickers",
            "param": {},
            "gzip": gzip
        }

        subscribed = await client.subscribe(message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "channel": "tickers",
                "topic": "tickers/all",
                "gzip": gzip,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to all tickers")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "channel": "tickers",
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to tickers")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to tickers: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def subscribe_ticker_skill(context: Dict[str, Any]) -> MEXCDataValue:
    symbol = context.get('symbol')
    gzip = context.get('gzip', True)
    client = context.get('mexc_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return MEXCDataValue(result)

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        message = {
            "method": "sub.ticker",
            "param": {
                "symbol": symbol
            },
            "gzip": gzip
        }

        subscribed = await client.subscribe(message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "channel": "ticker",
                "topic": f"ticker/{symbol.lower()}",
                "gzip": gzip,
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

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to ticker: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def subscribe_deal_skill(context: Dict[str, Any]) -> MEXCDataValue:
    symbol = context.get('symbol')
    gzip = context.get('gzip', True)
    compress = context.get('compress', True)
    client = context.get('mexc_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return MEXCDataValue(result)

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        message = {
            "method": "sub.deal",
            "param": {
                "symbol": symbol
            },
            "gzip": gzip
        }

        if not compress:
            message['param']['compress'] = False

        subscribed = await client.subscribe(message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "channel": "deal",
                "topic": f"deal/{symbol.lower()}",
                "gzip": gzip,
                "compress": compress,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to deals: {symbol}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to deals: {symbol}")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to deals: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def subscribe_depth_skill(context: Dict[str, Any]) -> MEXCDataValue:
    symbol = context.get('symbol')
    gzip = context.get('gzip', True)
    client = context.get('mexc_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return MEXCDataValue(result)

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        message = {
            "method": "sub.depth",
            "param": {
                "symbol": symbol
            },
            "gzip": gzip
        }

        subscribed = await client.subscribe(message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "channel": "depth",
                "topic": f"depth/{symbol.lower()}",
                "gzip": gzip,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to depth: {symbol}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to depth: {symbol}")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to depth: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def subscribe_depth_step_skill(context: Dict[str, Any]) -> MEXCDataValue:
    symbol = context.get('symbol')
    step = context.get('step')
    gzip = context.get('gzip', True)
    client = context.get('mexc_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return MEXCDataValue(result)

    if not step:
        result = {"success": False, "error": "Step is required"}
        return MEXCDataValue(result)

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        message = {
            "method": "sub.depth.step",
            "param": {
                "symbol": symbol,
                "step": step
            },
            "gzip": gzip
        }

        subscribed = await client.subscribe(message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "channel": "depth.step",
                "step": step,
                "topic": f"depth_step/{symbol.lower()}",
                "gzip": gzip,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to depth step {step}: {symbol}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "step": step,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to depth step: {symbol}")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to depth step: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def subscribe_kline_skill(context: Dict[str, Any]) -> MEXCDataValue:
    symbol = context.get('symbol')
    interval = context.get('interval', 'Min1')
    gzip = context.get('gzip', True)
    client = context.get('mexc_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return MEXCDataValue(result)

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        message = {
            "method": "sub.kline",
            "param": {
                "symbol": symbol,
                "interval": interval
            },
            "gzip": gzip
        }

        subscribed = await client.subscribe(message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "channel": "kline",
                "interval": interval,
                "topic": f"kline/{symbol.lower()}/{interval}",
                "gzip": gzip,
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

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to kline: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def subscribe_funding_rate_skill(context: Dict[str, Any]) -> MEXCDataValue:
    symbol = context.get('symbol')
    gzip = context.get('gzip', True)
    client = context.get('mexc_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return MEXCDataValue(result)

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        message = {
            "method": "sub.funding.rate",
            "param": {
                "symbol": symbol
            },
            "gzip": gzip
        }

        subscribed = await client.subscribe(message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "channel": "funding.rate",
                "topic": f"funding_rate/{symbol.lower()}",
                "gzip": gzip,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to funding rate: {symbol}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to funding rate: {symbol}")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to funding rate: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def subscribe_index_price_skill(context: Dict[str, Any]) -> MEXCDataValue:
    symbol = context.get('symbol')
    gzip = context.get('gzip', True)
    client = context.get('mexc_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return MEXCDataValue(result)

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        message = {
            "method": "sub.index.price",
            "param": {
                "symbol": symbol
            },
            "gzip": gzip
        }

        subscribed = await client.subscribe(message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "channel": "index.price",
                "topic": f"index_price/{symbol.lower()}",
                "gzip": gzip,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to index price: {symbol}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to index price: {symbol}")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to index price: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def subscribe_fair_price_skill(context: Dict[str, Any]) -> MEXCDataValue:
    symbol = context.get('symbol')
    gzip = context.get('gzip', True)
    client = context.get('mexc_client')

    if not symbol:
        result = {"success": False, "error": "Symbol is required"}
        return MEXCDataValue(result)

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        message = {
            "method": "sub.fair.price",
            "param": {
                "symbol": symbol
            },
            "gzip": gzip
        }

        subscribed = await client.subscribe(message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "symbol": symbol.upper(),
                "channel": "fair.price",
                "topic": f"fair_price/{symbol.lower()}",
                "gzip": gzip,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to fair price: {symbol}")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "symbol": symbol,
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to fair price: {symbol}")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to fair price: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def subscribe_contract_skill(context: Dict[str, Any]) -> MEXCDataValue:
    gzip = context.get('gzip', True)
    client = context.get('mexc_client')

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        message = {
            "method": "sub.contract",
            "gzip": gzip
        }

        subscribed = await client.subscribe(message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "channel": "contract",
                "topic": "contract/all",
                "gzip": gzip,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to contract data")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "channel": "contract",
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to contract data")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to contract: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)

async def subscribe_event_contract_skill(context: Dict[str, Any]) -> MEXCDataValue:
    gzip = context.get('gzip', True)
    client = context.get('mexc_client')

    if not client:
        result = {"success": False, "error": "MEXC client not available"}
        return MEXCDataValue(result)

    try:
        message = {
            "method": "sub.event.contract",
            "gzip": gzip
        }

        subscribed = await client.subscribe(message)

        if subscribed:
            analysis_result = {
                "success": True,
                "subscribed": True,
                "channel": "event.contract",
                "topic": "event_contract/all",
                "gzip": gzip,
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Subscribed to event contract data")

        else:
            analysis_result = {
                "success": False,
                "subscribed": False,
                "channel": "event.contract",
                "error": "Failed to subscribe",
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Failed to subscribe to event contract data")

        return MEXCDataValue(analysis_result)

    except Exception as e:
        print(f"Error subscribing to event contract: {e}")
        analysis_result = {
            "success": False,
            "error": f"Failed to subscribe: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MEXCDataValue(analysis_result)
