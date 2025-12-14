import requests
import time
from typing import List, Dict, Any
import json

class DedustComponents:
    BASE_URL_V1 = "https://api.dedust.io/v1"
    BASE_URL_V2 = "https://api.dedust.io/v2"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Dedust-Plugin/2.0.0',
            'Accept': 'application/json'
        })
        self.last_request_time = 0
        self.request_delay = 0.5
        self.rate_limit_remaining = 100

    def _request(self, method, endpoint, params=None, data=None, use_v1=False):
        base_url = self.BASE_URL_V1 if use_v1 else self.BASE_URL_V2
        url = f"{base_url}{endpoint}"

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        try:
            self.last_request_time = time.time()

            print(f"Request: {url}")

            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method == "POST":
                response = self.session.post(url, params=params, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if 'X-RateLimit-Remaining' in response.headers:
                self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
                print(f"Rate Limit Remaining: {self.rate_limit_remaining}")

            response.raise_for_status()

            if response.status_code == 204:
                return {}

            result = response.json()
            print(f"Success: {len(str(result))} bytes")
            return result

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 5
                print(f"Rate limit hit, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                return self._request(method, endpoint, params, data, use_v1)
            else:
                try:
                    error_msg = e.response.json()
                    print(f"HTTP error {e.response.status_code}: {json.dumps(error_msg)[:200]}")
                except:
                    error_msg = e.response.text[:200] if e.response.text else str(e)
                    print(f"HTTP error {e.response.status_code}: {error_msg}")
                raise Exception(f"HTTP error {e.response.status_code}")
        except requests.exceptions.Timeout:
            print("Request timeout")
            raise Exception("Request timeout")
        except requests.exceptions.ConnectionError:
            print("Connection error")
            raise Exception("Connection error")
        except json.JSONDecodeError:
            print("Invalid JSON response")
            raise Exception("Invalid JSON response")
        except Exception as e:
            print(f"Request failed: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")

    def get_liquidity_providers(self, pool_address: str) -> List[Dict[str, Any]]:
        endpoint = f"/pools/{pool_address}/liquidity-providers"
        try:
            return self._request("GET", endpoint, use_v1=True)
        except:
            return []

    def get_account_assets(self, account_address: str) -> Dict[str, Any]:
        endpoint = f"/accounts/{account_address}/assets"
        try:
            result = self._request("GET", endpoint)
            if isinstance(result, list):
                return {"asset_list": result}
            return result
        except:
            return {"asset_list": []}

    def get_account_trades(self, account_address: str) -> Dict[str, Any]:
        endpoint = f"/accounts/{account_address}/trades"
        try:
            result = self._request("GET", endpoint)
            if isinstance(result, list):
                return {"trade_list": result}
            return result
        except:
            return {"trade_list": []}

    def get_assets(self) -> Dict[str, Any]:
        endpoint = "/assets"
        try:
            result = self._request("GET", endpoint)
            if isinstance(result, list):
                return {"asset_list": result}
            return result
        except:
            return {"asset_list": []}

    def get_asset_details(self, symbol_or_address: str) -> Dict[str, Any]:
        try:
            assets_result = self.get_assets()
            assets = assets_result.get("asset_list", [])

            for asset in assets:
                if isinstance(asset, dict):
                    if (asset.get("symbol") == symbol_or_address or 
                        asset.get("address") == symbol_or_address):
                        return {"asset": asset}

            if symbol_or_address.startswith("EQ") and len(symbol_or_address) > 40:
                endpoint = f"/assets/{symbol_or_address}"
                try:
                    result = self._request("GET", endpoint)
                    return {"asset": result} if isinstance(result, dict) else {"asset": {}}
                except:
                    return {"asset": {}}

            return {"asset": {}}

        except Exception as e:
            print(f"Error fetching asset details for {symbol_or_address}: {e}")
            return {"asset": {}}

    def get_dns_info(self, domain: str) -> Dict[str, Any]:
        endpoint = f"/dns/{domain}"
        try:
            return self._request("GET", endpoint)
        except:
            return {}

    def get_coingecko_pairs(self) -> List[Dict[str, Any]]:
        endpoint = "/coingecko/pairs"
        try:
            result = self._request("GET", endpoint)
            return result if isinstance(result, list) else []
        except:
            return []

    def get_coingecko_tickers(self) -> List[Dict[str, Any]]:
        endpoint = "/coingecko/tickers"
        try:
            result = self._request("GET", endpoint)
            return result if isinstance(result, list) else []
        except:
            return []

    def get_coingecko_trades(self, limit: int = 100) -> List[Dict[str, Any]]:
        params = {"limit": limit}
        endpoint = "/coingecko/trades"
        try:
            result = self._request("GET", endpoint, params=params)
            return result if isinstance(result, list) else []
        except:
            return []

    def get_jetton_circulating_supply(self, jetton_address: str) -> Dict[str, Any]:
        endpoint = f"/jettons/{jetton_address}/circulating-supply"
        try:
            return self._request("GET", endpoint)
        except:
            return {}

    def get_jetton_holders(self, jetton_address: str) -> Dict[str, Any]:
        endpoint = f"/jettons/{jetton_address}/holders"
        try:
            result = self._request("GET", endpoint)
            if isinstance(result, list):
                return {"holders": result}
            return result
        except:
            return {"holders": []}

    def get_jetton_metadata(self, jetton_address: str) -> Dict[str, Any]:
        endpoint = f"/jettons/{jetton_address}"
        try:
            result = self._request("GET", endpoint)
            return result if isinstance(result, dict) else {}
        except:
            return {}

    def get_jetton_top_buys(self, jetton_address: str) -> List[Dict[str, Any]]:
        endpoint = f"/jettons/{jetton_address}/top-buys"
        try:
            result = self._request("GET", endpoint)
            return result if isinstance(result, list) else []
        except:
            return []

    def get_jetton_top_traders(self, jetton_address: str) -> List[Dict[str, Any]]:
        endpoint = f"/jettons/{jetton_address}/top-traders"
        try:
            result = self._request("GET", endpoint)
            return result if isinstance(result, list) else []
        except:
            return []

    def get_jetton_total_supply(self, jetton_address: str) -> Dict[str, Any]:
        endpoint = f"/jettons/{jetton_address}/total-supply"
        try:
            return self._request("GET", endpoint)
        except:
            return {}

    def get_pools(self) -> Dict[str, Any]:
        endpoint = "/pools"
        try:
            result = self._request("GET", endpoint)
            if isinstance(result, list):
                return {"pool_list": result}
            return result
        except:
            return {"pool_list": []}

    def get_pools_lite(self) -> Dict[str, Any]:
        endpoint = "/pools/lite"
        try:
            result = self._request("GET", endpoint)
            if isinstance(result, list):
                return {"pool_list": result}
            return result
        except:
            return {"pool_list": []}

    def get_pool_metadata(self, pool_address: str) -> Dict[str, Any]:
        endpoint = f"/pools/{pool_address}"
        try:
            result = self._request("GET", endpoint)
            return result if isinstance(result, dict) else {}
        except:
            return {}

    def get_pool_trades(self, pool_address: str, limit: int = 100) -> Dict[str, Any]:
        params = {"limit": limit}
        endpoint = f"/pools/{pool_address}/trades"
        try:
            result = self._request("GET", endpoint, params=params)
            if isinstance(result, list):
                return {"trades": result}
            return result
        except:
            return {"trades": []}

    def get_prices(self) -> Dict[str, Any]:
        endpoint = "/prices"
        try:
            result = self._request("GET", endpoint)
            if isinstance(result, list):
                return {"prices": result}
            return result
        except:
            return {"prices": []}

    def get_trace(self, hash: str) -> Dict[str, Any]:
        endpoint = f"/traces/{hash}"
        try:
            return self._request("GET", endpoint)
        except:
            return {}
