from formatters import (
    print_section, format_currency, 
    get_apy_level, get_volume_level, analyze_pool_health
)

def analyze_pools(agent, pools):
    print_section("POOL ANALYSIS", "💧")

    for pool_name, pool_address in pools:
        print(f"\n🎯 Analyzing {pool_name} Pool...")
        print(f"   Address: {pool_address}")

        try:
            print(f"   📥 Fetching pool data...")

            pool_analysis = agent.analyze_pool(pool_address)

            if pool_analysis["success"]:
                print(f"\n   📊 POOL METRICS:")
                print(f"      • Tokens: {pool_analysis['tokens'][0][:10]}... / {pool_analysis['tokens'][1][:10]}...")
                print(f"      • TVL: {format_currency(pool_analysis['tvl_usd'])}")
                print(f"      • 24h Volume: {format_currency(pool_analysis['volume_24h_usd'])}")
                print(f"      • Volume/TVL Ratio: {(pool_analysis['volume_24h_usd']/pool_analysis['tvl_usd'])*100 if pool_analysis['tvl_usd'] > 0 else 0:.2f}%")
                print(f"      • Total Fee: {pool_analysis['fees']['total_fee']:.2f}%")

                apy_30d = pool_analysis['apy']['30d']
                apy_level, apy_desc = get_apy_level(apy_30d)
                volume_ratio = pool_analysis['volume_24h_usd'] / pool_analysis['tvl_usd'] if pool_analysis['tvl_usd'] > 0 else 0
                volume_level, volume_desc = get_volume_level(volume_ratio)
                health_level, health_desc = analyze_pool_health(pool_analysis)

                print(f"\n   💰 YIELD ANALYSIS:")
                print(f"      • APY (30d): {apy_level} - {apy_30d:.2f}%")
                print(f"      • Activity: {volume_level} - {volume_desc}")
                print(f"      • Pool Health: {health_level} - {health_desc}")

                print(f"\n   🪙 LP TOKEN ANALYSIS:")
                print(f"      • LP Price: ${pool_analysis['lp_metrics']['price_usd']:.6f}")
                print(f"      • LP Value: ${pool_analysis['lp_metrics']['value']:.6f}")
                print(f"      • Total Supply: {pool_analysis['lp_metrics']['total_supply']:,.0f}")

                if pool_analysis['deprecated']:
                    print(f"      • ⚠️  WARNING: Pool is DEPRECATED")

            else:
                print(f"   ❌ Could not analyze pool: {pool_analysis.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"   ❌ Error analyzing pool {pool_name}: {e}")
