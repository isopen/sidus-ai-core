import os
import sys
import time
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.mexc import create_mexc_agent

def tickers_callback(data):
    print(f"\n📊 MEXC All Tickers:")
    print(f"   Channel: {data['channel']}")
    print(f"   Time: {data['timestamp']}")

    if data['data']:
        print(f"   Number of tickers: {len(data['data'])}")

        for i, ticker in enumerate(data['data'][:3]):
            print(f"   {i+1}. {ticker.get('symbol', 'N/A')}")
            print(f"      Last: ${ticker.get('lastPrice', 'N/A'):.2f}")
            print(f"      Change: {ticker.get('riseFallRate', 'N/A'):.4%}")
            print(f"      24h Volume: {ticker.get('volume24', 'N/A')}")

def ticker_callback(data):
    print(f"\n📊 MEXC Single Ticker:")
    print(f"   Channel: {data['channel']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    ticker_data = data['data']
    if ticker_data:
        print(f"   Last Price: ${ticker_data.get('lastPrice', 'N/A'):.2f}")
        print(f"   Bid: ${ticker_data.get('bid1', 'N/A'):.2f}")
        print(f"   Ask: ${ticker_data.get('ask1', 'N/A'):.2f}")
        print(f"   24h High: ${ticker_data.get('high24Price', 'N/A'):.2f}")
        print(f"   24h Low: ${ticker_data.get('lower24Price', 'N/A'):.2f}")
        print(f"   24h Volume: {ticker_data.get('volume24', 'N/A')}")
        print(f"   Change: {ticker_data.get('riseFallRate', 'N/A'):.4%}")
        print(f"   Funding Rate: {ticker_data.get('fundingRate', 'N/A'):.6%}")
        print(f"   Open Interest: {ticker_data.get('holdVol', 'N/A')}")

def deal_callback(data):
    print(f"\n💎 MEXC Trade:")
    print(f"   Channel: {data['channel']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    trade_data = data['data']
    if trade_data:
        trades = trade_data if isinstance(trade_data, list) else [trade_data]

        for i, trade in enumerate(trades[:3]):
            side = "BUY" if trade.get('T') == 1 else "SELL"
            price = trade.get('p', 'N/A')
            quantity = trade.get('v', 'N/A')
            timestamp = trade.get('t', 'N/A')

            print(f"   Trade {i+1}:")
            print(f"      Side: {side}")
            print(f"      Price: ${price}")
            print(f"      Quantity: {quantity}")
            print(f"      Time: {timestamp}")

def depth_callback(data):
    print(f"\n📚 MEXC Orderbook Depth:")
    print(f"   Channel: {data['channel']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    depth_data = data['data']
    if depth_data:
        version = depth_data.get('version', 'N/A')
        asks = depth_data.get('asks', [])
        bids = depth_data.get('bids', [])

        print(f"   Version: {version}")

        if bids:
            print(f"   Bids (top 3):")
            for i, bid in enumerate(bids[:3]):
                if len(bid) >= 3:
                    price, orders, quantity = bid
                    print(f"     {i+1}. ${price:.2f} x {quantity} ({orders} orders)")

        if asks:
            print(f"   Asks (top 3):")
            for i, ask in enumerate(asks[:3]):
                if len(ask) >= 3:
                    price, orders, quantity = ask
                    print(f"     {i+1}. ${price:.2f} x {quantity} ({orders} orders)")

def depth_step_callback(data):
    print(f"\n📚 MEXC Orderbook Depth Step:")
    print(f"   Channel: {data['channel']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    depth_data = data['data']
    if depth_data:
        version = depth_data.get('version', 'N/A')
        ask_market_price = depth_data.get('askMarketLevelPrice', 'N/A')
        bid_market_price = depth_data.get('bidMarketLevelPrice', 'N/A')
        asks = depth_data.get('asks', [])
        bids = depth_data.get('bids', [])

        print(f"   Version: {version}")
        print(f"   Best Ask: ${ask_market_price}")
        print(f"   Best Bid: ${bid_market_price}")

        if bids:
            print(f"   Bids (top 3):")
            for i, bid in enumerate(bids[:3]):
                if len(bid) >= 3:
                    price, orders, quantity = bid
                    print(f"     {i+1}. ${price:.2f} x {quantity} ({orders} orders)")

        if asks:
            print(f"   Asks (top 3):")
            for i, ask in enumerate(asks[:3]):
                if len(ask) >= 3:
                    price, orders, quantity = ask
                    print(f"     {i+1}. ${price:.2f} x {quantity} ({orders} orders)")

def kline_callback(data):
    print(f"\n📈 MEXC Kline:")
    print(f"   Channel: {data['channel']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    kline_data = data['data']
    if kline_data:
        interval = kline_data.get('interval', 'N/A')
        open_price = kline_data.get('o', 'N/A')
        high = kline_data.get('h', 'N/A')
        low = kline_data.get('l', 'N/A')
        close = kline_data.get('c', 'N/A')
        volume = kline_data.get('q', 'N/A')
        amount = kline_data.get('a', 'N/A')
        timestamp = kline_data.get('t', 'N/A')

        print(f"   Interval: {interval}")
        print(f"   Open: ${open_price:.2f}")
        print(f"   High: ${high:.2f}")
        print(f"   Low: ${low:.2f}")
        print(f"   Close: ${close:.2f}")
        print(f"   Volume: {volume}")
        print(f"   Amount: ${amount}")
        print(f"   Start Time: {timestamp}")

def funding_rate_callback(data):
    print(f"\n💰 MEXC Funding Rate:")
    print(f"   Channel: {data['channel']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    funding_data = data['data']
    if funding_data:
        rate = funding_data.get('rate', 'N/A')
        print(f"   Funding Rate: {rate:.6%}")

def index_price_callback(data):
    print(f"\n📊 MEXC Index Price:")
    print(f"   Channel: {data['channel']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    index_data = data['data']
    if index_data:
        price = index_data.get('price', 'N/A')
        print(f"   Index Price: ${price:.2f}")

def fair_price_callback(data):
    print(f"\n⚖️  MEXC Fair Price:")
    print(f"   Channel: {data['channel']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    fair_data = data['data']
    if fair_data:
        price = fair_data.get('price', 'N/A')
        print(f"   Fair Price: ${price:.2f}")

def contract_callback(data):
    print(f"\n📄 MEXC Contract Data:")
    print(f"   Channel: {data['channel']}")
    print(f"   Symbol: {data['symbol']}")
    print(f"   Time: {data['timestamp']}")

    contract_data = data['data']
    if contract_data:
        print(f"   Contract: {contract_data.get('symbol', 'N/A')}")
        print(f"   Display Name: {contract_data.get('displayNameEn', 'N/A')}")
        print(f"   Base Coin: {contract_data.get('baseCoin', 'N/A')}")
        print(f"   Quote Coin: {contract_data.get('quoteCoin', 'N/A')}")
        print(f"   Max Leverage: {contract_data.get('maxLeverage', 'N/A')}x")
        print(f"   Taker Fee: {contract_data.get('takerFeeRate', 'N/A'):.4%}")
        print(f"   Maker Fee: {contract_data.get('makerFeeRate', 'N/A'):.4%}")
        print(f"   Min Order Size: {contract_data.get('minVol', 'N/A')}")

def main():
    print("MEXC WEBSOCKET EXAMPLE - PERPETUAL FUTURES")

    agent = create_mexc_agent()

    print("\n1. Connect to MEXC Futures:")
    print("-" * 40)

    result = agent.connect()
    if result.get('success'):
        status = result.get('status', {})
        print(f"✅ Connected to MEXC Futures")
        print(f"   Trade Type: {result.get('trade_type', 'PERPETUAL')}")
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

    print("\n2. Subscribe to all tickers:")
    print("-" * 40)

    result = agent.subscribe_tickers(gzip=False)
    if result.get('success'):
        print(f"✅ Subscribed to all tickers")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        print(f"   GZIP: {result.get('gzip', 'N/A')}")
        agent.register_callback("tickers/all", tickers_callback)
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n3. Subscribe to BTC_USDT ticker:")
    print("-" * 40)

    result = agent.subscribe_ticker(symbol="BTC_USDT", gzip=False)
    if result.get('success'):
        print(f"✅ Subscribed to BTC_USDT ticker")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        agent.register_callback("ticker/btc_usdt", ticker_callback)
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n4. Subscribe to BTC_USDT trades:")
    print("-" * 40)

    result = agent.subscribe_deal(symbol="BTC_USDT", gzip=False, compress=False)
    if result.get('success'):
        print(f"✅ Subscribed to BTC_USDT trades")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        print(f"   GZIP: {result.get('gzip', 'N/A')}")
        print(f"   Compress: {result.get('compress', 'N/A')}")
        agent.register_callback("deal/btc_usdt", deal_callback)
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n5. Subscribe to BTC_USDT orderbook depth:")
    print("-" * 40)

    result = agent.subscribe_depth(symbol="BTC_USDT", gzip=False)
    if result.get('success'):
        print(f"✅ Subscribed to BTC_USDT orderbook depth")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        agent.register_callback("depth/btc_usdt", depth_callback)
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n6. Subscribe to BTC_USDT orderbook depth step 10:")
    print("-" * 40)

    result = agent.subscribe_depth_step(symbol="BTC_USDT", step="10", gzip=False)
    if result.get('success'):
        print(f"✅ Subscribed to BTC_USDT orderbook depth step 10")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        print(f"   Step: {result.get('step', 'N/A')}")
        agent.register_callback("depth_step/btc_usdt", depth_step_callback)
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n7. Subscribe to BTC_USDT 1-minute kline:")
    print("-" * 40)

    result = agent.subscribe_kline(symbol="BTC_USDT", interval="Min1", gzip=False)
    if result.get('success'):
        print(f"✅ Subscribed to BTC_USDT 1-minute kline")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        print(f"   Interval: {result.get('interval', 'N/A')}")
        agent.register_callback("kline/btc_usdt/Min1", kline_callback)
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n8. Subscribe to BTC_USDT funding rate:")
    print("-" * 40)

    result = agent.subscribe_funding_rate(symbol="BTC_USDT", gzip=False)
    if result.get('success'):
        print(f"✅ Subscribed to BTC_USDT funding rate")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        agent.register_callback("funding_rate/btc_usdt", funding_rate_callback)
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n9. Subscribe to BTC_USDT index price:")
    print("-" * 40)

    result = agent.subscribe_index_price(symbol="BTC_USDT", gzip=False)
    if result.get('success'):
        print(f"✅ Subscribed to BTC_USDT index price")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        agent.register_callback("index_price/btc_usdt", index_price_callback)
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n10. Subscribe to BTC_USDT fair price:")
    print("-" * 40)

    result = agent.subscribe_fair_price(symbol="BTC_USDT", gzip=False)
    if result.get('success'):
        print(f"✅ Subscribed to BTC_USDT fair price")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        agent.register_callback("fair_price/btc_usdt", fair_price_callback)
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n11. Subscribe to contract data:")
    print("-" * 40)

    result = agent.subscribe_contract(gzip=False)
    if result.get('success'):
        print(f"✅ Subscribed to contract data")
        print(f"   Topic: {result.get('topic', 'N/A')}")
        agent.register_callback("contract/all", contract_callback)
    else:
        print(f"❌ Error: {result.get('error')}")

    time.sleep(1)

    print("\n12. Check connection status:")
    print("-" * 40)

    result = agent.get_connections()
    if result.get('success'):
        status = result.get('status', {})
        summary = result.get('summary', {})

        if status.get('connected'):
            print(f"✅ Connected to MEXC")
            print(f"   Total subscriptions: {summary.get('total_subscriptions', 0)}")
            print(f"   Connection Type: {summary.get('connection_type', 'PERPETUAL')}")

            subscriptions = status.get('subscriptions', [])
            if subscriptions:
                print(f"   Active subscriptions:")
                for sub in subscriptions:
                    print(f"     - {sub}")
        else:
            print(f"❌ Not connected")
    else:
        print(f"❌ Error getting connection status: {result.get('error')}")

    print("\n13. Listening for data (15 seconds)...")
    print("-" * 40)
    print("You should see real-time updates from:")
    print("  • All tickers (every 1s)")
    print("  • BTC_USDT ticker (BBO changes)")
    print("  • BTC_USDT trades (individual trades)")
    print("  • BTC_USDT orderbook depth")
    print("  • BTC_USDT orderbook depth step")
    print("  • BTC_USDT 1-minute kline")
    print("  • BTC_USDT funding rate")
    print("  • BTC_USDT index price")
    print("  • BTC_USDT fair price")
    print("  • Contract data updates")
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

    print("\n14. Test additional symbols:")
    print("-" * 40)

    symbols = ["ETH_USDT", "SOL_USDT"]
    for symbol in symbols:
        result = agent.subscribe_ticker(symbol=symbol, gzip=False)
        if result.get('success'):
            print(f"✅ Subscribed to {symbol} ticker")
            agent.register_callback(f"ticker/{symbol.lower()}", ticker_callback)

    print("\n15. Test different kline intervals:")
    print("-" * 40)

    intervals = ["Min5", "Min15", "Min30", "Hour1", "Hour4"]
    for interval in intervals:
        result = agent.subscribe_kline(
            symbol="BTC_USDT", 
            interval=interval, 
            gzip=False
        )
        if result.get('success'):
            print(f"✅ Subscribed to {interval} kline")
            agent.register_callback(f"kline/btc_usdt/{interval}", kline_callback)

    print("Listening for different intervals (5 seconds)...")
    try:
        for i in range(5):
            print(f"⏳ {i+1}/5", end='\r')
            time.sleep(1)
        print()
    except KeyboardInterrupt:
        pass

    print("\n16. Test different depth steps:")
    print("-" * 40)

    steps = ["0.0001", "0.001", "0.01", "0.1"]
    for step in steps:
        result = agent.subscribe_depth_step(
            symbol="BTC_USDT",
            step=step,
            gzip=False
        )
        if result.get('success'):
            print(f"✅ Subscribed to depth step {step}")
            agent.register_callback(f"depth_step/btc_usdt", depth_step_callback)

    print("Listening for depth steps (3 seconds)...")
    try:
        for i in range(3):
            print(f"⏳ {i+1}/3", end='\r')
            time.sleep(1)
        print()
    except KeyboardInterrupt:
        pass

    print("\n17. Cleanup and disconnect:")
    print("-" * 40)

    result = agent.disconnect()
    if result.get('success'):
        print(f"✅ Disconnected from MEXC WebSocket")
    else:
        print(f"❌ Error during disconnect: {result.get('error')}")

    print("\n" + "="*50)
    print("MEXC WEBSOCKET FEATURES DEMONSTRATED:")
    print("="*50)
    print("✓ All tickers subscription")
    print("✓ Single ticker subscription")
    print("✓ Trades with aggregation control")
    print("✓ Orderbook depth (regular and step-based)")
    print("✓ Multiple kline intervals (Min1 to Month1)")
    print("✓ Funding rate updates")
    print("✓ Index price tracking")
    print("✓ Fair price calculation")
    print("✓ Contract specifications")
    print("✓ GZIP compression control")
    print("✓ Compress trade aggregation control")
    print("✓ Real-time market data")
    print("="*50)

if __name__ == "__main__":
    main()
