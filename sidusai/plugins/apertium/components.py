from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class MorphologicalAnalysis:
    original: str
    lemma: str
    tags: List[str]
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original": self.original,
            "lemma": self.lemma,
            "tags": self.tags,
            "weight": self.weight
        }

    @classmethod
    def from_string(cls, analysis_str: str) -> "MorphologicalAnalysis":
        if '<' not in analysis_str:
            return cls(
                original=analysis_str,
                lemma=analysis_str,
                tags=[]
            )

        lemma_end = analysis_str.find('<')
        lemma = analysis_str[:lemma_end]

        tags = []
        i = lemma_end
        while i < len(analysis_str):
            if analysis_str[i] == '<':
                tag_start = i + 1
                tag_end = analysis_str.find('>', tag_start)
                if tag_end != -1:
                    tag = analysis_str[tag_start:tag_end]
                    tags.append(tag)
                    i = tag_end + 1
                else:
                    break
            else:
                i += 1

        return cls(
            original=analysis_str,
            lemma=lemma,
            tags=tags
        )


class ApertiumAnalyzer:

    def __init__(self, base_url: str = "https://beta.apertium.org/apy"):
        self.base_url = base_url
        self.supported_morph_languages = {
            "kir": "Kyrgyz",
            "kaz": "Kazakh", 
            "tur": "Turkish",
            "uzb": "Uzbek",
            "aze": "Azerbaijani",
            "tat": "Tatar",
            "bak": "Bashkir",
            "chv": "Chuvash",
            "crh": "Crimean Tatar",
            "sah": "Yakut",
            "spa": "Spanish",
            "cat": "Catalan",
            "eng": "English",
            "por": "Portuguese",
            "glg": "Galician",
            "oci": "Occitan",
            "fra": "French",
            "epo": "Esperanto",
        }

        self.all_languages = {
            "rus": "Russian",
            "eng": "English",
            "spa": "Spanish",
            "fra": "French",
            "deu": "German",
            "por": "Portuguese",
            "ita": "Italian",
            "nld": "Dutch",
            "pol": "Polish",
            "tur": "Turkish",
            "ara": "Arabic",
            "hin": "Hindi",
            "jpn": "Japanese",
            "kor": "Korean",
            "zho": "Chinese",
            "ces": "Czech",
            "swe": "Swedish",
            "dan": "Danish",
            "nob": "Norwegian Bokmål",
            "nno": "Norwegian Nynorsk",
            "fin": "Finnish",
            "isl": "Icelandic",
            "cat": "Catalan",
            "ron": "Romanian",
            "srp": "Serbian",
            "hrv": "Croatian",
            "slv": "Slovenian",
            "mkd": "Macedonian",
            "bul": "Bulgarian",
            "bel": "Belarusian",
            "ell": "Greek",
            "heb": "Hebrew",
            "fas": "Persian",
            "urd": "Urdu",
            "aze": "Azerbaijani",
            "kaz": "Kazakh",
            "uzb": "Uzbek",
            "kir": "Kyrgyz",
            "tat": "Tatar",
            "bak": "Bashkir",
            "chv": "Chuvash",
            "sah": "Yakut",
            "mlg": "Malagasy",
            "epo": "Esperanto",
            "ido": "Ido",
            "bre": "Breton",
            "cym": "Welsh",
            "gle": "Irish",
            "gla": "Scottish Gaelic",
            "eus": "Basque",
            "oci": "Occitan",
            "glg": "Galician",
            "crh": "Crimean Tatar",
        }

    async def analyse_text(
        self, 
        text: str, 
        lang: str, 
        modes: str = "morph"
    ) -> Dict[str, Any]:
        import urllib.parse
        import urllib.request
        import json as json_module

        if lang not in self.supported_morph_languages:
            return {
                "error": f"Unsupported language for morphological analysis: {lang}",
                "supported_languages": list(self.supported_morph_languages.keys()),
                "available_for_translation": lang in self.all_languages
            }

        try:
            params = urllib.parse.urlencode({
                "lang": lang,
                "mode": f"{lang}_{modes}",
                "q": text
            })
            url = f"{self.base_url}/analyse?{params}"

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
                    json_data = json_module.loads(data)

                    return self._parse_response(json_data, text, lang)
                else:
                    error_text = response.read().decode('utf-8')
                    print(f"HTTP Error {response.status}: {error_text}")
                    return {
                        "error": f"HTTP {response.status}: {response.reason}",
                        "details": error_text,
                        "url": url
                    }

        except urllib.error.URLError as e:
            print(f"URL error: {e}")
            return {"error": f"Network error: {str(e)}"}
        except urllib.error.HTTPError as e:
            error_text = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            print(f"HTTP error: {e.code} - {e.reason}")
            print(f"Error details: {error_text}")
            return {"error": f"HTTP {e.code}: {e.reason}", "details": error_text}
        except Exception as e:
            print(f"Analysis error: {e}")
            return {"error": str(e)}

    def _parse_response(self, data: List, text: str, lang: str) -> Dict[str, Any]:
        result = {
            "text": text,
            "language": lang,
            "language_name": self.supported_morph_languages.get(lang, lang),
            "analyses": [],
            "raw_response": data
        }

        if not data:
            return result

        if isinstance(data, list) and len(data) > 0:
            analyses_raw = data[0]
            normalized = data[1] if len(data) > 1 else text

            result["normalized"] = normalized

            parsed_analyses = []

            if isinstance(analyses_raw, str):
                parts = analyses_raw.split('/')
                if len(parts) > 1:
                    for analysis_str in parts[1:]:
                        if analysis_str.strip():
                            morph_analysis = MorphologicalAnalysis.from_string(analysis_str)
                            parsed_analyses.append(morph_analysis.to_dict())

            elif isinstance(analyses_raw, list):
                for analysis_str in analyses_raw:
                    if isinstance(analysis_str, str) and analysis_str.strip():
                        morph_analysis = MorphologicalAnalysis.from_string(analysis_str)
                        parsed_analyses.append(morph_analysis.to_dict())

            result["analyses"] = parsed_analyses
            result["analysis_count"] = len(parsed_analyses)

        return result

    def get_supported_morph_languages(self) -> Dict[str, str]:
        return self.supported_morph_languages.copy()

    def get_all_languages(self) -> Dict[str, str]:
        return self.all_languages.copy()

    def validate_morph_language(self, lang: str) -> bool:
        return lang in self.supported_morph_languages

    def validate_language(self, lang: str) -> bool:
        return lang in self.all_languages

    def get_language_info(self, lang: str) -> Dict[str, Any]:
        if lang not in self.all_languages:
            return {"error": f"Language not found: {lang}"}

        return {
            "code": lang,
            "name": self.all_languages[lang],
            "morph_supported": lang in self.supported_morph_languages,
            "translation_supported": True
        }

    async def check_language_support(self, lang: str) -> Dict[str, Any]:
        import urllib.request
        import json as json_module

        try:
            url = f"{self.base_url}/listPairs"
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
                    pairs_data = json_module.loads(data)

                    supported_as_source = []
                    supported_as_target = []

                    if "responseData" in pairs_data and isinstance(pairs_data["responseData"], list):
                        for pair in pairs_data["responseData"]:
                            source = pair.get("sourceLanguage", {}).get("code", "")
                            target = pair.get("targetLanguage", {}).get("code", "")

                            if source == lang:
                                supported_as_target.append(target)
                            if target == lang:
                                supported_as_source.append(source)

                    return {
                        "language": lang,
                        "name": self.all_languages.get(lang, "Unknown"),
                        "morph_analysis": lang in self.supported_morph_languages,
                        "available_as_source": len(supported_as_source) > 0,
                        "available_as_target": len(supported_as_target) > 0,
                        "source_for_languages": supported_as_source[:10],
                        "target_for_languages": supported_as_target[:10]
                    }

        except Exception as e:
            print(f"Error checking language support: {e}")

        return {
            "language": lang,
            "name": self.all_languages.get(lang, "Unknown"),
            "morph_analysis": lang in self.supported_morph_languages,
            "available_as_source": False,
            "available_as_target": False
        }


class ApertiumCache:

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_order: List[str] = []

    def _make_key(self, text: str, lang: str, modes: str) -> str:
        return f"{lang}:{modes}:{text}"

    def get(self, text: str, lang: str, modes: str = "morph") -> Optional[Dict[str, Any]]:
        key = self._make_key(text, lang, modes)
        if key in self.cache:
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def set(self, text: str, lang: str, modes: str, result: Dict[str, Any]) -> None:
        key = self._make_key(text, lang, modes)

        if len(self.cache) >= self.max_size:
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]

        self.cache[key] = result
        self.access_order.append(key)

    def clear(self) -> None:
        self.cache.clear()
        self.access_order.clear()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "keys": list(self.cache.keys())[:10]
        }

__all__ = [
    "MorphologicalAnalysis",
    "ApertiumAnalyzer",
    "ApertiumCache"
]
