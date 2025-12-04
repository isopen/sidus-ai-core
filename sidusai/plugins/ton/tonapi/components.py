import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os

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

    def _make_request(self, endpoint: str, params: Dict = None, use_cache: bool = True) -> Optional[Dict]:
        url = f"{self.api_url}/{endpoint}"
        cache_key = f"{endpoint}:{json.dumps(params) if params else 'no_params'}"

        if use_cache and cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return cached_data

        try:
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if use_cache:
                    self.cache[cache_key] = (data, time.time())
                return data
            elif response.status_code == 429:
                print("⚠️ Rate limit exceeded, waiting 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint, params, use_cache)
            elif response.status_code == 401:
                print("❌ Invalid API key")
                return None
            else:
                print(f"⚠️ API Error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Request error: {e}")
            return None

    def get_ton_price(self, currencies: List[str] = ["USD", "EUR", "RUB"]) -> Dict[str, Any]:
        endpoint = "rates"
        params = {
            'tokens': 'ton',
            'currencies': ','.join(currencies)
        }

        data = self._make_request(endpoint, params)
        if not data or 'rates' not in data:
            return {'prices': {}, 'timestamp': datetime.now().isoformat(), 'source': 'TON API'}

        ton_data = data['rates'].get('TON', {})
        prices_data = ton_data.get('prices', {})

        prices = {}
        for currency in currencies:
            price = prices_data.get(currency, 0)
            prices[currency] = price

        return {
            'prices': prices,
            'diff_24h': ton_data.get('diff_24h', {}),
            'diff_7d': ton_data.get('diff_7d', {}),
            'diff_30d': ton_data.get('diff_30d', {}),
            'timestamp': datetime.now().isoformat(),
            'source': 'TON API'
        }

    def get_wallet_balance(self, wallet_address: str) -> Optional[Dict]:
        endpoint = f"accounts/{wallet_address}"

        data = self._make_request(endpoint)
        if not data:
            return None

        balance_nano = data.get('balance', 0)
        balance_ton = balance_nano / 1_000_000_000

        return {
            'address': wallet_address,
            'balance_nano': balance_nano,
            'balance_ton': balance_ton,
            'is_scam': data.get('is_scam', False),
            'is_wallet': data.get('is_wallet', False),
            'status': data.get('status', 'unknown'),
            'last_activity': data.get('last_activity', ''),
            'timestamp': datetime.now().isoformat()
        }

    def get_wallet_transactions(self, wallet_address: str, limit: int = 10) -> Optional[List[TONTransaction]]:
        endpoint = f"accounts/{wallet_address}/events"
        params = {
            'limit': limit,
            'subject_only': 'true'
        }

        data = self._make_request(endpoint, params)
        if not data or 'events' not in data:
            return None

        transactions = []
        for event in data['events']:
            if 'actions' in event:
                for action in event['actions']:
                    if action.get('type') == 'TonTransfer':
                        ton_transfer = action.get('TonTransfer', {})
                        sender = ton_transfer.get('sender', {})
                        recipient = ton_transfer.get('recipient', {})
                        amount_nano = ton_transfer.get('amount', 0)
                        comment = ton_transfer.get('comment', '')

                        timestamp = event.get('timestamp', 0)
                        if isinstance(timestamp, str):
                            try:
                                timestamp = int(timestamp)
                            except ValueError:
                                timestamp = 0

                        fee_nano = action.get('fee', 0)
                        if isinstance(fee_nano, dict):
                            fee_nano = fee_nano.get('value', 0)
                        elif isinstance(fee_nano, str):
                            try:
                                fee_nano = int(fee_nano)
                            except ValueError:
                                fee_nano = 0

                        if fee_nano == 0:
                            fee_nano = 4_000_000

                        amount_ton = amount_nano / 1_000_000_000
                        fee_ton = fee_nano / 1_000_000_000

                        tx = TONTransaction(
                            hash = event.get('event_id', ''),
                            lt = event.get('lt', 0),
                            from_address = sender.get('address', ''),
                            to_address = recipient.get('address', ''),
                            value = amount_ton,
                            fee = fee_ton,
                            timestamp = datetime.fromtimestamp(timestamp) if timestamp > 0 else datetime.now(),
                            message = comment,
                            operation = 'transfer'
                        )
                        transactions.append(tx)

        return transactions

    def get_token_info(self, token_address: str) -> Optional[Dict]:
        endpoint = f"jettons/{token_address}"

        data = self._make_request(endpoint)
        if not data:
            return None

        metadata = data.get('metadata', {})
        verification = data.get('verification', 'none')

        return {
            'address': token_address,
            'name': metadata.get('name', 'Unknown'),
            'symbol': metadata.get('symbol', 'UNKNOWN'),
            'decimals': metadata.get('decimals', 9),
            'description': metadata.get('description', ''),
            'image': metadata.get('image', ''),
            'social_links': metadata.get('social', []),
            'websites': metadata.get('websites', []),
            'is_verified': verification == 'whitelist',
            'is_scam': verification == 'blacklist',
            'total_supply': data.get('total_supply', 0),
            'holders_count': data.get('holders_count', 0),
            'timestamp': datetime.now().isoformat()
        }

    def get_jetton_holders(self, jetton_address: str, limit: int = 10) -> Optional[List[Dict]]:
        endpoint = f"jettons/{jetton_address}/holders"
        params = {
            'limit': limit
        }

        data = self._make_request(endpoint, params)
        if not data:
            return None

        addresses = data.get('addresses', [])

        holders = []
        for holder_data in addresses:
            address = holder_data.get('address', '')
            owner = holder_data.get('owner', {})
            balance_str = holder_data.get('balance', '0')

            try:
                balance = int(balance_str)
            except (ValueError, TypeError):
                balance = 0

            owner_name = owner.get('name', '')
            is_scam = owner.get('is_scam', False)
            is_wallet = owner.get('is_wallet', False)
            icon = owner.get('icon', '')

            holders.append({
                'address': address,
                'owner_address': owner.get('address', ''),
                'owner_name': owner_name,
                'balance': balance,
                'balance_str': balance_str,
                'is_scam': is_scam,
                'is_wallet': is_wallet,
                'icon': icon
            })

        return holders

    def get_nft_collection(self, collection_address: str) -> Optional[Dict]:
        endpoint = f"nfts/collections/{collection_address}"

        data = self._make_request(endpoint)
        if not data:
            return None

        metadata = data.get('metadata', {})
        previews = data.get('previews', [])

        image = ''
        if previews:
            largest_preview = max(previews, key=lambda x: x.get('resolution', '0x0'))
            image = largest_preview.get('url', '')

        approved_by = data.get('approved_by', [])
        is_verified = len(approved_by) > 0

        next_item_index = data.get('next_item_index', 0)
        items_count = next_item_index if next_item_index > 0 else "Unknown"

        if next_item_index == -1:
            items_count = "Variable"

        return {
            'address': collection_address,
            'name': metadata.get('name', 'Unknown'),
            'description': metadata.get('description', ''),
            'image': image,
            'external_link': metadata.get('external_link', ''),
            'social_links': metadata.get('social_links', []),
            'items_count': items_count,
            'is_verified': is_verified,
            'is_scam': data.get('is_scam', False),
            'owner_address': data.get('owner', {}).get('address', ''),
            'marketplaces': approved_by,
            'timestamp': datetime.now().isoformat()
        }

    def get_nft_item(self, nft_address: str) -> Optional[Dict]:
        endpoint = f"nfts/{nft_address}"

        data = self._make_request(endpoint)
        if not data:
            return None

        collection = data.get('collection', {})
        metadata = data.get('metadata', {})
        sale = data.get('sale', {})
        previews = data.get('previews', [])

        image = ''
        if previews:
            largest_preview = max(previews, key=lambda x: x.get('resolution', '0x0'))
            image = largest_preview.get('url', '')

        price_value = 0
        price_token = 'TON'
        is_for_sale = False

        if sale:
            is_for_sale = True
            price_data = sale.get('price', {})
            price_token = price_data.get('token_name', 'TON')
            price_str = price_data.get('value', '0')

            try:
                price_value = int(price_str) / 1_000_000_000
            except (ValueError, TypeError):
                price_value = 0

        owner = data.get('owner', {})

        return {
            'address': nft_address,
            'name': metadata.get('name', 'Unknown'),
            'description': metadata.get('description', ''),
            'image': image,
            'collection_name': collection.get('name', ''),
            'collection_address': collection.get('address', ''),
            'owner_address': owner.get('address', ''),
            'attributes': data.get('attributes', []),
            'is_for_sale': is_for_sale,
            'price': price_value,
            'price_token': price_token,
            'is_verified': data.get('verified', False),
            'is_scam': data.get('is_scam', False),
            'trust': data.get('trust', ''),
            'approved_by': data.get('approved_by', []),
            'timestamp': datetime.now().isoformat()
        }

    def get_jetton_list(self, limit: int = 50, offset: int = 0) -> Optional[List[Dict]]:
        endpoint = "jettons"
        params = {
            'limit': limit,
            'offset': offset
        }

        data = self._make_request(endpoint, params)
        return data.get('jettons') if data else None

    def get_nft_list(self, limit: int = 50, offset: int = 0) -> Optional[List[Dict]]:
        endpoint = "nfts/collections"
        params = {
            'limit': limit,
            'offset': offset
        }

        data = self._make_request(endpoint, params)
        return data.get('nft_collections') if data else None

    def test_connection(self) -> bool:
        if not self.api_key:
            print("❌ No API key provided for TON API")
            return False

        try:
            data = self.get_ton_price()
            return data is not None
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
