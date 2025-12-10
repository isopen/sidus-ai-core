import os
import sys
import numpy as np
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
from sidusai.plugins.dyor import DYORPlugin

def print_section(title, symbol="📊"):
    print(f"\n{symbol} {'='*50}")
    print(f"{symbol} {title}")
    print(f"{symbol} {'='*50}")

def format_currency(value):
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.2f}K"
    else:
        return f"${value:.2f}"

def get_risk_level(trust_score):
    if trust_score >= 80:
        return "🟢 LOW", "Excellent trust score"
    elif trust_score >= 60:
        return "🟡 MODERATE", "Average trust score"
    elif trust_score >= 40:
        return "🟠 ELEVATED", "Below average trust score"
    else:
        return "🔴 HIGH", "Poor trust score"

def analyze_holders(holders_count):
    if holders_count >= 100_000:
        return "📈 STRONG", "Large community support"
    elif holders_count >= 10_000:
        return "📊 HEALTHY", "Good distribution"
    elif holders_count >= 1_000:
        return "⚠️  MODERATE", "Moderate distribution"
    else:
        return "🚨 CONCENTRATED", "High concentration risk"

def analyze_liquidity(liquidity_usd):
    if liquidity_usd >= 1_000_000:
        return "💧 EXCELLENT", "High liquidity"
    elif liquidity_usd >= 100_000:
        return "💧 GOOD", "Sufficient liquidity"
    elif liquidity_usd >= 10_000:
        return "⚠️  LOW", "Limited liquidity"
    else:
        return "🚨 VERY LOW", "Illiquidity risk"

def analyze_price_trend(price_data):
    if len(price_data) < 10:
        return "📊 INSUFFICIENT DATA", "Not enough data for trend analysis"

    recent_prices = price_data.tail(10)
    price_change = ((recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]) * 100

    if price_change > 10:
        return "🚀 STRONG UPTREND", f"+{price_change:.1f}% over last 10 periods"
    elif price_change > 2:
        return "📈 UPTREND", f"+{price_change:.1f}% over last 10 periods"
    elif price_change < -10:
        return "📉 STRONG DOWNTREND", f"{price_change:.1f}% over last 10 periods"
    elif price_change < -2:
        return "📉 DOWNTREND", f"{price_change:.1f}% over last 10 periods"
    else:
        return "➡️  SIDEWAYS", f"{price_change:+.1f}% change over last 10 periods"

def calculate_support_resistance(price_data):
    if len(price_data) < 20:
        return [], []

    window = min(20, len(price_data))
    support_levels = []
    resistance_levels = []

    for i in range(window, len(price_data) - window):
        local_min = price_data.iloc[i-window:i+window].min()
        local_max = price_data.iloc[i-window:i+window].max()

        if price_data.iloc[i] == local_min:
            support_levels.append(price_data.iloc[i])
        elif price_data.iloc[i] == local_max:
            resistance_levels.append(price_data.iloc[i])

    support_levels = sorted(list(set(support_levels)))
    resistance_levels = sorted(list(set(resistance_levels)))

    return support_levels[-3:], resistance_levels[-3:]

