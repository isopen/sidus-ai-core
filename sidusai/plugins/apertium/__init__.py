import sidusai as sai
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json
import asyncio
import urllib.parse
import urllib.request
from .components import ApertiumAnalyzer, ApertiumCache
from .skills import MorphologicalAnalysisSkill, LanguageDetectionSkill, BatchAnalysisSkill

__apertium_agent_name__ = 'apertium_morph_agent'

class ApertiumPlugin(sai.AgentPlugin):
    def __init__(self, base_url: str = "https://beta.apertium.org/apy"):
        super().__init__()
        self.base_url = base_url
        self.analyzer = None
        self.cache = None
        self.morph_skill = None
        self.lang_detect_skill = None
        self.batch_skill = None

    def apply_plugin(self, agent: sai.Agent):
        self.analyzer = ApertiumAnalyzer(base_url=self.base_url)
        self.cache = ApertiumCache(max_size=1000)

        self.morph_skill = MorphologicalAnalysisSkill(self.analyzer, self.cache)
        self.lang_detect_skill = LanguageDetectionSkill(self.analyzer)
        self.batch_skill = BatchAnalysisSkill(self.analyzer, self.cache)

        self.skills = {}

        def analyse_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            text = context.get('text')
            lang = context.get('lang', 'eng')
            modes = context.get('modes', 'morph')

            if not text:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Text is required"}
                return return_value

            async def async_analyse():
                return await self.morph_skill.execute(text, lang, modes)

            try:
                result = asyncio.run(async_analyse())
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def detect_language_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            text = context.get('text')
            candidate_langs = context.get('candidate_langs')

            if not text:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Text is required"}
                return return_value

            async def async_detect():
                return await self.lang_detect_skill.execute(text, candidate_langs)

            try:
                result = asyncio.run(async_detect())
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def batch_analyse_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            texts = context.get('texts', [])
            lang = context.get('lang', 'eng')
            max_concurrent = context.get('max_concurrent', 5)

            if not texts:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Texts list is required"}
                return return_value

            async def async_batch():
                return await self.batch_skill.execute(texts, lang, max_concurrent=max_concurrent)

            try:
                result = asyncio.run(async_batch())
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        def get_metadata_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            result = {
                "name": "apertium",
                "version": "2.1.0",
                "description": "Morphological analysis using Apertium APY with extended language support",
                "base_url": self.base_url,
                "supported_morph_languages": self.analyzer.get_supported_morph_languages(),
                "all_languages": self.analyzer.get_all_languages()
            }
            return_value = sai.AgentValue()
            return_value.value = {"success": True, "data": result}
            return return_value

        def get_cache_stats_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            stats = self.cache.get_stats()
            return_value = sai.AgentValue()
            return_value.value = {"success": True, "data": stats}
            return return_value

        def clear_cache_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            result = self.morph_skill.clear_cache()
            return_value = sai.AgentValue()
            return_value.value = result
            return return_value

        def get_supported_morph_languages_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            languages = self.analyzer.get_supported_morph_languages()
            return_value = sai.AgentValue()
            return_value.value = {"success": True, "data": languages}
            return return_value

        def get_all_languages_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            languages = self.analyzer.get_all_languages()
            return_value = sai.AgentValue()
            return_value.value = {"success": True, "data": languages}
            return return_value

        def get_language_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            lang = context.get('lang')

            if not lang:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Language code is required"}
                return return_value

            info = self.analyzer.get_language_info(lang)
            return_value = sai.AgentValue()
            return_value.value = {"success": True, "data": info}
            return return_value

        def is_language_supported_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            lang = context.get('lang')

            if not lang:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Language code is required"}
                return return_value

            supported = self.analyzer.validate_language(lang)
            return_value = sai.AgentValue()
            return_value.value = {"success": True, "supported": supported}
            return return_value

        def is_morph_language_supported_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            lang = context.get('lang')

            if not lang:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Language code is required"}
                return return_value

            supported = self.analyzer.validate_morph_language(lang)
            return_value = sai.AgentValue()
            return_value.value = {"success": True, "supported": supported}
            return return_value

        async def async_check_language_support(lang):
            return await self.analyzer.check_language_support(lang)

        def check_language_support_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            lang = context.get('lang')

            if not lang:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": "Language code is required"}
                return return_value

            try:
                result = asyncio.run(async_check_language_support(lang))
                return_value = sai.AgentValue()
                return_value.value = {"success": True, "data": result}
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        async def async_transliterate(text, from_script, to_script):
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
                    result = json.loads(data)

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

        def transliterate_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            text = context.get('text')
            from_script = context.get('from_script')
            to_script = context.get('to_script')

            if not text or not from_script or not to_script:
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": False, 
                    "error": "Text, from_script and to_script are required"
                }
                return return_value

            try:
                result = asyncio.run(async_transliterate(text, from_script, to_script))
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        async def async_translate(text, from_lang, to_lang):
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
                    result = json.loads(data)

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

        def translate_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
            context = agent_value.value if hasattr(agent_value, 'value') else {}
            text = context.get('text')
            from_lang = context.get('from_lang')
            to_lang = context.get('to_lang')

            if not text or not from_lang or not to_lang:
                return_value = sai.AgentValue()
                return_value.value = {
                    "success": False, 
                    "error": "Text, from_lang and to_lang are required"
                }
                return return_value

            try:
                result = asyncio.run(async_translate(text, from_lang, to_lang))
                return_value = sai.AgentValue()
                return_value.value = result
                return return_value
            except Exception as e:
                return_value = sai.AgentValue()
                return_value.value = {"success": False, "error": str(e)}
                return return_value

        self.skills = {
            'analyse': analyse_wrapper,
            'detect_language': detect_language_wrapper,
            'batch_analyse': batch_analyse_wrapper,
            'get_metadata': get_metadata_wrapper,
            'get_cache_stats': get_cache_stats_wrapper,
            'clear_cache': clear_cache_wrapper,
            'get_supported_morph_languages': get_supported_morph_languages_wrapper,
            'get_all_languages': get_all_languages_wrapper,
            'get_language_info': get_language_info_wrapper,
            'is_language_supported': is_language_supported_wrapper,
            'is_morph_language_supported': is_morph_language_supported_wrapper,
            'check_language_support': check_language_support_wrapper,
            'transliterate': transliterate_wrapper,
            'translate': translate_wrapper,
        }

        for skill_name, skill_func in self.skills.items():
            agent.add_skill(skill_func, name=skill_name)

        agent.apertium_analyzer = self.analyzer
        agent.apertium_skills = self.skills

