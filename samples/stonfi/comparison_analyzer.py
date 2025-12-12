from formatters import print_section, format_currency

def analyze_comparison(agent, pools):
    print_section("COMPARATIVE ANALYSIS", "📊")

    try:
        print(f"\n🔍 Comparing top pools...")

        pool_addresses = [addr for _, addr in pools]
        comparison = agent.compare_pools(pool_addresses)

        if "summary" in comparison:
            summary = comparison["summary"]
            print(f"\n   📊 POOLS COMPARISON:")
            print(f"      • Total Pools: {summary['total_pools']}")
            print(f"      • Successfully Analyzed: {summary['successful_analyses']}")
            print(f"      • Best by TVL: {summary['best_by_tvl'][:20]}...")
            print(f"      • Best by Volume: {summary['best_by_volume'][:20]}...")
            print(f"      • Best by APY: {summary['best_by_apy'][:20]}...")
            print(f"      • Average TVL: {format_currency(summary['average_tvl'])}")
            print(f"      • Average APY: {summary['average_apy']:.2f}%")

    except Exception as e:
        print(f"   ❌ Error in comparison: {e}")
