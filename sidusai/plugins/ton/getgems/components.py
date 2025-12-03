import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
import os

@dataclass
class NFTItem:
    address: str
    name: str
    description: str
    image: str
    owner_address: str
    attributes: List[Dict]
    price: Optional[float] = None
    currency: str = "TON"
    marketplace: str = "getgems"
    collection_address: Optional[str] = None
    sale: Optional[Dict] = None
    created_at: Optional[str] = None

@dataclass
class CollectionInfo:
    address: str
    name: str
    description: str
    floor_price: float
    volume_24h: float
    total_supply: int
    owners: int
    verified: bool = False

class GetgemsClient:
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.getgems.io"
        self.api_key = api_key or os.getenv('GETGEMS_API_KEY')

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SidusAI-Getgems/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        if self.api_key:
            self.session.headers['Authorization'] = self.api_key

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error {response.status_code}: {endpoint}")
                return None

        except Exception as e:
            print(f"Request error: {e}")
            return None

    def get_nfts_on_sale(self, collection_address: str, limit: int = 50, cursor: str = None) -> Dict:
        endpoint = f"/public-api/v1/nfts/on-sale/{collection_address}"
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor

        data = self._make_request(endpoint, params)
        if not data:
            return {"success": False, "error": "API request failed"}

        return {
            "success": True,
            "data": data
        }

    def get_collection_nfts(self, collection_address: str, limit: int = 50, cursor: str = None) -> Dict:
        endpoint = f"/public-api/v1/nfts/collection/{collection_address}"
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor

        data = self._make_request(endpoint, params)
        if not data:
            return {"success": False, "error": "API request failed"}

        return {
            "success": True,
            "data": data
        }

    def get_nft_by_address(self, nft_address: str) -> Dict:
        endpoint = f"/public-api/v1/nft/{nft_address}"

        data = self._make_request(endpoint)
        if not data:
            return {"success": False, "error": "API request failed"}

        return {
            "success": True,
            "data": data
        }

    def get_collection_stats(self, collection_address: str) -> Dict:
        endpoint = f"/public-api/v1/collection/stats/{collection_address}"

        data = self._make_request(endpoint)
        if not data:
            return {"success": False, "error": "API request failed"}

        if not isinstance(data, dict):
            return {"success": False, "error": "Invalid API response format"}

        if not data.get("success", False):
            return {"success": False, "error": data.get("message", "API returned failure")}

        return {
            "success": True,
            "data": data
        }

    def get_collection_info(self, collection_address: str) -> Dict:
        """
        GET /public-api/v1/collection/{collectionAddress}
        """
        endpoint = f"/public-api/v1/collection/{collection_address}"

        data = self._make_request(endpoint)
        if not data:
            return {"success": False, "error": "API request failed"}

        if not isinstance(data, dict):
            return {"success": False, "error": "Invalid API response format"}

        if not data.get("success", False):
            return {"success": False, "error": data.get("message", "API returned failure")}

        return {
            "success": True,
            "data": data
        }

    def test_connection(self) -> bool:
        try:
            endpoint = "/public-api/v1/nfts/on-sale/EQCA14o1-VWhS2efqoh_9M1b_A9DtKTuoqfmkn83AbJzwnPi"
            params = {'limit': 1}

            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params,
                timeout=10
            )

            return response.status_code == 200
        except:
            return False
