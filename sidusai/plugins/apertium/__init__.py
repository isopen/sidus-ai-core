from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json

from .components import (
    MorphologicalAnalysis,
    ApertiumAnalyzer,
    ApertiumCache
)

from .skills import (
    MorphologicalAnalysisSkill,
    LanguageDetectionSkill,
    BatchAnalysisSkill
)

@dataclass
class AnalysisResult:
    raw_output: str
    normalized: str
    analyses: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_apertium_response(cls, data: List) -> "AnalysisResult":
        if not data or len(data) < 2:
            return cls(raw_output="", normalized="", analyses=[])

        raw_output = json.dumps(data) if isinstance(data, list) else str(data)
        normalized = str(data[1]) if len(data) > 1 else ""
        analyses = []

        if len(data) > 0 and data[0]:
            if isinstance(data[0], str):
                parts = data[0].split('/')
                analyses = parts[1:] if len(parts) > 1 else []
            elif isinstance(data[0], list):
                analyses = [str(item) for item in data[0]]

        return cls(
            raw_output=raw_output,
            normalized=normalized,
            analyses=analyses
        )

class ApertiumPlugin:

    def __init__(self):
        self.name = "apertium"
        self.version = "2.1.0"
        self.base_url = "https://beta.apertium.org/apy"

        self.analyzer = ApertiumAnalyzer(base_url=self.base_url)
        self.cache = ApertiumCache(max_size=1000)

        self.morph_skill = MorphologicalAnalysisSkill(self.analyzer, self.cache)
        self.lang_detect_skill = LanguageDetectionSkill(self.analyzer)
        self.batch_skill = BatchAnalysisSkill(self.analyzer, self.cache)

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": "Morphological analysis using Apertium APY with extended language support",
            "capabilities": [
                "morphological_analysis",
                "language_detection",
                "batch_analysis",
                "language_info",
                "transliteration",
                "translation"
            ],
            "supported_morph_languages": self.analyzer.get_supported_morph_languages(),
            "all_languages": self.analyzer.get_all_languages(),
            "base_url": self.base_url
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            self.base_url = config.get("base_url", self.base_url)
            self.analyzer.base_url = self.base_url

            cache_size = config.get("cache_size", 1000)
            self.cache = ApertiumCache(max_size=cache_size)

            self.morph_skill = MorphologicalAnalysisSkill(self.analyzer, self.cache)
            self.batch_skill = BatchAnalysisSkill(self.analyzer, self.cache)

            print(f"Apertium plugin v{self.version} initialized with base URL: {self.base_url}")
            print(f"Supported morph languages: {len(self.analyzer.supported_morph_languages)}")
            print(f"Total languages for translation: {len(self.analyzer.all_languages)}")
            return True
        except Exception as e:
            print(f"Failed to initialize Apertium plugin: {e}")
            return False

    async def shutdown(self) -> bool:
        try:
            self.cache.clear()
            print("Apertium plugin shutdown, cache cleared")
            return True
        except Exception as e:
            print(f"Error during shutdown: {e}")
            return False

    async def analyse(self, text: str, lang: str = "eng", modes: str = "morph") -> Dict[str, Any]:
        return await self.morph_skill.execute(text, lang, modes)

    async def detect_language(self, text: str, candidate_langs: Optional[List[str]] = None) -> Dict[str, Any]:
        return await self.lang_detect_skill.execute(text, candidate_langs)

    async def batch_analyse(self, texts: List[str], lang: str = "eng", max_concurrent: int = 5) -> Dict[str, Any]:
        return await self.batch_skill.execute(texts, lang, max_concurrent=max_concurrent)

    def get_cache_stats(self) -> Dict[str, Any]:
        return self.cache.get_stats()

    def clear_cache(self) -> Dict[str, Any]:
        return self.morph_skill.clear_cache()

    def get_supported_morph_languages(self) -> Dict[str, str]:
        return self.analyzer.get_supported_morph_languages()

    def get_all_languages(self) -> Dict[str, str]:
        return self.analyzer.get_all_languages()

    def get_language_info(self, lang: str) -> Dict[str, Any]:
        return self.analyzer.get_language_info(lang)

    def is_language_supported(self, lang: str) -> bool:
        return self.analyzer.validate_language(lang)

    def is_morph_language_supported(self, lang: str) -> bool:
        return self.analyzer.validate_morph_language(lang)

    async def check_language_support(self, lang: str) -> Dict[str, Any]:
        return await self.analyzer.check_language_support(lang)

    async def transliterate(self, text: str, from_script: str, to_script: str) -> Dict[str, Any]:
        try:
            import urllib.parse
            import urllib.request
            import json as json_module

            params = urllib.parse.urlencode({
                "from": from_script,
                "to": to_script,
                "q": text
            })
            url = f"{self.base_url}/transliterate?{params}"

            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "SidusAI-Apertium-Plugin/2.1.0",
                    "Accept": "application/json"
                }
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    result = json_module.loads(data)

                    return {
                        "success": True,
                        "text": text,
                        "from_script": from_script,
                        "to_script": to_script,
                        "transliterated": result.get("result", ""),
                        "raw_response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {response.reason}"
                    }

        except Exception as e:
            print(f"Transliteration error: {e}")
            return {"success": False, "error": str(e)}

    async def translate(self, text: str, from_lang: str, to_lang: str) -> Dict[str, Any]:
        try:
            import urllib.parse
            import urllib.request
            import json as json_module

            params = urllib.parse.urlencode({
                "langpair": f"{from_lang}|{to_lang}",
                "q": text
            })
            url = f"{self.base_url}/translate?{params}"

            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "SidusAI-Apertium-Plugin/2.1.0",
                    "Accept": "application/json"
                }
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    result = json_module.loads(data)

                    return {
                        "success": True,
                        "text": text,
                        "from_lang": from_lang,
                        "to_lang": to_lang,
                        "translation": result.get("responseData", {}).get("translatedText", ""),
                        "raw_response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {response.reason}"
                    }

        except Exception as e:
            print(f"Translation error: {e}")
            return {"success": False, "error": str(e)}

__all__ = [
    "ApertiumPlugin",
    "AnalysisResult",
    "MorphologicalAnalysis",
    "ApertiumAnalyzer",
    "ApertiumCache",
    "MorphologicalAnalysisSkill",
    "LanguageDetectionSkill",
    "BatchAnalysisSkill"
]