class ApertiumAgent(sai.Agent):
    def __init__(self, base_url: str = "https://beta.apertium.org/apy", name: str = __apertium_agent_name__):
        super().__init__()
        self._name = name
        self.base_url = base_url

        self.plugin = ApertiumPlugin(base_url=base_url)
        self.plugin.apply_plugin(self)

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        agent_value = sai.AgentValue()
        agent_value.value = context
        return agent_value

    def analyse(self, text: str, lang: str = "eng", modes: str = "morph") -> Dict[str, Any]:
        context = {
            'text': text,
            'lang': lang,
            'modes': modes
        }
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['analyse'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def detect_language(self, text: str, candidate_langs: Optional[List[str]] = None) -> Dict[str, Any]:
        context = {
            'text': text,
            'candidate_langs': candidate_langs
        }
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['detect_language'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def batch_analyse(self, texts: List[str], lang: str = "eng", max_concurrent: int = 5) -> Dict[str, Any]:
        context = {
            'texts': texts,
            'lang': lang,
            'max_concurrent': max_concurrent
        }
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['batch_analyse'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_metadata(self) -> Dict[str, Any]:
        agent_value = sai.AgentValue()
        agent_value.value = {}
        result = self.plugin.skills['get_metadata'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_cache_stats(self) -> Dict[str, Any]:
        agent_value = sai.AgentValue()
        agent_value.value = {}
        result = self.plugin.skills['get_cache_stats'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def clear_cache(self) -> Dict[str, Any]:
        agent_value = sai.AgentValue()
        agent_value.value = {}
        result = self.plugin.skills['clear_cache'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_supported_morph_languages(self) -> Dict[str, Any]:
        agent_value = sai.AgentValue()
        agent_value.value = {}
        result = self.plugin.skills['get_supported_morph_languages'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_all_languages(self) -> Dict[str, Any]:
        agent_value = sai.AgentValue()
        agent_value.value = {}
        result = self.plugin.skills['get_all_languages'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def get_language_info(self, lang: str) -> Dict[str, Any]:
        context = {'lang': lang}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['get_language_info'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def is_language_supported(self, lang: str) -> Dict[str, Any]:
        context = {'lang': lang}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['is_language_supported'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def is_morph_language_supported(self, lang: str) -> Dict[str, Any]:
        context = {'lang': lang}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['is_morph_language_supported'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def check_language_support(self, lang: str) -> Dict[str, Any]:
        context = {'lang': lang}
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['check_language_support'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def transliterate(self, text: str, from_script: str, to_script: str) -> Dict[str, Any]:
        context = {
            'text': text,
            'from_script': from_script,
            'to_script': to_script
        }
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['transliterate'](agent_value)
        return result.value if hasattr(result, 'value') else result

    def translate(self, text: str, from_lang: str, to_lang: str) -> Dict[str, Any]:
        context = {
            'text': text,
            'from_lang': from_lang,
            'to_lang': to_lang
        }
        agent_value = self._create_agent_value(context)
        result = self.plugin.skills['translate'](agent_value)
        return result.value if hasattr(result, 'value') else result

def create_apertium_agent(base_url: str = "https://beta.apertium.org/apy") -> ApertiumAgent:
    return ApertiumAgent(base_url=base_url)

__all__ = [
    'ApertiumPlugin',
    'ApertiumAgent',
    'create_apertium_agent',
    'ApertiumAnalyzer',
    'ApertiumCache',
    'MorphologicalAnalysisSkill',
    'LanguageDetectionSkill',
    'BatchAnalysisSkill'
]
