from sidusai.core.plugin import AgentValue
from typing import Dict, Any
from datetime import datetime

class TONDataValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class TONWalletValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class TONTokenValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class TONNFTValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class TONStakingValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

class TONDomainValue(AgentValue):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.value = data

def get_account_skill(context: Dict[str, Any]) -> TONWalletValue:
    print("🔧 Starting get_account_skill...")

    account_id = context.get('account_id')

    if not account_id:
        result = {"error": "No account ID provided"}
        return TONWalletValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONWalletValue(result)

        print(f"📋 Getting account info: {account_id}")

        account_data = tonapi_component.get_account(account_id)

        if not account_data:
            result = {"error": f"Failed to get account info for {account_id}"}
            return TONWalletValue(result)

        result = {
            "success": True,
            "account_id": account_id,
            "data": account_data,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Account info retrieved")
        return TONWalletValue(result)

    except Exception as e:
        print(f"❌ Error in get_account_skill: {e}")
        result = {"error": f"Failed to get account info: {str(e)}"}
        return TONWalletValue(result)

def get_accounts_bulk_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_accounts_bulk_skill...")

    account_ids = context.get('account_ids', [])

    if not account_ids:
        result = {"error": "No account IDs provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"📋 Getting bulk account info for {len(account_ids)} accounts...")

        accounts_data = tonapi_component.get_accounts_bulk(account_ids)

        if not accounts_data:
            result = {"error": "Failed to get bulk account info"}
            return TONDataValue(result)

        result = {
            "success": True,
            "account_ids": account_ids,
            "data": accounts_data,
            "count": len(accounts_data.get('accounts', [])),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Bulk account info retrieved for {len(account_ids)} accounts")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_accounts_bulk_skill: {e}")
        result = {"error": f"Failed to get bulk account info: {str(e)}"}
        return TONDataValue(result)

def get_account_jettons_balances_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_account_jettons_balances_skill...")

    account_id = context.get('account_id')
    currencies = context.get('currencies', ["ton", "usd"])

    if not account_id:
        result = {"error": "No account ID provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"💰 Getting jettons balances for account: {account_id}")

        balances_data = tonapi_component.get_account_jettons_balances(account_id, currencies)

        if not balances_data:
            result = {"error": f"Failed to get jettons balances for account {account_id}"}
            return TONDataValue(result)

        result = {
            "success": True,
            "account_id": account_id,
            "data": balances_data,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Jettons balances retrieved")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_account_jettons_balances_skill: {e}")
        result = {"error": f"Failed to get jettons balances: {str(e)}"}
        return TONDataValue(result)

def get_account_nft_items_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_account_nft_items_skill...")

    account_id = context.get('account_id')
    collection = context.get('collection')
    limit = context.get('limit', 1000)
    offset = context.get('offset', 0)
    indirect_ownership = context.get('indirect_ownership', False)

    if not account_id:
        result = {"error": "No account ID provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"🖼️ Getting NFT items for account: {account_id}")

        nft_data = tonapi_component.get_account_nft_items(
            account_id, collection, limit, offset, indirect_ownership
        )

        if not nft_data:
            result = {"error": f"Failed to get NFT items for account {account_id}"}
            return TONDataValue(result)

        result = {
            "success": True,
            "account_id": account_id,
            "data": nft_data,
            "count": len(nft_data.get('nft_items', [])),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(nft_data.get('nft_items', []))} NFT items")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_account_nft_items_skill: {e}")
        result = {"error": f"Failed to get NFT items: {str(e)}"}
        return TONDataValue(result)

def get_account_events_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_account_events_skill...")

    account_id = context.get('account_id')
    limit = context.get('limit', 20)
    before_lt = context.get('before_lt')
    start_date = context.get('start_date')
    end_date = context.get('end_date')
    subject_only = context.get('subject_only', False)
    initiator = context.get('initiator', False)

    if not account_id:
        result = {"error": "No account ID provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"📊 Getting events for account: {account_id}")

        events_data = tonapi_component.get_account_events(
            account_id, limit, before_lt, start_date, end_date, subject_only, initiator
        )

        if not events_data:
            result = {"error": f"Failed to get events for account {account_id}"}
            return TONDataValue(result)

        result = {
            "success": True,
            "account_id": account_id,
            "data": events_data,
            "count": len(events_data.get('events', [])),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(events_data.get('events', []))} events")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_account_events_skill: {e}")
        result = {"error": f"Failed to get account events: {str(e)}"}
        return TONDataValue(result)

def get_account_subscriptions_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_account_subscriptions_skill...")

    account_id = context.get('account_id')

    if not account_id:
        result = {"error": "No account ID provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"🔔 Getting subscriptions for account: {account_id}")

        subscriptions_data = tonapi_component.get_account_subscriptions(account_id)

        if not subscriptions_data:
            result = {"error": f"Failed to get subscriptions for account {account_id}"}
            return TONDataValue(result)

        result = {
            "success": True,
            "account_id": account_id,
            "data": subscriptions_data,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Subscriptions retrieved")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_account_subscriptions_skill: {e}")
        result = {"error": f"Failed to get subscriptions: {str(e)}"}
        return TONDataValue(result)

def get_nft_collections_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_nft_collections_skill...")

    limit = context.get('limit', 100)
    offset = context.get('offset', 0)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"🖼️ Getting NFT collections...")

        collections_data = tonapi_component.get_nft_collections(limit, offset)

        if not collections_data:
            result = {"error": "Failed to get NFT collections"}
            return TONDataValue(result)

        result = {
            "success": True,
            "data": collections_data,
            "count": len(collections_data.get('nft_collections', [])),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(collections_data.get('nft_collections', []))} NFT collections")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_nft_collections_skill: {e}")
        result = {"error": f"Failed to get NFT collections: {str(e)}"}
        return TONDataValue(result)

def get_nft_collection_items_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_nft_collection_items_skill...")

    collection_id = context.get('collection_id')
    limit = context.get('limit', 1000)
    offset = context.get('offset', 0)

    if not collection_id:
        result = {"error": "No collection ID provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"🖼️ Getting items from collection: {collection_id}")

        items_data = tonapi_component.get_items_from_collection(collection_id, limit, offset)

        if not items_data:
            result = {"error": f"Failed to get items from collection {collection_id}"}
            return TONDataValue(result)

        result = {
            "success": True,
            "collection_id": collection_id,
            "data": items_data,
            "count": len(items_data.get('nft_items', [])),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(items_data.get('nft_items', []))} items from collection")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_nft_collection_items_skill: {e}")
        result = {"error": f"Failed to get collection items: {str(e)}"}
        return TONDataValue(result)

def get_nft_items_bulk_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_nft_items_bulk_skill...")

    nft_addresses = context.get('nft_addresses', [])

    if not nft_addresses:
        result = {"error": "No NFT addresses provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"🖼️ Getting NFT items in bulk for {len(nft_addresses)} addresses...")

        nft_data = tonapi_component.get_nft_items_by_addresses(nft_addresses)

        if not nft_data:
            result = {"error": "Failed to get NFT items in bulk"}
            return TONDataValue(result)

        result = {
            "success": True,
            "nft_addresses": nft_addresses,
            "data": nft_data,
            "count": len(nft_data.get('nft_items', [])),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(nft_data.get('nft_items', []))} NFT items in bulk")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_nft_items_bulk_skill: {e}")
        result = {"error": f"Failed to get NFT items in bulk: {str(e)}"}
        return TONDataValue(result)

def get_jettons_list_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_jettons_list_skill...")

    limit = context.get('limit', 100)
    offset = context.get('offset', 0)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"💰 Getting jettons list...")

        jettons_data = tonapi_component.get_jettons(limit, offset)

        if not jettons_data:
            result = {"error": "Failed to get jettons list"}
            return TONDataValue(result)

        result = {
            "success": True,
            "data": jettons_data,
            "count": len(jettons_data.get('jettons', [])),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(jettons_data.get('jettons', []))} jettons")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_jettons_list_skill: {e}")
        result = {"error": f"Failed to get jettons list: {str(e)}"}
        return TONDataValue(result)

