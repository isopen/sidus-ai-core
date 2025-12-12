from formatters import print_section, format_currency, format_currency_safe
from config import ARBITRAGE_CONFIG

def analyze_arbitrage(agent):
    print_section("ARBITRAGE OPPORTUNITIES", "⚡")

    try:
        print(f"\n🔍 Searching for realistic arbitrage opportunities...")
        print(f"   Using filters: min profit ${ARBITRAGE_CONFIG['min_profit_usd']}, "
              f"min TVL ${ARBITRAGE_CONFIG['min_tvl']}, "
              f"max price diff {ARBITRAGE_CONFIG['max_price_diff']*100}%")

        arbitrage_ops = agent.find_arbitrage_opportunities(
            min_profit_usd=ARBITRAGE_CONFIG['min_profit_usd'],
            min_tvl=ARBITRAGE_CONFIG['min_tvl'],
            max_price_diff=ARBITRAGE_CONFIG['max_price_diff']
        )

        if arbitrage_ops:
            print(f"\n   ✅ Found {len(arbitrage_ops)} realistic opportunities")

            high_profit = [o for o in arbitrage_ops if o.get('net_profit_usd', 0) >= 100]
            medium_profit = [o for o in arbitrage_ops if 20 <= o.get('net_profit_usd', 0) < 100]
            low_profit = [o for o in arbitrage_ops if o.get('net_profit_usd', 0) < 20]

            print(f"\n   📊 Profit breakdown (after fees):")
            print(f"      • High (>$100): {len(high_profit)} opportunities")
            print(f"      • Medium ($20-$100): {len(medium_profit)} opportunities")
            print(f"      • Low (<$20): {len(low_profit)} opportunities")

            if arbitrage_ops:
                print(f"\n   🏆 TOP REALISTIC OPPORTUNITIES:")

                for i, opp in enumerate(arbitrage_ops[:3], 1):
                    if 'symbol_pair' in opp:
                        pair_display = opp['symbol_pair']
                    else:
                        token0_display = opp['token_pair'][0][:8] + '...' if len(opp['token_pair'][0]) > 8 else opp['token_pair'][0]
                        token1_display = opp['token_pair'][1][:8] + '...' if len(opp['token_pair'][1]) > 8 else opp['token_pair'][1]
                        pair_display = f"{token0_display}/{token1_display}"

                    print(f"\n   {i}. {pair_display}")

                    net_profit = opp.get('net_profit_usd', opp.get('estimated_profit_usd', 0))
                    price_diff = opp.get('price_difference_pct', 0)
                    trade_size = opp.get('trade_size_usd', opp.get('trade_size_estimate', 0))

                    print(f"      • Net Profit: {format_currency_safe(net_profit)}")
                    print(f"      • Price Difference: {price_diff:.2f}%")
                    print(f"      • Trade Size: {format_currency_safe(trade_size)}")

                    if 'estimated_profit_usd' in opp and 'net_profit_usd' in opp:
                        fee_est = opp['estimated_profit_usd'] - opp['net_profit_usd']
                        if fee_est > 0:
                            print(f"      • Fees (est.): {format_currency_safe(fee_est)}")

                    if 'cheap_price' in opp and 'expensive_price' in opp:
                        print(f"      • Cheap Price: {opp['cheap_price']:.6f}")
                        print(f"      • Expensive Price: {opp['expensive_price']:.6f}")

                    if 'cheap_pool_tvl' in opp and 'expensive_pool_tvl' in opp:
                        min_tvl = min(opp['cheap_pool_tvl'], opp['expensive_pool_tvl'])
                        if trade_size > 0:
                            tvl_ratio = min_tvl / trade_size
                            print(f"      • Min Pool TVL: {format_currency_safe(min_tvl)}")
                            print(f"      • TVL/Trade Ratio: {tvl_ratio:.1f}x")

                    print(f"      • Cheap Pool: {opp['cheap_pool'][:20]}...")
                    print(f"      • Expensive Pool: {opp['expensive_pool'][:20]}...")
        else:
            print(f"\n   ℹ️  No realistic arbitrage opportunities found")
            print(f"\n   💡 Suggestions for better results:")
            print(f"      1. Try lowering minimum profit to $5")
            print(f"      2. Increase max price difference to 15-20%")
            print(f"      3. Scan during high volatility periods")
            print(f"      4. Focus on major token pairs (TON/USDT, STON/USDT)")

    except Exception as e:
        print(f"   ❌ Error searching arbitrage: {e}")
        print(f"   🔧 If method doesn't support parameters, try basic search:")

        try:
            print(f"\n   🔄 Trying basic arbitrage search...")
            basic_arbitrage_ops = agent.find_arbitrage_opportunities()

            if basic_arbitrage_ops:
                print(f"\n   📊 Found {len(basic_arbitrage_ops)} opportunities (unfiltered)")
                print(f"   ⚠️  Note: Results may include unrealistic opportunities")

                realistic_count = 0
                for i, opp in enumerate(basic_arbitrage_ops[:5], 1):
                    price_diff = opp.get('price_difference_pct', 0)
                    profit = opp.get('estimated_profit_usd', 0)

                    if price_diff < 1000 and profit < 1000000:
                        realistic_count += 1
                        if realistic_count <= 2:
                            token0_display = opp['token_pair'][0][:8] + '...' if len(opp['token_pair'][0]) > 8 else opp['token_pair'][0]
                            token1_display = opp['token_pair'][1][:8] + '...' if len(opp['token_pair'][1]) > 8 else opp['token_pair'][1]

                            print(f"\n   {i}. {token0_display}/{token1_display}")
                            print(f"      • Price Difference: {price_diff:.2f}%")
                            print(f"      • Est. Profit: {format_currency_safe(profit)}")
                            print(f"      • Trade Size: {format_currency_safe(opp.get('trade_size_estimate', 0))}")

                if realistic_count == 0:
                    print(f"   ℹ️  No realistic opportunities found in basic scan")
            else:
                print(f"   ℹ️  No opportunities found")

        except Exception as e2:
            print(f"   ❌ Basic search also failed: {e2}")
