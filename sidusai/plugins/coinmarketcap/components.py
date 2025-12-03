import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class CurrencyConversion:
    symbol_from: str
    symbol_to: str
    amount: float
    converted_amount: float
    rate: float
    timestamp: datetime

@dataclass
class CryptoCurrency:
    id: int
    name: str
    symbol: str
    slug: str
    cmc_rank: int
    price: float
    volume_24h: float
    percent_change_1h: float
    percent_change_24h: float
    percent_change_7d: float
    market_cap: float
    circulating_supply: float
    total_supply: Optional[float]
    max_supply: Optional[float]
    last_updated: datetime
    tags: List[str]

class CoinMarketCapClient:
    def __init__(self, api_key: str = None):
        self.api_url = "https://pro-api.coinmarketcap.com/v1"
        self.api_key = api_key or os.getenv('COINMARKETCAP_API_KEY')

        if not self.api_key:
            print("⚠️ Warning: No CoinMarketCap API key provided")
            print("ℹ️ Get API key from: https://coinmarketcap.com/api/")

        self.cache = {}
        self.cache_duration = 60

        self.session = requests.Session()
        self.session.headers.update({
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json',
            'Accept-Encoding': 'deflate, gzip'
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

    def get_crypto_price(self, symbol: str, convert: str = "USD") -> Optional[Dict]:
        endpoint = "cryptocurrency/quotes/latest"
        params = {
            'symbol': symbol.upper(),
            'convert': convert.upper()
        }

        data = self._make_request(endpoint, params)
        if not data or 'data' not in data:
            return None

        crypto_data = data['data'].get(symbol.upper())
        if not crypto_data:
            return None

        quote = crypto_data.get('quote', {}).get(convert.upper(), {})

        return {
            'id': crypto_data.get('id'),
            'name': crypto_data.get('name'),
            'symbol': crypto_data.get('symbol'),
            'price': quote.get('price', 0),
            'percent_change_1h': quote.get('percent_change_1h', 0),
            'percent_change_24h': quote.get('percent_change_24h', 0),
            'percent_change_7d': quote.get('percent_change_7d', 0),
            'market_cap': quote.get('market_cap', 0),
            'volume_24h': quote.get('volume_24h', 0),
            'circulating_supply': crypto_data.get('circulating_supply'),
            'total_supply': crypto_data.get('total_supply'),
            'max_supply': crypto_data.get('max_supply'),
            'last_updated': quote.get('last_updated'),
            'timestamp': datetime.now().isoformat()
        }

    def get_crypto_market_data(self, limit: int = 50, convert: str = "USD") -> Optional[List[CryptoCurrency]]:
        endpoint = "cryptocurrency/listings/latest"
        params = {
            'start': 1,
            'limit': limit,
            'convert': convert.upper(),
            'sort': 'market_cap',
            'sort_dir': 'desc'
        }

        data = self._make_request(endpoint, params)
        if not data or 'data' not in data:
            return None

        cryptocurrencies = []
        for item in data['data']:
            quote = item.get('quote', {}).get(convert.upper(), {})

            crypto = CryptoCurrency(
                id=item.get('id', 0),
                name=item.get('name', ''),
                symbol=item.get('symbol', '').upper(),
                slug=item.get('slug', ''),
                cmc_rank=item.get('cmc_rank', 0),
                price=quote.get('price', 0),
                volume_24h=quote.get('volume_24h', 0),
                percent_change_1h=quote.get('percent_change_1h', 0),
                percent_change_24h=quote.get('percent_change_24h', 0),
                percent_change_7d=quote.get('percent_change_7d', 0),
                market_cap=quote.get('market_cap', 0),
                circulating_supply=item.get('circulating_supply', 0),
                total_supply=item.get('total_supply'),
                max_supply=item.get('max_supply'),
                last_updated=datetime.fromisoformat(quote.get('last_updated', '').replace('Z', '+00:00')),
                tags=item.get('tags', [])
            )
            cryptocurrencies.append(crypto)

        return cryptocurrencies

    def convert_currency(self, amount: float, symbol: str, convert: str) -> Optional[Dict]:
        price_data = self.get_crypto_price(symbol, convert)
        if not price_data:
            return None

        rate = price_data.get('price', 0)
        if not rate:
            return None

        converted_amount = amount * rate

        return {
            'success': True,
            'symbol_from': symbol.upper(),
            'symbol_to': convert.upper(),
            'amount': amount,
            'converted_amount': converted_amount,
            'rate': rate,
            'timestamp': datetime.now()
        }

    def get_historical_data(self, symbol: str, time_period: str = "7d", convert: str = "USD") -> Optional[Dict]:
        endpoint = "cryptocurrency/quotes/historical"
        params = {
            'symbol': symbol.upper(),
            'convert': convert.upper(),
            'time_period': time_period,
            'interval': 'daily'
        }

        data = self._make_request(endpoint, params)
        if not data or 'data' not in data:
            return None

        crypto_data = data['data'].get(symbol.upper())
        if not crypto_data:
            return None

        quotes = crypto_data.get('quotes', [])

        prices = []
        for quote in quotes:
            if 'quote' in quote and convert.upper() in quote['quote']:
                prices.append(quote['quote'][convert.upper()]['price'])

        if not prices:
            return None

        return {
            'symbol': symbol.upper(),
            'time_period': time_period,
            'convert': convert.upper(),
            'prices': prices,
            'current_price': prices[-1] if prices else 0,
            'min_price': min(prices) if prices else 0,
            'max_price': max(prices) if prices else 0,
            'avg_price': sum(prices) / len(prices) if prices else 0,
            'change_percentage': ((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) > 1 and prices[0] != 0 else 0,
            'data_points': len(prices),
            'timestamp': datetime.now().isoformat()
        }

    def get_currency_info(self, symbol: str) -> Optional[Dict]:
        endpoint = "cryptocurrency/info"
        params = {
            'symbol': symbol.upper()
        }

        data = self._make_request(endpoint, params)
        if not data or 'data' not in data:
            return None

        crypto_data = data['data'].get(symbol.upper())
        if not crypto_data:
            return None

        return {
            'id': crypto_data.get('id'),
            'name': crypto_data.get('name'),
            'symbol': crypto_data.get('symbol'),
            'category': crypto_data.get('category'),
            'description': crypto_data.get('description'),
            'slug': crypto_data.get('slug'),
            'logo': crypto_data.get('logo'),
            'urls': crypto_data.get('urls', {}),
            'date_added': crypto_data.get('date_added'),
            'tags': crypto_data.get('tags', []),
            'platform': crypto_data.get('platform'),
            'timestamp': datetime.now().isoformat()
        }

    def get_trending_cryptos(self) -> Optional[List[Dict]]:
        endpoint = "cryptocurrency/trending/latest"
        params = {
            'start': 1,
            'limit': 20,
            'sort': 'cmc_rank'
        }

        data = self._make_request(endpoint, params)
        if not data or 'data' not in data:
            return None

        trending = []
        for item in data['data']:
            trending.append({
                'id': item.get('id'),
                'name': item.get('name'),
                'symbol': item.get('symbol'),
                'cmc_rank': item.get('cmc_rank'),
                'trend_score': item.get('trend_score', 0),
                'social_score': item.get('social_score', 0),
                'market_score': item.get('market_score', 0)
            })

        return trending

    def get_global_metrics(self, convert: str = "USD") -> Optional[Dict]:
        endpoint = "global-metrics/quotes/latest"
        params = {
            'convert': convert.upper()
        }

        data = self._make_request(endpoint, params)
        if not data or 'data' not in data:
            return None

        quote = data['data'].get('quote', {}).get(convert.upper(), {})

        return {
            'total_market_cap': quote.get('total_market_cap', 0),
            'total_volume_24h': quote.get('total_volume_24h', 0),
            'btc_dominance': data['data'].get('btc_dominance', 0),
            'eth_dominance': data['data'].get('eth_dominance', 0),
            'active_cryptocurrencies': data['data'].get('active_cryptocurrencies', 0),
            'total_cryptocurrencies': data['data'].get('total_cryptocurrencies', 0),
            'timestamp': datetime.now().isoformat()
        }

    def get_listings_latest(self, limit: int = 100, convert: str = "USD") -> Optional[List[Dict]]:
        endpoint = "cryptocurrency/listings/latest"
        params = {
            'start': 1,
            'limit': limit,
            'convert': convert.upper()
        }

        data = self._make_request(endpoint, params)
        return data.get('data') if data else None

    def get_crypto_map(self) -> Optional[List[Dict]]:
        endpoint = "cryptocurrency/map"
        params = {
            'listing_status': 'active',
            'limit': 5000
        }

        data = self._make_request(endpoint, params)
        return data.get('data') if data else None

    def test_connection(self) -> bool:
        if not self.api_key:
            print("❌ No API key provided for CoinMarketCap")
            return False

        try:
            data = self.get_global_metrics()
            return data is not None
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False