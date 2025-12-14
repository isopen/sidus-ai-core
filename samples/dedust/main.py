import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))

from sidusai.plugins.dedust import DedustPlugin

def test_v2_api():
    print("TEST API v2")
    print("="*60)

    dedust = DedustPlugin()

    print("\n1. MARKET OVERVIEW v2")
    print("-"*40)

    market = dedust.get_market_overview()

    if market.get("success"):
        overview = market["market_overview"]
        print(f"Success!")
        print(f"   Total pools: {overview.get('total_pools')}")
        print(f"   Active pools: {overview.get('active_pools')}")
        print(f"   TVL: ${overview.get('total_tvl_usd', 0):,.2f}")
        print(f"   TVL (estimated): ${overview.get('estimated_total_tvl_usd', 0):,.2f}")
    else:
        print(f"Error: {market.get('error')}")

    print("\n2. POOL ANALYSIS v2")
    print("-"*40)

    pools_result = dedust.get_pools()
    if isinstance(pools_result, dict) and pools_result.get("pool_list"):
        pools = pools_result["pool_list"]
    elif isinstance(pools_result, list):
        pools = pools_result
    else:
        pools = []

    if pools:
        first_pool = pools[0]
        pool_address = first_pool.get("address") if isinstance(first_pool, dict) else None

        if pool_address:
            print(f"Analyzing pool: {pool_address[:16]}...")
            analysis = dedust.analyze_pool(pool_address)

            if analysis.get("success"):
                print(f"Success!")
                tokens = analysis.get("tokens", {})
                metrics = analysis.get("metrics", {})

                token0 = tokens.get("token0", {})
                token1 = tokens.get("token1", {})

                print(f"   Tokens: {token0.get('symbol')}/{token1.get('symbol')}")
                print(f"   TVL: ${metrics.get('tvl_usd', 0):,.2f}")
                print(f"   Type: {metrics.get('pool_type')}")
                print(f"   Fee: {metrics.get('trade_fee_percent')}%")
            else:
                print(f"Error: {analysis.get('error')}")
    else:
        print("No pool data")

    print("\n" + "="*60)
    print("TEST COMPLETED")

if __name__ == "__main__":
    test_v2_api()
