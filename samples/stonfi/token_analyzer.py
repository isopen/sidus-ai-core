from formatters import print_section, format_currency, get_risk_level, get_liquidity_level

def analyze_tokens(agent, tokens):
    print_section("TOKEN ANALYSIS", "💰")

    for token_name, token_address in tokens:
        print(f"\n🎯 Analyzing {token_name}...")
        print(f"   Address: {token_address}")

        try:
            print(f"   📥 Fetching token data...")

            asset_analysis = agent.analyze_asset(token_address)

            if asset_analysis["success"]:
                print(f"\n   📊 TOKEN METRICS:")
                print(f"      • Name: {asset_analysis.get('name', token_name)}")
                print(f"      • Symbol: {asset_analysis.get('symbol', 'UNKNOWN')}")
                print(f"      • Price: ${asset_analysis['price']['value']:.6f}")
                print(f"      • Market Cap: {format_currency(asset_analysis['metrics']['market_cap'])}")
                print(f"      • Price Source: {asset_analysis['price']['source']}")
                print(f"      • Trust Score: {asset_analysis['metrics']['popularity']}/100")

                risk_level, risk_desc = get_risk_level(asset_analysis.get('health_score', 0))
                liquidity_level, liquidity_desc = get_liquidity_level(asset_analysis.get('liquidity_usd', 0))

                print(f"\n   ⚠️  RISK ANALYSIS:")
                print(f"      • Health Score: {risk_level} - {risk_desc}")
                print(f"      • Liquidity: {liquidity_level} - {liquidity_desc}")

                flags = asset_analysis.get('flags', {})
                if flags.get('blacklisted', False):
                    print(f"      • ⚠️  BLACKLISTED - Token is blacklisted")
                if flags.get('deprecated', False):
                    print(f"      • ⚠️  DEPRECATED - Token is deprecated")
                if flags.get('community', False):
                    print(f"      • ✅ COMMUNITY - Community token")

            else:
                print(f"   ❌ Could not analyze token: {asset_analysis.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"   ❌ Error analyzing token {token_name}: {e}")
