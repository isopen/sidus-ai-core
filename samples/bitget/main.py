import os
import sys
import time
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.bitget import create_bitget_agent

def ticker_callback(data):
    print(f"\n📊 Bitget Ticker:")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp_readable']}")

    ticker_data = data['data']
    if isinstance(ticker_data, list) and len(ticker_data) > 0:
        ticker = ticker_data[0]
        print(f"   Last: {ticker.get('lastPr', ticker.get('last'))}")
        print(f"   Bid: {ticker.get('bidPr', ticker.get('bid'))}")
        print(f"   Ask: {ticker.get('askPr', ticker.get('ask'))}")

def main():
    print("BITGET WEBSOCKET TEST")
    print("=" * 50)

    agent = create_bitget_agent()

    print("\n1. Connect to Bitget:")
    print("-" * 40)

    result = agent.connect()
    if result.get('success'):
        print(f"✅ Connected to Bitget")
    else:
        print(f"❌ Error: {result.get('error')}")
        return

    time.sleep(2)

    print("\n2. Register callback:")
    print("-" * 40)

    agent.register_callback("ticker/BTCUSDT", ticker_callback)

    print("\n3. Subscribe to BTCUSDT ticker (SPOT):")
    print("-" * 40)

    result = agent.subscribe_ticker(symbol="BTCUSDT")
    if result.get('success'):
        print(f"✅ Subscribed")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n4. Subscribe to BTCUSDT 1min candle:")
    print("-" * 40)

    result = agent.subscribe_kline(symbol="BTCUSDT", interval="1min")
    if result.get('success'):
        print(f"✅ Subscribed")
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n5. Check status:")
    print("-" * 40)

    result = agent.get_connections()
    if result.get('success'):
        status = result.get('status', {})
        if status.get('connected'):
            subs = status.get('subscriptions', [])
            print(f"✅ Connected, {len(subs)} subs")

    print("\n6. Waiting for data (20 seconds)...")
    print("-" * 40)

    try:
        for i in range(20):
            print(f"⏳ {i+1}/20", end='\r')
            time.sleep(1)
        print()
    except KeyboardInterrupt:
        print("\n⏹️  Stopped")

    print("\n7. Cleanup:")
    print("-" * 40)

    result = agent.disconnect()
    if result.get('success'):
        print(f"✅ Disconnected")

if __name__ == "__main__":
    main()
