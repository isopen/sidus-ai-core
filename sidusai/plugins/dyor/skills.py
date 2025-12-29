from typing import Dict, Any, List
from datetime import datetime
import numpy as np

def get_jetton_analysis_skill(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Starting jetton analysis skill...")

    address = context.get('address')

    try:
        client = context.get('dyor_client')

        if not client:
            return {"success": False, "error": "DYOR client not available"}

        try:
            jetton_data = client.get_jetton(address)
            metrics_data = client.get_jetton_metrics(address)

            if 'details' in jetton_data:
                jetton = jetton_data['details']
            else:
                jetton = {}

            if 'metrics' in metrics_data:
                metrics = metrics_data['metrics']
            else:
                metrics = {}

            holders_count = metrics.get('holdersCount', '0')
            try:
                holders = int(holders_count)
            except:
                holders = 0

            price_usd = client._format_value(metrics.get('priceUsd', {}))
            mcap_usd = client._format_value(metrics.get('mcap', {}))
            liquidity_usd = client._format_value(metrics.get('liquidityUsd', {}))
            trust_score = metrics.get('trustScore', 0)

            analysis_result = {
                'success': True,
                'address': address,
                'name': jetton.get('metadata', {}).get('name', 'Unknown'),
                'symbol': jetton.get('metadata', {}).get('symbol', 'UNKNOWN'),
                'description': jetton.get('metadata', {}).get('description', ''),
                'image_url': jetton.get('metadata', {}).get('image', ''),
                'price_usd': price_usd,
                'price_formatted': f"${price_usd:.6f}" if price_usd else "N/A",
                'market_cap_usd': mcap_usd,
                'market_cap_formatted': f"${mcap_usd:,.0f}" if mcap_usd else "N/A",
                'holders': holders,
                'holders_formatted': f"{holders:,}",
                'liquidity_usd': liquidity_usd,
                'liquidity_formatted': f"${liquidity_usd:,.0f}" if liquidity_usd else "N/A",
                'trust_score': trust_score,
                'trust_score_formatted': f"{trust_score}/100",
                'created_at': jetton.get('createdAt', ''),
                'timestamp': datetime.now().isoformat()
            }

            print(f"✅ Jetton analysis: {analysis_result['name']} ({analysis_result['symbol']})")
            print(f"   Price: {analysis_result['price_formatted']}")
            print(f"   Market Cap: {analysis_result['market_cap_formatted']}")
            print(f"   Holders: {analysis_result['holders_formatted']}")
            print(f"   Trust Score: {analysis_result['trust_score_formatted']}")

            return analysis_result

        except Exception as e:
            print(f"Error getting jetton info: {e}")
            return {
                "success": False,
                "error": f"Failed to get jetton info: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        print(f"Error in jetton analysis: {e}")
        return {
            "success": False,
            "error": f"Jetton analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def analyze_technical_skill(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Starting technical analysis skill...")

    address = context.get('address')

    try:
        client = context.get('dyor_client')

        if not client:
            return {"success": False, "error": "DYOR client not available"}

        results = {}

        try:
            df = client.fetch_price_data(address, limit=100)
            if len(df) < 15:
                rsi_result = {'success': False, 'error': 'Insufficient data for RSI'}
            else:
                delta = df['price'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = float(rsi.iloc[-1])

                signal = "NEUTRAL"
                if current_rsi > 70:
                    signal = "OVERBOUGHT"
                elif current_rsi < 30:
                    signal = "OVERSOLD"

                rsi_result = {
                    'success': True,
                    'current_rsi': round(current_rsi, 2),
                    'signal': signal,
                    'period': 14
                }
                print(f"   RSI: {current_rsi:.1f} ({signal})")
        except Exception as e:
            rsi_result = {'success': False, 'error': str(e)}

        if rsi_result['success']:
            results['rsi'] = rsi_result

        try:
            df = client.fetch_price_data(address, limit=100)
            if len(df) < 26:
                macd_result = {'success': False, 'error': 'Insufficient data for MACD'}
            else:
                ema_fast = df['price'].ewm(span=12, adjust=False).mean()
                ema_slow = df['price'].ewm(span=26, adjust=False).mean()
                macd_line = ema_fast - ema_slow
                signal_line = macd_line.ewm(span=9, adjust=False).mean()
                histogram = macd_line - signal_line

                current_macd = float(macd_line.iloc[-1])
                current_signal = float(signal_line.iloc[-1])
                current_histogram = float(histogram.iloc[-1])

                signal = "NEUTRAL"
                if current_macd > current_signal and current_histogram > 0:
                    signal = "BULLISH"
                elif current_macd < current_signal and current_histogram < 0:
                    signal = "BEARISH"

                macd_result = {
                    'success': True,
                    'current_macd': round(current_macd, 6),
                    'current_signal': round(current_signal, 6),
                    'histogram': round(current_histogram, 6),
                    'signal': signal
                }
                print(f"   MACD: {signal}")
        except Exception as e:
            macd_result = {'success': False, 'error': str(e)}

        if macd_result['success']:
            results['macd'] = macd_result

        try:
            df = client.fetch_price_data(address, limit=100)
            if len(df) < 20:
                volatility_result = {'success': False, 'error': 'Insufficient data for volatility'}
            else:
                returns = df['price'].pct_change()
                volatility = returns.rolling(window=20).std() * np.sqrt(365)
                current_volatility = float(volatility.iloc[-1])

                volatility_result = {
                    'success': True,
                    'volatility': round(current_volatility, 4)
                }

                if current_volatility is not None and not np.isnan(current_volatility):
                    volatility_result['volatility_percent'] = f"{current_volatility:.2%}"
                    print(f"   Volatility: {current_volatility:.2%}")
                else:
                    volatility_result['volatility_percent'] = "Insufficient data"
                    print(f"   Volatility: insufficient data")

        except Exception as e:
            volatility_result = {'success': False, 'error': str(e)}

        if volatility_result['success']:
            results['volatility'] = volatility_result

        result = {
            "success": True,
            "technical_indicators": results,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Technical analysis completed")

        return result

    except Exception as e:
        print(f"Error in technical analysis: {e}")
        return {
            "success": False,
            "error": f"Technical analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def generate_report_skill(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Starting report generation skill...")

    address = context.get('address')

    try:
        client = context.get('dyor_client')

        if not client:
            return {"success": False, "error": "DYOR client not available"}

        analysis = get_jetton_analysis_skill({'dyor_client': client, 'address': address})

        if not analysis.get('success'):
            return analysis

        technical = analyze_technical_skill({'dyor_client': client, 'address': address})
        technical_indicators = technical.get('technical_indicators', {}) if technical.get('success') else {}

        try:
            holders_data = client.get_jetton_holders(address)
            if 'items' in holders_data:
                total_holders = len(holders_data['items'])
            else:
                total_holders = 0
        except:
            total_holders = 0

        try:
            markets_data = client.get_jetton_markets(address)
            markets = markets_data.get('items', []) if markets_data else []
        except:
            markets = []

        report_text = generate_report_text(analysis, technical_indicators, total_holders, markets)

        report = {
            "success": True,
            "address": address,
            "name": analysis.get('name'),
            "symbol": analysis.get('symbol'),
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "technical_analysis": technical_indicators,
            "holders_count": total_holders,
            "markets": markets[:3] if markets else [],
            "report_text": report_text
        }

        print(f"✅ Report generated for {analysis['name']} ({analysis['symbol']})")

        return report

    except Exception as e:
        print(f"Error in report generation: {e}")
        return {
            "success": False,
            "error": f"Report generation failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def generate_report_text(analysis: Dict[str, Any], technical: Dict[str, Any], 
                        total_holders: int, markets: List[Dict[str, Any]]) -> str:

    name = analysis.get('name', 'Unknown')
    symbol = analysis.get('symbol', 'UNKNOWN')
    price = analysis.get('price_formatted', 'N/A')
    market_cap = analysis.get('market_cap_formatted', 'N/A')
    liquidity = analysis.get('liquidity_formatted', 'N/A')
    trust_score = analysis.get('trust_score_formatted', 'N/A')

    report_lines = [
        f"{'='*60}",
        f"DYOR ANALYSIS REPORT - {name} ({symbol})",
        f"{'='*60}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "BASIC METRICS:",
        f"  Price: {price}",
        f"  Market Cap: {market_cap}",
        f"  Liquidity: {liquidity}",
        f"  Holders: {total_holders:,}",
        f"  Trust Score: {trust_score}",
        ""
    ]

    if technical:
        report_lines.append("TECHNICAL INDICATORS:")

        if 'rsi' in technical and technical['rsi'].get('success'):
            rsi = technical['rsi']
            report_lines.append(f"  RSI ({rsi.get('period', 14)}): {rsi.get('current_rsi', 0):.1f} - {rsi.get('signal', 'NEUTRAL')}")

        if 'macd' in technical and technical['macd'].get('success'):
            macd = technical['macd']
            report_lines.append(f"  MACD: {macd.get('signal', 'NEUTRAL')}")

        if 'volatility' in technical and technical['volatility'].get('success'):
            vol = technical['volatility']
            report_lines.append(f"  Volatility: {vol.get('volatility_percent', 'N/A')}")

        report_lines.append("")

    if markets:
        report_lines.append("AVAILABLE MARKETS:")
        for i, market in enumerate(markets[:3], 1):
            exchange = market.get('exchange', {}).get('name', 'Unknown')
            report_lines.append(f"  {i}. {exchange}")
        report_lines.append("")

    report_lines.extend([
        "RECOMMENDATIONS:",
        "  1. Always verify contract address",
        "  2. Check multiple data sources",
        "  3. Consider market conditions",
        "  4. Never invest more than you can afford to lose",
        "",
        f"{'='*60}",
        "DISCLAIMER: This report is for informational purposes only.",
        "Not financial advice. Always do your own research.",
        f"{'='*60}"
    ])

    return "\n".join(report_lines)

def compare_jettons_skill(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Starting jettons comparison skill...")

    addresses = context.get('addresses', [])

    try:
        client = context.get('dyor_client')

        if not client:
            return {"success": False, "error": "DYOR client not available"}

        if not addresses or len(addresses) < 2:
            return {"success": False, "error": "At least 2 addresses required"}

        results = {}
        comparison_data = []

        for address in addresses:
            try:
                analysis = get_jetton_analysis_skill({'dyor_client': client, 'address': address})

                if analysis.get('success'):
                    results[address] = analysis

                    comparison_data.append({
                        'address': address,
                        'name': analysis.get('name', 'Unknown'),
                        'symbol': analysis.get('symbol', 'UNKNOWN'),
                        'price_usd': analysis.get('price_usd', 0),
                        'market_cap_usd': analysis.get('market_cap_usd', 0),
                        'holders': analysis.get('holders', 0),
                        'liquidity_usd': analysis.get('liquidity_usd', 0),
                        'trust_score': analysis.get('trust_score', 0)
                    })
                    print(f"   ✓ {analysis.get('name')} ({analysis.get('symbol')})")
                else:
                    results[address] = analysis
                    print(f"   ✗ Failed to analyze {address[:12]}...")

            except Exception as e:
                results[address] = {'success': False, 'error': str(e)}
                print(f"   ✗ Error analyzing {address[:12]}...: {str(e)[:50]}")

        if comparison_data:
            comparison_data.sort(key=lambda x: x['market_cap_usd'], reverse=True)

            best_price = max(comparison_data, key=lambda x: x['price_usd']) if comparison_data else None
            best_market_cap = comparison_data[0] if comparison_data else None
            best_holders = max(comparison_data, key=lambda x: x['holders']) if comparison_data else None
            best_liquidity = max(comparison_data, key=lambda x: x['liquidity_usd']) if comparison_data else None
            best_trust = max(comparison_data, key=lambda x: x['trust_score']) if comparison_data else None

            comparison_summary = {
                'best_by_price': best_price,
                'best_by_market_cap': best_market_cap,
                'best_by_holders': best_holders,
                'best_by_liquidity': best_liquidity,
                'best_by_trust': best_trust,
                'total_analyzed': len(comparison_data),
                'successful_analysis': len([r for r in results.values() if r.get('success')])
            }
        else:
            comparison_summary = {}

        result = {
            "success": True,
            "individual_results": results,
            "comparison_data": comparison_data,
            "comparison_summary": comparison_summary,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Comparison completed: {len([r for r in results.values() if r.get('success')])}/{len(addresses)} successful")

        return result

    except Exception as e:
        print(f"Error in jettons comparison: {e}")
        return {
            "success": False,
            "error": f"Jettons comparison failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
