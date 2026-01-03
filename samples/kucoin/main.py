import os
import sys
import time
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.kucoin import create_kucoin_agent

def ticker_callback(data):
    print(f"\n📊 KuCoin Ticker:")
    print(f"   Trade Type: {data['trade_type']}")
    print(f"   Channel: {data['channel_type']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    ticker_data = data['data']
    if ticker_data:
        print(f"   Last Price: {ticker_data.get('l', 'N/A')}")
        print(f"   Bid: {ticker_data.get('b', 'N/A')} x {ticker_data.get('B', 'N/A')}")
        print(f"   Ask: {ticker_data.get('a', 'N/A')} x {ticker_data.get('A', 'N/A')}")
        print(f"   Volume: {ticker_data.get('q', 'N/A')}")
        print(f"   Side: {ticker_data.get('S', 'N/A')}")
        print(f"   Sequence: {ticker_data.get('E', 'N/A')}")

def kline_callback(data):
    print(f"\n📈 KuCoin Kline:")
    print(f"   Trade Type: {data['trade_type']}")
    print(f"   Channel: {data['channel_type']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    kline_data = data['data']
    if kline_data:
        print(f"   Interval: {kline_data.get('i', 'N/A')}")
        print(f"   Open Time: {kline_data.get('O', 'N/A')}")
        print(f"   Close Time: {kline_data.get('C', 'N/A')}")
        print(f"   Open: {kline_data.get('o', 'N/A')}")
        print(f"   High: {kline_data.get('h', 'N/A')}")
        print(f"   Low: {kline_data.get('l', 'N/A')}")
        print(f"   Close: {kline_data.get('c', 'N/A')}")
        print(f"   Volume: {kline_data.get('v', 'N/A')}")
        print(f"   Amount: {kline_data.get('a', 'N/A')}")

def orderbook_callback(data):
    print(f"\n📚 KuCoin Orderbook:")
    print(f"   Trade Type: {data['trade_type']}")
    print(f"   Channel: {data['channel_type']}")
    print(f"   Push Type: {data['push_type']}")
    print(f"   Depth Level: {data['depth_level']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    ob_data = data['data']
    if ob_data:
        print(f"   Sequence Start: {ob_data.get('O', 'N/A')}")
        print(f"   Sequence End: {ob_data.get('C', 'N/A')}")

        bids = ob_data.get('b', [])
        asks = ob_data.get('a', [])

        if data['push_type'] == 'snapshot':
            print(f"   📸 SNAPSHOT received")
        elif data['push_type'] == 'delta':
            print(f"   📈 DELTA update received")

        print(f"   Bids (top 3):")
        for i, bid in enumerate(bids[:3]):
            if len(bid) >= 2:
                if len(bid) == 2:
                    print(f"     {i+1}. {bid[0]} x {bid[1]}")
                elif len(bid) == 3:
                    print(f"     {i+1}. {bid[0]} x {bid[1]} (RPI: {bid[2]})")

        print(f"   Asks (top 3):")
        for i, ask in enumerate(asks[:3]):
            if len(ask) >= 2:
                if len(ask) == 2:
                    print(f"     {i+1}. {ask[0]} x {ask[1]}")
                elif len(ask) == 3:
                    print(f"     {i+1}. {ask[0]} x {ask[1]} (RPI: {ask[2]})")

def trades_callback(data):
    print(f"\n💎 KuCoin Trade:")
    print(f"   Trade Type: {data['trade_type']}")
    print(f"   Channel: {data['channel_type']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    trade_data = data['data']
    if trade_data:
        print(f"   Price: {trade_data.get('p', 'N/A')}")
        print(f"   Quantity: {trade_data.get('q', 'N/A')}")
        print(f"   Side: {trade_data.get('S', 'N/A')}")
        print(f"   Trade ID: {trade_data.get('ti', 'N/A')}")
        print(f"   Sequence: {trade_data.get('E', 'N/A')}")
        print(f"   RPI Order: {trade_data.get('rpi', 'N/A')}")

def main():
    print("KUCOIN WEBSOCKET EXAMPLE - SPOT & FUTURES")

    agent = create_kucoin_agent()

    print("\n1. Connect to KuCoin SPOT:")
    print("-" * 40)

    result = agent.connect("SPOT")
    if result.get('success'):
        status = result.get('status', {})
        print(f"✅ Connected to KuCoin SPOT")
        print(f"   Trade Type: {result.get('trade_type', 'N/A')}")
        print(f"   Time: {result.get('timestamp', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error')}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Check firewall settings")
        print("3. Make sure websockets is installed:")
        print("   pip install websockets")
        return

    time.sleep(2)

    print("\n2. Register callbacks for BTC-USDT (SPOT):")
    print("-" * 40)

    agent.register_callback("ticker/btc-usdt", ticker_callback)
    agent.register_callback("kline/btc-usdt/1min", kline_callback)
    agent.register_callback("orderbook/btc-usdt", orderbook_callback)
    agent.register_callback("trade/btc-usdt", trades_callback)

    print("✅ Callbacks registered for BTC-USDT (SPOT)")

    print("\n3. Subscribe to BTC-USDT SPOT ticker:")
    print("-" * 40)

    result = agent.subscribe_ticker(symbol="BTC-USDT", trade_type="SPOT")
    if result.get('success'):
        print(f"✅ Subscribed to BTC-USDT SPOT ticker")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        print(f"   Channel: {result.get('channel', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n4. Subscribe to BTC-USDT SPOT 1min kline:")
    print("-" * 40)

    result = agent.subscribe_kline(symbol="BTC-USDT", interval="1min", trade_type="SPOT")
    if result.get('success'):
        print(f"✅ Subscribed to BTC-USDT SPOT 1min kline")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        print(f"   Interval: {result.get('interval', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n5. Subscribe to BTC-USDT SPOT orderbook (depth 5):")
    print("-" * 40)

    result = agent.subscribe_orderbook(symbol="BTC-USDT", depth="5", trade_type="SPOT", rpi_filter=0)
    if result.get('success'):
        print(f"✅ Subscribed to BTC-USDT SPOT orderbook")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        print(f"   Depth: {result.get('depth', 'N/A')}")
        print(f"   RPI Filter: {result.get('rpi_filter', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n6. Subscribe to BTC-USDT SPOT trades:")
    print("-" * 40)

    result = agent.subscribe_trades(symbol="BTC-USDT", trade_type="SPOT")
    if result.get('success'):
        print(f"✅ Subscribed to BTC-USDT SPOT trades")
        print(f"   Topic: {result.get('topic', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n7. Check connection status:")
    print("-" * 40)

    result = agent.get_connections()
    if result.get('success'):
        status = result.get('status', {})
        summary = result.get('summary', {})

        if status.get('connected'):
            print(f"✅ Connected to KuCoin")
            print(f"   SPOT Connected: {summary.get('spot_connected', False)}")
            print(f"   Total subscriptions: {summary.get('total_subscriptions', 0)}")

            subscriptions = status.get('subscriptions', [])
            if subscriptions:
                print(f"   Active subscriptions:")
                for sub in subscriptions:
                    print(f"     - {sub}")
        else:
            print(f"❌ Not connected")
    else:
        print(f"❌ Error getting connection status: {result.get('error')}")

    print("\n8. Listening for SPOT data (10 seconds)...")
    print("-" * 40)
    print("You should see real-time updates from:")
    print("  • Ticker (BBO changes)")
    print("  • Kline (1-minute candles)")
    print("  • Orderbook (depth 5, 100ms updates)")
    print("  • Trades (individual trades)")
    print("\nPress Ctrl+C to stop early")

    try:
        start_time = time.time()
        while time.time() - start_time < 10:
            elapsed = int(time.time() - start_time)
            print(f"⏳ Listening SPOT... {elapsed}/10 seconds", end='\r')
            time.sleep(1)
        print()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping early...")

    print("\n9. Connect to KuCoin FUTURES:")
    print("-" * 40)

    result = agent.connect("FUTURES")
    if result.get('success'):
        print(f"✅ Connected to KuCoin FUTURES")
        print(f"   Trade Type: {result.get('trade_type', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(2)

    print("\n10. Subscribe to XBTUSDTM FUTURES data:")
    print("-" * 40)

    result = agent.subscribe_ticker(symbol="XBTUSDTM", trade_type="FUTURES")
    if result.get('success'):
        print(f"✅ Subscribed to XBTUSDTM FUTURES ticker")
        agent.register_callback("ticker/xbtusdtm", ticker_callback)

    result = agent.subscribe_orderbook(
        symbol="XBTUSDTM", 
        depth="5", 
        trade_type="FUTURES", 
        rpi_filter=0
    )
    if result.get('success'):
        print(f"✅ Subscribed to XBTUSDTM FUTURES orderbook")
        agent.register_callback("orderbook/xbtusdtm", orderbook_callback)

    result = agent.subscribe_trades(symbol="XBTUSDTM", trade_type="FUTURES")
    if result.get('success'):
        print(f"✅ Subscribed to XBTUSDTM FUTURES trades")
        agent.register_callback("trade/xbtusdtm", trades_callback)

    print("\n11. Listening for FUTURES data (8 seconds)...")
    print("-" * 40)
    print("KuCoin Futures features:")
    print("  • Different symbol format (XBTUSDTM instead of BTC-USDT)")
    print("  • RPI (Reduce-Only Position) orders filter")
    print("  • Real-time mark prices")
    print("  • Funding rate information")

    try:
        start_time = time.time()
        while time.time() - start_time < 8:
            elapsed = int(time.time() - start_time)
            print(f"⏳ Listening FUTURES... {elapsed}/8 seconds", end='\r')
            time.sleep(1)
        print()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping early...")

    print("\n12. Test BBO (Best Bid/Offer) orderbook:")
    print("-" * 40)

    result = agent.subscribe_orderbook(
        symbol="ETH-USDT", 
        depth="1",
        trade_type="SPOT",
        rpi_filter=0
    )
    if result.get('success'):
        print(f"✅ Subscribed to ETH-USDT BBO")
        agent.register_callback("orderbook/eth-usdt", orderbook_callback)

        print("Listening for BBO updates (5 seconds)...")
        try:
            for i in range(5):
                print(f"⏳ {i+1}/5", end='\r')
                time.sleep(1)
            print()
        except KeyboardInterrupt:
            pass

    print("\n13. Test different kline intervals:")
    print("-" * 40)

    intervals = ["5min", "15min", "1hour"]
    for interval in intervals:
        result = agent.subscribe_kline(
            symbol="BTC-USDT", 
            interval=interval, 
            trade_type="SPOT"
        )
        if result.get('success'):
            print(f"✅ Subscribed to {interval} kline")
            agent.register_callback(f"kline/btc-usdt/{interval}", kline_callback)

    print("Listening for different kline intervals (5 seconds)...")
    try:
        for i in range(5):
            print(f"⏳ {i+1}/5", end='\r')
            time.sleep(1)
        print()
    except KeyboardInterrupt:
        pass

    print("\n14. Cleanup and disconnect:")
    print("-" * 40)

    result = agent.disconnect()
    if result.get('success'):
        print(f"✅ Disconnected from KuCoin WebSocket")
    else:
        print(f"❌ Error during disconnect: {result.get('error')}")

    print("\n" + "="*50)
    print("KUCOIN WEBSOCKET FEATURES DEMONSTRATED:")
    print("="*50)
    print("✓ SPOT and FUTURES support")
    print("✓ Ticker (real-time BBO updates)")
    print("✓ Kline (multiple intervals: 1min, 5min, 15min, 1hour)")
    print("✓ Orderbook (BBO, depth 5, depth 50, increment)")
    print("✓ Trades (with RPI order indication)")
    print("✓ RPI filter support")
    print("✓ Sequence number tracking")
    print("✓ Dual WebSocket connections (SPOT + FUTURES)")
    print("="*50)

if __name__ == "__main__":
    main()
