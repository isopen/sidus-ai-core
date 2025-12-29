import sidusai as sai
from typing import Optional, Dict, Any, List
from datetime import datetime
from .components import DedustComponents
from .skills import DedustSkills

__dedust_agent_name__ = 'dedust_dex_agent'

class DedustPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        self.dedust_client = None

    def apply_plugin(self, agent: sai.Agent):
        components = DedustComponents()
        if self.api_key:
            components.api_key = self.api_key

        dedust_skills = DedustSkills(components)

        self.skills = {}

        def analyze_pool_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            pool_address = context.get('pool_address')
            if not pool_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Pool address is required"}
                return return_value

            try:
                result = dedust_skills.analyze_pool(pool_address)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def analyze_asset_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            symbol = context.get('symbol')
            if not symbol:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Symbol is required"}
                return return_value

            try:
                result = dedust_skills.analyze_asset(symbol)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def find_arbitrage_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            min_profit_usd = context.get('min_profit_usd', 10.0)
            min_tvl = context.get('min_tvl', 1000.0)
            max_price_diff = context.get('max_price_diff', 0.10)

            try:
                result = dedust_skills.find_arbitrage_opportunities(
                    min_profit_usd, min_tvl, max_price_diff
                )
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def compare_pools_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            pool_addresses = context.get('pool_addresses', [])
            if not pool_addresses or len(pool_addresses) < 2:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "At least 2 pool addresses required"}
                return return_value

            try:
                result = dedust_skills.compare_pools(pool_addresses)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def analyze_liquidity_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            token_address = context.get('token_address')
            if not token_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Token address is required"}
                return return_value

            try:
                result = dedust_skills.get_liquidity_analysis(token_address)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_top_pools_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            period = context.get('period', '24h')
            limit = context.get('limit', 10)

            try:
                result = dedust_skills.get_top_performing_pools(period, limit)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def generate_pool_report_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            pool_address = context.get('pool_address')
            if not pool_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Pool address is required"}
                return return_value

            try:
                result = dedust_skills.generate_pool_report(pool_address)
                return_value = sai.AgentValue()
                return_value.value = {"success": True, "report": result}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def calculate_impermanent_loss_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            pool_address = context.get('pool_address')
            token_a_change = context.get('token_a_change', 0.0)
            token_b_change = context.get('token_b_change', 0.0)

            if not pool_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Pool address is required"}
                return return_value

            try:
                result = dedust_skills.calculate_impermanent_loss(
                    pool_address, token_a_change, token_b_change
                )
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def analyze_wallet_portfolio_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            wallet_address = context.get('wallet_address')
            if not wallet_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Wallet address is required"}
                return return_value

            try:
                result = dedust_skills.analyze_wallet_portfolio(wallet_address)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_swap_recommendations_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            offer_token = context.get('offer_token')
            ask_token = context.get('ask_token')
            amount = context.get('amount', 1.0)

            if not offer_token or not ask_token:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Offer token and ask token are required"}
                return return_value

            if amount <= 0:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Amount must be positive"}
                return return_value

            try:
                result = dedust_skills.get_swap_recommendations(
                    offer_token, ask_token, amount
                )
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def calculate_apy_breakdown_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            jetton_address = context.get('jetton_address')
            if not jetton_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Jetton address is required"}
                return return_value

            try:
                result = dedust_skills.calculate_apy_breakdown(jetton_address)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def analyze_jetton_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            jetton_address = context.get('jetton_address')
            if not jetton_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Jetton address is required"}
                return return_value

            try:
                result = dedust_skills.analyze_jetton(jetton_address)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_market_overview_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            try:
                result = dedust_skills.get_market_overview()
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_pools_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            try:
                result = components.get_pools()
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                } if result else {"success": False, "error": "Failed to fetch pools"}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_assets_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            try:
                result = components.get_assets()
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                } if result else {"success": False, "error": "Failed to fetch assets"}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_prices_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            try:
                result = components.get_prices()
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                } if result else {"success": False, "error": "Failed to fetch prices"}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_liquidity_providers_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            pool_address = context.get('pool_address')

            if not pool_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Pool address is required"}
                return return_value

            try:
                result = components.get_liquidity_providers(pool_address)
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                } if result else {"success": False, "error": "Failed to fetch liquidity providers"}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_account_assets_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            account_address = context.get('account_address')

            if not account_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Account address is required"}
                return return_value

            try:
                result = components.get_account_assets(account_address)
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                } if result else {"success": False, "error": "Failed to fetch account assets"}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_account_trades_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            account_address = context.get('account_address')

            if not account_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Account address is required"}
                return return_value

            try:
                result = components.get_account_trades(account_address)
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                } if result else {"success": False, "error": "Failed to fetch account trades"}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_pool_metadata_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            pool_address = context.get('pool_address')

            if not pool_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Pool address is required"}
                return return_value

            try:
                result = components.get_pool_metadata(pool_address)
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                } if result else {"success": False, "error": "Failed to fetch pool metadata"}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_pool_trades_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            pool_address = context.get('pool_address')
            limit = context.get('limit', 100)

            if not pool_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Pool address is required"}
                return return_value

            try:
                result = components.get_pool_trades(pool_address, limit)
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                } if result else {"success": False, "error": "Failed to fetch pool trades"}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_asset_details_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            symbol = context.get('symbol')

            if not symbol:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Symbol is required"}
                return return_value

            try:
                result = components.get_asset_details(symbol)
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                } if result else {"success": False, "error": "Failed to fetch asset details"}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_dns_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            domain = context.get('domain')

            if not domain:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Domain is required"}
                return return_value

            try:
                result = components.get_dns_info(domain)
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                } if result else {"success": False, "error": "Failed to fetch DNS info"}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_jetton_metadata_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            jetton_address = context.get('jetton_address')

            if not jetton_address:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Jetton address is required"}
                return return_value

            try:
                result = components.get_jetton_metadata(jetton_address)
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                } if result else {"success": False, "error": "Failed to fetch jetton metadata"}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        self.skills = {
            'analyze_pool': analyze_pool_wrapper,
            'analyze_asset': analyze_asset_wrapper,
            'find_arbitrage_opportunities': find_arbitrage_wrapper,
            'compare_pools': compare_pools_wrapper,
            'analyze_token_liquidity': analyze_liquidity_wrapper,
            'get_top_performing_pools': get_top_pools_wrapper,
            'generate_pool_report': generate_pool_report_wrapper,
            'calculate_impermanent_loss': calculate_impermanent_loss_wrapper,
            'analyze_wallet_portfolio': analyze_wallet_portfolio_wrapper,
            'get_swap_recommendations': get_swap_recommendations_wrapper,
            'calculate_apy_breakdown': calculate_apy_breakdown_wrapper,
            'analyze_jetton': analyze_jetton_wrapper,
            'get_market_overview': get_market_overview_wrapper,
            'get_pools': get_pools_wrapper,
            'get_assets': get_assets_wrapper,
            'get_prices': get_prices_wrapper,
            'get_liquidity_providers': get_liquidity_providers_wrapper,
            'get_account_assets': get_account_assets_wrapper,
            'get_account_trades': get_account_trades_wrapper,
            'get_pool_metadata': get_pool_metadata_wrapper,
            'get_pool_trades': get_pool_trades_wrapper,
            'get_asset_details': get_asset_details_wrapper,
            'get_dns_info': get_dns_info_wrapper,
            'get_jetton_metadata': get_jetton_metadata_wrapper,
        }

        for skill_name, skill_func in self.skills.items():
            agent.add_skill(skill_func, name=skill_name)

        agent.dedust_components = components
        agent.dedust_skills = dedust_skills
        agent.dedust_skills_dict = self.skills

