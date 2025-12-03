import requests
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class CurrencyRate:
    currency_from: str
    currency_to: str
    rate: float
    timestamp: datetime
    change_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    volume_24h: Optional[float] = None

@dataclass
class CryptoCurrency:
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: float
    market_cap_rank: int
    price_change_24h: float
    price_change_percentage_24h: float
    circulating_supply: float
    total_supply: float
    last_updated: datetime
    image: Optional[str] = None

class CoingeckoClient:
    def __init__(self, api_key: str = None):
        self.api_url = "https://api.coingecko.com/api/v3"
        self.api_key = api_key or os.getenv('COINGECKO_API_KEY')

        self.cache = {}
        self.cache_duration = 60

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SidusAI-Coingecko/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        if self.api_key:
            self.session.headers['Authorization'] = f'Bearer {self.api_key}'

    def _make_request(self, url: str, params: Dict = None, use_cache: bool = True) -> Optional[Dict]:
        cache_key = f"{url}:{json.dumps(params) if params else 'no_params'}"

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
                print("⚠️ Rate limit exceeded, waiting...")
                time.sleep(60)
                return self._make_request(url, params, use_cache)
            else:
                print(f"⚠️ API Error {response.status_code}: {url}")
                return None

        except Exception as e:
            print(f"❌ Request error: {e}")
            return None

    def get_crypto_price(self, crypto_id: str, vs_currency: str = "usd") -> Optional[Dict]:
        endpoint = f"{self.api_url}/simple/price"
        params = {
            'ids': crypto_id,
            'vs_currencies': vs_currency,
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }

        return self._make_request(endpoint, params)

    def get_multiple_crypto_prices(self, crypto_ids: List[str], vs_currency: str = "usd") -> Optional[Dict]:
        endpoint = f"{self.api_url}/simple/price"
        params = {
            'ids': ','.join(crypto_ids),
            'vs_currencies': vs_currency,
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }

        return self._make_request(endpoint, params)

    def get_crypto_market_data(self, vs_currency: str = "usd", limit: int = 50) -> Optional[List[CryptoCurrency]]:
        endpoint = f"{self.api_url}/coins/markets"
        params = {
            'vs_currency': vs_currency,
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': 'false'
        }

        data = self._make_request(endpoint, params)
        if not data:
            return None

        cryptocurrencies = []
        for item in data:
            crypto = CryptoCurrency(
                id=item.get('id', ''),
                symbol=item.get('symbol', '').upper(),
                name=item.get('name', ''),
                current_price=item.get('current_price', 0),
                market_cap=item.get('market_cap', 0),
                market_cap_rank=item.get('market_cap_rank', 0),
                price_change_24h=item.get('price_change_24h', 0),
                price_change_percentage_24h=item.get('price_change_percentage_24h', 0),
                circulating_supply=item.get('circulating_supply', 0),
                total_supply=item.get('total_supply', 0),
                last_updated=datetime.fromisoformat(item.get('last_updated', '').replace('Z', '+00:00')),
                image=item.get('image', '')
            )
            cryptocurrencies.append(crypto)

        return cryptocurrencies

    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Optional[Dict]:
        crypto_data = self.get_multiple_crypto_prices([from_currency, to_currency])
        if not crypto_data or from_currency not in crypto_data or to_currency not in crypto_data:
            return None

        from_price = crypto_data[from_currency].get('usd', 0)
        to_price = crypto_data[to_currency].get('usd', 0)

        if not from_price or not to_price:
            return None

        converted_amount = (amount * from_price) / to_price
        return {
            'success': True,
            'from_currency': from_currency,
            'to_currency': to_currency,
            'amount': amount,
            'converted_amount': converted_amount,
            'rate': from_price / to_price,
            'timestamp': datetime.now()
        }

    def get_historical_data(self, crypto_id: str, vs_currency: str = "usd", days: int = 7) -> Optional[Dict]:
        endpoint = f"{self.api_url}/coins/{crypto_id}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days
        }

        return self._make_request(endpoint, params)

    def get_currency_info(self, crypto_id: str) -> Optional[Dict]:
        endpoint = f"{self.api_url}/coins/{crypto_id}"
        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'true',
            'community_data': 'false',
            'developer_data': 'false',
            'sparkline': 'false'
        }

        return self._make_request(endpoint, params)

    def get_trending_cryptos(self) -> Optional[List[Dict]]:
        endpoint = f"{self.api_url}/search/trending"

        data = self._make_request(endpoint)
        if not data:
            return None

        return data.get('coins', [])

    def get_supported_cryptocurrencies(self) -> Optional[List[Dict]]:
        endpoint = f"{self.api_url}/coins/list"
        return self._make_request(endpoint, use_cache=False)

    def get_crypto_ohlc(self, crypto_id: str, vs_currency: str = "usd", days: int = 7) -> Optional[List[List]]:
        endpoint = f"{self.api_url}/coins/{crypto_id}/ohlc"
        params = {
            'vs_currency': vs_currency,
            'days': days
        }

        return self._make_request(endpoint, params)

    def test_connection(self) -> bool:
        try:
            endpoint = f"{self.api_url}/ping"
            response = self.session.get(endpoint, timeout=10)

            if response.status_code == 200:
                return True
            return False

        except:
            return False
