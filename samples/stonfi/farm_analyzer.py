from formatters import print_section, format_currency, get_apy_level
import json

def analyze_farms(agent, pools, show_full_addresses=False):
    print_section("FARMING ANALYSIS", "🌾")

    all_farms_info = []

    for pool_name, pool_address in pools:
        print(f"\n🎯 Finding farms for {pool_name}...")

        try:
            farms_data = agent.get_farms_by_pool(pool_address)

            if "farm_list" in farms_data and farms_data["farm_list"]:
                farms = farms_data["farm_list"][:5]

                print(f"   📊 Found {len(farms_data['farm_list'])} farms")

                pool_total_locked = 0
                pool_total_rewards = 0
                active_farms = 0

                for i, farm in enumerate(farms, 1):
                    farm_address = farm.get("address", "")
                    apy_str = farm.get("apy", "0")

                    try:
                        apy = float(apy_str)
                    except:
                        apy = 0.0

                    status = farm.get("status", "Unknown")

                    farm_info = {
                        "pool": pool_name,
                        "status": status,
                        "apy": apy,
                        "address": farm_address,
                        "locked_lp": float(farm.get("locked_total_lp", "0")),
                        "locked_lp_usd": float(farm.get("locked_total_lp_usd", "0"))
                    }

                    if status.lower() in ["operational", "active"]:
                        active_farms += 1
                        pool_total_locked += farm_info["locked_lp_usd"]

                    print(f"\n   {i}. Farm Analysis:")

                    if status.lower() == "operational":
                        status_icon = "🟢"
                    elif status.lower() == "retired":
                        status_icon = "🔴"
                    elif status.lower() == "active":
                        status_icon = "🟡"
                    else:
                        status_icon = "⚪"

                    print(f"      • {status_icon} Status: {status}")

                    apy_level, apy_desc = get_apy_level(apy * 100)
                    print(f"      • APY: {apy:.4%} {apy_level}")
                    print(f"      • APY Rating: {apy_desc}")

                    if farm_info["locked_lp_usd"] > 0:
                        print(f"      • Locked Liquidity: {format_currency(farm_info['locked_lp_usd'])}")
                        print(f"      • Locked LP Tokens: {farm_info['locked_lp']:,.2f}")

                    if show_full_addresses:
                        print(f"      • Address: {farm_address}")
                    else:
                        if len(farm_address) > 30:
                            print(f"      • Address: {farm_address[:15]}...{farm_address[-15:]}")
                        else:
                            print(f"      • Address: {farm_address}")

                    try:
                        apy_breakdown = agent.calculate_apy_breakdown(farm_address)
                        if apy_breakdown["success"]:
                            breakdown = apy_breakdown["apy_breakdown"]

                            print(f"\n      📊 APY BREAKDOWN:")
                            print(f"         • Total APY: {breakdown['total_apy']:.2f}%")
                            print(f"         • Rewards APY: {breakdown['calculated_apy']:.2f}%")
                            print(f"         • Pool APY: {breakdown['pool_apy']:.2f}%")

                            reported_apy = breakdown.get('reported_apy', apy * 100)
                            diff = breakdown['total_apy'] - reported_apy
                            if abs(diff) > 0.1:
                                diff_text = f"{diff:+.2f}%" if diff > 0 else f"{diff:.2f}%"
                                print(f"         • Difference from reported: {diff_text}")

                            if 'staking_metrics' in apy_breakdown:
                                staking = apy_breakdown['staking_metrics']

                                print(f"\n      💰 STAKING METRICS:")
                                if 'locked_lp_usd' in staking and staking['locked_lp_usd'] > 0:
                                    print(f"         • Locked Value: {format_currency(staking['locked_lp_usd'])}")

                                if 'total_rewards_value' in staking and staking['total_rewards_value'] > 0:
                                    print(f"         • Total Rewards Value: {format_currency(staking['total_rewards_value'])}")

                                if 'min_stake_duration' in staking and staking['min_stake_duration']:
                                    try:
                                        days = int(staking['min_stake_duration']) // 86400
                                        if days > 0:
                                            print(f"         • Min Stake Duration: {days} days")
                                    except:
                                        pass

                                pool_total_rewards += staking.get('total_rewards_value', 0)

                            if 'rewards' in apy_breakdown and apy_breakdown['rewards']:
                                rewards = apy_breakdown['rewards']
                                print(f"\n      🎁 REWARDS ({len(rewards)} tokens):")

                                for reward in rewards[:3]:
                                    token_addr = reward.get('token_address', 'Unknown')[:8] + '...'
                                    daily = reward.get('daily_reward', 0)
                                    annual = reward.get('annual_value', 0)

                                    if daily > 0:
                                        print(f"         • {token_addr}: {daily:.4f}/day (~{format_currency(annual)}/year)")

                    except Exception as apy_error:
                        error_msg = str(apy_error)
                        if len(error_msg) > 50:
                            error_msg = error_msg[:50] + "..."
                        print(f"      • 📊 APY Details: Not available ({error_msg})")

                    try:
                        farm_details = agent.get_farm(farm_address)
                        if "farm" in farm_details:
                            farm_data = farm_details["farm"]

                            if "create_timestamp" in farm_data:
                                create_date = farm_data["create_timestamp"][:10]
                                print(f"      • 📅 Created: {create_date}")

                            if "owner_address" in farm_data:
                                owner = farm_data["owner_address"][:10] + "..."
                                print(f"      • 👤 Owner: {owner}")

                            if "custodian_address" in farm_data:
                                custodian = farm_data["custodian_address"][:10] + "..."
                                print(f"      • 🏛️  Custodian: {custodian}")

                    except:
                        pass

                    if i < len(farms):
                        print(f"      {'─'*40}")

                    all_farms_info.append(farm_info)

                print(f"\n   📈 POOL FARMING SUMMARY:")
                print(f"      • Active farms: {active_farms}/{len(farms)}")
                print(f"      • Total locked: {format_currency(pool_total_locked)}")
                print(f"      • Total rewards value: {format_currency(pool_total_rewards)}")

                if pool_total_locked > 0:
                    weighted_sum = 0
                    for f in all_farms_info:
                        if f['pool'] == pool_name and f['locked_lp_usd'] > 0:
                            weighted_sum += f['apy'] * f['locked_lp_usd']

                    avg_apy = weighted_sum / pool_total_locked if pool_total_locked > 0 else 0
                    print(f"      • Weighted avg APY: {avg_apy:.2%}")

            else:
                print(f"   ℹ️  No farms found for this pool")

        except Exception as e:
            print(f"   ❌ Error finding farms: {e}")

    if all_farms_info:
        print_section("OVERALL FARMING SUMMARY", "📊")

        total_farms = len(all_farms_info)
        active_farms = len([f for f in all_farms_info if f['status'].lower() in ['operational', 'active']])
        retired_farms = len([f for f in all_farms_info if f['status'].lower() == 'retired'])
        total_locked = sum(f['locked_lp_usd'] for f in all_farms_info)

        print(f"\n   🌐 TOTAL FARMING OVERVIEW:")
        print(f"      • Total farms analyzed: {total_farms}")
        if total_farms > 0:
            print(f"      • Active farms: {active_farms} ({active_farms/total_farms*100:.1f}%)")
            print(f"      • Retired farms: {retired_farms} ({retired_farms/total_farms*100:.1f}%)")
        print(f"      • Total locked value: {format_currency(total_locked)}")

        if total_locked > 0:
            weighted_apy = sum(f['apy'] * f['locked_lp_usd'] for f in all_farms_info) / total_locked
            apy_level, apy_desc = get_apy_level(weighted_apy * 100)
            print(f"      • Weighted avg APY: {weighted_apy:.2%} {apy_level}")

        active_farms_list = [f for f in all_farms_info if f['status'].lower() in ['operational', 'active']]
        if active_farms_list:
            farms_sorted_by_apy = sorted(active_farms_list, key=lambda x: x['apy'], reverse=True)
            print(f"\n   🏆 TOP ACTIVE FARMS BY APY:")
            for i, farm in enumerate(farms_sorted_by_apy[:3], 1):
                print(f"      {i}. {farm['pool']}: {farm['apy']:.2%} ({farm['status']})")

        active_farms_with_locked = [f for f in active_farms_list if f['locked_lp_usd'] > 0]
        if active_farms_with_locked:
            farms_sorted_by_locked = sorted(active_farms_with_locked, 
                                          key=lambda x: x['locked_lp_usd'], reverse=True)
            print(f"\n   💰 TOP ACTIVE FARMS BY LOCKED VALUE:")
            for i, farm in enumerate(farms_sorted_by_locked[:3], 1):
                print(f"      {i}. {farm['pool']}: {format_currency(farm['locked_lp_usd'])}")

        print(f"\n   📊 STATUS DISTRIBUTION:")
        status_counts = {}
        for farm in all_farms_info:
            status = farm['status'].lower()
            status_counts[status] = status_counts.get(status, 0) + 1

        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
            if total_farms > 0:
                percentage = count / total_farms * 100
            else:
                percentage = 0

            if status == "operational":
                icon = "🟢"
            elif status == "retired":
                icon = "🔴"
            elif status == "active":
                icon = "🟡"
            else:
                icon = "⚪"
            print(f"      • {icon} {status.title()}: {count} ({percentage:.1f}%)")

        print(f"\n   💡 FARMING RECOMMENDATIONS:")

        if active_farms > 0:
            highest_apy_farm = None
            highest_apy = 0

            for farm in active_farms_list:
                if farm['apy'] > highest_apy:
                    highest_apy = farm['apy']
                    highest_apy_farm = farm

            if highest_apy_farm:
                print(f"      1. 🏆 Highest APY: {highest_apy_farm['pool']} ({highest_apy_farm['apy']:.2%})")

            most_liquid_farm = None
            most_liquid_value = 0

            for farm in active_farms_list:
                if farm['locked_lp_usd'] > most_liquid_value:
                    most_liquid_value = farm['locked_lp_usd']
                    most_liquid_farm = farm

            if most_liquid_farm and most_liquid_farm['locked_lp_usd'] > 10000:
                print(f"      2. 💧 Most liquid: {most_liquid_farm['pool']} ({format_currency(most_liquid_farm['locked_lp_usd'])})")

        if retired_farms > 0:
            print(f"      3. ⚠️  Avoid {retired_farms} retired farm(s)")

        print(f"\n      4. 📈 General tips:")
        print(f"         • Check farm status before investing")
        print(f"         • Monitor reward distribution")
        print(f"         • Consider lock-up periods")
        print(f"         • Diversify across multiple farms")
        print(f"         • Calculate impermanent loss risks")
