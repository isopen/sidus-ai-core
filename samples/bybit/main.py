import os
import sys
import time
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.bybit import create_bybit_agent

def ticker_callback(data):
    print(f"\n📊 Ticker update:")
    print(f"   Symbol: {data['topic'].replace('tickers.', '')}")
    print(f"   Time: {data['timestamp_readable']}")

    ticker_data = data['data']
    if isinstance(ticker_data, dict):
        print(f"   Last price: {ticker_data.get('lastPrice', 'N/A')}")
        print(f"   24h Change: {ticker_data.get('price24hPcnt', 'N/A')}")

def kline_callback(data):
    print(f"\n📈 Kline update:")
    print(f"   Symbol: {data['topic'].replace('kline.', '')}")
    print(f"   Time: {data['timestamp_readable']}")

    kline_data = data['data']
    if isinstance(kline_data, list) and len(kline_data) > 0:
        candle = kline_data[0]
        print(f"   Open: {candle.get('open', 'N/A')}")
        print(f"   Close: {candle.get('close', 'N/A')}")
        print(f"   Volume: {candle.get('volume', 'N/A')}")

def main():
    print("BYBIT WEBSOCKET")
    print("=" * 50)

    agent = create_bybit_agent(testnet=True)

    print("\n1. Connect to Bybit Testnet:")
    print("-" * 40)

    result = agent.connect(stream_type='spot')
    if result.get('success'):
        print(f"✅ Connected to Bybit Testnet")
        print(f"   URL: {result.get('status', {}).get('url', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error')}")
        return

    time.sleep(1)

    print("\n2. Register callbacks:")
    print("-" * 40)

    agent.register_callback("tickers.BTCUSDT", ticker_callback)
    agent.register_callback("tickers.ETHUSDT", ticker_callback)
    agent.register_callback("kline.1.BTCUSDT", kline_callback)

    print("\n3. Subscribe to BTCUSDT ticker:")
    print("-" * 40)

    result = agent.subscribe_ticker(symbol="BTCUSDT", stream_type='spot')
    if result.get('success'):
        print(f"✅ Subscribed to BTCUSDT ticker")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n4. Subscribe to ETHUSDT ticker:")
    print("-" * 40)

    result = agent.subscribe_ticker(symbol="ETHUSDT", stream_type='spot')
    if result.get('success'):
        print(f"✅ Subscribed to ETHUSDT ticker")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n5. Subscribe to BTCUSDT kline:")
    print("-" * 40)

    result = agent.subscribe_kline(symbol="BTCUSDT", interval="1", stream_type='spot')
    if result.get('success'):
        print(f"✅ Subscribed to BTCUSDT 1m kline")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n6. Check connection status:")
    print("-" * 40)

    result = agent.get_connections()
    if result.get('success'):
        summary = result.get('summary', {})
        print(f"✅ Connections: {summary.get('connected', 0)} connected")
        print(f"   Total subscriptions: {summary.get('total_subscriptions', 0)}")

        for conn in result.get('connections', []):
            if conn.get('connected'):
                print(f"   {conn['stream_type']}: ✅ Connected")
                for sub in conn.get('subscriptions', []):
                    print(f"     - {sub}")

    print("\n7. Listening for data (15 seconds)...")
    print("-" * 40)
    print("You should see real-time updates")

    try:
        for i in range(15):
            print(f"⏳ {i+1}/15 seconds", end='\r')
            time.sleep(1)
        print()
    except KeyboardInterrupt:
        print("\nStopping...")

    print("\n8. Cleanup:")
    print("-" * 40)

    result = agent.disconnect()
    if result.get('success'):
        print(f"✅ Disconnected successfully")

if __name__ == "__main__":
    main()
