import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.okx import create_okx_agent

def main():
    print("OKX PUBLIC API")
    print("=" * 50)

    agent = create_okx_agent()

    print("\n1. Server time synchronization:")
    print("-" * 30)

    result = agent.get_server_time()
    if result.get('success'):
        print(f"✅ OKX Server Time: {result.get('server_time_readable')}")
        print(f"   Local Time: {result.get('local_time_readable')}")
        print(f"   Time Difference: {result.get('time_difference_formatted')}")
        print(f"   In Sync: {'✅ Yes' if result.get('server_in_sync') else '❌ No'}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n2. Spot instruments analysis:")
    print("-" * 30)

    result = agent.get_instruments(
        inst_type='SPOT'
    )

    if result.get('success'):
        print(f"✅ Found {result.get('instruments_count')} spot instruments")
        summary = result.get('summary', {})
        print(f"   Live: {summary.get('live_count')}")
        print(f"   Suspended: {summary.get('suspended_count')}")

        instruments = result.get('instruments', [])[:5]
        print(f"\n   Top 5 instruments:")
        for i, instr in enumerate(instruments, 1):
            print(f"   {i}. {instr['instId']} ({instr['state']})")
            print(f"      Min: {instr['minSz']}, Tick: {instr['tickSz']}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n3. Swap position tiers (BTC-USDT):")
    print("-" * 30)

    result = agent.get_position_tiers(
        inst_type='SWAP',
        inst_family='BTC-USDT',
        td_mode='cross'
    )

    if result.get('success'):
        print(f"✅ Found {result.get('tiers_count')} position tiers")
        summary = result.get('summary', {})
        print(f"   Unique instruments: {summary.get('unique_instruments')}")
        print(f"   Max leverage range: {summary.get('max_lever_range')}")

        if summary.get('margin_requirements'):
            margin = summary['margin_requirements']
            print(f"   IMR range: {margin.get('min_imr')} - {margin.get('max_imr')}")

        tiers = result.get('tiers', [])[:3]
        if tiers:
            print(f"\n   Top 3 tiers:")
            for i, tier in enumerate(tiers, 1):
                print(f"   {i}. Tier {tier['tier']}: Max {tier['maxLever']}x, IMR: {tier['imr_percentage']}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n4. Insurance fund analysis (BTC-USDT SWAP):")
    print("-" * 30)

    result = agent.get_insurance_fund(
        inst_type='SWAP',
        inst_family='BTC-USDT',
        limit='50'
    )

    if result.get('success'):
        print(f"✅ Found {result.get('summary', {}).get('total_funds', 0)} insurance funds")
        summary = result.get('summary', {})
        print(f"   Total amount: {summary.get('total_amount_formatted', '$0')}")
        print(f"   Currencies: {', '.join(summary.get('currencies', []))}")

        funds = result.get('insurance_funds', [])[:2]
        if funds:
            print(f"\n   Top funds:")
            for i, fund in enumerate(funds, 1):
                print(f"   {i}. {fund.get('instFamily', fund.get('instType', 'N/A'))}: {fund.get('total_formatted', '$0')}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n5. Alternative: Insurance fund with uly (ETH-USD):")
    print("-" * 30)

    result = agent.get_insurance_fund(
        inst_type='SWAP',
        uly='ETH-USD',
        limit='50'
    )

    if result.get('success'):
        print(f"✅ Found {result.get('summary', {}).get('total_funds', 0)} insurance funds")
        summary = result.get('summary', {})
        print(f"   Total amount: {summary.get('total_amount_formatted', '$0')}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n6. Get specific instrument (BTC-USDT):")
    print("-" * 30)

    result = agent.get_instruments(
        inst_type='SPOT',
        inst_id='BTC-USDT'
    )

    if result.get('success'):
        instruments = result.get('instruments', [])
        if instruments:
            instr = instruments[0]
            print(f"✅ BTC-USDT instrument details:")
            print(f"   State: {instr['state']}")
            print(f"   Base: {instr['baseCcy']}, Quote: {instr['quoteCcy']}")
            print(f"   Min size: {instr['minSz']}")
            print(f"   Tick size: {instr['tickSz']}")
            print(f"   Listed: {instr['listTimeReadable']}")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    main()
