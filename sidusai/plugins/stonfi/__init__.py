import sidusai as sai
from typing import Optional, Dict, Any, List

from .components import StonFiClientComponent
from .skills import (
    token_analysis_skill,
    swap_simulation_skill,
    pool_analysis_skill,
    wallet_info_skill,
    arbitrage_finder_skill
)

__stonfi_agent_name__ = 'stonfi_dex_agent'

class StonFiPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        self.stonfi_client = None
        print(f"STON.fi Plugin initialized")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying STON.fi plugin to agent...")

        try:
            self.stonfi_client = StonFiClientComponent(api_key=self.api_key)
            print("STON.fi client component created")

            self.skills = {}

            def analyze_token_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = getattr(agent_value, 'value', {})
                if not context:
                    context = agent_value
                context['stonfi_client'] = self.stonfi_client
                result = token_analysis_skill(context)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value

            def simulate_swap_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = getattr(agent_value, 'value', {})
                if not context:
                    context = agent_value
                context['stonfi_client'] = self.stonfi_client
                result = swap_simulation_skill(context)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value

            def analyze_pool_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = getattr(agent_value, 'value', {})
                if not context:
                    context = agent_value
                context['stonfi_client'] = self.stonfi_client
                result = pool_analysis_skill(context)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value

            def analyze_portfolio_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = getattr(agent_value, 'value', {})
                if not context:
                    context = agent_value
                context['stonfi_client'] = self.stonfi_client
                result = wallet_info_skill(context)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value

            def find_arbitrage_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = getattr(agent_value, 'value', {})
                if not context:
                    context = agent_value
                context['stonfi_client'] = self.stonfi_client
                result = arbitrage_finder_skill(context)
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value

            self.skills = {
                'analyze_token': analyze_token_wrapper,
                'simulate_swap': simulate_swap_wrapper,
                'analyze_pool': analyze_pool_wrapper,
                'analyze_portfolio': analyze_portfolio_wrapper,
                'find_arbitrage': find_arbitrage_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.stonfi_client = self.stonfi_client
            agent.stonfi_skills = self.skills

            print("STON.fi plugin applied successfully")

        except Exception as e:
            print(f"Error applying STON.fi plugin: {e}")
            import traceback
            traceback.print_exc()

class StonFiAgent(sai.Agent):
    def __init__(self, api_key: Optional[str] = None, name: str = __stonfi_agent_name__):
        super().__init__()
        self._name = name
        self.api_key = api_key

        print(f"Creating STON.fi Agent '{name}'...")
        self.plugin = StonFiPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)
        print(f"STON.fi Agent '{name}' created successfully")

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        try:
            agent_value = sai.AgentValue()
            agent_value.value = context
            return agent_value
        except Exception as e:
            print(f"Error creating AgentValue: {e}")
            agent_value = sai.AgentValue()
            setattr(agent_value, 'value', context)
            return agent_value

    def analyze_token(self, 
                     token_address: str,
                     include_related_pools: bool = True,
                     include_price_history: bool = False,
                     price_history_interval: str = '1d',
                     price_history_limit: int = 30,
                     pool_search_limit: int = 10,
                     calculate_volatility: bool = False,
                     min_liquidity: float = 1000) -> Dict[str, Any]:

        context = {
            'token_address': token_address,
            'include_related_pools': include_related_pools,
            'include_price_history': include_price_history,
            'price_history_interval': price_history_interval,
            'price_history_limit': price_history_limit,
            'pool_search_limit': pool_search_limit,
            'calculate_volatility': calculate_volatility,
            'min_liquidity': min_liquidity
        }

        if 'analyze_token' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['analyze_token'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def simulate_swap(self,
                     offer_address: str,
                     ask_address: str,
                     units: str,
                     slippage_tolerance: float = 0.01,
                     pool_address: Optional[str] = None,
                     referral_address: Optional[str] = None,
                     referral_fee_bps: Optional[str] = None,
                     dex_v2: bool = True,
                     dex_version: Optional[List[str]] = None,
                     simulate_both_directions: bool = False,
                     optimize_route: bool = True,
                     max_routes_to_check: int = 5) -> Dict[str, Any]:

        context = {
            'offer_address': offer_address,
            'ask_address': ask_address,
            'units': units,
            'slippage_tolerance': slippage_tolerance,
            'pool_address': pool_address,
            'referral_address': referral_address,
            'referral_fee_bps': referral_fee_bps,
            'dex_v2': dex_v2,
            'dex_version': dex_version,
            'simulate_both_directions': simulate_both_directions,
            'optimize_route': optimize_route,
            'max_routes_to_check': max_routes_to_check
        }

        if 'simulate_swap' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['simulate_swap'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def analyze_pool(self, 
                     pool_address: str,
                     include_stats: bool = True,
                     stats_period_days: int = 7,
                     include_farms: bool = True,
                     include_wallet_position: bool = False,
                     wallet_address: Optional[str] = None,
                     calculate_apy: bool = True,
                     compare_with_market: bool = False,
                     market_asset_0: Optional[str] = None,
                     market_asset_1: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'pool_address': pool_address,
            'include_stats': include_stats,
            'stats_period_days': stats_period_days,
            'include_farms': include_farms,
            'include_wallet_position': include_wallet_position,
            'wallet_address': wallet_address,
            'calculate_apy': calculate_apy,
            'compare_with_market': compare_with_market,
            'market_asset_0': market_asset_0,
            'market_asset_1': market_asset_1
        }

        if 'analyze_pool' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['analyze_pool'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def analyze_portfolio(self, 
                         wallet_address: str,
                         include_assets: bool = True,
                         include_pools: bool = True,
                         include_farms: bool = True,
                         include_stakes: bool = True,
                         include_transactions: bool = False,
                         transactions_limit: int = 20,
                         min_asset_value: float = 1.0,
                         calculate_performance: bool = False,
                         performance_period_days: int = 30,
                         group_by_category: bool = True) -> Dict[str, Any]:

        context = {
            'wallet_address': wallet_address,
            'include_assets': include_assets,
            'include_pools': include_pools,
            'include_farms': include_farms,
            'include_stakes': include_stakes,
            'include_transactions': include_transactions,
            'transactions_limit': transactions_limit,
            'min_asset_value': min_asset_value,
            'calculate_performance': calculate_performance,
            'performance_period_days': performance_period_days,
            'group_by_category': group_by_category
        }

        if 'analyze_portfolio' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['analyze_portfolio'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def find_arbitrage(self, 
                  base_token: str = 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c',  # Правильный адрес TON
                  tokens_to_analyze: List[str] = None,
                  min_profit_percentage: float = 0.1,
                  max_tokens_to_analyze: int = 8,
                  max_route_length: int = 4,
                  min_pool_liquidity: float = 1000,
                  include_liquidity_check: bool = True,
                  check_triangular: bool = True,
                  exclude_tokens: List[str] = None) -> Dict[str, Any]:

        context = {
            'base_token': base_token,
            'tokens_to_analyze': tokens_to_analyze or [],
            'min_profit_percentage': min_profit_percentage,
            'max_tokens_to_analyze': max_tokens_to_analyze,
            'max_route_length': max_route_length,
            'min_pool_liquidity': min_pool_liquidity,
            'include_liquidity_check': include_liquidity_check,
            'check_triangular': check_triangular,
            'exclude_tokens': exclude_tokens or []
        }

        if 'find_arbitrage' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['find_arbitrage'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def market_research(self,
                       research_type: str = 'general',
                       target_market: Optional[str] = None,
                       time_frame_days: int = 7,
                       top_n: int = 10,
                       include_volume_analysis: bool = True,
                       include_liquidity_analysis: bool = True,
                       include_price_action: bool = True,
                       min_daily_volume: float = 10000,
                       sort_by: str = 'volume') -> Dict[str, Any]:

        context = {
            'research_type': research_type,
            'target_market': target_market,
            'time_frame_days': time_frame_days,
            'top_n': top_n,
            'include_volume_analysis': include_volume_analysis,
            'include_liquidity_analysis': include_liquidity_analysis,
            'include_price_action': include_price_action,
            'min_daily_volume': min_daily_volume,
            'sort_by': sort_by
        }

        if 'market_research' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['market_research'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def simulate_liquidity(self,
                          provision_type: str = 'Balanced',
                          token_a: str = None,
                          token_b: str = None,
                          token_a_units: Optional[str] = None,
                          token_b_units: Optional[str] = None,
                          pool_address: Optional[str] = None,
                          wallet_address: Optional[str] = None,
                          slippage_tolerance: float = 0.01,
                          simulate_multiple_scenarios: bool = False,
                          scenario_count: int = 3,
                          include_impermanent_loss: bool = True,
                          price_change_scenarios: List[float] = None) -> Dict[str, Any]:

        if price_change_scenarios is None:
            price_change_scenarios = [-0.1, 0.0, 0.1]

        context = {
            'provision_type': provision_type,
            'token_a': token_a,
            'token_b': token_b,
            'token_a_units': token_a_units,
            'token_b_units': token_b_units,
            'pool_address': pool_address,
            'wallet_address': wallet_address,
            'slippage_tolerance': slippage_tolerance,
            'simulate_multiple_scenarios': simulate_multiple_scenarios,
            'scenario_count': scenario_count,
            'include_impermanent_loss': include_impermanent_loss,
            'price_change_scenarios': price_change_scenarios
        }

        if 'simulate_liquidity' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['simulate_liquidity'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

def create_stonfi_agent(api_key: Optional[str] = None) -> StonFiAgent:
    return StonFiAgent(api_key=api_key)

class SimpleStonFiClient:
    def __init__(self, api_key: Optional[str] = None):
        from .components import StonFiClientComponent
        self.client = StonFiClientComponent(api_key=api_key)

    def analyze_pool(self, pool_address: str) -> Dict[str, Any]:
        return self.client.get_pool(pool_address)

    def analyze_asset(self, asset_address: str) -> Dict[str, Any]:
        return self.client.get_asset(asset_address)

    def test_connection(self) -> bool:
        try:
            return self.client.test_connection()
        except:
            return False

__all__ = [
    'StonFiPlugin',
    'StonFiAgent',
    'SimpleStonFiClient',
    'create_stonfi_agent',
    'StonFiClientComponent',
]
