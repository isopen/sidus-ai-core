import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class DogBreed:
    name: str
    sub_breeds: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'sub_breeds': self.sub_breeds,
            'images': self.images[:10] if self.images else []
        }

class DogCEOClient:

    BASE_URL = "https://dog.ceo/api"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'SidusAI-DogCEO/1.0'
        })

        self.timeout = 30
        self.max_retries = 3

        self._breeds_cache = None
        self._breeds_cache_time = 0
        self._breeds_cache_duration = 600

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> Optional[Dict]:
        url = f"{self.BASE_URL}/{endpoint}"
        timeout = timeout or self.timeout

        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, params=params, timeout=timeout)
                elif method.upper() == "POST":
                    response = self.session.post(url, json=params, timeout=timeout)
                else:
                    print(f"Unsupported HTTP method: {method}")
                    return None

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    print(f"Not Found (404): Endpoint {endpoint} not found")
                    return None
                elif response.status_code == 429:
                    retry_after = response.headers.get('Retry-After', '1')
                    wait_time = int(retry_after) if retry_after.isdigit() else 1

                    print(f"Rate limit exceeded (429). Waiting {wait_time}s...")

                    if attempt < self.max_retries - 1:
                        time.sleep(wait_time)
                        continue
                    else:
                        print("Max retries exceeded for rate limit")
                        return None
                elif response.status_code >= 500:
                    print(f"Server error ({response.status_code})")
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    return None
                else:
                    print(f"HTTP {response.status_code}: {response.text[:200]}")
                    return None

            except requests.exceptions.Timeout:
                print(f"Request timeout after {timeout}s (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    continue
                return None
            except requests.exceptions.ConnectionError:
                print(f"Connection error (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                return None
            except Exception as e:
                print(f"Request error: {str(e)}")
                return None

        return None

    def get_breeds_from_api(self) -> Dict[str, Any]:
        print("Fetching dog breeds from Dog CEO API...")

        response = self._make_request("breeds/list/all", method="GET", timeout=15)

        if not response:
            print("Failed to fetch breeds from API")
            return {'message': {}, 'status': 'error'}

        return response

    def get_all_breeds(self) -> Dict[str, Any]:
        current_time = time.time()
        if (self._breeds_cache is not None and 
            current_time - self._breeds_cache_time < self._breeds_cache_duration):
            print("Using cached breeds data")
            breeds_data = self._breeds_cache
        else:
            breeds_data = self.get_breeds_from_api()
            if breeds_data and breeds_data.get('status') == 'success':
                self._breeds_cache = breeds_data
                self._breeds_cache_time = current_time

        if not breeds_data or breeds_data.get('status') != 'success':
            return {
                "success": False,
                "error": "Failed to get breeds data",
                "breeds": []
            }

        breeds_dict = breeds_data.get('message', {})
        breeds_list = []

        for breed, sub_breeds in breeds_dict.items():
            breed_info = {
                'name': breed,
                'sub_breeds': sub_breeds,
                'total_sub_breeds': len(sub_breeds),
                'images': []
            }
            breeds_list.append(breed_info)

        breeds_list.sort(key=lambda x: x['name'])

        categories = self._categorize_breeds(breeds_list)

        return {
            "success": True,
            "total_breeds": len(breeds_list),
            "breeds": breeds_list,
            "categories": categories,
            "timestamp": datetime.now().isoformat()
        }

    def _categorize_breeds(self, breeds: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        categories = {
            "Small Dogs": [],
            "Medium Dogs": [],
            "Large Dogs": [],
            "Working Dogs": [],
            "Sporting Dogs": [],
            "Toy Dogs": [],
            "Herding Dogs": [],
            "Hound Dogs": [],
            "Terrier Dogs": [],
            "Non-Sporting Dogs": []
        }

        small_breeds = ['chihuahua', 'pug', 'pomeranian', 'shih', 'pembroke', 'corgi', 'dachshund', 
                       'maltese', 'boston', 'cairn', 'westhighland', 'yorkshire']

        large_breeds = ['german', 'retriever', 'rottweiler', 'bernese', 'mastiff', 'great', 'saint', 
                       'newfoundland', 'leonberg', 'pyrenees', 'wolfhound']

        working_breeds = ['german', 'rottweiler', 'boxer', 'doberman', 'bernese', 'mastiff', 
                         'saint', 'newfoundland', 'siberian', 'akita']

        sporting_breeds = ['retriever', 'spaniel', 'setter', 'pointer', 'weimaraner', 'vizsla']

        toy_breeds = ['chihuahua', 'pug', 'pomeranian', 'shih', 'maltese', 'pekinese', 
                     'papillon', 'poodle-toy']

        herding_breeds = ['collie', 'sheepdog', 'corgi', 'shepherd', 'border', 'australian']

        hound_breeds = ['hound', 'beagle', 'dachshund', 'greyhound', 'whippet', 'basset', 
                       'bloodhound', 'foxhound', 'afghan']

        terrier_breeds = ['terrier', 'scottish', 'westhighland', 'cairn', 'yorkshire', 
                         'airedale', 'bull', 'staffordshire']

        for breed in breeds:
            breed_name = breed['name'].lower()
            added = False

            if any(keyword in breed_name for keyword in terrier_breeds):
                categories["Terrier Dogs"].append(breed)
                added = True
            elif any(keyword in breed_name for keyword in hound_breeds):
                categories["Hound Dogs"].append(breed)
                added = True
            elif any(keyword in breed_name for keyword in herding_breeds):
                categories["Herding Dogs"].append(breed)
                added = True
            elif any(keyword in breed_name for keyword in working_breeds):
                categories["Working Dogs"].append(breed)
                added = True
            elif any(keyword in breed_name for keyword in sporting_breeds):
                categories["Sporting Dogs"].append(breed)
                added = True
            elif any(keyword in breed_name for keyword in toy_breeds):
                categories["Toy Dogs"].append(breed)
                added = True
            elif any(keyword in breed_name for keyword in small_breeds):
                categories["Small Dogs"].append(breed)
                added = True
            elif any(keyword in breed_name for keyword in large_breeds):
                categories["Large Dogs"].append(breed)
                added = True
            else:
                categories["Medium Dogs"].append(breed)

        categories = {k: v for k, v in categories.items() if v}

        return categories

    def get_random_dog(self, breed: Optional[str] = None, count: int = 1) -> Dict[str, Any]:
        endpoint = "breeds/image/random"
        params = None

        if breed:
            breed_clean = breed.lower().replace(' ', '-')
            endpoint = f"breed/{breed_clean}/images/random"

        if count > 1:
            endpoint = endpoint.replace("/random", f"/random/{count}")

        print(f"Fetching random dog image(s)...")
        response = self._make_request(endpoint, method="GET")

        if not response or response.get('status') != 'success':
            error_msg = response.get('message', 'Unknown error') if response else 'Request failed'
            return {
                "success": False,
                "error": error_msg,
                "breed": breed,
                "count": count
            }

        images = response.get('message', [])
        if isinstance(images, str):
            images = [images]

        return {
            "success": True,
            "images": images,
            "breed": breed,
            "count": len(images),
            "timestamp": datetime.now().isoformat()
        }

    def get_breed_images(self, breed: str, count: int = 10) -> Dict[str, Any]:
        breed_clean = breed.lower().replace(' ', '-')

        print(f"Fetching images for breed: {breed}")

        endpoint = f"breed/{breed_clean}/images/random/{min(count, 50)}"
        response = self._make_request(endpoint, method="GET")

        if not response or response.get('status') != 'success':
            error_msg = response.get('message', 'Unknown error') if response else 'Request failed'
            return {
                "success": False,
                "error": error_msg,
                "breed": breed,
                "count": 0
            }

        images = response.get('message', [])
        if isinstance(images, str):
            images = [images]

        return {
            "success": True,
            "images": images,
            "breed": breed,
            "count": len(images),
            "timestamp": datetime.now().isoformat()
        }

    def get_sub_breeds(self, breed: str) -> Dict[str, Any]:
        breed_clean = breed.lower().replace(' ', '-')

        print(f"Fetching sub-breeds for: {breed}")

        response = self._make_request(f"breed/{breed_clean}/list", method="GET")

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "breed": breed,
                "sub_breeds": []
            }

        if response.get('status') != 'success':
            error_msg = response.get('message', 'Unknown error')
            return {
                "success": False,
                "error": error_msg,
                "breed": breed,
                "sub_breeds": []
            }

        sub_breeds = response.get('message', [])

        return {
            "success": True,
            "breed": breed,
            "sub_breeds": sub_breeds,
            "count": len(sub_breeds),
            "timestamp": datetime.now().isoformat()
        }

    def test_connection(self) -> bool:
        try:
            response = self._make_request("breeds/list/all", method="GET", timeout=10)

            if response and response.get('status') == 'success':
                breeds = response.get('message', {})
                print(f"Connection successful: Retrieved {len(breeds)} dog breeds")

                random_response = self._make_request("breeds/image/random", method="GET", timeout=5)

                if random_response and random_response.get('status') == 'success':
                    print(f"Image endpoint working: {random_response.get('message', '')[:50]}...")

                return True
            else:
                print("Connection test: No breeds retrieved")
                return False

        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def refresh_cache(self):
        self._breeds_cache = None
        self._breeds_cache_time = 0
        print("Cache refreshed")

    def get_popular_breeds(self, limit: int = 10) -> List[Dict[str, Any]]:
        breeds_data = self.get_all_breeds()

        if not breeds_data.get('success'):
            return []

        all_breeds = breeds_data.get('breeds', [])

        popular_breed_names = [
            'labrador', 'german shepherd', 'golden retriever', 'french bulldog',
            'bulldog', 'poodle', 'beagle', 'rottweiler', 'yorkshire terrier',
            'boxer', 'dachshund', 'siberian husky', 'great dane', 'pomeranian',
            'chihuahua', 'shih tzu', 'boston terrier', 'cavalier king charles spaniel',
            'australian shepherd', 'corgi'
        ]

        popular_breeds = []
        for breed_name in popular_breed_names:
            for breed in all_breeds:
                if breed_name.lower() in breed['name'].lower():
                    popular_breeds.append(breed)
                    break

        return popular_breeds[:limit]

    def search_breeds(self, query: str) -> List[Dict[str, Any]]:
        breeds_data = self.get_all_breeds()

        if not breeds_data.get('success'):
            return []

        all_breeds = breeds_data.get('breeds', [])
        query_lower = query.lower()

        results = []
        for breed in all_breeds:
            breed_name = breed['name'].lower()

            if (query_lower in breed_name or 
                any(query_lower in sub.lower() for sub in breed['sub_breeds'])):
                results.append(breed)

        return results
