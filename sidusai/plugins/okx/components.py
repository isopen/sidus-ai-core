import requests
import time
from typing import Optional, Dict, Any

class OKXClientComponent:
    API_VERSION = "v5"

    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_delay = 0.1

        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/{self.API_VERSION}{endpoint}"

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        try:
            self.last_request_time = time.time()

            if method == "GET":
                if params:
                    processed_params = {}
                    for key, value in params.items():
                        if isinstance(value, bool):
                            processed_params[key] = str(value).lower()
                        else:
                            processed_params[key] = value
                    response = self.session.get(url, params=processed_params, timeout=30)
                else:
                    response = self.session.get(url, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()

            try:
                return response.json()
            except:
                return {"code": "0", "data": response.text, "msg": ""}

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 2
                time.sleep(wait_time)
                return self._request(method, endpoint, params)
            else:
                error_msg = e.response.text[:200] if e.response.text else str(e)
                raise Exception(f"HTTP error {e.response.status_code}: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def test_connection(self) -> bool:
        try:
            response = self._request("GET", "/public/time")
            return response.get('code') == '0'
        except Exception:
            return False

    def get_instruments(self, inst_type: str = 'SPOT', uly: Optional[str] = None, 
                       inst_family: Optional[str] = None, inst_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"instType": inst_type}

        if uly:
            params["uly"] = uly
        if inst_family:
            params["instFamily"] = inst_family
        if inst_id:
            params["instId"] = inst_id

        return self._request("GET", "/public/instruments", params=params)

    def get_server_time(self) -> Dict[str, Any]:
        return self._request("GET", "/public/time")

    def get_position_tiers(self, inst_type: str = 'SWAP', uly: Optional[str] = None,
                          inst_family: Optional[str] = None, inst_id: Optional[str] = None,
                          td_mode: str = 'cross') -> Dict[str, Any]:
        params = {"instType": inst_type, "tdMode": td_mode}

        if uly:
            params["uly"] = uly
        if inst_family:
            params["instFamily"] = inst_family
        if inst_id:
            params["instId"] = inst_id

        return self._request("GET", "/public/position-tiers", params=params)

    def get_insurance_fund(self, inst_type: str = 'SWAP', uly: Optional[str] = None,
                          inst_family: Optional[str] = None, ccy: Optional[str] = None,
                          before: Optional[str] = None, after: Optional[str] = None,
                          limit: str = '100') -> Dict[str, Any]:
        params = {"instType": inst_type, "limit": limit}

        if uly:
            params["uly"] = uly
        if inst_family:
            params["instFamily"] = inst_family
        if ccy:
            params["ccy"] = ccy
        if before:
            params["before"] = before
        if after:
            params["after"] = after

        return self._request("GET", "/public/insurance-fund", params=params)
