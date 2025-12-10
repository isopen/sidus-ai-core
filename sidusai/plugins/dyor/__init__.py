from .components import DYORComponents
from .skills import DYORSkills

class DYORPlugin:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.components = DYORComponents(api_key)
        self.skills = DYORSkills(api_key)

    def get_jettons(self, sort="createdAt", order="asc", currency="ton", limit=50, offset=0):
        return self.components.get_jettons(sort, order, currency, limit, offset)

    def get_jetton(self, address):
        return self.components.get_jetton(address)

    def get_jetton_metrics(self, address, currency="ton"):
        return self.components.get_jetton_metrics(address, currency)

    def get_jetton_price(self, address, currency="ton"):
        return self.components.get_jetton_price(address, currency)

    def get_jetton_holders(self, address):
        return self.components.get_jetton_holders(address)

    def get_jetton_transactions(self, address, exchange_id=None):
        return self.components.get_jetton_transactions(address, exchange_id)

    def get_jetton_markets(self, address, exchange_id=None):
        return self.components.get_jetton_markets(address, exchange_id)

    def analyze_jetton(self, address):
        return self.skills.get_jetton_analysis(address)

    def analyze_technical(self, address):
        results = {}
        rsi = self.skills.calculate_rsi(address)
        if rsi['success']:
            results['rsi'] = rsi

        macd = self.skills.calculate_macd(address)
        if macd['success']:
            results['macd'] = macd

        volatility = self.skills.calculate_volatility(address)
        if volatility['success']:
            results['volatility'] = volatility

        return results

    def generate_report(self, address):
        return self.skills.generate_report(address)

    def compare_jettons(self, addresses):
        results = {}
        for address in addresses:
            try:
                analysis = self.skills.get_jetton_analysis(address)
                results[address] = analysis
            except Exception as e:
                results[address] = {'success': False, 'error': str(e)}
        return results

    def get_top_gainers(self, period="24h"):
        try:
            volume_data = self.components.get_jetton_trading_volume_change()
            if 'items' in volume_data:
                items = volume_data['items']
                sorted_items = sorted(items, 
                    key=lambda x: x.get('changes', {}).get('total', {}).get(period, {}).get('changePercent', 0), 
                    reverse=True)
                return sorted_items[:10]
        except:
            pass
        return []

    def get_jetton_trading_volume_change(self, currency="ton"):
        return self.components.get_jetton_trading_volume_change(currency)
