import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
from sidusai.plugins.dedust import create_dedust_agent

def test_v2_api():
    print("DEEP DRIVE")
    print("="*60)

    agent = create_dedust_agent()

    print("\n1. MARKET OVERVIEW v2")
    print("-"*40)

    market = agent.get_market_overview()

    if market.get("success"):
        overview = market.get("market_overview", {})
        print(f"Success!")
        print(f"   Total pools: {overview.get('total_pools')}")
        print(f"   Active pools: {overview.get('active_pools')}")
        print(f"   TVL: ${overview.get('total_tvl_usd', 0):,.2f}")
        print(f"   TVL (estimated): ${overview.get('estimated_total_tvl_usd', 0):,.2f}")
    else:
        print(f"Error: {market.get('error')}")

    print("\n2. POOLS LIST")
    print("-"*40)

    pools_result = agent.get_pools()

    if pools_result.get("success"):
        data = pools_result.get("data", {})
        if isinstance(data, dict) and "pool_list" in data:
            pools = data["pool_list"]
        elif isinstance(data, list):
            pools = data
        else:
            pools = data.get("pool_list", [])

        if pools:
            print(f"Success! Found {len(pools)} pools")

            first_pool = pools[0]
            if isinstance(first_pool, dict):
                pool_address = first_pool.get("address")
            else:
                pool_address = None

            if pool_address:
                print(f"\n3. POOL ANALYSIS v2")
                print("-"*40)
                print(f"Analyzing pool: {pool_address[:16]}...")
                analysis = agent.analyze_pool(pool_address)

                if analysis.get("success"):
                    tokens = analysis.get("tokens", {})
                    metrics = analysis.get("metrics", {})

                    token0 = tokens.get("token0", {})
                    token1 = tokens.get("token1", {})

                    print(f"Success!")
                    print(f"   Tokens: {token0.get('symbol')}/{token1.get('symbol')}")
                    print(f"   TVL: ${metrics.get('tvl_usd', 0):,.2f}")
                    print(f"   Type: {metrics.get('pool_type')}")
                    print(f"   Fee: {metrics.get('trade_fee_percent')}%")
                else:
                    print(f"Error: {analysis.get('error')}")
        else:
            print("No pool data found")
    else:
        print(f"Error: {pools_result.get('error')}")

    print("\n4. PRICES")
    print("-"*40)

    prices = agent.get_prices()

    if prices.get("success"):
        data = prices.get("data", {})
        if isinstance(data, dict) and "prices" in data:
            price_list = data["prices"]
        elif isinstance(data, list):
            price_list = data
        else:
            price_list = data.get("prices", [])

        if price_list:
            print(f"Success! {len(price_list)} prices")

            if len(price_list) > 0:
                first_price = price_list[0]
                if isinstance(first_price, dict):
                    symbol = first_price.get("symbol")
                    price = first_price.get("price")
                    print(f"   Example: {symbol} = ${price}")
    else:
        print(f"Error: {prices.get('error')}")

    print("\n" + "="*60)
    print("TEST COMPLETED")

if __name__ == "__main__":
    test_v2_api()