class DedustAgent(sai.Agent):
    def __init__(self, api_key: Optional[str] = None, name: str = __dedust_agent_name__):
        super().__init__()
        self._name = name
        self.api_key = api_key

        self.plugin = DedustPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        agent_value = sai.AgentValue()
        agent_value.value = context
        return agent_value

    def analyze_pool(self, pool_address: str) -> Dict[str, Any]:
        context = {'pool_address': pool_address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['analyze_pool'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def analyze_asset(self, symbol: str) -> Dict[str, Any]:
        context = {'symbol': symbol}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['analyze_asset'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def find_arbitrage_opportunities(self, 
                                   min_profit_usd: float = 10.0, 
                                   min_tvl: float = 1000.0, 
                                   max_price_diff: float = 0.10) -> Dict[str, Any]:
        context = {
            'min_profit_usd': min_profit_usd,
            'min_tvl': min_tvl,
            'max_price_diff': max_price_diff
        }
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['find_arbitrage_opportunities'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def compare_pools(self, pool_addresses: List[str]) -> Dict[str, Any]:
        context = {'pool_addresses': pool_addresses}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['compare_pools'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def analyze_token_liquidity(self, token_address: str) -> Dict[str, Any]:
        context = {'token_address': token_address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['analyze_token_liquidity'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_top_performing_pools(self, period: str = "24h", limit: int = 10) -> Dict[str, Any]:
        context = {
            'period': period,
            'limit': limit
        }
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_top_performing_pools'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def generate_pool_report(self, pool_address: str) -> Dict[str, Any]:
        context = {'pool_address': pool_address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['generate_pool_report'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def calculate_impermanent_loss(self, pool_address: str, 
                                 token_a_change: float, 
                                 token_b_change: float) -> Dict[str, Any]:
        context = {
            'pool_address': pool_address,
            'token_a_change': token_a_change,
            'token_b_change': token_b_change
        }
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['calculate_impermanent_loss'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def analyze_wallet_portfolio(self, wallet_address: str) -> Dict[str, Any]:
        context = {'wallet_address': wallet_address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['analyze_wallet_portfolio'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_swap_recommendations(self, offer_token: str, ask_token: str, 
                               amount: float = 1.0) -> Dict[str, Any]:
        context = {
            'offer_token': offer_token,
            'ask_token': ask_token,
            'amount': amount
        }
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_swap_recommendations'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def calculate_apy_breakdown(self, jetton_address: str) -> Dict[str, Any]:
        context = {'jetton_address': jetton_address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['calculate_apy_breakdown'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def analyze_jetton(self, jetton_address: str) -> Dict[str, Any]:
        context = {'jetton_address': jetton_address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['analyze_jetton'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_market_overview(self) -> Dict[str, Any]:
        agent_value = sai.AgentValue()
        agent_value.value = {}
        result = self.plugin.skills['get_market_overview'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_pools(self) -> Dict[str, Any]:
        agent_value = sai.AgentValue()
        agent_value.value = {}
        result = self.plugin.skills['get_pools'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_assets(self) -> Dict[str, Any]:
        agent_value = sai.AgentValue()
        agent_value.value = {}
        result = self.plugin.skills['get_assets'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_prices(self) -> Dict[str, Any]:
        agent_value = sai.AgentValue()
        agent_value.value = {}
        result = self.plugin.skills['get_prices'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_liquidity_providers(self, pool_address: str) -> Dict[str, Any]:
        context = {'pool_address': pool_address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_liquidity_providers'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_account_assets(self, account_address: str) -> Dict[str, Any]:
        context = {'account_address': account_address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_account_assets'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_account_trades(self, account_address: str) -> Dict[str, Any]:
        context = {'account_address': account_address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_account_trades'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_pool_metadata(self, pool_address: str) -> Dict[str, Any]:
        context = {'pool_address': pool_address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_pool_metadata'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_pool_trades(self, pool_address: str, limit: int = 100) -> Dict[str, Any]:
        context = {
            'pool_address': pool_address,
            'limit': limit
        }
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_pool_trades'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_asset_details(self, symbol: str) -> Dict[str, Any]:
        context = {'symbol': symbol}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_asset_details'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_dns_info(self, domain: str) -> Dict[str, Any]:
        context = {'domain': domain}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_dns_info'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_jetton_metadata(self, jetton_address: str) -> Dict[str, Any]:
        context = {'jetton_address': jetton_address}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_jetton_metadata'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_jetton_circulating_supply(self, jetton_address: str) -> Dict[str, Any]:
        try:
            if hasattr(self, 'dedust_components'):
                result = self.dedust_components.get_jetton_circulating_supply(jetton_address)
                return {"success": True, "data": result}
            return {"success": False, "error": "Components not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_jetton_holders(self, jetton_address: str) -> Dict[str, Any]:
        try:
            if hasattr(self, 'dedust_components'):
                result = self.dedust_components.get_jetton_holders(jetton_address)
                return {"success": True, "data": result}
            return {"success": False, "error": "Components not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_jetton_top_buys(self, jetton_address: str) -> Dict[str, Any]:
        try:
            if hasattr(self, 'dedust_components'):
                result = self.dedust_components.get_jetton_top_buys(jetton_address)
                return {"success": True, "data": result}
            return {"success": False, "error": "Components not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_jetton_top_traders(self, jetton_address: str) -> Dict[str, Any]:
        try:
            if hasattr(self, 'dedust_components'):
                result = self.dedust_components.get_jetton_top_traders(jetton_address)
                return {"success": True, "data": result}
            return {"success": False, "error": "Components not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_jetton_total_supply(self, jetton_address: str) -> Dict[str, Any]:
        try:
            if hasattr(self, 'dedust_components'):
                result = self.dedust_components.get_jetton_total_supply(jetton_address)
                return {"success": True, "data": result}
            return {"success": False, "error": "Components not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_coingecko_pairs(self) -> Dict[str, Any]:
        try:
            if hasattr(self, 'dedust_components'):
                result = self.dedust_components.get_coingecko_pairs()
                return {"success": True, "data": result}
            return {"success": False, "error": "Components not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_coingecko_tickers(self) -> Dict[str, Any]:
        try:
            if hasattr(self, 'dedust_components'):
                result = self.dedust_components.get_coingecko_tickers()
                return {"success": True, "data": result}
            return {"success": False, "error": "Components not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_coingecko_trades(self, limit: int = 100) -> Dict[str, Any]:
        try:
            if hasattr(self, 'dedust_components'):
                result = self.dedust_components.get_coingecko_trades(limit)
                return {"success": True, "data": result}
            return {"success": False, "error": "Components not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_trace(self, hash: str) -> Dict[str, Any]:
        try:
            if hasattr(self, 'dedust_components'):
                result = self.dedust_components.get_trace(hash)
                return {"success": True, "data": result}
            return {"success": False, "error": "Components not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def create_dedust_agent(api_key: Optional[str] = None) -> DedustAgent:
    return DedustAgent(api_key=api_key)

__all__ = [
    'DedustPlugin',
    'DedustAgent',
    'create_dedust_agent',
    'DedustComponents',
    'DedustSkills',
]
