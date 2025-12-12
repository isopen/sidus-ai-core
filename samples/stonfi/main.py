import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))

from sidusai.plugins.stonfi import StonFiPlugin
from config import WALLETS, POPULAR_TOKENS, POPULAR_POOLS, SHOW_FULL_ADDRESSES
from wallet_analyzer import analyze_wallets
from token_analyzer import analyze_tokens
from pool_analyzer import analyze_pools
from farm_analyzer import analyze_farms
from arbitrage_analyzer import analyze_arbitrage
from comparison_analyzer import analyze_comparison
from dex_stats import analyze_dex_stats

def main():
    print("=" * 25)
    print("🌟 STON.FI PORTFOLIO ANALYZER")
    print("=" * 25)

    agent = StonFiPlugin()

    analyze_wallets(agent, WALLETS)
    analyze_tokens(agent, POPULAR_TOKENS)
    analyze_pools(agent, POPULAR_POOLS)
    analyze_farms(agent, POPULAR_POOLS, SHOW_FULL_ADDRESSES)
    analyze_arbitrage(agent)
    analyze_comparison(agent, POPULAR_POOLS)
    analyze_dex_stats(agent)

if __name__ == "__main__":
    main()
