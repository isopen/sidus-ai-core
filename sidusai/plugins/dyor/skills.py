import numpy as np
from datetime import datetime

class DYORSkills:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def _get_components(self):
        from .components import DYORComponents
        return DYORComponents(self.api_key)

    def calculate_rsi(self, address, period=14):
        try:
            components = self._get_components()
            df = components.fetch_price_data(address)

            if len(df) < period + 1:
                return {'success': False, 'error': 'Insufficient data'}

            delta = df['price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            current_rsi = float(rsi.iloc[-1])

            signal = "NEUTRAL"
            if current_rsi > 70:
                signal = "OVERBOUGHT"
            elif current_rsi < 30:
                signal = "OVERSOLD"

            return {
                'success': True,
                'current_rsi': round(current_rsi, 2),
                'signal': signal,
                'period': period
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def calculate_macd(self, address):
        try:
            components = self._get_components()
            df = components.fetch_price_data(address)

            if len(df) < 26:
                return {'success': False, 'error': 'Insufficient data'}

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

            return {
                'success': True,
                'current_macd': round(current_macd, 6),
                'current_signal': round(current_signal, 6),
                'signal': signal
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def calculate_volatility(self, address, window=20):
        try:
            components = self._get_components()
            df = components.fetch_price_data(address)

            if len(df) < window:
                return {'success': False, 'error': 'Insufficient data'}

            returns = df['price'].pct_change()
            volatility = returns.rolling(window=window).std() * np.sqrt(365)
            current_volatility = float(volatility.iloc[-1])

            return {
                'success': True,
                'volatility': round(current_volatility, 4),
                'window': window
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_jetton_analysis(self, address):
        try:
            components = self._get_components()

            jetton_data = components.get_jetton(address)
            metrics_data = components.get_jetton_metrics(address)
            price_data = components.get_jetton_price(address)

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

            price_usd = components._format_value(metrics.get('priceUsd', {}))
            mcap_usd = components._format_value(metrics.get('mcap', {}))
            liquidity_usd = components._format_value(metrics.get('liquidityUsd', {}))
            trust_score = metrics.get('trustScore', 0)

            return {
                'success': True,
                'address': address,
                'name': jetton.get('metadata', {}).get('name', 'Unknown'),
                'symbol': jetton.get('metadata', {}).get('symbol', 'UNKNOWN'),
                'price_usd': price_usd,
                'market_cap_usd': mcap_usd,
                'holders': holders,
                'liquidity_usd': liquidity_usd,
                'trust_score': trust_score,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_report(self, address):
        try:
            analysis = self.get_jetton_analysis(address)
            if not analysis['success']:
                return f"Error: {analysis['error']}"

            rsi_result = self.calculate_rsi(address)
            macd_result = self.calculate_macd(address)
            volatility_result = self.calculate_volatility(address)

            report = f"""
            {'='*80}
            DYOR ANALYSIS REPORT
            {'='*80}

            TOKEN: {analysis.get('name', 'Unknown')} ({analysis.get('symbol', 'UNKNOWN')})
            ADDRESS: {address}
            REPORT TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            DATA SOURCE: DYOR.io API

            {'='*80}
            METRICS
            {'='*80}
            Price: ${analysis.get('price_usd', 0):.6f}
            Market Cap: ${analysis.get('market_cap_usd', 0):,.0f}
            Holders: {analysis.get('holders', 0):,}
            Liquidity: ${analysis.get('liquidity_usd', 0):,.0f}
            Trust Score: {analysis.get('trust_score', 0)}/100

            {'='*80}
            TECHNICAL ANALYSIS
            {'='*80}
            """

            if rsi_result['success']:
                report += f"RSI ({rsi_result['period']}): {rsi_result['current_rsi']:.1f} ({rsi_result['signal']})\n"

            if macd_result['success']:
                report += f"MACD: {macd_result['signal']}\n"

            if volatility_result['success']:
                report += f"Volatility ({volatility_result['window']}D): {volatility_result['volatility']:.2%}\n"

            report += f"""
            {'='*80}
            RECOMMENDATIONS
            {'='*80}
            """

            recommendations = []

            if rsi_result['success']:
                rsi_val = rsi_result['current_rsi']
                if rsi_val > 70:
                    recommendations.append("RSI indicates overbought conditions")
                elif rsi_val < 30:
                    recommendations.append("RSI indicates oversold conditions")

            if macd_result['success']:
                if macd_result['signal'] == "BULLISH":
                    recommendations.append("MACD shows bullish momentum")
                elif macd_result['signal'] == "BEARISH":
                    recommendations.append("MACD shows bearish momentum")

            trust_score = analysis.get('trust_score', 0)
            if trust_score < 50:
                recommendations.append(f"Low trust score ({trust_score}/100)")

            holders = analysis.get('holders', 0)
            if holders < 100:
                recommendations.append(f"Low number of holders ({holders})")

            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    report += f"{i}. {rec}\n"
            else:
                report += "No specific recommendations\n"

            report += f"""
            {'='*80}
            DISCLAIMER
            {'='*80}
            This report is for informational purposes only.
            Not financial advice. Always do your own research.
            {'='*80}
            """

            return report

        except Exception as e:
            return f"Error generating report: {str(e)}"
