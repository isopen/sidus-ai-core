import requests
import json
import time
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class CatImage:
    id: str
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    mime_type: Optional[str] = None
    breeds: List[Dict[str, Any]] = field(default_factory=list)
    categories: List[Dict[str, Any]] = field(default_factory=list)
    sub_id: Optional[str] = None
    created_at: Optional[str] = None
    original_filename: Optional[str] = None
    pending: Optional[int] = None
    approved: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CatImage':
        return cls(
            id=data.get('id', ''),
            url=data.get('url', ''),
            width=data.get('width'),
            height=data.get('height'),
            mime_type=data.get('mime_type'),
            breeds=data.get('breeds', []),
            categories=data.get('categories', []),
            sub_id=data.get('sub_id'),
            created_at=data.get('created_at'),
            original_filename=data.get('original_filename'),
            pending=data.get('pending'),
            approved=data.get('approved')
        )

@dataclass
class CatBreed:
    id: str
    name: str
    description: str
    temperament: str
    origin: str
    life_span: str
    adaptability: int
    affection_level: int
    child_friendly: int
    dog_friendly: int
    energy_level: int
    grooming: int
    health_issues: int
    intelligence: int
    shedding_level: int
    social_needs: int
    stranger_friendly: int
    vocalisation: int
    experimental: int
    hairless: int
    natural: int
    rare: int
    rex: int
    suppressed_tail: int
    short_legs: int
    wikipedia_url: str
    hypoallergenic: int
    reference_image_id: str
    weight: Dict[str, str] = field(default_factory=dict)
    image: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CatBreed':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            temperament=data.get('temperament', ''),
            origin=data.get('origin', ''),
            life_span=data.get('life_span', ''),
            adaptability=data.get('adaptability', 0),
            affection_level=data.get('affection_level', 0),
            child_friendly=data.get('child_friendly', 0),
            dog_friendly=data.get('dog_friendly', 0),
            energy_level=data.get('energy_level', 0),
            grooming=data.get('grooming', 0),
            health_issues=data.get('health_issues', 0),
            intelligence=data.get('intelligence', 0),
            shedding_level=data.get('shedding_level', 0),
            social_needs=data.get('social_needs', 0),
            stranger_friendly=data.get('stranger_friendly', 0),
            vocalisation=data.get('vocalisation', 0),
            experimental=data.get('experimental', 0),
            hairless=data.get('hairless', 0),
            natural=data.get('natural', 0),
            rare=data.get('rare', 0),
            rex=data.get('rex', 0),
            suppressed_tail=data.get('suppressed_tail', 0),
            short_legs=data.get('short_legs', 0),
            wikipedia_url=data.get('wikipedia_url', ''),
            hypoallergenic=data.get('hypoallergenic', 0),
            reference_image_id=data.get('reference_image_id', ''),
            weight=data.get('weight', {}),
            image=data.get('image')
        )

@dataclass
class Favourite:
    id: int
    user_id: str
    image_id: str
    sub_id: Optional[str] = None
    created_at: Optional[str] = None
    image: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Favourite':
        return cls(
            id=data.get('id', 0),
            user_id=data.get('user_id', ''),
            image_id=data.get('image_id', ''),
            sub_id=data.get('sub_id'),
            created_at=data.get('created_at'),
            image=data.get('image')
        )

@dataclass
class Vote:
    id: int
    image_id: str
    sub_id: Optional[str] = None
    created_at: Optional[str] = None
    value: Optional[int] = None
    country_code: Optional[str] = None
    image: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vote':
        return cls(
            id=data.get('id', 0),
            image_id=data.get('image_id', ''),
            sub_id=data.get('sub_id'),
            created_at=data.get('created_at'),
            value=data.get('value'),
            country_code=data.get('country_code'),
            image=data.get('image')
        )

@dataclass
class Fact:
    id: str
    fact: str
    breed_id: Optional[str] = None
    title: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Fact':
        return cls(
            id=data.get('id', ''),
            fact=data.get('fact', ''),
            breed_id=data.get('breed_id'),
            title=data.get('title')
        )

@dataclass
class UploadResponse:
    id: str
    url: str
    sub_id: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    original_filename: Optional[str] = None
    pending: Optional[int] = None
    approved: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UploadResponse':
        return cls(
            id=data.get('id', ''),
            url=data.get('url', ''),
            sub_id=data.get('sub_id'),
            width=data.get('width'),
            height=data.get('height'),
            original_filename=data.get('original_filename'),
            pending=data.get('pending'),
            approved=data.get('approved')
        )

