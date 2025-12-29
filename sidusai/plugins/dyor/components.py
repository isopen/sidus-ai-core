import requests
import pandas as pd
from datetime import datetime
import time
from typing import Optional, Dict, Any

class DYORComponents:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.dyor.io/v1"
        self.session = requests.Session()
        if api_key and api_key != 'test_key':
            self.session.headers.update({"x-api-key": api_key})
        self.last_request_time = 0
        self.request_delay = 2

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        try:
            self.last_request_time = time.time()

            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method == "POST":
                response = self.session.post(url, params=params, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 5
                print(f"⚠️ Rate limit hit, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                return self._request(endpoint, params, method, data)
            else:
                error_text = e.response.text[:200] if e.response.text else str(e)
                raise Exception(f"HTTP error {e.response.status_code}: {error_text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def _format_value(self, value_dict: Dict[str, Any]) -> float:
        if not value_dict or 'value' not in value_dict:
            return 0.0
        try:
            value = float(value_dict['value'])
            decimals = value_dict.get('decimals', 9)
            return value / (10 ** decimals)
        except:
            return 0.0

    def ping(self):
        return self._request("/system/ping")

    def get_jettons(self, sort="createdAt", order="asc", currency="ton", limit=50, offset=0):
        params = {
            "sort": sort,
            "order": order,
            "currency": currency,
            "limit": limit,
            "offset": offset
        }
        return self._request("/jettons", params)

    def get_jetton(self, address):
        return self._request(f"/jettons/{address}")

    def get_jetton_trust_score(self, address):
        return self._request(f"/jettons/{address}/trust-score")

    def get_jetton_trust_score_list(self, addresses=None, currency="ton"):
        if addresses and isinstance(addresses, list):
            data = {"addresses": addresses, "currency": currency}
            return self._request("/jettons/trust-score", method="POST", data=data)
        else:
            params = {"currency": currency}
            return self._request("/jettons/trust-score", params)

    def get_jetton_metrics(self, address, currency="ton"):
        params = {"currency": currency}
        return self._request(f"/jettons/{address}/metrics", params)

    def get_jetton_metrics_list(self, addresses=None, currency="ton"):
        if addresses and isinstance(addresses, list):
            data = {"addresses": addresses, "currency": currency}
            return self._request("/jettons/metrics", method="POST", data=data)
        else:
            params = {"currency": currency}
            return self._request("/jettons/metrics", params)

    def get_jetton_statistics(self, address):
        return self._request(f"/jettons/{address}/stats")

    def get_jetton_statistics_list(self, addresses=None):
        if addresses and isinstance(addresses, list):
            data = {"addresses": addresses}
            return self._request("/jettons/stats", method="POST", data=data)
        else:
            return self._request("/jettons/stats")

    def get_jetton_price(self, address, currency="ton"):
        params = {"currency": currency}
        return self._request(f"/jettons/{address}/price", params)

    def get_jetton_price_chart(self, address, currency="ton", interval="1d", limit=30):
        params = {
            "currency": currency,
            "interval": interval,
            "limit": limit
        }
        return self._request(f"/jettons/{address}/price/chart", params)

    def get_jetton_price_history(self, address, currency="ton", limit=100):
        params = {
            "currency": currency,
            "limit": limit
        }
        return self._request(f"/jettons/{address}/price/ticks", params)

    def get_price_change_list(self, addresses=None, currency="ton", period="24h"):
        if addresses and isinstance(addresses, list):
            data = {
                "addresses": addresses,
                "currency": currency,
                "period": period
            }
            return self._request("/jettons/price/change", method="POST", data=data)
        else:
            params = {
                "currency": currency,
                "period": period
            }
            return self._request("/jettons/price/change", params)

    def get_jetton_liquidity(self, address, currency="ton"):
        params = {"currency": currency}
        return self._request(f"/jettons/{address}/liquidity", params)

    def get_trading_volume_change_list(self, addresses=None, currency="ton", period="24h"):
        if addresses and isinstance(addresses, list):
            data = {
                "addresses": addresses,
                "currency": currency,
                "period": period
            }
            return self._request("/jettons/trading-volume/change", method="POST", data=data)
        else:
            params = {
                "currency": currency,
                "period": period
            }
            return self._request("/jettons/trading-volume/change", params)

    def get_jetton_holders(self, address, limit=100, offset=0):
        params = {
            "limit": limit,
            "offset": offset
        }
        return self._request(f"/jettons/{address}/holders", params)

    def get_jetton_holders_history(self, address):
        return self._request(f"/jettons/{address}/holders/ticks")

    def get_traders_number_change_list(self, addresses=None, period="24h"):
        if addresses and isinstance(addresses, list):
            data = {
                "addresses": addresses,
                "period": period
            }
            return self._request("/jettons/traders/change", method="POST", data=data)
        else:
            params = {"period": period}
            return self._request("/jettons/traders/change", params)

    def get_jetton_transactions(self, address, exchange_id=None, limit=50, offset=0):
        params = {
            "limit": limit,
            "offset": offset
        }
        if exchange_id:
            params["exchangeId"] = exchange_id
        return self._request(f"/jettons/{address}/transactions", params)

    def get_transactions_number_change_list(self, addresses=None, period="24h"):
        if addresses and isinstance(addresses, list):
            data = {
                "addresses": addresses,
                "period": period
            }
            return self._request("/jettons/transactions/change", method="POST", data=data)
        else:
            params = {"period": period}
            return self._request("/jettons/transactions/change", params)

    def get_jetton_markets(self, address, exchange_id=None, limit=20, offset=0):
        params = {
            "limit": limit,
            "offset": offset
        }
        if exchange_id:
            params["exchangeId"] = exchange_id
        return self._request(f"/jettons/{address}/markets", params)

    def get_jetton_market_statistics(self, address, pool_address):
        return self._request(f"/jettons/{address}/markets/{pool_address}/stats")

    def get_jetton_market_price(self, address, pool_address, currency="ton"):
        params = {"currency": currency}
        return self._request(f"/jettons/{address}/markets/{pool_address}/price", params)

    def get_jetton_market_price_history(self, address, pool_address, currency="ton", limit=100):
        params = {
            "currency": currency,
            "limit": limit
        }
        return self._request(f"/jettons/{address}/markets/{pool_address}/price/ticks", params)

    def get_jetton_market_liquidity(self, address, pool_address, currency="ton"):
        params = {"currency": currency}
        return self._request(f"/jettons/{address}/markets/{pool_address}/liquidity", params)

    def get_jetton_market_liquidity_history(self, address, pool_address):
        return self._request(f"/jettons/{address}/markets/{pool_address}/liquidity/ticks")

    def fetch_price_data(self, address, limit=100, currency="ton"):
        try:
            ticks = self.get_jetton_price_history(address, currency, limit)
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
