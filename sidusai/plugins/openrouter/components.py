import requests
import json
import time
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    role: MessageRole
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role.value, "content": self.content}


@dataclass
class ModelInfo:
    id: str
    name: str
    description: Optional[str] = None
    context_length: Optional[int] = None
    architecture: Optional[Dict[str, Any]] = None
    pricing: Dict[str, float] = field(default_factory=lambda: {"prompt": 0, "completion": 0})
    is_free: bool = False
    tags: List[str] = field(default_factory=list)
    top_provider: Optional[Dict[str, Any]] = None
    per_request_limits: Optional[Dict[str, Any]] = None
    created: Optional[int] = None
    updated: Optional[int] = None


class OpenRouterClient:

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')

        if not self.api_key:
            print("Warning: No OpenRouter API key provided")
            print("Get free API key from: https://openrouter.ai/keys")
            print("Then set: export OPENROUTER_API_KEY='your_key_here'")

        self.session = requests.Session()

        headers = {
            'Content-Type': 'application/json',
        }

        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        headers.update({
            'HTTP-Referer': 'https://sidusai.com',
            'X-Title': 'SidusAI',
        })

        self.session.headers.update(headers)

        self._models_cache = None
        self._models_cache_time = 0
        self._models_cache_duration = 300

        self.timeout = 30
        self.max_retries = 3

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None,
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
                    response = self.session.post(url, json=data, timeout=timeout)
                else:
                    print(f"Unsupported HTTP method: {method}")
                    return None

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 400:
                    error_data = response.json()
                    print(f"Bad Request (400): {json.dumps(error_data, ensure_ascii=False)[:200]}")
                    return None
                elif response.status_code == 401:
                    print("Unauthorized (401): Invalid or missing API key")
                    return None
                elif response.status_code == 403:
                    print("Forbidden (403): Insufficient permissions")
                    return None
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

    def get_models_from_api(self) -> List[Dict[str, Any]]:
        print("Fetching models from OpenRouter API...")

        response = self._make_request("models", method="GET", timeout=15)

        if not response:
            print("Failed to fetch models from API")
            return []

        if 'data' not in response:
            print(f"Invalid API response format: {response.keys()}")
            return []

        models = response['data']
        print(f"Successfully fetched {len(models)} models from API")

        return models

    def _safe_float(self, value) -> float:
        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0

        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def analyze_free_models(self, models: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not models:
            return {
                "total_models": 0,
                "free_models": 0,
                "free_models_list": [],
                "categories": {},
                "analysis": {}
            }

        free_models = []
        categories = {}

        for model in models:
            model_id = model.get('id', '')
            if not model_id:
                continue

            pricing = model.get('pricing', {})
            prompt_price = self._safe_float(pricing.get('prompt', 1))
            completion_price = self._safe_float(pricing.get('completion', 1))

            is_free = (prompt_price == 0 and completion_price == 0)

            if not is_free:
                continue

            category = self._determine_model_category(model)

            if category not in categories:
                categories[category] = []

            model_info = {
                'id': model_id,
                'name': model.get('name', model_id.split('/')[-1]),
                'description': model.get('description', ''),
                'context_length': model.get('context_length', 4096),
                'pricing': pricing,
                'is_free': True,
                'tags': model.get('tags', []),
                'architecture': model.get('architecture'),
                'top_provider': model.get('top_provider'),
                'per_request_limits': model.get('per_request_limits'),
                'category': category
            }

            free_models.append(model_info)
            categories[category].append(model_info)

        analysis = {
            'total_models': len(models),
            'free_models_count': len(free_models),
            'free_percentage': (len(free_models) / len(models) * 100) if models else 0,
            'context_length_stats': self._analyze_context_lengths(free_models),
            'category_distribution': {cat: len(models) for cat, models in categories.items()},
            'provider_distribution': self._analyze_providers(free_models),
        }

        return {
            "total_models": len(models),
            "free_models": len(free_models),
            "free_models_list": free_models,
            "categories": categories,
            "analysis": analysis
        }

    def get_available_models(self, free_only: bool = True) -> List[Dict[str, Any]]:
        current_time = time.time()
        if (self._models_cache is not None and 
            current_time - self._models_cache_time < self._models_cache_duration):
            print("Using cached models data")
            models_data = self._models_cache
        else:
            models_data = self.get_models_from_api()
            if models_data:
                self._models_cache = models_data
                self._models_cache_time = current_time

        if not models_data:
            print("No models data available")
            return []

        analysis = self.analyze_free_models(models_data)

        if free_only:
            free_models = analysis.get('free_models_list', [])
            print(f"Found {len(free_models)} free models")
            return free_models
        else:
            all_models = []
            for model in models_data:
                model_id = model.get('id', '')
                if not model_id:
                    continue

                pricing = model.get('pricing', {})
                prompt_price = self._safe_float(pricing.get('prompt', 1))
                completion_price = self._safe_float(pricing.get('completion', 1))

                is_free = (prompt_price == 0 and completion_price == 0)

                model_info = {
                    'id': model_id,
                    'name': model.get('name', model_id.split('/')[-1]),
                    'description': model.get('description', ''),
                    'context_length': model.get('context_length', 4096),
                    'pricing': pricing,
                    'is_free': is_free,
                    'tags': model.get('tags', []),
                    'architecture': model.get('architecture'),
                    'top_provider': model.get('top_provider'),
                    'per_request_limits': model.get('per_request_limits'),
                    'category': self._determine_model_category(model)
                }
                all_models.append(model_info)

            free_count = sum(1 for m in all_models if m.get('is_free', False))
            print(f"Found {len(all_models)} total models ({free_count} free)")
            return all_models

    def _determine_model_category(self, model: Dict[str, Any]) -> str:
        model_id = model.get('id', '').lower()
        name = model.get('name', '').lower()
        tags = [tag.lower() for tag in model.get('tags', [])]

        if any(x in model_id for x in ['google', 'gemma', 'palm']):
            return "Google"
        elif any(x in model_id for x in ['microsoft', 'phi']):
            return "Microsoft"
        elif any(x in model_id for x in ['meta', 'llama']):
            return "Meta"
        elif any(x in model_id for x in ['mistral', 'mixtral']):
            return "Mistral"
        elif any(x in model_id for x in ['openai', 'gpt']):
            return "OpenAI"
        elif any(x in model_id for x in ['anthropic', 'claude']):
            return "Anthropic"
        elif any(x in model_id for x in ['deepseek']):
            return "DeepSeek"
        elif any(x in model_id for x in ['qwen']):
            return "Qwen"
        elif any(x in model_id for x in ['codellama', 'code']):
            return "Coding"
        elif any(x in model_id for x in ['neural', 'nous']):
            return "Community"

        if 'coding' in tags:
            return "Coding"
        elif 'chat' in tags:
            return "Chat"
        elif 'reasoning' in tags:
            return "Reasoning"

        return "Other"

    def _analyze_context_lengths(self, models: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not models:
            return {"average": 0, "min": 0, "max": 0, "distribution": {}}

        contexts = [m.get('context_length', 4096) for m in models]

        distribution = {
            "0-4K": len([c for c in contexts if c <= 4096]),
            "4K-8K": len([c for c in contexts if 4096 < c <= 8192]),
            "8K-16K": len([c for c in contexts if 8192 < c <= 16384]),
            "16K-32K": len([c for c in contexts if 16384 < c <= 32768]),
            "32K+": len([c for c in contexts if c > 32768]),
        }

        return {
            "average": sum(contexts) // len(contexts),
            "min": min(contexts),
            "max": max(contexts),
            "distribution": distribution
        }

    def _analyze_providers(self, models: List[Dict[str, Any]]) -> Dict[str, int]:
        providers = {}

        for model in models:
            top_provider = model.get('top_provider', {})
            provider_name = top_provider.get('name', 'Unknown')

            if provider_name not in providers:
                providers[provider_name] = 0
            providers[provider_name] += 1

        return dict(sorted(providers.items(), key=lambda x: x[1], reverse=True))

    def get_detailed_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        models = self.get_available_models(free_only=False)

        for model in models:
            if model['id'] == model_id:
                return model

        return None

    def find_cheapest_model(
        self,
        min_context_length: int = 0,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        include_free: bool = True,
        include_paid: bool = True
    ) -> Optional[Dict[str, Any]]:
        if not include_free and not include_paid:
            print("Both free and paid models excluded")
            return None

        models = self.get_available_models(free_only=False)

        if not models:
            return None

        filtered_models = []

        for model in models:
            model_id = model.get('id', '')
            if not model_id:
                continue

            is_free = model.get('is_free', False)

            if is_free and not include_free:
                continue

            if not is_free and not include_paid:
                continue

            if model.get('context_length', 0) < min_context_length:
                continue

            if category and model.get('category') != category:
                continue

            if tags:
                model_tags = [t.lower() for t in model.get('tags', [])]
                required_tags = [t.lower() for t in tags]

                if not all(tag in model_tags for tag in required_tags):
                    continue

            filtered_models.append(model)

        if not filtered_models:
            print("No models match the criteria")
            return None

        cheapest_model = None
        cheapest_cost = float('inf')

        for model in filtered_models:
            if model.get('is_free', False):
                cheapest_model = model
                cheapest_cost = 0
                break

            pricing = model.get('pricing', {})
            prompt_price = self._safe_float(pricing.get('prompt', 0))
            completion_price = self._safe_float(pricing.get('completion', 0))

            total_price_per_1k = prompt_price + completion_price

            if total_price_per_1k < cheapest_cost:
                cheapest_cost = total_price_per_1k
                cheapest_model = model

        if cheapest_model:
            model_name = cheapest_model.get('name', cheapest_model['id'])
            pricing = cheapest_model.get('pricing', {})

            if cheapest_cost == 0:
                print(f"Found free model: {model_name}")
            else:
                print(f"Found cheapest model: {model_name}")
                print(f"Cost per 1K tokens: ${cheapest_cost:.6f} USD")
                print(f"Prompt price: ${self._safe_float(pricing.get('prompt', 0)):.6f}/1K")
                print(f"Completion price: ${self._safe_float(pricing.get('completion', 0)):.6f}/1K")

        return cheapest_model

    def find_min_cost_models(self, top_n: int = 5) -> List[Dict[str, Any]]:
        models = self.get_available_models(free_only=False)

        if not models:
            return []

        def calculate_cost(model):
            if model.get('is_free', False):
                return 0

            pricing = model.get('pricing', {})
            prompt_price = self._safe_float(pricing.get('prompt', 1))
            completion_price = self._safe_float(pricing.get('completion', 1))
            return prompt_price + completion_price

        models_with_cost = []
        for model in models:
            cost = calculate_cost(model)
            models_with_cost.append((model, cost))

        models_with_cost.sort(key=lambda x: x[1])

        result = []
        for i, (model, cost) in enumerate(models_with_cost[:top_n]):
            model_info = model.copy()
            model_info['cost_per_1k'] = cost
            result.append(model_info)

        return result

    def compare_model_costs(self, model_ids: List[str]) -> List[Dict[str, Any]]:
        comparison = []

        for model_id in model_ids:
            model_info = self.get_detailed_model_info(model_id)

            if not model_info:
                continue

            pricing = model_info.get('pricing', {})
            prompt_price = self._safe_float(pricing.get('prompt', 0))
            completion_price = self._safe_float(pricing.get('completion', 0))
            total_per_1k = prompt_price + completion_price

            comparison_data = {
                'id': model_id,
                'name': model_info.get('name', model_id),
                'is_free': model_info.get('is_free', False),
                'context_length': model_info.get('context_length', 0),
                'category': model_info.get('category', 'Unknown'),
                'prompt_price': prompt_price,
                'completion_price': completion_price,
                'total_per_1k': total_per_1k,
                'cost_for_1000_prompt_500_completion': (prompt_price * 1) + (completion_price * 0.5)
            }

            comparison.append(comparison_data)

        comparison.sort(key=lambda x: x['total_per_1k'])

        return comparison

    def calculate_usage_cost(self, model_id: str, prompt_tokens: int, completion_tokens: int) -> Dict[str, Any]:
        model_info = self.get_detailed_model_info(model_id)

        if not model_info:
            return {
                "success": False,
                "error": f"Model {model_id} not found"
            }

        pricing = model_info.get('pricing', {})
        prompt_price = self._safe_float(pricing.get('prompt', 0))
        completion_price = self._safe_float(pricing.get('completion', 0))

        prompt_cost = (prompt_tokens / 1000) * prompt_price
        completion_cost = (completion_tokens / 1000) * completion_price
        total_cost = prompt_cost + completion_cost

        return {
            "success": True,
            "model_id": model_id,
            "model_name": model_info.get('name', model_id),
            "is_free": model_info.get('is_free', False),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "prompt_cost": prompt_cost,
            "completion_cost": completion_cost,
            "total_cost": total_cost,
            "currency": "USD",
            "pricing": pricing
        }

    def get_cost_analysis(self) -> Dict[str, Any]:
        models = self.get_available_models(free_only=False)

        if not models:
            return {
                "total_models": 0,
                "free_models": 0,
                "paid_models": 0,
                "price_ranges": {},
                "average_costs": {}
            }

        free_count = sum(1 for m in models if m.get('is_free', False))
        paid_count = len(models) - free_count

        paid_models = [m for m in models if not m.get('is_free', False)]

        price_ranges = {
            "free": free_count,
            "ultra_low": 0,
            "low": 0,
            "medium": 0,
            "high": 0,
            "very_high": 0
        }

        for model in paid_models:
            pricing = model.get('pricing', {})
            total_price = self._safe_float(pricing.get('prompt', 0)) + self._safe_float(pricing.get('completion', 0))

            if total_price < 0.001:
                price_ranges["ultra_low"] += 1
            elif total_price < 0.01:
                price_ranges["low"] += 1
            elif total_price < 0.1:
                price_ranges["medium"] += 1
            elif total_price < 1.0:
                price_ranges["high"] += 1
            else:
                price_ranges["very_high"] += 1

        prompt_prices = []
        completion_prices = []
        total_prices = []

        for model in paid_models:
            pricing = model.get('pricing', {})
            prompt_prices.append(self._safe_float(pricing.get('prompt', 0)))
            completion_prices.append(self._safe_float(pricing.get('completion', 0)))
            total_prices.append(self._safe_float(pricing.get('prompt', 0)) + self._safe_float(pricing.get('completion', 0)))

        def safe_average(values):
            return sum(values) / len(values) if values else 0

        return {
            "timestamp": datetime.now().isoformat(),
            "total_models": len(models),
            "free_models": free_count,
            "paid_models": paid_count,
            "price_ranges": price_ranges,
            "average_costs": {
                "prompt": safe_average(prompt_prices),
                "completion": safe_average(completion_prices),
                "total_per_1k": safe_average(total_prices)
            },
            "min_costs": {
                "prompt": min(prompt_prices) if prompt_prices else 0,
                "completion": min(completion_prices) if completion_prices else 0,
                "total_per_1k": min(total_prices) if total_prices else 0
            },
            "max_costs": {
                "prompt": max(prompt_prices) if prompt_prices else 0,
                "completion": max(completion_prices) if completion_prices else 0,
                "total_per_1k": max(total_prices) if total_prices else 0
            }
        }

    def find_free_model_by_criteria(
        self,
        min_context_length: int = 0,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        free_models = self.get_available_models(free_only=True)

        if not free_models:
            return None

        for model in free_models:
            if model.get('context_length', 0) < min_context_length:
                continue

            if category and model.get('category') != category:
                continue

            if tags:
                model_tags = [t.lower() for t in model.get('tags', [])]
                required_tags = [t.lower() for t in tags]

                if not all(tag in model_tags for tag in required_tags):
                    continue

            return model

        return None

    def get_recommended_free_models(self) -> Dict[str, Any]:
        free_models = self.get_available_models(free_only=True)

        if not free_models:
            return {
                "general": None,
                "coding": None,
                "creative": None,
                "fast": None
            }

        recommendations = {
            "general": None,
            "coding": None,
            "creative": None,
            "fast": None
        }

        for model in free_models:
            model_id = model['id']
            model_name = model.get('name', '')
            context_length = model.get('context_length', 0)
            tags = [t.lower() for t in model.get('tags', [])]

            if not recommendations["general"] and context_length >= 4096:
                recommendations["general"] = model_id

            if not recommendations["coding"] and 'coding' in tags:
                recommendations["coding"] = model_id

            if not recommendations["creative"] and context_length >= 8192:
                recommendations["creative"] = model_id

            if not recommendations["fast"] and context_length <= 4096:
                recommendations["fast"] = model_id

        return recommendations

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "error": "No API key provided",
                "success": False,
                "code": "NO_API_KEY"
            }

        if model is None:
            free_models = self.get_available_models(free_only=True)
            if not free_models:
                return {
                    "error": "No free models available",
                    "success": False,
                    "code": "NO_FREE_MODELS"
                }
            model = free_models[0]['id']
            print(f"Using free model: {model}")

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        for key in ['top_p', 'frequency_penalty', 'presence_penalty', 'stop', 'stream']:
            if key in kwargs:
                payload[key] = kwargs[key]

        print(f"Sending request to: {model}")

        response = self._make_request(
            "chat/completions",
            method="POST",
            data=payload,
            timeout=60
        )

        if not response:
            return {
                "error": "Request failed",
                "success": False,
                "code": "REQUEST_FAILED"
            }

        if 'error' in response:
            return {
                "error": response['error'].get('message', 'Unknown error'),
                "success": False,
                "code": response['error'].get('code', 'UNKNOWN'),
                "raw_response": response
            }

        if 'choices' in response and response['choices']:
            choice = response['choices'][0]
            message = choice.get('message', {})

            result = {
                "success": True,
                "id": response.get('id', ''),
                "model": response.get('model', model),
                "created": response.get('created', int(time.time())),
                "choices": response.get('choices', []),
                "usage": response.get('usage', {}),
                "content": message.get('content', ''),
                "role": message.get('role', 'assistant'),
                "finish_reason": choice.get('finish_reason', ''),
            }

            return result
        else:
            return {
                "error": "Invalid response format",
                "success": False,
                "code": "INVALID_RESPONSE",
                "raw_response": response
            }

    def test_connection(self) -> bool:
        if not self.api_key:
            print("No API key provided")
            return False

        try:
            models = self.get_models_from_api()
            if models:
                print(f"Connection successful: Retrieved {len(models)} models")

                analysis = self.analyze_free_models(models)
                free_count = analysis.get('free_models', 0)
                total_count = analysis.get('total_models', 0)

                print(f"Analysis: {free_count} free models out of {total_count} total")

                if free_count > 0:
                    print("\nAvailable free model categories:")
                    categories = analysis.get('categories', {})
                    for category, models_list in categories.items():
                        print(f"   • {category}: {len(models_list)} models")

                return True
            else:
                print("Connection test: No models retrieved")
                return False

        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def refresh_cache(self):
        self._models_cache = None
        self._models_cache_time = 0
        print("Cache refreshed")

    def get_api_stats(self) -> Dict[str, Any]:
        models = self.get_models_from_api()

        if not models:
            return {"error": "No data available"}

        analysis = self.analyze_free_models(models)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_models": len(models),
            "free_models": analysis.get('free_models', 0),
            "free_percentage": analysis.get('analysis', {}).get('free_percentage', 0),
            "categories": analysis.get('categories', {}).keys(),
            "context_length_stats": analysis.get('analysis', {}).get('context_length_stats', {}),
            "provider_distribution": analysis.get('analysis', {}).get('provider_distribution', {}),
        }
