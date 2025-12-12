from datetime import datetime, timedelta
from formatters import print_section, format_currency
from config import TIME_CONFIG

def analyze_dex_stats(agent):
    print_section("DEX STATISTICS", "📈")

    try:
        print(f"\n📊 Fetching STON.fi statistics...")

        dex_stats = agent.get_dex_stats(TIME_CONFIG['since'], TIME_CONFIG['until'])

        if "stats" in dex_stats:
            stats = dex_stats["stats"]
            print(f"\n   📊 24H DEX STATS:")
            print(f"      • Total Volume: {format_currency(float(stats.get('volume_usd', 0)))}")
            print(f"      • Total TVL: {format_currency(float(stats.get('tvl', 0)))}")
            print(f"      • Total Trades: {stats.get('trades', 0):,}")
            print(f"      • Unique Wallets: {stats.get('unique_wallets', 0):,}")
            print(f"      • Time Period: {dex_stats.get('since', 'N/A')} to {dex_stats.get('until', 'N/A')}")

    except Exception as e:
        print(f"   ❌ Could not fetch DEX stats: {e}")
