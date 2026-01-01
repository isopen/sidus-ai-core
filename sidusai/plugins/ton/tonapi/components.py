import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os
from enum import Enum

class TONAPIMethod(Enum):
    GET = "GET"
    POST = "POST"

@dataclass
class TONWallet:
    address: str
    balance: float
    balance_usd: float
    last_activity: datetime
    is_scam: bool
    is_wallet: bool
    status: str

@dataclass
class TONToken:
    address: str
    name: str
    symbol: str
    decimals: int
    total_supply: float
    market_cap_usd: Optional[float]
    volume_24h_usd: Optional[float]
    price_usd: Optional[float]
    holders: int
    is_verified: bool
    is_scam: bool

@dataclass
class TONTransaction:
    hash: str
    lt: int
    from_address: str
    to_address: str
    value: float
    fee: float
    timestamp: datetime
    message: Optional[str]
    operation: str

@dataclass
class TONNFTItem:
    address: str
    name: str
    description: str
    image: str
    collection_name: str
    collection_address: str
    owner_address: str
    is_for_sale: bool
    price: float
    price_token: str
    is_verified: bool
    is_scam: bool

@dataclass
class TONNFTCollection:
    address: str
    name: str
    description: str
    image: str
    items_count: int
    is_verified: bool
    is_scam: bool
    owner_address: str

@dataclass
class TONJettonHolder:
    address: str
    owner_address: str
    balance: int
    percentage: float
    is_scam: bool
    is_wallet: bool

@dataclass
class TONDomainInfo:
    name: str
    expiring_at: Optional[int]
    item: Optional[Dict[str, Any]]

@dataclass
class TONStakingPool:
    address: str
    name: str
    total_amount: int
    implementation: str
    apy: float
    min_stake: int
    cycle_start: int
    cycle_end: int
    verified: bool
    current_nominators: int
    max_nominators: int

@dataclass
class TONAccountEvent:
    event_id: str
    account: Dict[str, Any]
    timestamp: int
    actions: List[Dict[str, Any]]
    is_scam: bool
    lt: int
    in_progress: bool