def get_jettons_bulk_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_jettons_bulk_skill...")

    jetton_addresses = context.get('jetton_addresses', [])

    if not jetton_addresses:
        result = {"error": "No jetton addresses provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"💰 Getting jettons in bulk for {len(jetton_addresses)} addresses...")

        jettons_data = tonapi_component.get_jetton_infos_by_addresses(jetton_addresses)

        if not jettons_data:
            result = {"error": "Failed to get jettons in bulk"}
            return TONDataValue(result)

        result = {
            "success": True,
            "jetton_addresses": jetton_addresses,
            "data": jettons_data,
            "count": len(jettons_data.get('jettons', [])),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(jettons_data.get('jettons', []))} jettons in bulk")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_jettons_bulk_skill: {e}")
        result = {"error": f"Failed to get jettons in bulk: {str(e)}"}
        return TONDataValue(result)

def get_jetton_holders_full_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_jetton_holders_full_skill...")

    jetton_id = context.get('jetton_id')
    limit = context.get('limit', 1000)
    offset = context.get('offset', 0)

    if not jetton_id:
        result = {"error": "No jetton ID provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"👥 Getting holders for jetton: {jetton_id}")

        holders_data = tonapi_component.get_jetton_holders(jetton_id, limit, offset)

        if not holders_data:
            result = {"error": f"Failed to get holders for jetton {jetton_id}"}
            return TONDataValue(result)

        result = {
            "success": True,
            "jetton_id": jetton_id,
            "data": holders_data,
            "total_holders": holders_data.get('total', 0),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved holders data for jetton")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_jetton_holders_full_skill: {e}")
        result = {"error": f"Failed to get jetton holders: {str(e)}"}
        return TONDataValue(result)

def get_dns_info_skill(context: Dict[str, Any]) -> TONDomainValue:
    print("🔧 Starting get_dns_info_skill...")

    domain_name = context.get('domain_name')

    if not domain_name:
        result = {"error": "No domain name provided"}
        return TONDomainValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDomainValue(result)

        print(f"🌐 Getting DNS info for domain: {domain_name}")

        dns_data = tonapi_component.get_dns_info(domain_name)

        if not dns_data:
            result = {"error": f"Failed to get DNS info for domain {domain_name}"}
            return TONDomainValue(result)

        result = {
            "success": True,
            "domain_name": domain_name,
            "data": dns_data,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ DNS info retrieved for {domain_name}")
        return TONDomainValue(result)

    except Exception as e:
        print(f"❌ Error in get_dns_info_skill: {e}")
        result = {"error": f"Failed to get DNS info: {str(e)}"}
        return TONDomainValue(result)

def dns_resolve_skill(context: Dict[str, Any]) -> TONDomainValue:
    print("🔧 Starting dns_resolve_skill...")

    domain_name = context.get('domain_name')
    filter_results = context.get('filter', False)

    if not domain_name:
        result = {"error": "No domain name provided"}
        return TONDomainValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDomainValue(result)

        print(f"🌐 Resolving DNS for domain: {domain_name}")

        resolve_data = tonapi_component.dns_resolve(domain_name, filter_results)

        if not resolve_data:
            result = {"error": f"Failed to resolve DNS for domain {domain_name}"}
            return TONDomainValue(result)

        result = {
            "success": True,
            "domain_name": domain_name,
            "data": resolve_data,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ DNS resolved for {domain_name}")
        return TONDomainValue(result)

    except Exception as e:
        print(f"❌ Error in dns_resolve_skill: {e}")
        result = {"error": f"Failed to resolve DNS: {str(e)}"}
        return TONDomainValue(result)

def get_domain_bids_skill(context: Dict[str, Any]) -> TONDomainValue:
    print("🔧 Starting get_domain_bids_skill...")

    domain_name = context.get('domain_name')

    if not domain_name:
        result = {"error": "No domain name provided"}
        return TONDomainValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDomainValue(result)

        print(f"💰 Getting domain bids for: {domain_name}")

        bids_data = tonapi_component.get_domain_bids(domain_name)

        if not bids_data:
            result = {"error": f"Failed to get domain bids for {domain_name}"}
            return TONDomainValue(result)

        result = {
            "success": True,
            "domain_name": domain_name,
            "data": bids_data,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Domain bids retrieved for {domain_name}")
        return TONDomainValue(result)

    except Exception as e:
        print(f"❌ Error in get_domain_bids_skill: {e}")
        result = {"error": f"Failed to get domain bids: {str(e)}"}
        return TONDomainValue(result)

def get_rates_full_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_rates_full_skill...")

    tokens = context.get('tokens', ["ton"])
    currencies = context.get('currencies', ["USD", "EUR", "RUB"])

    if not tokens or not currencies:
        result = {"error": "Tokens and currencies lists must be provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"💰 Getting rates for {len(tokens)} tokens in {len(currencies)} currencies...")

        rates_data = tonapi_component.get_rates(tokens, currencies)

        if not rates_data:
            result = {"error": "Failed to get rates"}
            return TONDataValue(result)

        formatted_rates = {}
        for token, token_data in rates_data.get('rates', {}).items():
            formatted_rates[token] = {
                'prices': token_data.get('prices', {}),
                'diff_24h': token_data.get('diff_24h', 'N/A'),
                'diff_7d': token_data.get('diff_7d', 'N/A'),
                'diff_30d': token_data.get('diff_30d', 'N/A')
            }

        result = {
            "success": True,
            "tokens": tokens,
            "currencies": currencies,
            "rates": formatted_rates,
            "raw_data": rates_data,
            "timestamp": datetime.now().isoformat()
        }

        for token, token_data in formatted_rates.items():
            print(f"✅ {token.upper()}:")
            for currency, price in token_data['prices'].items():
                print(f"   {currency}: ${price:.4f}")
            if token_data.get('diff_24h'):
                print(f"   24h change: {token_data['diff_24h']}%")

        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_rates_full_skill: {e}")
        result = {"error": f"Failed to get rates: {str(e)}"}
        return TONDataValue(result)

def get_chart_rates_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_chart_rates_skill...")

    token = context.get('token')
    currency = context.get('currency', 'usd')
    start_date = context.get('start_date')
    end_date = context.get('end_date')
    points_count = context.get('points_count', 200)

    if not token:
        result = {"error": "No token provided"}
        return TONDataValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"📈 Getting chart rates for token: {token}")

        chart_data = tonapi_component.get_chart_rates(
            token, currency, start_date, end_date, points_count
        )

        if not chart_data:
            result = {"error": f"Failed to get chart rates for token {token}"}
            return TONDataValue(result)

        result = {
            "success": True,
            "token": token,
            "currency": currency,
            "data": chart_data,
            "points_count": len(chart_data.get('points', [])),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Chart rates retrieved with {len(chart_data.get('points', []))} points")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_chart_rates_skill: {e}")
        result = {"error": f"Failed to get chart rates: {str(e)}"}
        return TONDataValue(result)

def get_markets_rates_skill(context: Dict[str, Any]) -> TONDataValue:
    print("🔧 Starting get_markets_rates_skill...")

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONDataValue(result)

        print(f"🏪 Getting market rates...")

        markets_data = tonapi_component.get_markets_rates()

        if not markets_data:
            result = {"error": "Failed to get market rates"}
            return TONDataValue(result)

        result = {
            "success": True,
            "data": markets_data,
            "count": len(markets_data.get('markets', [])),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Market rates retrieved from {len(markets_data.get('markets', []))} markets")
        return TONDataValue(result)

    except Exception as e:
        print(f"❌ Error in get_markets_rates_skill: {e}")
        result = {"error": f"Failed to get market rates: {str(e)}"}
        return TONDataValue(result)

def get_staking_pools_skill(context: Dict[str, Any]) -> TONStakingValue:
    print("🔧 Starting get_staking_pools_skill...")

    available_for = context.get('available_for')
    include_unverified = context.get('include_unverified', False)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONStakingValue(result)

        print(f"🏦 Getting staking pools...")

        pools_data = tonapi_component.get_staking_pools(available_for, include_unverified)

        if not pools_data:
            result = {"error": "Failed to get staking pools"}
            return TONStakingValue(result)

        result = {
            "success": True,
            "data": pools_data,
            "count": len(pools_data.get('pools', [])),
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(pools_data.get('pools', []))} staking pools")
        return TONStakingValue(result)

    except Exception as e:
        print(f"❌ Error in get_staking_pools_skill: {e}")
        result = {"error": f"Failed to get staking pools: {str(e)}"}
        return TONStakingValue(result)

def get_staking_pool_info_skill(context: Dict[str, Any]) -> TONStakingValue:
    print("🔧 Starting get_staking_pool_info_skill...")

    pool_address = context.get('pool_address')

    if not pool_address:
        result = {"error": "No pool address provided"}
        return TONStakingValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONStakingValue(result)

        print(f"🏦 Getting staking pool info for: {pool_address}")

        response_data = tonapi_component.get_staking_pool_info(pool_address)

        if response_data is None:
            result = {
                "success": False,
                "error": "API returned None - pool may not exist",
                "pool_address": pool_address,
                "timestamp": datetime.now().isoformat()
            }
            return TONStakingValue(result)

        pool_data = response_data.get('pool') if 'pool' in response_data else response_data

        if not isinstance(pool_data, dict):
            result = {
                "success": False,
                "error": f"Invalid data format: {type(pool_data)}",
                "pool_address": pool_address,
                "timestamp": datetime.now().isoformat()
            }
            return TONStakingValue(result)

        if 'error' in pool_data:
            result = {
                "success": False,
                "error": pool_data.get('error', 'Unknown error'),
                "pool_address": pool_address,
                "timestamp": datetime.now().isoformat()
            }
            return TONStakingValue(result)

        min_stake_nano = pool_data.get('min_stake', 0)
        total_amount_nano = pool_data.get('total_amount', 0)
        profit_per_month_nano = pool_data.get('profit_per_month', 0)

        min_stake_ton = min_stake_nano / 1000000000 if min_stake_nano > 0 else 0
        total_amount_ton = total_amount_nano / 1000000000 if total_amount_nano > 0 else 0
        profit_per_month_ton = profit_per_month_nano / 1000000000 if profit_per_month_nano > 0 else 0

        current_nominators = pool_data.get('current_nominators', 0)
        average_stake_ton = total_amount_ton / current_nominators if current_nominators > 0 else 0

        metadata = pool_data.get('metadata', {})
        pool_name = metadata.get('name', pool_data.get('name', 'Unknown'))
        description = metadata.get('description', pool_data.get('description', ''))

        formatted_pool = {
            "address": pool_data.get('address', pool_address),
            "name": pool_name,
            "description": description,
            "implementation": pool_data.get('implementation', ''),
            "apy": pool_data.get('apy', 0),
            "min_stake": min_stake_ton,
            "total_amount": total_amount_ton,
            "current_nominators": current_nominators,
            "max_nominators": pool_data.get('max_nominators', 0),
            "verified": pool_data.get('verified', False),
            "cycle_start": pool_data.get('cycle_start', 0),
            "cycle_end": pool_data.get('cycle_end', 0),
            "profit_per_month": profit_per_month_ton,
            "average_stake": average_stake_ton,
            "metadata": metadata
        }

        result = {
            "success": True,
            "pool_address": pool_address,
            "pool_info": formatted_pool,
            "raw_response": response_data,
            "timestamp": datetime.now().isoformat()
        }

        if formatted_pool['total_amount'] > 0:
            print(f"✅ Staking pool info retrieved")
            print(f"   Name: {formatted_pool['name']}")
            print(f"   APY: {formatted_pool['apy']:.2f}%")
            print(f"   Min Stake: {formatted_pool['min_stake']:,.2f} TON")
            print(f"   Total Staked: {formatted_pool['total_amount']:,.2f} TON")
            print(f"   Nominators: {formatted_pool['current_nominators']:,}/{formatted_pool['max_nominators']:,}")
        else:
            print(f"⚠️  Pool data may be incomplete or pool is inactive")

        return TONStakingValue(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        result = {"error": f"Failed to get staking pool info: {str(e)}"}
        return TONStakingValue(result)

def get_account_nominators_pools_skill(context: Dict[str, Any]) -> TONStakingValue:
    print("🔧 Starting get_account_nominators_pools_skill...")

    account_id = context.get('account_id')

    if not account_id:
        result = {"error": "No account ID provided"}
        return TONStakingValue(result)

    try:
        tonapi_component = context.get('tonapi_component')
        if not tonapi_component:
            result = {"error": "TON API component not available"}
            return TONStakingValue(result)

        print(f"🏦 Getting nominator pools for account: {account_id}")

        pools_data = tonapi_component.get_account_nominators_pools(account_id)

        if not pools_data:
            result = {"error": f"API returned None for account {account_id}"}
            return TONStakingValue(result)

        pools = pools_data.get('pools', [])

        if not pools:
            result = {
                "success": True,
                "account_id": account_id,
                "pools": [],
                "total_pools": 0,
                "total_staked": 0,
                "timestamp": datetime.now().isoformat()
            }
            return TONStakingValue(result)

        formatted_pools = []
        total_staked_nano = 0

        for pool_info in pools:
            pool_address = pool_info.get('pool', '')
            amount_nano = pool_info.get('amount', 0)
            pending_deposit_nano = pool_info.get('pending_deposit', 0)
            pending_withdraw_nano = pool_info.get('pending_withdraw', 0)
            ready_withdraw_nano = pool_info.get('ready_withdraw', 0)

            amount_ton = amount_nano / 1_000_000_000
            pending_deposit_ton = pending_deposit_nano / 1_000_000_000
            pending_withdraw_ton = pending_withdraw_nano / 1_000_000_000
            ready_withdraw_ton = ready_withdraw_nano / 1_000_000_000

            total_staked_nano += amount_nano

            formatted_pool = {
                "pool_address": pool_address,
                "amount": amount_ton,
                "amount_nano": amount_nano,
                "pending_deposit": pending_deposit_ton,
                "pending_deposit_nano": pending_deposit_nano,
                "pending_withdraw": pending_withdraw_ton,
                "pending_withdraw_nano": pending_withdraw_nano,
                "ready_withdraw": ready_withdraw_ton,
                "ready_withdraw_nano": ready_withdraw_nano,
                "total": amount_ton + pending_deposit_ton - pending_withdraw_ton
            }

            formatted_pools.append(formatted_pool)

        total_staked_ton = total_staked_nano / 1_000_000_000

        result = {
            "success": True,
            "account_id": account_id,
            "pools": formatted_pools,
            "total_pools": len(formatted_pools),
            "total_staked": total_staked_ton,
            "total_staked_nano": total_staked_nano,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Retrieved {len(formatted_pools)} nominator pools")
        if formatted_pools:
            print(f"   Total staked: {total_staked_ton:,.2f} TON")
            for i, pool in enumerate(formatted_pools[:3]):
                print(f"   Pool {i+1}: {pool['pool_address']} - {pool['amount']:,.2f} TON")
            if len(formatted_pools) > 3:
                print(f"   ... and {len(formatted_pools) - 3} more pools")

        return TONStakingValue(result)

    except Exception as e:
        print(f"❌ Error in get_account_nominators_pools_skill: {e}")
        result = {"error": f"Failed to get nominator pools: {str(e)}"}
        return TONStakingValue(result)
