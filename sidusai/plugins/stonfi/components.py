import requests
import time
from typing import Optional, List, Dict, Any

class StonFiComponents:
    BASE_API_VERSION = "v1"

    def __init__(self):
        self.base_url = "https://api.ston.fi"
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_delay = 0.1

    def _bool_to_str(self, value: bool) -> str:
        return "true" if value else "false"

    def _request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_url}{endpoint}"

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        try:
            self.last_request_time = time.time()

            if params:
                processed_params = {}
                for key, value in params.items():
                    if isinstance(value, bool):
                        processed_params[key] = self._bool_to_str(value)
                    else:
                        processed_params[key] = value
            else:
                processed_params = params

            if method == "GET":
                response = self.session.get(url, params=processed_params, timeout=30)
            elif method == "POST":
                response = self.session.post(url, params=processed_params, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()

            if response.status_code == 204:
                return {}

            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 2
                print(f"Rate limit hit, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                return self._request(method, endpoint, params, data)
            else:
                error_msg = e.response.text[:200] if e.response.text else str(e)
                raise Exception(f"HTTP error {e.response.status_code}: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_asset(self, address: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/assets/{address}")

    def get_assets(self) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/assets")

    def query_assets(self, condition: Optional[str] = None, 
                    limit: Optional[int] = None,
                    search_terms: Optional[List[str]] = None,
                    sort_by: Optional[List[str]] = None,
                    unconditional_assets: Optional[List[str]] = None,
                    wallet_address: Optional[str] = None) -> Dict[str, Any]:

        data = {}
        if condition is not None:
            data["condition"] = condition
        if limit is not None:
            data["limit"] = limit
        if search_terms is not None:
            data["search_terms"] = search_terms
        if sort_by is not None:
            data["sort_by"] = sort_by
        if unconditional_assets is not None:
            data["unconditional_assets"] = unconditional_assets
        if wallet_address is not None:
            data["wallet_address"] = wallet_address

        return self._request("POST", f"/{self.BASE_API_VERSION}/assets/query", data=data)

    def search_assets(self, search_string: str,
                     condition: Optional[str] = None,
                     unconditional_asset: Optional[List[str]] = None,
                     limit: Optional[int] = None,
                     wallet_address: Optional[str] = None) -> Dict[str, Any]:

        params = {"search_string": search_string}
        if condition is not None:
            params["condition"] = condition
        if unconditional_asset is not None:
            params["unconditional_asset"] = unconditional_asset
        if limit is not None:
            params["limit"] = limit
        if wallet_address is not None:
            params["wallet_address"] = wallet_address

        return self._request("POST", f"/{self.BASE_API_VERSION}/assets/search", params=params)

    def get_pool(self, address: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/pools/{address}")

    def get_pools(self, dex_v2: bool = True) -> Dict[str, Any]:
        params = {"dex_v2": self._bool_to_str(dex_v2)}
        return self._request("GET", f"/{self.BASE_API_VERSION}/pools", params=params)

    def get_pools_by_market(self, asset_0: str, asset_1: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/pools/by_market/{asset_0}/{asset_1}")

    def query_pools(self, condition: Optional[str] = None,
                   dex_v2: bool = True,
                   limit: Optional[int] = None,
                   search_terms: Optional[List[str]] = None,
                   sort_by: Optional[List[str]] = None,
                   unconditional_assets: Optional[List[str]] = None,
                   wallet_address: Optional[str] = None) -> Dict[str, Any]:

        data = {"dex_v2": self._bool_to_str(dex_v2)}
        if condition is not None:
            data["condition"] = condition
        if limit is not None:
            data["limit"] = limit
        if search_terms is not None:
            data["search_terms"] = search_terms
        if sort_by is not None:
            data["sort_by"] = sort_by
        if unconditional_assets is not None:
            data["unconditional_assets"] = unconditional_assets
        if wallet_address is not None:
            data["wallet_address"] = wallet_address

        return self._request("POST", f"/{self.BASE_API_VERSION}/pools/query", data=data)

    def get_farm(self, address: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/farms/{address}")

    def get_farms(self, dex_v2: bool = True, only_active: bool = False) -> Dict[str, Any]:
        params = {
            "dex_v2": self._bool_to_str(dex_v2),
            "only_active": self._bool_to_str(only_active)
        }
        return self._request("GET", f"/{self.BASE_API_VERSION}/farms", params=params)

    def get_farms_by_pool(self, pool_address: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/farms/by_pool/{pool_address}")

    def simulate_swap(self, offer_address: str, ask_address: str, units: str,
                     slippage_tolerance: str, pool_address: Optional[str] = None,
                     referral_address: Optional[str] = None,
                     referral_fee_bps: Optional[str] = None,
                     dex_v2: bool = True,
                     dex_version: Optional[List[str]] = None) -> Dict[str, Any]:

        params = {
            "offer_address": offer_address,
            "ask_address": ask_address,
            "units": units,
            "slippage_tolerance": slippage_tolerance,
            "dex_v2": self._bool_to_str(dex_v2)
        }

        if pool_address:
            params["pool_address"] = pool_address
        if referral_address:
            params["referral_address"] = referral_address
        if referral_fee_bps:
            params["referral_fee_bps"] = referral_fee_bps
        if dex_version:
            params["dex_version"] = dex_version

        return self._request("POST", f"/{self.BASE_API_VERSION}/swap/simulate", params=params)

    def simulate_reverse_swap(self, offer_address: str, ask_address: str, units: str,
                             slippage_tolerance: str, pool_address: Optional[str] = None,
                             referral_address: Optional[str] = None,
                             referral_fee_bps: Optional[str] = None,
                             dex_v2: bool = True,
                             dex_version: Optional[List[str]] = None) -> Dict[str, Any]:

        params = {
            "offer_address": offer_address,
            "ask_address": ask_address,
            "units": units,
            "slippage_tolerance": slippage_tolerance,
            "dex_v2": self._bool_to_str(dex_v2)
        }

        if pool_address:
            params["pool_address"] = pool_address
        if referral_address:
            params["referral_address"] = referral_address
        if referral_fee_bps:
            params["referral_fee_bps"] = referral_fee_bps
        if dex_version:
            params["dex_version"] = dex_version

        return self._request("POST", f"/{self.BASE_API_VERSION}/reverse_swap/simulate", params=params)

    def get_swap_status(self, router_address: str, owner_address: str, query_id: str) -> Dict[str, Any]:
        params = {
            "router_address": router_address,
            "owner_address": owner_address,
            "query_id": query_id
        }
        return self._request("GET", f"/{self.BASE_API_VERSION}/swap/status", params=params)

    def simulate_liquidity_provision(self, provision_type: str, token_a: str, token_b: str,
                                    slippage_tolerance: str, pool_address: Optional[str] = None,
                                    wallet_address: Optional[str] = None,
                                    token_a_units: Optional[str] = None,
                                    token_b_units: Optional[str] = None) -> Dict[str, Any]:

        params = {
            "provision_type": provision_type,
            "token_a": token_a,
            "token_b": token_b,
            "slippage_tolerance": slippage_tolerance
        }

        if pool_address:
            params["pool_address"] = pool_address
        if wallet_address:
            params["wallet_address"] = wallet_address
        if token_a_units:
            params["token_a_units"] = token_a_units
        if token_b_units:
            params["token_b_units"] = token_b_units

        return self._request("POST", f"/{self.BASE_API_VERSION}/liquidity_provision/simulate", params=params)

    def get_markets(self, dex_v2: bool = True) -> Dict[str, Any]:
        params = {"dex_v2": self._bool_to_str(dex_v2)}
        return self._request("GET", f"/{self.BASE_API_VERSION}/markets", params=params)

    def get_router(self, address: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/routers/{address}")

    def get_routers(self, dex_v2: bool = True) -> Dict[str, Any]:
        params = {"dex_v2": self._bool_to_str(dex_v2)}
        return self._request("GET", f"/{self.BASE_API_VERSION}/routers", params=params)

    def get_transaction_action_tree(self, hash: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/transactions/{hash}/action_tree")

    def query_transactions(self, wallet_address: Optional[str] = None,
                          query_id: Optional[int] = None,
                          min_tx_timestamp: Optional[str] = None,
                          ext_msg_hash: Optional[str] = None) -> Dict[str, Any]:

        params = {}
        if wallet_address:
            params["wallet_address"] = wallet_address
        if query_id is not None:
            params["query_id"] = query_id
        if min_tx_timestamp:
            params["min_tx_timestamp"] = min_tx_timestamp
        if ext_msg_hash:
            params["ext_msg_hash"] = ext_msg_hash

        return self._request("GET", f"/{self.BASE_API_VERSION}/transactions/query", params=params)

    def get_jetton_wallet_address(self, jetton_address: str, owner_address: str) -> Dict[str, Any]:
        params = {"owner_address": owner_address}
        return self._request("GET", f"/{self.BASE_API_VERSION}/jetton/{jetton_address}/address", params=params)

    def get_wallet_asset(self, wallet_address: str, asset_address: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/wallets/{wallet_address}/assets/{asset_address}")

    def get_wallet_assets(self, wallet_address: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/wallets/{wallet_address}/assets")

    def get_wallet_pool(self, wallet_address: str, pool_address: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/wallets/{wallet_address}/pools/{pool_address}")

    def get_wallet_pools(self, wallet_address: str, dex_v2: bool = True) -> Dict[str, Any]:
        params = {"dex_v2": self._bool_to_str(dex_v2)}
        return self._request("GET", f"/{self.BASE_API_VERSION}/wallets/{wallet_address}/pools", params=params)

    def get_wallet_farm(self, wallet_address: str, farm_address: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/wallets/{wallet_address}/farms/{farm_address}")

    def get_wallet_farms(self, wallet_address: str, dex_v2: bool = True, only_active: bool = False) -> Dict[str, Any]:
        params = {
            "dex_v2": self._bool_to_str(dex_v2),
            "only_active": self._bool_to_str(only_active)
        }
        return self._request("GET", f"/{self.BASE_API_VERSION}/wallets/{wallet_address}/farms", params=params)

    def get_wallet_fee_vaults(self, wallet_address: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/wallets/{wallet_address}/fee_vaults")

    def get_wallet_operations(self, wallet_address: str, since: str, until: str,
                             op_type: Optional[List[str]] = None,
                             dex_v2: bool = True) -> Dict[str, Any]:

        params = {
            "since": since,
            "until": until,
            "dex_v2": self._bool_to_str(dex_v2)
        }

        if op_type:
            params["op_type"] = op_type

        return self._request("GET", f"/{self.BASE_API_VERSION}/wallets/{wallet_address}/operations", params=params)

    def get_wallet_stakes(self, wallet_address: str) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/wallets/{wallet_address}/stakes")

    def get_wallet_last_transactions(self, wallet_address: str, limit: int = 10,
                                    min_tx_timestamp: Optional[str] = None) -> Dict[str, Any]:

        params = {"limit": limit}
        if min_tx_timestamp:
            params["min_tx_timestamp"] = min_tx_timestamp

        return self._request("GET", f"/{self.BASE_API_VERSION}/wallets/{wallet_address}/transactions/last", params=params)

    def get_dex_stats(self, since: Optional[str] = None, until: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        return self._request("GET", f"/{self.BASE_API_VERSION}/stats/dex", params=params)

    def get_fee_accruals(self, referrer_address: str, since: str, until: str) -> Dict[str, Any]:
        params = {
            "referrer_address": referrer_address,
            "since": since,
            "until": until
        }
        return self._request("GET", f"/{self.BASE_API_VERSION}/stats/fee_accruals", params=params)

    def get_fee_withdrawals(self, referrer_address: str, since: str, until: str) -> Dict[str, Any]:
        params = {
            "referrer_address": referrer_address,
            "since": since,
            "until": until
        }
        return self._request("GET", f"/{self.BASE_API_VERSION}/stats/fee_withdrawals", params=params)

    def get_fees_stats(self, referrer_address: str, since: str, until: str) -> Dict[str, Any]:
        params = {
            "referrer_address": referrer_address,
            "since": since,
            "until": until
        }
        return self._request("GET", f"/{self.BASE_API_VERSION}/stats/fees", params=params)

    def get_operations_stats(self, since: str, until: str,
                            pool_address: Optional[List[str]] = None) -> Dict[str, Any]:

        params = {
            "since": since,
            "until": until
        }

        if pool_address:
            params["pool_address"] = pool_address

        return self._request("GET", f"/{self.BASE_API_VERSION}/stats/operations", params=params)

    def get_pool_stats(self, since: str, until: str,
                      pool_address: Optional[List[str]] = None) -> Dict[str, Any]:

        params = {
            "since": since,
            "until": until
        }

        if pool_address:
            params["pool_address"] = pool_address

        return self._request("GET", f"/{self.BASE_API_VERSION}/stats/pool", params=params)

    def get_staking_stats(self) -> Dict[str, Any]:
        return self._request("GET", f"/{self.BASE_API_VERSION}/stats/staking")

    def get_cmc_data(self) -> List[Dict[str, Any]]:
        return self._request("GET", "/export/cmc/v1")

    def get_screener_asset_info(self, address: str) -> Dict[str, Any]:
        return self._request("GET", f"/export/dexscreener/v1/asset/{address}")

    def get_screener_events(self, from_block: int, to_block: int) -> Dict[str, Any]:
        params = {
            "fromBlock": from_block,
            "toBlock": to_block
        }
        return self._request("GET", "/export/dexscreener/v1/events", params=params)

    def get_screener_latest_block(self) -> Dict[str, Any]:
        return self._request("GET", "/export/dexscreener/v1/latest-block")

    def get_screener_pool_info(self, address: str) -> Dict[str, Any]:
        return self._request("GET", f"/export/dexscreener/v1/pair/{address}")
