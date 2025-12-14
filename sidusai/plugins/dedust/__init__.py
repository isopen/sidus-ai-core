from .components import DedustComponents
from .skills import DedustSkills

class DedustPlugin:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.components = DedustComponents()
        self.skills = DedustSkills(self.components)

    def get_liquidity_providers(self, pool_address):
        return self.components.get_liquidity_providers(pool_address)

    def get_account_assets(self, account_address):
        return self.components.get_account_assets(account_address)

    def get_account_trades(self, account_address):
        return self.components.get_account_trades(account_address)

    def get_assets(self):
        return self.components.get_assets()

    def get_asset_details(self, symbol):
        return self.components.get_asset_details(symbol)

    def get_dns_info(self, domain):
        return self.components.get_dns_info(domain)

    def get_coingecko_pairs(self):
        return self.components.get_coingecko_pairs()

    def get_coingecko_tickers(self):
        return self.components.get_coingecko_tickers()

    def get_coingecko_trades(self, limit=100):
        return self.components.get_coingecko_trades(limit)

    def get_jetton_circulating_supply(self, jetton_address):
        return self.components.get_jetton_circulating_supply(jetton_address)

    def get_jetton_holders(self, jetton_address):
        return self.components.get_jetton_holders(jetton_address)

    def get_jetton_metadata(self, jetton_address):
        return self.components.get_jetton_metadata(jetton_address)

    def get_jetton_top_buys(self, jetton_address):
        return self.components.get_jetton_top_buys(jetton_address)

    def get_jetton_top_traders(self, jetton_address):
        return self.components.get_jetton_top_traders(jetton_address)

    def get_jetton_total_supply(self, jetton_address):
        return self.components.get_jetton_total_supply(jetton_address)

    def get_pools(self):
        return self.components.get_pools()

    def get_pools_lite(self):
        return self.components.get_pools_lite()

    def get_pool_metadata(self, pool_address):
        return self.components.get_pool_metadata(pool_address)

    def get_pool_trades(self, pool_address, limit=100):
        return self.components.get_pool_trades(pool_address, limit)

    def get_prices(self):
        return self.components.get_prices()

    def get_trace(self, hash):
        return self.components.get_trace(hash)

    def analyze_pool(self, pool_address):
        return self.skills.analyze_pool(pool_address)

    def analyze_asset(self, symbol):
        return self.skills.analyze_asset(symbol)

    def find_arbitrage_opportunities(self, min_profit_usd=10.0, min_tvl=1000.0, max_price_diff=0.10):
        return self.skills.find_arbitrage_opportunities(min_profit_usd, min_tvl, max_price_diff)

    def compare_pools(self, pool_addresses):
        return self.skills.compare_pools(pool_addresses)

    def get_liquidity_analysis(self, token_address):
        return self.skills.get_liquidity_analysis(token_address)

    def get_top_performing_pools(self, period="24h", limit=10):
        return self.skills.get_top_performing_pools(period, limit)

    def generate_pool_report(self, pool_address):
        return self.skills.generate_pool_report(pool_address)

    def calculate_impermanent_loss(self, pool_address, token_a_change, token_b_change):
        return self.skills.calculate_impermanent_loss(pool_address, token_a_change, token_b_change)

    def analyze_wallet_portfolio(self, wallet_address):
        return self.skills.analyze_wallet_portfolio(wallet_address)

    def get_swap_recommendations(self, offer_token, ask_token, amount):
        return self.skills.get_swap_recommendations(offer_token, ask_token, amount)

    def calculate_apy_breakdown(self, jetton_address):
        return self.skills.calculate_apy_breakdown(jetton_address)

    def analyze_jetton(self, jetton_address):
        return self.skills.analyze_jetton(jetton_address)

    def get_market_overview(self):
        return self.skills.get_market_overview()
