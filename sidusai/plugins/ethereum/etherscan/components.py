import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class EthereumWallet:
    address: str
    balance_eth: float
    balance_usd: float
    transaction_count: int

@dataclass
class EthereumToken:
    address: str
    name: str
    symbol: str
    decimals: int
    total_supply: float
    price_usd: Optional[float]
    market_cap_usd: Optional[float]
    volume_24h_usd: Optional[float]
    holders: int
    is_verified: bool

@dataclass
class EthereumTransaction:
    hash: str
    block_number: int
    from_address: str
    to_address: str
    value: float
    gas: float
    gas_price: float
    timestamp: datetime
    input: str
    status: str

class EtherscanClient:
    def __init__(self, api_key: str = None, network: str = "mainnet"):
        self.networks = {
            "mainnet": "api.etherscan.io",
            "goerli": "api-goerli.etherscan.io",
            "sepolia": "api-sepolia.etherscan.io"
        }

        self.api_key = api_key or os.getenv('ETHERSCAN_API_KEY')
        self.network = network
        self.base_url = f"https://api.etherscan.io/v2/api"

        if not self.api_key:
            print("⚠️ Warning: No Etherscan API key provided")
            print("ℹ️ Get API key from: https://etherscan.io/apis")

        self.cache = {}
        self.cache_duration = 60

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SidusAI-Etherscan/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def _make_request(self, module: str, action: str, params: Dict = None, use_cache: bool = True) -> Optional[Dict]:
        all_params = {
            'tag': 'latest',
            'module': module,
            'action': action,
            'apikey': self.api_key,
            'chainId': 1
        }

        if params:
            all_params.update(params)

        cache_key = f"{module}:{action}:{json.dumps(params) if params else 'no_params'}"

        if use_cache and cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return cached_data

        try:
            response = self.session.get(self.base_url, params=all_params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1' and data.get('message') == 'OK':
                    result = data.get('result', {})
                    if use_cache:
                        self.cache[cache_key] = (result, time.time())
                    return result
                else:
                    print(f"⚠️ API Error: {data.get('message', 'Unknown error')}")
                    return None
            elif response.status_code == 429:
                print("⚠️ Rate limit exceeded, waiting 5 seconds...")
                time.sleep(5)
                return self._make_request(module, action, params, use_cache)
            else:
                print(f"⚠️ HTTP Error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Request error: {e}")
            return None

    def get_eth_price(self) -> Dict[str, Any]:
        result = self._make_request('stats', 'ethprice')
        if not result:
            return {
                'ethusd': 0,
                'ethusd_timestamp': '0',
                'ethbtc': 0,
                'ethbtc_timestamp': '0',
                'timestamp': datetime.now().isoformat()
            }

        return {
            'ethusd': float(result.get('ethusd', 0)),
            'ethusd_timestamp': result.get('ethusd_timestamp', '0'),
            'ethbtc': float(result.get('ethbtc', 0)),
            'ethbtc_timestamp': result.get('ethbtc_timestamp', '0'),
            'timestamp': datetime.now().isoformat()
        }

    def get_wallet_balance(self, wallet_address: str) -> Dict[str, Any]:
        result = self._make_request('account', 'balance', {
            'address': wallet_address
        })

        if result is None:
            return None

        balance_wei = int(result) if isinstance(result, str) else 0
        balance_eth = balance_wei / 1_000_000_000_000_000_000

        eth_price = self.get_eth_price()
        balance_usd = balance_eth * eth_price.get('ethusd', 0)

        return {
            'address': wallet_address,
            'balance_wei': balance_wei,
            'balance_eth': balance_eth,
            'balance_usd': balance_usd,
            'timestamp': datetime.now().isoformat()
        }

    def get_wallet_transactions(self, wallet_address: str, limit: int = 10) -> List[EthereumTransaction]:
        result = self._make_request('account', 'txlist', {
            'address': wallet_address,
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': limit,
            'sort': 'desc'
        })

        if not isinstance(result, list):
            return []

        transactions = []
        for tx in result:
            try:
                value_wei = int(tx.get('value', '0'))
                value_eth = value_wei / 1_000_000_000_000_000_000

                gas = int(tx.get('gas', '0'))
                gas_price_wei = int(tx.get('gasPrice', '0'))
                gas_price_gwei = gas_price_wei / 1_000_000_000

                timestamp = int(tx.get('timeStamp', '0'))

                tx_obj = EthereumTransaction(
                    hash=tx.get('hash', ''),
                    block_number=int(tx.get('blockNumber', '0')),
                    from_address=tx.get('from', ''),
                    to_address=tx.get('to', ''),
                    value=value_eth,
                    gas=gas,
                    gas_price=gas_price_gwei,
                    timestamp=datetime.fromtimestamp(timestamp),
                    input=tx.get('input', ''),
                    status=tx.get('txreceipt_status', '')
                )
                transactions.append(tx_obj)
            except (ValueError, KeyError) as e:
                continue

        return transactions

    def get_gas_price(self) -> Dict[str, Any]:
        result = self._make_request('gastracker', 'gasoracle', {'chainId' : 1})

        if not isinstance(result, dict):
            return {
                'safe_gas_price': 0,
                'propose_gas_price': 0,
                'fast_gas_price': 0,
                'suggest_base_fee': 0,
                'gas_used_ratio': 0,
                'timestamp': datetime.now().isoformat()
            }

        return {
            'safe_gas_price': float(result.get('SafeGasPrice', 0)),
            'propose_gas_price': float(result.get('ProposeGasPrice', 0)),
            'fast_gas_price': float(result.get('FastGasPrice', 0)),
            'suggest_base_fee': float(result.get('suggestBaseFee', 0)),
            'gas_used_ratio': result.get('gasUsedRatio', '0'),
            'timestamp': datetime.now().isoformat()
        }

    def test_connection(self) -> bool:
        if not self.api_key:
            print("❌ No API key provided for Etherscan")
            return False

        try:
            result = self._make_request('account', 'balance', {
                'address': '0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae',
                'tag': 'latest',
                'chainId': 1
            }, use_cache=False)

            if result is not None and isinstance(result, str):
                print(f"✅ Etherscan API connection successful")
                balance_wei = int(result)
                balance_eth = balance_wei / 1_000_000_000_000_000_000
                print(f"Test balance: {balance_eth:.6f} ETH")
                return True
            else:
                print(f"❌ Etherscan API test failed")
                return False

        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
