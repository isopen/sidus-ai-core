import os
import sys
import time
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.binance import create_binance_agent

def ticker_callback(data):
    print(f"\n📊 Binance Futures Ticker:")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Event: {data['event_type']}")
    print(f"   Time: {data['timestamp_readable']}")

    ticker_data = data['data']
    if ticker_data:
        print(f"   Last: {ticker_data.get('c', 'N/A')}")
        print(f"   Change: {ticker_data.get('P', 'N/A')}%")
        print(f"   Volume: {ticker_data.get('v', 'N/A')}")
        print(f"   High: {ticker_data.get('h', 'N/A')}")
        print(f"   Low: {ticker_data.get('l', 'N/A')}")

def kline_callback(data):
    print(f"\n📈 Binance Futures Kline:")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Event: {data['event_type']}")
    print(f"   Time: {data['timestamp_readable']}")

    kline_data = data['data']
    if kline_data and 'k' in kline_data:
        k = kline_data['k']
        print(f"   Open: {k.get('o', 'N/A')}")
        print(f"   High: {k.get('h', 'N/A')}")
        print(f"   Low: {k.get('l', 'N/A')}")
        print(f"   Close: {k.get('c', 'N/A')}")
        print(f"   Volume: {k.get('v', 'N/A')}")
        print(f"   Trades: {k.get('n', 'N/A')}")

def orderbook_callback(data):
    print(f"\n📚 Binance Futures Orderbook:")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Event: {data['event_type']}")
    print(f"   Time: {data['timestamp_readable']}")

    depth_data = data['data']
    if depth_data and 'b' in depth_data and 'a' in depth_data:
        bids = depth_data.get('b', [])
        asks = depth_data.get('a', [])

        print(f"   Bids (top 3):")
        for i, bid in enumerate(bids[:3]):
            if len(bid) >= 2:
                print(f"     {i+1}. {bid[0]} x {bid[1]}")

        print(f"   Asks (top 3):")
        for i, ask in enumerate(asks[:3]):
            if len(ask) >= 2:
                print(f"     {i+1}. {ask[0]} x {ask[1]}")

def trades_callback(data):
    print(f"\n💎 Binance Futures Trade:")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Event: {data['event_type']}")
    print(f"   Time: {data['timestamp_readable']}")

    trade_data = data['data']
    if trade_data:
        print(f"   Price: {trade_data.get('p', 'N/A')}")
        print(f"   Quantity: {trade_data.get('q', 'N/A')}")
        print(f"   Side: {'SELL' if trade_data.get('m') else 'BUY'}")
        print(f"   Trade ID: {trade_data.get('t', 'N/A')}")

def agg_trades_callback(data):
    print(f"\n⚡ Binance Futures Agg Trade:")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Event: {data['event_type']}")
    print(f"   Time: {data['timestamp_readable']}")

    agg_data = data['data']
    if agg_data:
        print(f"   Price: {agg_data.get('p', 'N/A')}")
        print(f"   Quantity: {agg_data.get('q', 'N/A')}")
        print(f"   First Trade ID: {agg_data.get('f', 'N/A')}")
        print(f"   Last Trade ID: {agg_data.get('l', 'N/A')}")

def mark_price_callback(data):
    print(f"\n🏷️  Binance Futures Mark Price:")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Event: {data['event_type']}")
    print(f"   Time: {data['timestamp_readable']}")

    mark_data = data['data']
    if mark_data:
        print(f"   Mark Price: {mark_data.get('p', 'N/A')}")
        print(f"   Index Price: {mark_data.get('i', 'N/A')}")
        print(f"   Estimated Settle: {mark_data.get('P', 'N/A')}")
        print(f"   Funding Rate: {mark_data.get('r', 'N/A')}")
        print(f"   Next Funding: {mark_data.get('T', 'N/A')}")

def funding_rate_callback(data):
    print(f"\n💰 Binance Futures Funding Rate:")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Event: {data['event_type']}")
    print(f"   Time: {data['timestamp_readable']}")

    funding_data = data['data']
    if funding_data:
        print(f"   Funding Rate: {funding_data.get('r', 'N/A')}")
        print(f"   Funding Time: {funding_data.get('T', 'N/A')}")