class TONAPIClient:
    def __init__(self, api_key: str = None):
        self.api_url = "https://tonapi.io/v2"
        self.api_key = api_key or os.getenv('TONAPI_API_KEY')

        if not self.api_key:
            print("⚠️ Warning: No TON API key provided")
            print("ℹ️ Get API key from: https://tonconsole.com/")

        self.cache = {}
        self.cache_duration = 60

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def _make_request(self, method: TONAPIMethod, endpoint: str, params: Dict = None, 
                     data: Dict = None, use_cache: bool = True) -> Optional[Dict]:
        url = f"{self.api_url}/{endpoint}"
        cache_key = f"{method.value}:{endpoint}:{json.dumps(params) if params else 'no_params'}:{json.dumps(data) if data else 'no_data'}"

        if use_cache and method == TONAPIMethod.GET and cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return cached_data

        try:
            if method == TONAPIMethod.GET:
                response = self.session.get(url, params=params, timeout=30)
            elif method == TONAPIMethod.POST:
                response = self.session.post(url, json=data, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code == 200:
                data = response.json()
                if use_cache and method == TONAPIMethod.GET:
                    self.cache[cache_key] = (data, time.time())
                return data
            elif response.status_code == 429:
                print("⚠️ Rate limit exceeded, waiting 60 seconds...")
                time.sleep(60)
                return self._make_request(method, endpoint, params, data, use_cache)
            elif response.status_code == 401:
                print("❌ Invalid API key")
                return None
            else:
                print(f"⚠️ API Error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Request error: {e}")
            return None

    # Accounts API
    def get_account(self, account_id: str) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_accounts_bulk(self, account_ids: List[str]) -> Optional[Dict]:
        endpoint = "accounts/_bulk"
        data = {"account_ids": account_ids}
        return self._make_request(TONAPIMethod.POST, endpoint, data=data)

    def get_account_jettons_balances(self, account_id: str, currencies: List[str] = None) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/jettons"
        params = {}
        if currencies:
            params['currencies'] = ','.join(currencies)
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_account_jetton_balance(self, account_id: str, jetton_id: str, currencies: List[str] = None) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/jettons/{jetton_id}"
        params = {}
        if currencies:
            params['currencies'] = ','.join(currencies)
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_account_jettons_history(self, account_id: str, limit: int = 100, before_lt: Optional[int] = None) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/jettons/history"
        params = {'limit': limit}
        if before_lt:
            params['before_lt'] = before_lt
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_account_nft_items(self, account_id: str, collection: Optional[str] = None, 
                             limit: int = 1000, offset: int = 0, indirect_ownership: bool = False) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/nfts"
        params = {
            'limit': limit,
            'offset': offset,
            'indirect_ownership': indirect_ownership
        }
        if collection:
            params['collection'] = collection
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_account_nft_history(self, account_id: str, limit: int = 100, before_lt: Optional[int] = None) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/nfts/history"
        params = {'limit': limit}
        if before_lt:
            params['before_lt'] = before_lt
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_account_events(self, account_id: str, limit: int = 20, before_lt: Optional[int] = None,
                          start_date: Optional[int] = None, end_date: Optional[int] = None,
                          subject_only: bool = False, initiator: bool = False) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/events"
        params = {'limit': limit, 'subject_only': subject_only, 'initiator': initiator}
        if before_lt:
            params['before_lt'] = before_lt
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_account_event(self, account_id: str, event_id: str, subject_only: bool = False) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/events/{event_id}"
        params = {'subject_only': subject_only}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_account_traces(self, account_id: str, limit: int = 100, before_lt: Optional[int] = None) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/traces"
        params = {'limit': limit}
        if before_lt:
            params['before_lt'] = before_lt
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_account_subscriptions(self, account_id: str) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/subscriptions"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_account_dns_expiring(self, account_id: str, period: Optional[int] = None) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/dns/expiring"
        params = {}
        if period:
            params['period'] = period
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_account_public_key(self, account_id: str) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/publickey"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_account_multisigs(self, account_id: str) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/multisigs"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_account_diff(self, account_id: str, start_date: int, end_date: int) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/diff"
        params = {'start_date': start_date, 'end_date': end_date}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def account_dns_back_resolve(self, account_id: str) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/dns/backresolve"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def search_accounts(self, name: str) -> Optional[Dict]:
        endpoint = "accounts/search"
        params = {'name': name}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    # Blockchain API
    def get_blockchain_raw_account(self, account_id: str) -> Optional[Dict]:
        endpoint = f"blockchain/accounts/{account_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_blockchain_account_transactions(self, account_id: str, limit: int = 100,
                                           after_lt: Optional[int] = None,
                                           before_lt: Optional[int] = None,
                                           sort_order: str = 'desc') -> Optional[Dict]:
        endpoint = f"blockchain/accounts/{account_id}/transactions"
        params = {'limit': limit, 'sort_order': sort_order}
        if after_lt:
            params['after_lt'] = after_lt
        if before_lt:
            params['before_lt'] = before_lt
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def exec_get_method_for_blockchain_account(self, account_id: str, method_name: str,
                                              args: Optional[List[str]] = None) -> Optional[Dict]:
        endpoint = f"blockchain/accounts/{account_id}/methods/{method_name}"
        params = {}
        if args:
            params['args'] = args
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def exec_get_method_with_body_for_blockchain_account(self, account_id: str, method_name: str,
                                                        args: List[Dict]) -> Optional[Dict]:
        endpoint = f"blockchain/accounts/{account_id}/methods/{method_name}"
        return self._make_request(TONAPIMethod.POST, endpoint, data={'args': args})

    def get_blockchain_transaction(self, transaction_id: str) -> Optional[Dict]:
        endpoint = f"blockchain/transactions/{transaction_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_blockchain_transaction_by_message_hash(self, msg_id: str) -> Optional[Dict]:
        endpoint = f"blockchain/messages/{msg_id}/transaction"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_blockchain_block(self, block_id: str) -> Optional[Dict]:
        endpoint = f"blockchain/blocks/{block_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_blockchain_block_transactions(self, block_id: str) -> Optional[Dict]:
        endpoint = f"blockchain/blocks/{block_id}/transactions"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_blockchain_masterchain_head(self) -> Optional[Dict]:
        endpoint = "blockchain/masterchain-head"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_blockchain_validators(self) -> Optional[Dict]:
        endpoint = "blockchain/validators"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_blockchain_config(self) -> Optional[Dict]:
        endpoint = "blockchain/config"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_raw_blockchain_config(self) -> Optional[Dict]:
        endpoint = "blockchain/config/raw"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def blockchain_account_inspect(self, account_id: str) -> Optional[Dict]:
        endpoint = f"blockchain/accounts/{account_id}/inspect"
        return self._make_request(TONAPIMethod.GET, endpoint)

    # NFT API
    def get_nft_collections(self, limit: int = 100, offset: int = 0) -> Optional[Dict]:
        endpoint = "nfts/collections"
        params = {'limit': limit, 'offset': offset}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_nft_collection(self, account_id: str) -> Optional[Dict]:
        endpoint = f"nfts/collections/{account_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_nft_collection_items_by_addresses(self, account_ids: List[str]) -> Optional[Dict]:
        endpoint = "nfts/collections/_bulk"
        data = {"account_ids": account_ids}
        return self._make_request(TONAPIMethod.POST, endpoint, data=data)

    def get_items_from_collection(self, account_id: str, limit: int = 1000, offset: int = 0) -> Optional[Dict]:
        endpoint = f"nfts/collections/{account_id}/items"
        params = {'limit': limit, 'offset': offset}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_nft_items_by_addresses(self, account_ids: List[str]) -> Optional[Dict]:
        endpoint = "nfts/_bulk"
        data = {"account_ids": account_ids}
        return self._make_request(TONAPIMethod.POST, endpoint, data=data)

    def get_nft_item_by_address(self, account_id: str) -> Optional[Dict]:
        endpoint = f"nfts/{account_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    # Jettons API
    def get_jettons(self, limit: int = 100, offset: int = 0) -> Optional[Dict]:
        endpoint = "jettons"
        params = {'limit': limit, 'offset': offset}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_jetton_info(self, account_id: str) -> Optional[Dict]:
        endpoint = f"jettons/{account_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_jetton_infos_by_addresses(self, account_ids: List[str]) -> Optional[Dict]:
        endpoint = "jettons/_bulk"
        data = {"account_ids": account_ids}
        return self._make_request(TONAPIMethod.POST, endpoint, data=data)

    def get_jetton_holders(self, account_id: str, limit: int = 1000, offset: int = 0) -> Optional[Dict]:
        endpoint = f"jettons/{account_id}/holders"
        params = {'limit': limit}
        if offset:
            params['offset'] = offset
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_jetton_transfer_payload(self, jetton_id: str, account_id: str) -> Optional[Dict]:
        endpoint = f"jettons/{jetton_id}/transfer/{account_id}/payload"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_jetton_account_history_by_id(self, jetton_id: str, account_id: str, limit: int = 100,
                                        before_lt: Optional[int] = None,
                                        start_date: Optional[int] = None,
                                        end_date: Optional[int] = None) -> Optional[Dict]:
        endpoint = f"jettons/{jetton_id}/accounts/{account_id}/history"
        params = {'limit': limit}
        if before_lt:
            params['before_lt'] = before_lt
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    # DNS API
    def get_dns_info(self, domain_name: str) -> Optional[Dict]:
        endpoint = f"dns/{domain_name}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def dns_resolve(self, domain_name: str, filter: bool = False) -> Optional[Dict]:
        endpoint = f"dns/{domain_name}/resolve"
        params = {'filter': filter}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_domain_bids(self, domain_name: str) -> Optional[Dict]:
        endpoint = f"dns/{domain_name}/bids"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_all_auctions(self, tld: Optional[str] = None) -> Optional[Dict]:
        endpoint = "dns/auctions"
        params = {}
        if tld:
            params['tld'] = tld
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    # Rates API
    def get_rates(self, tokens: List[str], currencies: List[str]) -> Optional[Dict]:
        endpoint = "rates"
        params = {
            'tokens': ','.join(tokens),
            'currencies': ','.join(currencies)
        }
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_chart_rates(self, token: str, currency: Optional[str] = None,
                       start_date: Optional[int] = None, end_date: Optional[int] = None,
                       points_count: int = 200) -> Optional[Dict]:
        endpoint = "rates/chart"
        params = {'token': token, 'points_count': points_count}
        if currency:
            params['currency'] = currency
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_markets_rates(self) -> Optional[Dict]:
        endpoint = "rates/markets"
        return self._make_request(TONAPIMethod.GET, endpoint)

    # Staking API
    def get_account_nominators_pools(self, account_id: str) -> Optional[Dict]:
        endpoint = f"staking/nominator/{account_id}/pools"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_staking_pool_info(self, account_id: str) -> Optional[Dict]:
        endpoint = f"staking/pool/{account_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_staking_pool_history(self, account_id: str) -> Optional[Dict]:
        endpoint = f"staking/pool/{account_id}/history"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_staking_pools(self, available_for: Optional[str] = None,
                         include_unverified: bool = False) -> Optional[Dict]:
        endpoint = "staking/pools"
        params = {'include_unverified': include_unverified}
        if available_for:
            params['available_for'] = available_for
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    # Storage API
    def get_storage_providers(self) -> Optional[Dict]:
        endpoint = "storage/providers"
        return self._make_request(TONAPIMethod.GET, endpoint)

    # Traces API
    def get_trace(self, trace_id: str) -> Optional[Dict]:
        endpoint = f"traces/{trace_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    # Events API
    def get_event(self, event_id: str) -> Optional[Dict]:
        endpoint = f"events/{event_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_jettons_events(self, event_id: str) -> Optional[Dict]:
        endpoint = f"events/{event_id}/jettons"
        return self._make_request(TONAPIMethod.GET, endpoint)

    # Wallet API
    def get_wallet_info(self, account_id: str) -> Optional[Dict]:
        endpoint = f"wallet/{account_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_account_seqno(self, account_id: str) -> Optional[Dict]:
        endpoint = f"wallet/{account_id}/seqno"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_wallets_by_public_key(self, public_key: str) -> Optional[Dict]:
        endpoint = f"pubkeys/{public_key}/wallets"
        return self._make_request(TONAPIMethod.GET, endpoint)

    # Connect API
    def get_ton_connect_payload(self) -> Optional[Dict]:
        endpoint = "tonconnect/payload"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_account_info_by_state_init(self, state_init: str) -> Optional[Dict]:
        endpoint = "tonconnect/stateinit"
        data = {"state_init": state_init}
        return self._make_request(TONAPIMethod.POST, endpoint, data=data)

    def ton_connect_proof(self, address: str, proof: Dict) -> Optional[Dict]:
        endpoint = "wallet/auth/proof"
        data = {"address": address, "proof": proof}
        return self._make_request(TONAPIMethod.POST, endpoint, data=data)

    # Gasless API
    def gasless_config(self) -> Optional[Dict]:
        endpoint = "gasless/config"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def gasless_estimate(self, master_id: str, messages: List[Dict], wallet_address: str,
                        wallet_public_key: str, throw_error_if_not_enough_jettons: bool = False,
                        return_emulation: bool = False) -> Optional[Dict]:
        endpoint = f"gasless/estimate/{master_id}"
        data = {
            "messages": messages,
            "wallet_address": wallet_address,
            "wallet_public_key": wallet_public_key,
            "throw_error_if_not_enough_jettons": throw_error_if_not_enough_jettons,
            "return_emulation": return_emulation
        }
        return self._make_request(TONAPIMethod.POST, endpoint, data=data)

    def gasless_send(self, boc: str, wallet_public_key: str) -> Optional[Dict]:
        endpoint = "gasless/send"
        data = {
            "boc": boc,
            "wallet_public_key": wallet_public_key
        }
        return self._make_request(TONAPIMethod.POST, endpoint, data=data)

    # Multisig API
    def get_multisig_account(self, account_id: str) -> Optional[Dict]:
        endpoint = f"multisig/{account_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_multisig_order(self, account_id: str) -> Optional[Dict]:
        endpoint = f"multisig/order/{account_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    # Emulation API
    def decode_message(self, boc: str) -> Optional[Dict]:
        endpoint = "message/decode"
        data = {"boc": boc}
        return self._make_request(TONAPIMethod.POST, endpoint, data=data)

    def emulate_message_to_event(self, boc: str, ignore_signature_check: bool = False) -> Optional[Dict]:
        endpoint = "events/emulate"
        params = {'ignore_signature_check': ignore_signature_check}
        data = {"boc": boc}
        return self._make_request(TONAPIMethod.POST, endpoint, params=params, data=data)

    def emulate_message_to_trace(self, boc: str, ignore_signature_check: bool = False) -> Optional[Dict]:
        endpoint = "traces/emulate"
        params = {'ignore_signature_check': ignore_signature_check}
        data = {"boc": boc}
        return self._make_request(TONAPIMethod.POST, endpoint, params=params, data=data)

    def emulate_message_to_wallet(self, boc: str, currency: Optional[str] = None) -> Optional[Dict]:
        endpoint = "wallet/emulate"
        params = {}
        if currency:
            params['currency'] = currency
        data = {"boc": boc}
        return self._make_request(TONAPIMethod.POST, endpoint, params=params, data=data)

    def emulate_message_to_account_event(self, account_id: str, boc: str,
                                        ignore_signature_check: bool = False) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/events/emulate"
        params = {'ignore_signature_check': ignore_signature_check}
        data = {"boc": boc}
        return self._make_request(TONAPIMethod.POST, endpoint, params=params, data=data)

    # Purchases API
    def get_purchase_history(self, account_id: str, limit: int = 100,
                            before_lt: Optional[int] = None) -> Optional[Dict]:
        endpoint = f"purchases/{account_id}/history"
        params = {'limit': limit}
        if before_lt:
            params['before_lt'] = before_lt
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    # ExtraCurrency API
    def get_extra_currency_info(self, id: int) -> Optional[Dict]:
        endpoint = f"extra-currency/{id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_account_extra_currency_history_by_id(self, account_id: str, id: int, limit: int = 100,
                                                before_lt: Optional[int] = None,
                                                start_date: Optional[int] = None,
                                                end_date: Optional[int] = None) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/extra-currency/{id}/history"
        params = {'limit': limit}
        if before_lt:
            params['before_lt'] = before_lt
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    # Lite Server API
    def get_raw_masterchain_info(self) -> Optional[Dict]:
        endpoint = "liteserver/get_masterchain_info"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_raw_masterchain_info_ext(self, mode: int) -> Optional[Dict]:
        endpoint = "liteserver/get_masterchain_info_ext"
        params = {'mode': mode}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_raw_time(self) -> Optional[Dict]:
        endpoint = "liteserver/get_time"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_raw_blockchain_block(self, block_id: str) -> Optional[Dict]:
        endpoint = f"liteserver/get_block/{block_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_raw_blockchain_block_state(self, block_id: str) -> Optional[Dict]:
        endpoint = f"liteserver/get_state/{block_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_raw_blockchain_block_header(self, block_id: str, mode: int) -> Optional[Dict]:
        endpoint = f"liteserver/get_block_header/{block_id}"
        params = {'mode': mode}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def send_raw_message(self, body: str) -> Optional[Dict]:
        endpoint = "liteserver/send_message"
        data = {"body": body}
        return self._make_request(TONAPIMethod.POST, endpoint, data=data)

    def get_raw_account_state(self, account_id: str, target_block: Optional[str] = None) -> Optional[Dict]:
        endpoint = f"liteserver/get_account_state/{account_id}"
        params = {}
        if target_block:
            params['target_block'] = target_block
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_raw_shard_info(self, block_id: str, workchain: int, shard: int, exact: bool) -> Optional[Dict]:
        endpoint = f"liteserver/get_shard_info/{block_id}"
        params = {'workchain': workchain, 'shard': shard, 'exact': exact}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_all_raw_shards_info(self, block_id: str) -> Optional[Dict]:
        endpoint = f"liteserver/get_all_shards_info/{block_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_raw_transactions(self, account_id: str, count: int, lt: int, hash: str) -> Optional[Dict]:
        endpoint = f"liteserver/get_transactions/{account_id}"
        params = {'count': count, 'lt': lt, 'hash': hash}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_raw_list_block_transactions(self, block_id: str, mode: int, count: int,
                                       account_id: Optional[str] = None,
                                       lt: Optional[int] = None) -> Optional[Dict]:
        endpoint = f"liteserver/list_block_transactions/{block_id}"
        params = {'mode': mode, 'count': count}
        if account_id:
            params['account_id'] = account_id
        if lt:
            params['lt'] = lt
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_raw_block_proof(self, known_block: str, target_block: Optional[str] = None,
                           mode: int = 0) -> Optional[Dict]:
        endpoint = "liteserver/get_block_proof"
        params = {'known_block': known_block, 'mode': mode}
        if target_block:
            params['target_block'] = target_block
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_raw_config(self, block_id: str, mode: int) -> Optional[Dict]:
        endpoint = f"liteserver/get_config_all/{block_id}"
        params = {'mode': mode}
        return self._make_request(TONAPIMethod.GET, endpoint, params=params)

    def get_raw_shard_block_proof(self, block_id: str) -> Optional[Dict]:
        endpoint = f"liteserver/get_shard_block_proof/{block_id}"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_out_msg_queue_sizes(self) -> Optional[Dict]:
        endpoint = "liteserver/get_out_msg_queue_sizes"
        return self._make_request(TONAPIMethod.GET, endpoint)

    # Utilities
    def get_status(self) -> Optional[Dict]:
        endpoint = "status"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def get_openapi_json(self) -> Optional[Dict]:
        endpoint = "v2/openapi.json"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def address_parse(self, account_id: str) -> Optional[Dict]:
        endpoint = f"address/{account_id}/parse"
        return self._make_request(TONAPIMethod.GET, endpoint)

    def reindex_account(self, account_id: str) -> Optional[Dict]:
        endpoint = f"accounts/{account_id}/reindex"
        return self._make_request(TONAPIMethod.POST, endpoint)

    def test_connection(self) -> bool:
        if not self.api_key:
            print("❌ No API key provided for TON API")
            return False

        try:
            data = self.get_status()
            return data is not None
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
