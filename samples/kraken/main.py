import os
import sys
import time
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.kraken import create_kraken_agent

def main():
    print("KRAKEN WEBSOCKET")
    print("=" * 50)

    print("Test 1: Ticker")
    print("-" * 40)

    agent = create_kraken_agent()

    result = agent.connect()
    if not result.get('success'):
        print(f"❌ Connection failed: {result.get('error')}")
        return

    print("✅ Connected")

    def simple_ticker_callback(data):
        print(f"\n📊 Ticker update received")
        data_payload = data.get('data', [])
        if data_payload:
            ticker = data_payload[0]
            print(f"   Symbol: {ticker.get('symbol', 'N/A')}")
            print(f"   Bid: {ticker.get('bid', 'N/A')}")
            print(f"   Ask: {ticker.get('ask', 'N/A')}")

    agent.register_callback("ticker/BTC/USD", simple_ticker_callback)

    result = agent.subscribe_ticker(symbols=["BTC/USD"], event_trigger="trades", snapshot=True)
    if result.get('success'):
        print("✅ Ticker subscription successful")
        print("Listening for 5 seconds...")
        time.sleep(5)

        agent.unsubscribe_ticker(symbols=["BTC/USD"])
        print("✅ Unsubscribed from ticker")
    else:
        print(f"❌ Ticker subscription failed: {result.get('error')}")

    agent.disconnect()
    print("✅ Disconnected")

    print("\n\nTest 2: Book")
    print("-" * 40)

    agent2 = create_kraken_agent()

    result = agent2.connect()
    if not result.get('success'):
        print(f"❌ Connection failed: {result.get('error')}")
        return

    print("✅ Connected")

    def simple_book_callback(data):
        print(f"\n📚 Book update received")
        data_payload = data.get('data', [])
        if data_payload:
            book = data_payload[0]
            print(f"   Symbol: {book.get('symbol', 'N/A')}")
            print(f"   Type: {data.get('type', 'N/A')}")

    agent2.register_callback("book/BTC/USD", simple_book_callback)

    for depth in [10, 25, 100]:
        print(f"\nTrying book with depth={depth}...")
        result = agent2.subscribe_book(symbols=["BTC/USD"], depth=depth, snapshot=True)
        if result.get('success'):
            print(f"✅ Book subscription successful with depth={depth}")
            print("Listening for 5 seconds...")
            time.sleep(5)

            agent2.unsubscribe_book(symbols=["BTC/USD"], depth=depth)
            print("✅ Unsubscribed from book")
            break
        else:
            print(f"❌ Book subscription failed with depth={depth}: {result.get('error')}")
            time.sleep(1)

    agent2.disconnect()
    print("✅ Disconnected")

    print("\n\nTest 3: OHLC with different intervals")
    print("-" * 40)

    agent3 = create_kraken_agent()

    result = agent3.connect()
    if not result.get('success'):
        print(f"❌ Connection failed: {result.get('error')}")
        return

    print("✅ Connected")

    def simple_ohlc_callback(data):
        print(f"\n📈 OHLC update received")
        data_payload = data.get('data', [])
        if data_payload:
            candle = data_payload[0]
            print(f"   Symbol: {candle.get('symbol', 'N/A')}")
            print(f"   Interval: {candle.get('interval', 'N/A')}m")
            print(f"   Open: {candle.get('open', 'N/A')}")
            print(f"   Close: {candle.get('close', 'N/A')}")

    agent3.register_callback("ohlc/BTC/USD/1", simple_ohlc_callback)

    for interval in [1, 5, 15]:
        print(f"\nTrying OHLC with interval={interval}...")
        result = agent3.subscribe_ohlc(symbols=["BTC/USD"], interval=interval, snapshot=True)
        if result.get('success'):
            print(f"✅ OHLC subscription successful with interval={interval}")
            print("Listening for 10 seconds...")
            time.sleep(10)

            agent3.unsubscribe_ohlc(symbols=["BTC/USD"], interval=interval)
            print("✅ Unsubscribed from OHLC")
            break
        else:
            print(f"❌ OHLC subscription failed with interval={interval}: {result.get('error')}")
            time.sleep(1)

    agent3.disconnect()
    print("✅ Disconnected")

    print("\n\nTest 4: Trades")
    print("-" * 40)

    agent4 = create_kraken_agent()

    result = agent4.connect()
    if not result.get('success'):
        print(f"❌ Connection failed: {result.get('error')}")
        return

    print("✅ Connected")

    def simple_trade_callback(data):
        print(f"\n💎 Trade update received")
        data_payload = data.get('data', [])
        print(f"   Number of trades: {len(data_payload)}")
        if data_payload:
            trade = data_payload[0]
            print(f"   Symbol: {trade.get('symbol', 'N/A')}")
            print(f"   Price: {trade.get('price', 'N/A')}")
            print(f"   Quantity: {trade.get('qty', 'N/A')}")

    agent4.register_callback("trade/BTC/USD", simple_trade_callback)

    for snapshot in [True, False]:
        print(f"\nTrying trades with snapshot={snapshot}...")
        result = agent4.subscribe_trade(symbols=["BTC/USD"], snapshot=snapshot)
        if result.get('success'):
            print(f"✅ Trade subscription successful with snapshot={snapshot}")
            print("Listening for 10 seconds...")
            time.sleep(10)

            agent4.unsubscribe_trade(symbols=["BTC/USD"])
            print("✅ Unsubscribed from trades")
            break
        else:
            print(f"❌ Trade subscription failed with snapshot={snapshot}: {result.get('error')}")
            time.sleep(1)

    agent4.disconnect()
    print("✅ Disconnected")

if __name__ == "__main__":
    main()
