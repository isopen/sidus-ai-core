from .components import StonFiComponents
from .skills import StonFiSkills

class StonFiPlugin:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.components = StonFiComponents()
        self.skills = StonFiSkills(self.components)

    def get_asset(self, address):
        return self.components.get_asset(address)

    def get_assets(self):
        return self.components.get_assets()

    def query_assets(self, condition=None, limit=None, search_terms=None, sort_by=None, unconditional_assets=None, wallet_address=None):
        return self.components.query_assets(condition, limit, search_terms, sort_by, unconditional_assets, wallet_address)

    def search_assets(self, search_string, condition=None, unconditional_asset=None, limit=None, wallet_address=None):
        return self.components.search_assets(search_string, condition, unconditional_asset, limit, wallet_address)

    def get_pool(self, address):
        return self.components.get_pool(address)

    def get_pools(self, dex_v2=True):
        return self.components.get_pools(dex_v2)

    def get_pools_by_market(self, asset_0, asset_1):
        return self.components.get_pools_by_market(asset_0, asset_1)

    def query_pools(self, condition=None, dex_v2=True, limit=None, search_terms=None, sort_by=None, unconditional_assets=None, wallet_address=None):
        return self.components.query_pools(condition, dex_v2, limit, search_terms, sort_by, unconditional_assets, wallet_address)

    def get_farm(self, address):
        return self.components.get_farm(address)

    def get_farms(self, dex_v2=True, only_active=False):
        return self.components.get_farms(dex_v2, only_active)

    def get_farms_by_pool(self, pool_address):
        return self.components.get_farms_by_pool(pool_address)

    def simulate_swap(self, offer_address, ask_address, units, slippage_tolerance, pool_address=None, referral_address=None, referral_fee_bps=None, dex_v2=True, dex_version=None):
        return self.components.simulate_swap(offer_address, ask_address, units, slippage_tolerance, pool_address, referral_address, referral_fee_bps, dex_v2, dex_version)

    def simulate_reverse_swap(self, offer_address, ask_address, units, slippage_tolerance, pool_address=None, referral_address=None, referral_fee_bps=None, dex_v2=True, dex_version=None):
        return self.components.simulate_reverse_swap(offer_address, ask_address, units, slippage_tolerance, pool_address, referral_address, referral_fee_bps, dex_v2, dex_version)

    def get_swap_status(self, router_address, owner_address, query_id):
        return self.components.get_swap_status(router_address, owner_address, query_id)

    def simulate_liquidity_provision(self, provision_type, token_a, token_b, slippage_tolerance, pool_address=None, wallet_address=None, token_a_units=None, token_b_units=None):
        return self.components.simulate_liquidity_provision(provision_type, token_a, token_b, slippage_tolerance, pool_address, wallet_address, token_a_units, token_b_units)

    def get_markets(self, dex_v2=True):
        return self.components.get_markets(dex_v2)

    def get_router(self, address):
        return self.components.get_router(address)

    def get_routers(self, dex_v2=True):
        return self.components.get_routers(dex_v2)

    def get_transaction_action_tree(self, hash):
        return self.components.get_transaction_action_tree(hash)

    def query_transactions(self, wallet_address=None, query_id=None, min_tx_timestamp=None, ext_msg_hash=None):
        return self.components.query_transactions(wallet_address, query_id, min_tx_timestamp, ext_msg_hash)

    def get_jetton_wallet_address(self, jetton_address, owner_address):
        return self.components.get_jetton_wallet_address(jetton_address, owner_address)

    def get_wallet_asset(self, wallet_address, asset_address):
        return self.components.get_wallet_asset(wallet_address, asset_address)

    def get_wallet_assets(self, wallet_address):
        return self.components.get_wallet_assets(wallet_address)

    def get_wallet_pool(self, wallet_address, pool_address):
        return self.components.get_wallet_pool(wallet_address, pool_address)

    def get_wallet_pools(self, wallet_address, dex_v2=True):
        return self.components.get_wallet_pools(wallet_address, dex_v2)

    def get_wallet_farm(self, wallet_address, farm_address):
        return self.components.get_wallet_farm(wallet_address, farm_address)

    def get_wallet_farms(self, wallet_address, dex_v2=True, only_active=False):
        return self.components.get_wallet_farms(wallet_address, dex_v2, only_active)

    def get_wallet_fee_vaults(self, wallet_address):
        return self.components.get_wallet_fee_vaults(wallet_address)

    def get_wallet_operations(self, wallet_address, since, until, op_type=None, dex_v2=True):
        return self.components.get_wallet_operations(wallet_address, since, until, op_type, dex_v2)

    def get_wallet_stakes(self, wallet_address):
        return self.components.get_wallet_stakes(wallet_address)

    def get_wallet_last_transactions(self, wallet_address, limit=10, min_tx_timestamp=None):
        return self.components.get_wallet_last_transactions(wallet_address, limit, min_tx_timestamp)

    def get_dex_stats(self, since=None, until=None):
        return self.components.get_dex_stats(since, until)

    def get_fee_accruals(self, referrer_address, since, until):
        return self.components.get_fee_accruals(referrer_address, since, until)

    def get_fee_withdrawals(self, referrer_address, since, until):
        return self.components.get_fee_withdrawals(referrer_address, since, until)

    def get_fees_stats(self, referrer_address, since, until):
        return self.components.get_fees_stats(referrer_address, since, until)

    def get_operations_stats(self, since, until, pool_address=None):
        return self.components.get_operations_stats(since, until, pool_address)

    def get_pool_stats(self, since, until, pool_address=None):
        return self.components.get_pool_stats(since, until, pool_address)

    def get_staking_stats(self):
        return self.components.get_staking_stats()

    def get_cmc_data(self):
        return self.components.get_cmc_data()

    def get_screener_asset_info(self, address):
        return self.components.get_screener_asset_info(address)

    def get_screener_events(self, from_block, to_block):
        return self.components.get_screener_events(from_block, to_block)

    def get_screener_latest_block(self):
        return self.components.get_screener_latest_block()

    def get_screener_pool_info(self, address):
        return self.components.get_screener_pool_info(address)

    def analyze_pool(self, pool_address):
        return self.skills.analyze_pool(pool_address)

    def analyze_asset(self, asset_address):
        return self.skills.analyze_asset(asset_address)

    def find_arbitrage_opportunities(self):
        return self.skills.find_arbitrage_opportunities()

    def compare_pools(self, pool_addresses):
        return self.skills.compare_pools(pool_addresses)

    def get_liquidity_analysis(self, token_address):
        return self.skills.get_liquidity_analysis(token_address)

    def get_top_performing_pools(self, period="24h"):
        return self.skills.get_top_performing_pools(period)

    def generate_pool_report(self, pool_address):
        return self.skills.generate_pool_report(pool_address)

    def calculate_impermanent_loss(self, pool_address, token_a_change, token_b_change):
        return self.skills.calculate_impermanent_loss(pool_address, token_a_change, token_b_change)

    def analyze_wallet_portfolio(self, wallet_address):
        return self.skills.analyze_wallet_portfolio(wallet_address)

    def get_swap_recommendations(self, offer_token, ask_token, amount):
        return self.skills.get_swap_recommendations(offer_token, ask_token, amount)

    def calculate_apy_breakdown(self, farm_address):
        return self.skills.calculate_apy_breakdown(farm_address)

    def find_arbitrage_opportunities(self, min_profit_usd: float = 10.0, 
                               min_tvl: float = 1000.0, 
                               max_price_diff: float = 0.10):
        return self.skills.find_arbitrage_opportunities(min_profit_usd, min_tvl, max_price_diff)