def main():
    print("BINANCE FUTURES WEBSOCKET EXAMPLE")

    agent = create_binance_agent()

    print("\n1. Connect to Binance Futures:")
    print("-" * 40)

    result = agent.connect()
    if result.get('success'):
        status = result.get('status', {})
        print(f"✅ Connected to Binance Futures")
        print(f"   URL: {status.get('url', 'N/A')}")
        print(f"   Time: {status.get('connected_at', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error')}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Check firewall settings")
        print("3. Make sure websockets is installed:")
        print("   pip install websockets")
        return

    time.sleep(2)

    print("\n2. Register callbacks for BTCUSDT:")
    print("-" * 40)

    agent.register_callback("24hrticker/btcusdt", ticker_callback)
    agent.register_callback("kline/btcusdt", kline_callback)
    agent.register_callback("depthupdate/btcusdt", orderbook_callback)
    agent.register_callback("trade/btcusdt", trades_callback)
    agent.register_callback("aggtrade/btcusdt", agg_trades_callback)
    agent.register_callback("markpriceupdate/btcusdt", mark_price_callback)
    agent.register_callback("fundingrate/btcusdt", funding_rate_callback)

    print("✅ Callbacks registered for BTCUSDT")

    print("\n3. Subscribe to BTCUSDT ticker:")
    print("-" * 40)

    result = agent.subscribe_ticker(symbol="BTCUSDT")
    if result.get('success'):
        print(f"✅ Subscribed to BTCUSDT ticker")
        print(f"   Stream: {result.get('streams', ['N/A'])[0]}")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n4. Subscribe to BTCUSDT 1m kline:")
    print("-" * 40)

    result = agent.subscribe_kline(symbol="BTCUSDT", interval="1m")
    if result.get('success'):
        print(f"✅ Subscribed to BTCUSDT 1m kline")
        print(f"   Stream: {result.get('streams', ['N/A'])[0]}")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n5. Subscribe to BTCUSDT orderbook (level 5):")
    print("-" * 40)

    result = agent.subscribe_orderbook(symbol="BTCUSDT", level="5")
    if result.get('success'):
        print(f"✅ Subscribed to BTCUSDT orderbook (depth5)")
        print(f"   Stream: {result.get('streams', ['N/A'])[0]}")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n6. Subscribe to BTCUSDT trades:")
    print("-" * 40)

    result = agent.subscribe_trades(symbol="BTCUSDT")
    if result.get('success'):
        print(f"✅ Subscribed to BTCUSDT trades")
        print(f"   Stream: {result.get('streams', ['N/A'])[0]}")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n7. Subscribe to BTCUSDT aggregated trades:")
    print("-" * 40)

    result = agent.subscribe_agg_trades(symbol="BTCUSDT")
    if result.get('success'):
        print(f"✅ Subscribed to BTCUSDT aggregated trades")
        print(f"   Stream: {result.get('streams', ['N/A'])[0]}")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n8. Subscribe to BTCUSDT mark price:")
    print("-" * 40)

    result = agent.subscribe_mark_price(symbol="BTCUSDT")
    if result.get('success'):
        print(f"✅ Subscribed to BTCUSDT mark price")
        print(f"   Stream: {result.get('streams', ['N/A'])[0]}")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n9. Check connection status:")
    print("-" * 40)

    result = agent.get_connections()
    if result.get('success'):
        status = result.get('status', {})
        summary = result.get('summary', {})

        if status.get('connected'):
            print(f"✅ Connected to Binance Futures")
            print(f"   URL: {status.get('url', 'N/A')}")
            print(f"   Total subscriptions: {summary.get('total_subscriptions', 0)}")

            subscriptions = status.get('subscriptions', [])
            if subscriptions:
                print(f"   Active streams:")
                for stream in subscriptions:
                    print(f"     - {stream}")
        else:
            print(f"❌ Not connected")
    else:
        print(f"❌ Error getting connection status: {result.get('error')}")

    print("\n10. Listening for real-time data (15 seconds)...")
    print("-" * 40)
    print("You should see real-time updates from:")
    print("  • Ticker (24hr statistics)")
    print("  • Kline (1-minute candles)")
    print("  • Orderbook (depth updates)")
    print("  • Trades (individual trades)")
    print("  • Aggregated Trades")
    print("  • Mark Price & Funding Rate")
    print("\nPress Ctrl+C to stop early")

    try:
        start_time = time.time()
        while time.time() - start_time < 15:
            elapsed = int(time.time() - start_time)
            print(f"⏳ Listening... {elapsed}/15 seconds", end='\r')
            time.sleep(1)
        print()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping early...")

    print("\n11. Test with ETHUSDT (quick test):")
    print("-" * 40)

    agent.register_callback("24hrticker/ethusdt", ticker_callback)

    result = agent.subscribe_ticker(symbol="ETHUSDT")
    if result.get('success'):
        print(f"✅ Subscribed to ETHUSDT ticker")

        print("Listening for ETH data (3 seconds)...")
        try:
            for i in range(3):
                print(f"⏳ {i+1}/3", end='\r')
                time.sleep(1)
            print()
        except KeyboardInterrupt:
            pass
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n12. Cleanup and disconnect:")
    print("-" * 40)

    result = agent.disconnect()
    if result.get('success'):
        print(f"✅ Disconnected from Binance Futures")
    else:
        print(f"❌ Error during disconnect: {result.get('error')}")

if __name__ == "__main__":
    main()
