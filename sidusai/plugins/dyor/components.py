import requests
import pandas as pd
from datetime import datetime
import time

class DYORComponents:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.dyor.io/v1"
        self.session = requests.Session()
        if api_key and api_key != 'test_key':
            self.session.headers.update({"x-api-key": api_key})
        self.last_request_time = 0
        self.request_delay = 2

    def _request(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        try:
            self.last_request_time = time.time()
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 5
                print(f"⚠️ Rate limit hit, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                return self._request(endpoint, params)
            else:
                raise Exception(f"HTTP error {e.response.status_code}: {e.response.text[:100]}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def _format_value(self, value_dict):
        if not value_dict or 'value' not in value_dict:
            return 0.0
        try:
            value = float(value_dict['value'])
            decimals = value_dict.get('decimals', 9)
            return value / (10 ** decimals)
        except:
            return 0.0

    def get_jettons(self, sort="createdAt", order="asc", currency="ton", limit=50, offset=0):
        params = {"sort": sort, "order": order, "currency": currency, "limit": limit, "offset": offset}
        return self._request("/jettons", params)

    def get_jetton(self, address):
        return self._request(f"/jettons/{address}")

    def get_jetton_metrics(self, address, currency="ton"):
        params = {"currency": currency}
        return self._request(f"/jettons/{address}/metrics", params)

    def get_jetton_price(self, address, currency="ton"):
        params = {"currency": currency}
        return self._request(f"/jettons/{address}/price", params)

    def get_jetton_price_ticks(self, address):
        return self._request(f"/jettons/{address}/price/ticks")

    def get_jetton_holders(self, address):
        return self._request(f"/jettons/{address}/holders")

    def get_jetton_holders_ticks(self, address):
        return self._request(f"/jettons/{address}/holders/ticks")

    def get_jetton_transactions(self, address, exchange_id=None):
        params = {}
        if exchange_id:
            params["exchangeId"] = exchange_id
        return self._request(f"/jettons/{address}/transactions", params)

    def get_jetton_markets(self, address, exchange_id=None):
        params = {}
        if exchange_id:
            params["exchangeId"] = exchange_id
        return self._request(f"/jettons/{address}/markets", params)

    def get_jetton_market_stats(self, address, pool_address):
        return self._request(f"/jettons/{address}/markets/{pool_address}/stats")

    def get_jetton_market_price(self, address, pool_address):
        return self._request(f"/jettons/{address}/markets/{pool_address}/price")

    def get_jetton_market_price_ticks(self, address, pool_address):
        return self._request(f"/jettons/{address}/markets/{pool_address}/price/ticks")

    def get_jetton_market_liquidity(self, address, pool_address):
        return self._request(f"/jettons/{address}/markets/{pool_address}/liquidity")

    def fetch_price_data(self, address, limit=100):
        try:
            ticks = self.get_jetton_price_ticks(address)
            if 'items' in ticks and ticks['items']:
                data = []
                items = ticks['items'][:limit]
                for item in items:
                    if 'value' in item and 'ton' in item['value']:
                        timestamp = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
                        price = self._format_value(item['value']['ton'])
                        data.append({
                            'timestamp': timestamp,
                            'price': price
                        })

                if data:
                    df = pd.DataFrame(data)
                    df.set_index('timestamp', inplace=True)
                    return df
        except Exception as e:
            print(f"Warning: Could not fetch price data: {e}")
        return pd.DataFrame()