def main():
    print("=" * 21)
    print("🌟 TOKEN DEEP DRIVE")
    print("=" * 21)

    API_KEY = os.environ.get('DYOR_API_KEY')

    if not API_KEY:
        print("⚠️  Running in public mode (rate limited)")
    else:
        print(f"🔑 API Key: {API_KEY[:8]}...")

    agent = DYORPlugin(api_key=API_KEY)

    jettons_to_analyze = [
        ("STON", "EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO"),
        ("NOT", "EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT"),
        ("USDT", "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"),
        ("GRAM", "EQC47093oX5Xhb0xuk2lCr2RhS8rj-vul61u4W2UH5ORmG_O"),
        ("EVAA", "EQBKMfjX_a_dsOLm-juxyVZytFP7_KKnzGv6J01kGc72gVBp")
    ]

    for token_name, token_address in jettons_to_analyze:
        print(f"\n🎯 Analyzing {token_name}...")
        print(f"   Address: {token_address[:20]}...")

        try:
            print(f"   📥 Fetching data...")

            jetton_data = agent.get_jetton(token_address)
            metrics_data = agent.get_jetton_metrics(token_address)

            if 'details' in jetton_data:
                details = jetton_data['details']
                metadata = details.get('metadata', {})

                price_usd = agent.components._format_value(metrics_data.get('metrics', {}).get('priceUsd', {}))
                mcap_usd = agent.components._format_value(metrics_data.get('metrics', {}).get('mcap', {}))
                liquidity_usd = agent.components._format_value(metrics_data.get('metrics', {}).get('liquidityUsd', {}))
                holders_count = int(metrics_data.get('metrics', {}).get('holdersCount', '0'))
                trust_score = metrics_data.get('metrics', {}).get('trustScore', 0)

                print(f"\n   📊 TOKEN METRICS:")
                print(f"      • Name: {metadata.get('name', token_name)}")
                print(f"      • Symbol: {metadata.get('symbol', 'UNKNOWN')}")
                print(f"      • Price: ${price_usd:.6f}")
                print(f"      • Market Cap: {format_currency(mcap_usd)}")
                print(f"      • Liquidity: {format_currency(liquidity_usd)}")
                print(f"      • Holders: {holders_count:,}")
                print(f"      • Trust Score: {trust_score}/100")

                risk_level, risk_desc = get_risk_level(trust_score)
                holders_level, holders_desc = analyze_holders(holders_count)
                liquidity_level, liquidity_desc = analyze_liquidity(liquidity_usd)

                print(f"\n   ⚠️  RISK ANALYSIS:")
                print(f"      • Trust: {risk_level} - {risk_desc}")
                print(f"      • Distribution: {holders_level} - {holders_desc}")
                print(f"      • Liquidity: {liquidity_level} - {liquidity_desc}")

            print(f"\n   📈 TECHNICAL ANALYSIS:")

            price_df = agent.components.fetch_price_data(token_address, limit=50)

            if not price_df.empty:
                trend_level, trend_desc = analyze_price_trend(price_df['price'])
                print(f"      • Trend: {trend_level} - {trend_desc}")

                supports, resistances = calculate_support_resistance(price_df['price'])
                if supports:
                    print(f"      • Support Levels: ${supports[0]:.6f}, ${supports[1] if len(supports) > 1 else supports[0]:.6f}")
                if resistances:
                    print(f"      • Resistance Levels: ${resistances[0]:.6f}, ${resistances[1] if len(resistances) > 1 else resistances[0]:.6f}")

                if len(price_df) >= 20:
                    returns = price_df['price'].pct_change()
                    volatility = returns.std() * np.sqrt(365) * 100
                    vol_level = "🟢 LOW" if volatility < 50 else "🟡 MODERATE" if volatility < 100 else "🔴 HIGH"
                    print(f"      • Volatility: {vol_level} ({volatility:.1f}% annualized)")

            print(f"\n   🏪 MARKET ANALYSIS:")
            try:
                markets = agent.get_jetton_markets(token_address)
                if 'markets' in markets and markets['markets']:
                    print(f"      • Available on {len(markets['markets'])} DEXs")
                    for market in markets['markets'][:3]:
                        exchange = market.get('exchangeId', 'Unknown')
                        liquidity = agent.components._format_value(market.get('liquidity', {}).get('usd', {}))
                        print(f"        - {exchange}: {format_currency(liquidity)} liquidity")
                else:
                    print(f"      • No market data available")
            except:
                print(f"      • Market data unavailable")

            print(f"\n   📋 GENERATING REPORT...")
            try:
                report = agent.generate_report(token_address)

                lines = report.split('\n')
                print("\n   📄 REPORT SUMMARY:")
                print("   " + "="*40)

                key_lines = []
                for line in lines:
                    if any(keyword in line for keyword in ['TOKEN:', 'Price:', 'Market Cap:', 'Holders:', 'Trust Score:',
                                                          'RSI:', 'MACD:', 'Trend:', 'Volatility:']):
                        if line.strip():
                            key_lines.append(line.strip())

                for line in key_lines[:10]:
                    print(f"   {line}")

                print("   " + "="*40)

            except Exception as e:
                print(f"   ❌ Could not generate report: {e}")

            print(f"\n   ✅ {token_name} analysis completed!")
            print(f"   {'─'*40}")

        except Exception as e:
            print(f"   ❌ Error analyzing {token_name}: {e}")
            continue

    print_section("COMPARATIVE ANALYSIS", "⚖️")

    print("\n🔍 Comparative Metrics:")
    print("Token            | Price     | Market Cap | Holders   | Trust Score")
    print("─────────────────┼───────────┼────────────┼───────────┼────────────")

    comparative_data = []
    for token_name, token_address in jettons_to_analyze:
        try:
            metrics = agent.get_jetton_metrics(token_address)
            if 'metrics' in metrics:
                m = metrics['metrics']
                price = agent.components._format_value(m.get('priceUsd', {}))
                mcap = agent.components._format_value(m.get('mcap', {}))
                holders = m.get('holdersCount', '0')
                trust = m.get('trustScore', 0)

                comparative_data.append({
                    'name': token_name,
                    'price': price,
                    'mcap': mcap,
                    'holders': int(holders),
                    'trust': trust
                })

                print(f"{token_name:15} | ${price:8.6f} | {format_currency(mcap):10} | {int(holders):9,} | {trust:11}/100")
        except:
            print(f"{token_name:15} | {'N/A':9} | {'N/A':10} | {'N/A':9} | {'N/A':11}")

    if comparative_data:
        print("\n📊 SUMMARY:")
        total_mcap = sum(item['mcap'] for item in comparative_data)
        total_holders = sum(item['holders'] for item in comparative_data)
        avg_trust = sum(item['trust'] for item in comparative_data) / len(comparative_data)

        print(f"• Total Market Cap Analyzed: {format_currency(total_mcap)}")
        print(f"• Total Holders: {total_holders:,}")
        print(f"• Average Trust Score: {avg_trust:.1f}/100")

    print_section("RECOMMENDATIONS", "💡")

    print("\n🎯 Based on analysis:")
    print("1. 📈 Monitor high-trust tokens for long-term opportunities")
    print("2. ⚠️  Be cautious with low-liquidity tokens")
    print("3. 🔍 Look for tokens with growing holder bases")
    print("4. 💧 Prioritize tokens with strong DEX liquidity")
    print("5. 📊 Always verify with multiple data sources")

    print("\n📡 Data Sources:")
    print("• DYOR.io API - Real-time TON blockchain data")
    print("• Historical price data for technical analysis")
    print("• On-chain metrics for fundamental analysis")

    print("\n⚠️  Limitations:")
    print("• Rate limited API (2+ seconds between requests)")
    print("• Historical data may be limited")
    print("• Market conditions can change rapidly")

if __name__ == "__main__":
    main()
