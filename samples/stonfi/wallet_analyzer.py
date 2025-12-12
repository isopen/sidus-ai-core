from formatters import print_section, format_currency, get_risk_level

def analyze_wallets(agent, wallets):
    print_section("WALLET PORTFOLIO ANALYSIS", "👛")

    for wallet_name, wallet_address in wallets:
        print(f"\n🎯 Analyzing {wallet_name}...")
        print(f"   Address: {wallet_address}")

        try:
            print(f"   📥 Fetching portfolio data...")

            portfolio_analysis = agent.analyze_wallet_portfolio(wallet_address)

            if portfolio_analysis["success"]:
                portfolio = portfolio_analysis["portfolio_summary"]

                print(f"\n   📊 PORTFOLIO SUMMARY:")
                print(f"      • Total Value: {format_currency(portfolio['total_value'])}")
                print(f"      • Assets: {format_currency(portfolio['asset_value'])} ({portfolio['asset_allocation']:.1f}%)")
                print(f"      • LP Positions: {format_currency(portfolio['lp_value'])} ({portfolio['lp_allocation']:.1f}%)")
                print(f"      • Farm Positions: {format_currency(portfolio['farm_value'])} ({portfolio['farm_allocation']:.1f}%)")
                print(f"      • Diversification Score: {portfolio_analysis['diversification_score']}/100")

                risk_level, risk_desc = get_risk_level(portfolio_analysis['diversification_score'])
                print(f"\n   ⚠️  RISK ANALYSIS:")
                print(f"      • Diversification: {risk_level} - {risk_desc}")

                if portfolio['lp_allocation'] > 70:
                    print(f"      • Warning: High LP concentration ({portfolio['lp_allocation']:.1f}%)")
                if portfolio['farm_allocation'] > 50:
                    print(f"      • Warning: High farm concentration ({portfolio['farm_allocation']:.1f}%)")

            else:
                print(f"   ❌ Could not analyze portfolio: {portfolio_analysis.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"   ❌ Error analyzing wallet {wallet_name}: {e}")
