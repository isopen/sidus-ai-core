import sidusai as sai
from typing import Optional, Dict, Any, List
import os
from .components import TONAPIClient, TONWallet, TONToken, TONTransaction, TONNFTItem, TONNFTCollection, TONJettonHolder, TONDomainInfo, TONStakingPool, TONAccountEvent
from .skills import (
    get_account_skill,
    get_accounts_bulk_skill,
    get_account_jettons_balances_skill,
    get_account_nft_items_skill,
    get_account_events_skill,
    get_account_subscriptions_skill,
    get_nft_collections_skill,
    get_nft_collection_items_skill,
    get_nft_items_bulk_skill,
    get_jettons_list_skill,
    get_jettons_bulk_skill,
    get_jetton_holders_full_skill,
    get_dns_info_skill,
    dns_resolve_skill,
    get_domain_bids_skill,
    get_rates_full_skill,
    get_chart_rates_skill,
    get_markets_rates_skill,
    get_staking_pools_skill,
    get_staking_pool_info_skill,
    get_account_nominators_pools_skill,
    TONDataValue,
    TONWalletValue,
    TONTokenValue,
    TONNFTValue,
    TONStakingValue,
    TONDomainValue
)

__tonapi_agent_name__ = 'tonapi_agent'

class TONAPIPlugin(sai.AgentPlugin):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv('TONAPI_API_KEY')
        self.tonapi_client = None
        print(f"🔧 TON API Plugin initialized")

        if self.api_key and not os.getenv('TONAPI_API_KEY'):
            os.environ['TONAPI_API_KEY'] = self.api_key

    def apply_plugin(self, agent: sai.Agent):
        print("🔧 Applying TON API plugin to agent...")

        try:
            self.tonapi_client = TONAPIClient(api_key=self.api_key)

            if self.tonapi_client.test_connection():
                print("✅ TON API connection successful")
            else:
                print("⚠️ TON API connection issues - some features may not work")

            self.skills = {}

            # Accounts API Skills
            def account_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_account_skill(context)
                return TONWalletValue(result.value)

            def accounts_bulk_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_accounts_bulk_skill(context)
                return TONDataValue(result.value)

            def account_jettons_balances_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_account_jettons_balances_skill(context)
                return TONDataValue(result.value)

            def account_nft_items_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_account_nft_items_skill(context)
                return TONDataValue(result.value)

            def account_events_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_account_events_skill(context)
                return TONDataValue(result.value)

            def account_subscriptions_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_account_subscriptions_skill(context)
                return TONDataValue(result.value)

            # NFT API Skills
            def nft_collections_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_nft_collections_skill(context)
                return TONDataValue(result.value)

            def nft_collection_items_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_nft_collection_items_skill(context)
                return TONDataValue(result.value)

            def nft_items_bulk_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_nft_items_bulk_skill(context)
                return TONDataValue(result.value)

            # Jettons API Skills
            def jettons_list_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_jettons_list_skill(context)
                return TONDataValue(result.value)

            def jettons_bulk_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_jettons_bulk_skill(context)
                return TONDataValue(result.value)

            def jetton_holders_full_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_jetton_holders_full_skill(context)
                return TONDataValue(result.value)

            # DNS API Skills
            def dns_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_dns_info_skill(context)
                return TONDomainValue(result.value)

            def dns_resolve_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = dns_resolve_skill(context)
                return TONDomainValue(result.value)

            def domain_bids_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_domain_bids_skill(context)
                return TONDomainValue(result.value)

            # Rates API Skills
            def rates_full_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_rates_full_skill(context)
                return TONDataValue(result.value)

            def chart_rates_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_chart_rates_skill(context)
                return TONDataValue(result.value)

            def markets_rates_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_markets_rates_skill(context)
                return TONDataValue(result.value)

            # Staking API Skills
            def staking_pools_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_staking_pools_skill(context)
                return TONStakingValue(result.value)

            def staking_pool_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_staking_pool_info_skill(context)
                return TONStakingValue(result.value)

            def account_nominators_pools_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                context = agent_value.value
                context['tonapi_component'] = self.tonapi_client
                result = get_account_nominators_pools_skill(context)
                return TONStakingValue(result.value)

            self.skills = {
                # Accounts API
                'get_account': account_wrapper,
                'get_accounts_bulk': accounts_bulk_wrapper,
                'get_account_jettons_balances': account_jettons_balances_wrapper,
                'get_account_nft_items': account_nft_items_wrapper,
                'get_account_events': account_events_wrapper,
                'get_account_subscriptions': account_subscriptions_wrapper,

                # NFT API
                'get_nft_collections': nft_collections_wrapper,
                'get_nft_collection_items': nft_collection_items_wrapper,
                'get_nft_items_bulk': nft_items_bulk_wrapper,

                # Jettons API
                'get_jettons_list': jettons_list_wrapper,
                'get_jettons_bulk': jettons_bulk_wrapper,
                'get_jetton_holders_full': jetton_holders_full_wrapper,

                # DNS API
                'get_dns_info': dns_info_wrapper,
                'dns_resolve': dns_resolve_wrapper,
                'get_domain_bids': domain_bids_wrapper,

                # Rates API
                'get_rates_full': rates_full_wrapper,
                'get_chart_rates': chart_rates_wrapper,
                'get_markets_rates': markets_rates_wrapper,

                # Staking API
                'get_staking_pools': staking_pools_wrapper,
                'get_staking_pool_info': staking_pool_info_wrapper,
                'get_account_nominators_pools': account_nominators_pools_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.tonapi_client = self.tonapi_client
            agent.tonapi_skills = self.skills

            print(f"✅ TON API plugin applied successfully with {len(self.skills)} skills")

        except Exception as e:
            print(f"❌ Error applying TON API plugin: {e}")
            import traceback
            traceback.print_exc()

class TONAPIAgent(sai.Agent):
    def __init__(self, api_key: Optional[str] = None, name: str = __tonapi_agent_name__):
        super().__init__()
        self._name = name

        print(f"🤖 Creating TON API Agent '{name}'...")
        self.plugin = TONAPIPlugin(api_key=api_key)
        self.plugin.apply_plugin(self)

        print(f"✅ TON API Agent '{name}' created successfully")

    @property
    def name(self):
        """Get agent name"""
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        try:
            return sai.AgentValue(value=context)
        except TypeError:
            agent_value = sai.AgentValue()
            agent_value.value = context
            return agent_value

    # Accounts API Methods
    def get_account(self, account_id: str) -> Dict[str, Any]:
        context = {'account_id': account_id}
        if 'get_account' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_account'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_accounts_bulk(self, account_ids: List[str]) -> Dict[str, Any]:
        context = {'account_ids': account_ids}
        if 'get_accounts_bulk' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_accounts_bulk'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_account_jettons_balances(self, account_id: str, currencies: List[str] = None) -> Dict[str, Any]:
        context = {'account_id': account_id}
        if currencies:
            context['currencies'] = currencies
        if 'get_account_jettons_balances' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_account_jettons_balances'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_account_nft_items(self, account_id: str, collection: Optional[str] = None, 
                               limit: int = 1000, offset: int = 0, indirect_ownership: bool = False) -> Dict[str, Any]:
        context = {
            'account_id': account_id,
            'limit': limit,
            'offset': offset,
            'indirect_ownership': indirect_ownership
        }
        if collection:
            context['collection'] = collection
        if 'get_account_nft_items' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_account_nft_items'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_account_events(self, account_id: str, limit: int = 20, before_lt: Optional[int] = None,
                          start_date: Optional[int] = None, end_date: Optional[int] = None,
                          subject_only: bool = False, initiator: bool = False) -> Dict[str, Any]:
        context = {
            'account_id': account_id,
            'limit': limit,
            'subject_only': subject_only,
            'initiator': initiator
        }
        if before_lt:
            context['before_lt'] = before_lt
        if start_date:
            context['start_date'] = start_date
        if end_date:
            context['end_date'] = end_date
        if 'get_account_events' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_account_events'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_account_subscriptions(self, account_id: str) -> Dict[str, Any]:
        context = {'account_id': account_id}
        if 'get_account_subscriptions' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_account_subscriptions'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    # NFT API Methods
    def get_nft_collections(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        context = {'limit': limit, 'offset': offset}
        if 'get_nft_collections' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_nft_collections'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_nft_collection_items(self, collection_id: str, limit: int = 1000, offset: int = 0) -> Dict[str, Any]:
        context = {
            'collection_id': collection_id,
            'limit': limit,
            'offset': offset
        }
        if 'get_nft_collection_items' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_nft_collection_items'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_nft_items_bulk(self, nft_addresses: List[str]) -> Dict[str, Any]:
        context = {'nft_addresses': nft_addresses}
        if 'get_nft_items_bulk' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_nft_items_bulk'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    # Jettons API Methods
    def get_jettons_list(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        context = {'limit': limit, 'offset': offset}
        if 'get_jettons_list' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_jettons_list'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_jettons_bulk(self, jetton_addresses: List[str]) -> Dict[str, Any]:
        context = {'jetton_addresses': jetton_addresses}
        if 'get_jettons_bulk' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_jettons_bulk'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_jetton_holders_full(self, jetton_id: str, limit: int = 1000, offset: int = 0) -> Dict[str, Any]:
        context = {
            'jetton_id': jetton_id,
            'limit': limit,
            'offset': offset
        }
        if 'get_jetton_holders_full' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_jetton_holders_full'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    # DNS API Methods
    def get_dns_info(self, domain_name: str) -> Dict[str, Any]:
        context = {'domain_name': domain_name}
        if 'get_dns_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_dns_info'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def dns_resolve(self, domain_name: str, filter_results: bool = False) -> Dict[str, Any]:
        context = {'domain_name': domain_name, 'filter': filter_results}
        if 'dns_resolve' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['dns_resolve'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_domain_bids(self, domain_name: str) -> Dict[str, Any]:
        context = {'domain_name': domain_name}
        if 'get_domain_bids' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_domain_bids'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    # Rates API Methods
    def get_rates_full(self, tokens: List[str], currencies: List[str]) -> Dict[str, Any]:
        context = {'tokens': tokens, 'currencies': currencies}
        if 'get_rates_full' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_rates_full'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_chart_rates(self, token: str, currency: str = 'usd', 
                         start_date: Optional[int] = None, end_date: Optional[int] = None,
                         points_count: int = 200) -> Dict[str, Any]:
        context = {
            'token': token,
            'currency': currency,
            'points_count': points_count
        }
        if start_date:
            context['start_date'] = start_date
        if end_date:
            context['end_date'] = end_date
        if 'get_chart_rates' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_chart_rates'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_markets_rates(self) -> Dict[str, Any]:
        context = {}
        if 'get_markets_rates' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_markets_rates'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    # Staking API Methods
    def get_staking_pools(self, available_for: Optional[str] = None, 
                           include_unverified: bool = False) -> Dict[str, Any]:
        context = {'include_unverified': include_unverified}
        if available_for:
            context['available_for'] = available_for
        if 'get_staking_pools' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_staking_pools'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_staking_pool_info(self, pool_address: str) -> Dict[str, Any]:
        context = {'pool_address': pool_address}
        if 'get_staking_pool_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_staking_pool_info'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

    def get_account_nominators_pools(self, account_id: str) -> Dict[str, Any]:
        context = {'account_id': account_id}
        if 'get_account_nominators_pools' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_account_nominators_pools'](agent_value)
            return result.value if hasattr(result, 'value') else result
        else:
            return {"error": "Skill not available"}

def create_tonapi_agent(api_key: Optional[str] = None) -> TONAPIAgent:
    return TONAPIAgent(api_key=api_key)

class SimpleTONAPIClient:
    def __init__(self, api_key: Optional[str] = None):
        from .components import TONAPIClient

        actual_api_key = api_key or os.getenv('TONAPI_API_KEY')

        if actual_api_key and not os.getenv('TONAPI_API_KEY'):
            os.environ['TONAPI_API_KEY'] = actual_api_key

        self.client = TONAPIClient(api_key=actual_api_key)

    # Accounts API
    def get_account(self, account_id: str) -> Optional[Dict]:
        return self.client.get_account(account_id)

    def get_accounts_bulk(self, account_ids: List[str]) -> Optional[Dict]:
        return self.client.get_accounts_bulk(account_ids)

    def get_account_jettons_balances(self, account_id: str, currencies: List[str] = None) -> Optional[Dict]:
        return self.client.get_account_jettons_balances(account_id, currencies)

    def get_account_nft_items(self, account_id: str, collection: Optional[str] = None, 
                               limit: int = 1000, offset: int = 0, indirect_ownership: bool = False) -> Optional[Dict]:
        return self.client.get_account_nft_items(account_id, collection, limit, offset, indirect_ownership)

    def get_account_events(self, account_id: str, limit: int = 20, before_lt: Optional[int] = None,
                          start_date: Optional[int] = None, end_date: Optional[int] = None,
                          subject_only: bool = False, initiator: bool = False) -> Optional[Dict]:
        return self.client.get_account_events(account_id, limit, before_lt, start_date, end_date, subject_only, initiator)

    # NFT API
    def get_nft_collections(self, limit: int = 100, offset: int = 0) -> Optional[List[Dict]]:
        result = self.client.get_nft_collections(limit, offset)
        return result.get('nft_collections') if result else None

    def get_nft_collection(self, account_id: str) -> Optional[Dict]:
        return self.client.get_nft_collection(account_id)

    def get_items_from_collection(self, account_id: str, limit: int = 1000, offset: int = 0) -> Optional[Dict]:
        return self.client.get_items_from_collection(account_id, limit, offset)

    # Jettons API
    def get_jettons(self, limit: int = 100, offset: int = 0) -> Optional[List[Dict]]:
        result = self.client.get_jettons(limit, offset)
        return result.get('jettons') if result else None

    def get_jetton_info(self, account_id: str) -> Optional[Dict]:
        return self.client.get_jetton_info(account_id)

    def get_jetton_holders(self, jetton_address: str, limit: int = 10) -> Optional[List[Dict]]:
        result = self.client.get_jetton_holders(jetton_address, limit)
        return result.get('addresses') if result else None

    # DNS API
    def get_dns_info(self, domain_name: str) -> Optional[Dict]:
        return self.client.get_dns_info(domain_name)

    def dns_resolve(self, domain_name: str, filter_results: bool = False) -> Optional[Dict]:
        return self.client.dns_resolve(domain_name, filter_results)

    # Rates API
    def get_rates(self, tokens: List[str], currencies: List[str]) -> Optional[Dict]:
        return self.client.get_rates(tokens, currencies)

    def get_chart_rates(self, token: str, currency: Optional[str] = None,
                         start_date: Optional[int] = None, end_date: Optional[int] = None,
                         points_count: int = 200) -> Optional[Dict]:
        return self.client.get_chart_rates(token, currency, start_date, end_date, points_count)

    # Staking API
    def get_staking_pools(self, available_for: Optional[str] = None,
                           include_unverified: bool = False) -> Optional[Dict]:
        return self.client.get_staking_pools(available_for, include_unverified)

    def get_staking_pool_info(self, account_id: str) -> Optional[Dict]:
        return self.client.get_staking_pool_info(account_id)

    def test_connection(self) -> bool:
        return self.client.test_connection()


__all__ = [
    'TONAPIPlugin',
    'TONAPIAgent',
    'SimpleTONAPIClient',
    'create_tonapi_agent',
    'TONAPIClient',
    'TONWallet',
    'TONToken',
    'TONTransaction',
    'TONNFTItem',
    'TONNFTCollection',
    'TONJettonHolder',
    'TONDomainInfo',
    'TONStakingPool',
    'TONAccountEvent',
    # Skills
    'get_account_skill',
    'get_accounts_bulk_skill',
    'get_account_jettons_balances_skill',
    'get_account_nft_items_skill',
    'get_account_events_skill',
    'get_account_subscriptions_skill',
    'get_nft_collections_skill',
    'get_nft_collection_items_skill',
    'get_nft_items_bulk_skill',
    'get_jettons_list_skill',
    'get_jettons_bulk_skill',
    'get_jetton_holders_full_skill',
    'get_dns_info_skill',
    'dns_resolve_skill',
    'get_domain_bids_skill',
    'get_rates_full_skill',
    'get_chart_rates_skill',
    'get_markets_rates_skill',
    'get_staking_pools_skill',
    'get_staking_pool_info_skill',
    'get_account_nominators_pools_skill',
    # Values
    'TONDataValue',
    'TONWalletValue',
    'TONTokenValue',
    'TONNFTValue',
    'TONStakingValue',
    'TONDomainValue',
]
