import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.stonfi import create_stonfi_agent

def main():
    print("DEEP DRIVE")
    print("=" * 50)

    agent = create_stonfi_agent()

    print("\n1. Token analysis:")
    print("-" * 30)

    agent.analyze_token(
        token_address="EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"
    )

    print("\n2. Swap simulation:")
    print("=" * 35)

    agent.simulate_swap(
        offer_address="EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c",
        ask_address="EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs",
        units="1000000000",
        slippage_tolerance=0.01,
        simulate_both_directions=True
    )

    print("\n3. Detailed wallet analysis:")
    print("=" * 45)

    agent.analyze_portfolio(
        wallet_address="UQDYzZmfsrGzhObKJUw4gzdeIxEai3jAFbiGKGwxvxHinf4K",
        include_assets=True,
        include_pools=True,
        include_farms=True,
        include_stakes=True,
        min_asset_value=0.01,
        group_by_category=True
    )

    print("\n6. Arbitrage opportunity search:")
    print("-" * 45)

    sample_tokens = [
        "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs",
        "EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT",
        "EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO",
        "EQCvxJy4eG8hyHBFsZ7eePxrRsUQSFE_jpptRAYBmcG_DOGS",
        "EQA1EIDrR33zgL21rwDIfGo7h4ETWieentUvg7jIT-3aP5GG",
        "EQBaCgUwOoc6gHCNln_oJzb0mVs79YG7wYoavh-o1ItaneLA",
        "EQBZ_cafPyDr5KUTs0aNxh0ZTDhkpEZONmLJA2SNGlLm4Cko",
        "EQBsosmcZrD6FHijA7qWGLw5wo_aH8UN435hi935jJ_STORM",
        "EQBKMfjX_a_dsOLm-juxyVZytFP7_KKnzGv6J01kGc72gVBp",
        "EQAIb6KmdfdDR7CN1GBqVJuP25iCnLKCvBlJ07Evuu2dzP5f",
        "EQA1R_LuQCLHlMgOo1S4G7Y7W1cd0FrAkbA10Zq7rddKxi9k",
        "EQBCDdOHy1Ub6gN1OUd2PpJ8yswkzBsVg56Fi9L8PKSlFkdt",
        "EQBKVUJEjjBBSwU2DKTIMD6-nVHR8Ipxh_RdxwjtNIbR0OIw"
    ]

    agent.find_arbitrage(
        base_token="EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c",
        tokens_to_analyze=sample_tokens,
        min_profit_percentage=0.1,
        max_tokens_to_analyze=50,
        min_pool_liquidity=1000,
        max_route_length=3
    )

if __name__ == "__main__":
    main()