class CatAPIClient:
    BASE_URL = "https://api.thecatapi.com/v1"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required for CatAPIClient")

        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'SidusAI-TheCatAPI/1.0',
            'x-api-key': api_key
        })

        self.timeout = 30
        self.max_retries = 3

        self._breeds_cache = None
        self._breeds_cache_time = 0
        self._breeds_cache_duration = 600

        self._categories_cache = None
        self._categories_cache_time = 0
        self._categories_cache_duration = 3600

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Dict = None,
        data: Dict = None,
        files: Dict = None,
        timeout: int = None
    ) -> Any:
        url = f"{self.BASE_URL}/{endpoint}"
        timeout = timeout or self.timeout

        for attempt in range(self.max_retries):
            try:
                headers = self.session.headers.copy()

                if files:
                    headers.pop('Content-Type', None)

                if method.upper() == "GET":
                    response = self.session.get(url, params=params, headers=headers, timeout=timeout)
                elif method.upper() == "POST":
                    if files:
                        response = self.session.post(url, data=data, files=files, headers=headers, timeout=timeout)
                    else:
                        response = self.session.post(url, json=data, headers=headers, timeout=timeout)
                elif method.upper() == "DELETE":
                    response = self.session.delete(url, headers=headers, timeout=timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                if response.status_code == 200 or response.status_code == 201:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return response.text

                elif response.status_code == 401:
                    error_msg = "Unauthorized (401): Invalid or missing API key"
                    raise ConnectionError(error_msg)

                elif response.status_code == 403:
                    error_msg = "Forbidden (403): API key doesn't have required permissions"
                    raise PermissionError(error_msg)

                elif response.status_code == 404:
                    return None

                elif response.status_code == 429:
                    retry_after = response.headers.get('Retry-After', '1')
                    wait_time = int(retry_after) if retry_after.isdigit() else 1

                    if attempt < self.max_retries - 1:
                        time.sleep(wait_time)
                        continue
                    else:
                        raise ConnectionError("Max retries exceeded for rate limit")

                elif response.status_code >= 500:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                        continue
                    raise ConnectionError(f"Server error: {response.status_code}")

                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    raise ConnectionError(error_msg)

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    continue
                raise ConnectionError("Request timeout")

            except requests.exceptions.ConnectionError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                raise ConnectionError(f"Connection failed: {e}")

            except Exception as e:
                raise

        return None

    def get_random_cat(
        self, 
        size: str = None,
        mime_types: str = None,
        format: str = "json",
        has_breeds: bool = None,
        order: str = "RANDOM",
        page: int = 0,
        limit: int = 1
    ) -> Dict[str, Any]:
        params = {
            'limit': min(limit, 25),
            'page': page,
            'order': order,
            'format': format
        }

        if size:
            params['size'] = size
        if mime_types:
            params['mime_types'] = mime_types
        if has_breeds is not None:
            params['has_breeds'] = str(has_breeds).lower()

        response = self._make_request("images/search", method="GET", params=params)

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "images": []
            }

        if isinstance(response, list):
            images = [CatImage.from_dict(img) for img in response]
        else:
            images = []

        return {
            "success": True,
            "images": [img.__dict__ for img in images],
            "count": len(images),
            "timestamp": datetime.now().isoformat()
        }

    def get_breed_images(self, breed_id: str, limit: int = 10) -> Dict[str, Any]:
        params = {
            'breed_id': breed_id,
            'limit': min(limit, 100)
        }

        response = self._make_request("images/search", method="GET", params=params)

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "breed_id": breed_id,
                "images": []
            }

        if isinstance(response, list):
            images = [CatImage.from_dict(img) for img in response]
        else:
            images = []

        return {
            "success": True,
            "images": [img.__dict__ for img in images],
            "breed_id": breed_id,
            "count": len(images),
            "timestamp": datetime.now().isoformat()
        }

    def upload_image(self, file_path: str, sub_id: str = None, breed_ids: str = None) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        files = {'file': open(file_path, 'rb')}
        data = {}

        if sub_id:
            data['sub_id'] = sub_id
        if breed_ids:
            data['breed_ids'] = breed_ids

        try:
            response = self._make_request("images/upload", method="POST", data=data, files=files)

            if not response:
                return {
                    "success": False,
                    "error": "Upload failed",
                    "file_path": file_path
                }

            upload_response = UploadResponse.from_dict(response)

            return {
                "success": True,
                "upload": upload_response.__dict__,
                "message": f"Image uploaded successfully: {upload_response.id}",
                "timestamp": datetime.now().isoformat()
            }
        finally:
            files['file'].close()

    def delete_image(self, image_id: str) -> Dict[str, Any]:
        response = self._make_request(f"images/{image_id}", method="DELETE")

        if response is None:
            return {
                "success": True,
                "message": f"Image {image_id} deleted successfully",
                "timestamp": datetime.now().isoformat()
            }

        return {
            "success": False,
            "error": f"Failed to delete image: {image_id}",
            "timestamp": datetime.now().isoformat()
        }

    def get_user_images(self, limit: int = 10, page: int = 0, order: str = "DESC") -> Dict[str, Any]:
        params = {
            'limit': min(limit, 10),
            'page': page,
            'order': order
        }

        response = self._make_request("images/", method="GET", params=params)

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "images": []
            }

        if isinstance(response, list):
            images = [CatImage.from_dict(img) for img in response]
        else:
            images = []

        return {
            "success": True,
            "images": [img.__dict__ for img in images],
            "count": len(images),
            "page": page,
            "order": order,
            "timestamp": datetime.now().isoformat()
        }

    def get_image_analysis(self, image_id: str) -> Dict[str, Any]:
        response = self._make_request(f"images/{image_id}", method="GET")

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "image_id": image_id
            }

        return {
            "success": True,
            "analysis": response,
            "image_id": image_id,
            "timestamp": datetime.now().isoformat()
        }

    def get_all_breeds(self, limit: int = 10, page: int = 0) -> Dict[str, Any]:
        current_time = time.time()
        if (self._breeds_cache is not None and 
            current_time - self._breeds_cache_time < self._breeds_cache_duration):
            breeds_data = self._breeds_cache
        else:
            params = {
                'limit': limit,
                'page': page
            }
            breeds_data = self._make_request("breeds", method="GET", params=params)

            if breeds_data:
                self._breeds_cache = breeds_data
                self._breeds_cache_time = current_time

        if not breeds_data:
            return {
                "success": False,
                "error": "Failed to get breeds data",
                "breeds": []
            }

        if isinstance(breeds_data, list):
            breeds = [CatBreed.from_dict(breed) for breed in breeds_data]
        else:
            breeds = []

        categories = self._categorize_breeds([breed.__dict__ for breed in breeds])

        return {
            "success": True,
            "breeds": [breed.__dict__ for breed in breeds],
            "categories": categories,
            "total_breeds": len(breeds),
            "page": page,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }

    def _categorize_breeds(self, breeds: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        categories = {
            "Affectionate Cats": [],
            "Intelligent Cats": [],
            "Playful Cats": [],
            "Calm Cats": [],
            "Hypoallergenic Cats": [],
            "Rare Cats": [],
            "Natural Breeds": [],
            "Hairless Cats": []
        }

        for breed in breeds:
            if breed.get('affection_level', 0) >= 4:
                categories["Affectionate Cats"].append(breed)

            if breed.get('intelligence', 0) >= 4:
                categories["Intelligent Cats"].append(breed)

            if breed.get('energy_level', 0) >= 4:
                categories["Playful Cats"].append(breed)

            if breed.get('energy_level', 0) <= 2:
                categories["Calm Cats"].append(breed)

            if breed.get('hypoallergenic', 0) == 1:
                categories["Hypoallergenic Cats"].append(breed)

            if breed.get('rare', 0) == 1:
                categories["Rare Cats"].append(breed)

            if breed.get('natural', 0) == 1:
                categories["Natural Breeds"].append(breed)

            if breed.get('hairless', 0) == 1:
                categories["Hairless Cats"].append(breed)

        categories = {k: v for k, v in categories.items() if v}

        return categories

    def search_breeds(self, query: str, attach_image: int = 1) -> Dict[str, Any]:
        params = {
            'q': query,
            'attach_image': attach_image
        }

        response = self._make_request("breeds/search", method="GET", params=params)

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "query": query,
                "breeds": []
            }

        if isinstance(response, list):
            breeds = [CatBreed.from_dict(breed) for breed in response]
        else:
            breeds = []

        return {
            "success": True,
            "breeds": [breed.__dict__ for breed in breeds],
            "query": query,
            "count": len(breeds),
            "timestamp": datetime.now().isoformat()
        }

    def get_favourites(self) -> Dict[str, Any]:
        response = self._make_request("favourites", method="GET")

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "favourites": []
            }

        if isinstance(response, list):
            favourites = [Favourite.from_dict(fav) for fav in response]
        else:
            favourites = []

        return {
            "success": True,
            "favourites": [fav.__dict__ for fav in favourites],
            "count": len(favourites),
            "timestamp": datetime.now().isoformat()
        }

    def add_favourite(self, image_id: str, sub_id: str = None) -> Dict[str, Any]:
        data = {"image_id": image_id}
        if sub_id:
            data["sub_id"] = sub_id

        response = self._make_request("favourites", method="POST", data=data)

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "image_id": image_id
            }

        return {
            "success": True,
            "favourite": response,
            "message": f"Image {image_id} added to favourites",
            "timestamp": datetime.now().isoformat()
        }

    def delete_favourite(self, favourite_id: int) -> Dict[str, Any]:
        response = self._make_request(f"favourites/{favourite_id}", method="DELETE")

        if response is None:
            return {
                "success": True,
                "message": f"Favourite {favourite_id} deleted successfully",
                "timestamp": datetime.now().isoformat()
            }

        return {
            "success": False,
            "error": f"Failed to delete favourite: {favourite_id}",
            "timestamp": datetime.now().isoformat()
        }

    def get_votes(self) -> Dict[str, Any]:
        response = self._make_request("votes", method="GET")

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "votes": []
            }

        if isinstance(response, list):
            votes = [Vote.from_dict(vote) for vote in response]
        else:
            votes = []

        return {
            "success": True,
            "votes": [vote.__dict__ for vote in votes],
            "count": len(votes),
            "timestamp": datetime.now().isoformat()
        }

    def add_vote(self, image_id: str, value: int, sub_id: str = None) -> Dict[str, Any]:
        data = {
            "image_id": image_id,
            "value": value
        }
        if sub_id:
            data["sub_id"] = sub_id

        response = self._make_request("votes", method="POST", data=data)

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "image_id": image_id
            }

        return {
            "success": True,
            "vote": response,
            "message": f"Vote added for image {image_id}",
            "timestamp": datetime.now().isoformat()
        }

    def delete_vote(self, vote_id: int) -> Dict[str, Any]:
        response = self._make_request(f"votes/{vote_id}", method="DELETE")

        if response is None:
            return {
                "success": True,
                "message": f"Vote {vote_id} deleted successfully",
                "timestamp": datetime.now().isoformat()
            }

        return {
            "success": False,
            "error": f"Failed to delete vote: {vote_id}",
            "timestamp": datetime.now().isoformat()
        }

    def get_facts(self, limit: int = 1) -> Dict[str, Any]:
        params = {'limit': min(limit, 100)}

        response = self._make_request("facts", method="GET", params=params)

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "facts": []
            }

        if isinstance(response, list):
            facts = [Fact.from_dict(fact) for fact in response]
        else:
            facts = []

        return {
            "success": True,
            "facts": [fact.__dict__ for fact in facts],
            "count": len(facts),
            "timestamp": datetime.now().isoformat()
        }

    def get_breed_facts(self, breed_id: str, limit: int = 5, page: int = 0, order: str = "ASC") -> Dict[str, Any]:
        params = {
            'limit': min(limit, 100),
            'page': page,
            'order': order
        }

        response = self._make_request(f"breeds/{breed_id}/facts", method="GET", params=params)

        if not response:
            return {
                "success": False,
                "error": "Request failed",
                "breed_id": breed_id,
                "facts": []
            }

        if isinstance(response, list):
            facts = [Fact.from_dict(fact) for fact in response]
        else:
            facts = []

        return {
            "success": True,
            "facts": [fact.__dict__ for fact in facts],
            "breed_id": breed_id,
            "count": len(facts),
            "page": page,
            "order": order,
            "timestamp": datetime.now().isoformat()
        }

    def get_categories(self) -> Dict[str, Any]:
        current_time = time.time()
        if (self._categories_cache is not None and 
            current_time - self._categories_cache_time < self._categories_cache_duration):
            categories_data = self._categories_cache
        else:
            categories_data = self._make_request("categories", method="GET")

            if categories_data:
                self._categories_cache = categories_data
                self._categories_cache_time = current_time

        if not categories_data:
            return {
                "success": False,
                "error": "Failed to get categories",
                "categories": []
            }

        return {
            "success": True,
            "categories": categories_data,
            "count": len(categories_data),
            "timestamp": datetime.now().isoformat()
        }

    def test_connection(self) -> bool:
        try:
            response = self._make_request("breeds", method="GET", timeout=10, params={'limit': 1})

            if response:
                return True
            else:
                return False

        except Exception:
            return False

    def refresh_cache(self):
        self._breeds_cache = None
        self._breeds_cache_time = 0
        self._categories_cache = None
        self._categories_cache_time = 0

    def get_popular_breeds(self, limit: int = 10) -> List[Dict[str, Any]]:
        breeds_data = self.get_all_breeds()

        if not breeds_data.get('success'):
            return []

        all_breeds = breeds_data.get('breeds', [])

        popular_breed_names = [
            'siamese', 'persian', 'maine coon', 'ragdoll', 'bengal',
            'british shorthair', 'abyssinian', 'sphynx', 'scottish fold',
            'russian blue', 'norwegian forest', 'burmese', 'birman',
            'oriental', 'tonkinese', 'balinese', 'himalayan', 'somali',
            'devon rex', 'cornish rex'
        ]

        popular_breeds = []
        for breed_name in popular_breed_names:
            for breed in all_breeds:
                if breed_name.lower() in breed.get('name', '').lower():
                    popular_breeds.append(breed)
                    break

        return popular_breeds[:limit]
