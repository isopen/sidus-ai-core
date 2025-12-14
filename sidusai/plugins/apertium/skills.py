from typing import Dict, Any, List, Optional
from datetime import datetime
from .components import ApertiumAnalyzer, ApertiumCache

class MorphologicalAnalysisSkill:
    def __init__(self, analyzer: Optional[ApertiumAnalyzer] = None, cache: Optional[ApertiumCache] = None):
        self.analyzer = analyzer or ApertiumAnalyzer()
        self.cache = cache or ApertiumCache(max_size=500)
        self.name = "morphological_analysis"
        self.description = "Analyze morphology of words using Apertium"
        self.version = "1.0.0"

    async def execute(
        self, 
        text: str, 
        lang: str = "eng", 
        modes: str = "morph",
        use_cache: bool = True,
        detailed: bool = False
    ) -> Dict[str, Any]:
        if not text or not text.strip():
            return self._create_error_response("Text cannot be empty")

        if not self.analyzer.validate_morph_language(lang):
            return self._create_error_response(
                f"Unsupported language for morphological analysis: {lang}",
                {"supported_languages": self.analyzer.get_supported_morph_languages()}
            )

        if use_cache:
            cached_result = self.cache.get(text, lang, modes)
            if cached_result:
                return self._enhance_response(cached_result, from_cache=True)

        start_time = datetime.now()
        result = await self.analyzer.analyse_text(text, lang, modes)
        processing_time = (datetime.now() - start_time).total_seconds()

        if "error" in result:
            print(f"Analysis error: {result['error']}")
            return self._enhance_response(result, processing_time)

        if use_cache and "error" not in result:
            self.cache.set(text, lang, modes, result)

        enhanced = self._enhance_response(result, processing_time, detailed)

        print(f"Analysis completed for '{text[:30]}...' in {processing_time:.2f}s")
        return enhanced

    def _enhance_response(
        self, 
        result: Dict[str, Any], 
        processing_time: float = 0.0,
        detailed: bool = False,
        from_cache: bool = False
    ) -> Dict[str, Any]:
        enhanced = {
            "success": "error" not in result,
            "timestamp": datetime.now().isoformat(),
            "processing_time": processing_time,
            "from_cache": from_cache,
            "data": result
        }

        if "error" in result:
            enhanced["error"] = result["error"]
            return enhanced

        if "analyses" in result:
            analyses = result["analyses"]
            enhanced["summary"] = {
                "word_count": len(result.get("text", "").split()),
                "analysis_count": len(analyses),
                "unique_lemmas": len(set(a.get("lemma", "") for a in analyses)),
                "tags_found": sum(len(a.get("tags", [])) for a in analyses)
            }

            if detailed:
                enhanced["detailed_analysis"] = self._create_detailed_analysis(analyses)

        return enhanced

    def _create_detailed_analysis(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        detailed = {
            "by_lemma": {},
            "by_tag": {},
            "tag_frequency": {}
        }

        for analysis in analyses:
            lemma = analysis.get("lemma", "unknown")
            tags = analysis.get("tags", [])

            if lemma not in detailed["by_lemma"]:
                detailed["by_lemma"][lemma] = []
            detailed["by_lemma"][lemma].append({
                "tags": tags,
                "original": analysis.get("original", "")
            })

            for tag in tags:
                if tag not in detailed["tag_frequency"]:
                    detailed["tag_frequency"][tag] = 0
                detailed["tag_frequency"][tag] += 1

                if tag not in detailed["by_tag"]:
                    detailed["by_tag"][tag] = []
                detailed["by_tag"][tag].append(lemma)

        detailed["tag_frequency"] = dict(
            sorted(detailed["tag_frequency"].items(), key=lambda x: x[1], reverse=True)
        )

        return detailed

    def _create_error_response(self, message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        response = {
            "success": False,
            "error": message,
            "timestamp": datetime.now().isoformat(),
            "processing_time": 0.0,
            "from_cache": False,
            "data": {}
        }

        if details:
            response["details"] = details

        return response

    def get_cache_stats(self) -> Dict[str, Any]:
        return self.cache.get_stats()

    def clear_cache(self) -> Dict[str, Any]:
        previous_size = len(self.cache.cache)
        self.cache.clear()
        return {
            "success": True,
            "message": f"Cache cleared ({previous_size} items removed)",
            "previous_size": previous_size,
            "current_size": 0
        }


class LanguageDetectionSkill:

    def __init__(self, analyzer: Optional[ApertiumAnalyzer] = None):
        self.analyzer = analyzer or ApertiumAnalyzer()
        self.name = "language_detection"
        self.description = "Detect language of text using Apertium capabilities"
        self.version = "1.0.0"

    async def execute(self, text: str, candidate_langs: Optional[List[str]] = None) -> Dict[str, Any]:
        if not text or not text.strip():
            return self._create_error_response("Text cannot be empty")

        if not candidate_langs:
            candidate_langs = list(self.analyzer.supported_morph_languages.keys())

        valid_langs = []
        invalid_langs = []

        for lang in candidate_langs:
            if self.analyzer.validate_morph_language(lang):
                valid_langs.append(lang)
            else:
                invalid_langs.append(lang)

        if not valid_langs:
            return self._create_error_response(
                "No valid languages to check for morphological analysis",
                {
                    "invalid_languages": invalid_langs,
                    "supported_morph_languages": list(self.analyzer.supported_morph_languages.keys())
                }
            )

        print(f"Detecting language for text: '{text[:50]}...' among {len(valid_langs)} languages")

        results = []
        start_time = datetime.now()

        for lang in valid_langs:
            try:
                print(f"  Testing language: {lang} ({self.analyzer.supported_morph_languages.get(lang, 'Unknown')})")
                result = await self.analyzer.analyse_text(text, lang, "morph")

                score = 0.0
                if "error" not in result:
                    if "analyses" in result and result["analyses"]:
                        analyses = result["analyses"]
                        analysis_count = len(analyses)

                        if analysis_count > 0:
                            base_score = 0.3
                            count_score = min(0.3, analysis_count * 0.05)
                            avg_tags = sum(len(a.get("tags", [])) for a in analyses) / analysis_count
                            tag_score = min(0.4, avg_tags * 0.1)
                            score = base_score + count_score + tag_score

                            if len(text.split()) < 2 and analysis_count == 1:
                                score *= 0.8

                results.append({
                    "language": lang,
                    "language_name": self.analyzer.supported_morph_languages.get(lang, lang),
                    "score": round(score, 3),
                    "analysis_count": len(result.get("analyses", [])),
                    "success": "error" not in result,
                    "error": result.get("error") if "error" in result else None
                })

            except Exception as e:
                print(f"Failed to analyze with language {lang}: {e}")
                results.append({
                    "language": lang,
                    "language_name": self.analyzer.supported_morph_languages.get(lang, lang),
                    "score": 0.0,
                    "error": str(e),
                    "success": False
                })

        results.sort(key=lambda x: x["score"], reverse=True)

        processing_time = (datetime.now() - start_time).total_seconds()

        detected_lang = None
        confidence = 0.0

        if results:
            top_result = results[0]
            if top_result["score"] > 0.1:
                detected_lang = top_result["language"]
                confidence = top_result["score"]

        top_candidates = []
        for result in results[:3]:
            lang_info = self.analyzer.get_language_info(result["language"])
            top_candidates.append({
                **result,
                "language_info": lang_info
            })

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "processing_time": round(processing_time, 3),
            "text_length": len(text),
            "text_sample": text[:100] + ("..." if len(text) > 100 else ""),
            "detected_language": detected_lang,
            "detected_language_name": self.analyzer.supported_morph_languages.get(detected_lang, detected_lang) if detected_lang else None,
            "confidence": round(confidence, 3),
            "all_results": results,
            "top_candidates": top_candidates,
            "invalid_candidates": invalid_langs,
            "total_tested": len(valid_langs)
        }

    def _create_error_response(self, message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        response = {
            "success": False,
            "error": message,
            "timestamp": datetime.now().isoformat(),
            "processing_time": 0.0
        }

        if details:
            response["details"] = details

        return response


class BatchAnalysisSkill:

    def __init__(self, analyzer: Optional[ApertiumAnalyzer] = None, cache: Optional[ApertiumCache] = None):
        self.analyzer = analyzer or ApertiumAnalyzer()
        self.cache = cache or ApertiumCache(max_size=1000)
        self.name = "batch_analysis"
        self.description = "Batch morphological analysis of multiple texts"
        self.version = "1.0.0"

    async def execute(
        self, 
        texts: List[str], 
        lang: str = "eng", 
        modes: str = "morph",
        max_concurrent: int = 5
    ) -> Dict[str, Any]:
        if not texts:
            return self._create_error_response("Texts list cannot be empty")

        if not self.analyzer.validate_morph_language(lang):
            return self._create_error_response(
                f"Unsupported language for morphological analysis: {lang}",
                {"supported_languages": self.analyzer.get_supported_morph_languages()}
            )

        start_time = datetime.now()
        results = []
        successful = 0
        failed = 0

        import asyncio

        for i in range(0, len(texts), max_concurrent):
            batch = texts[i:i + max_concurrent]
            batch_tasks = []

            for text in batch:
                task = self._analyze_single(text, lang, modes)
                batch_tasks.append(task)

            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                for j, result in enumerate(batch_results):
                    text = batch[j]

                    if isinstance(result, Exception):
                        print(f"Failed to analyze '{text}': {result}")
                        results.append({
                            "text": text,
                            "success": False,
                            "error": str(result)
                        })
                        failed += 1
                    else:
                        results.append(result)
                        if result.get("success"):
                            successful += 1
                        else:
                            failed += 1

            except Exception as e:
                print(f"Batch processing error: {e}")
                for text in batch:
                    results.append({
                        "text": text,
                        "success": False,
                        "error": f"Batch processing error: {str(e)}"
                    })
                    failed += 1

        processing_time = (datetime.now() - start_time).total_seconds()

        summary = {
            "total_texts": len(texts),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(texts) if texts else 0,
            "processing_time": processing_time,
            "avg_time_per_text": processing_time / len(texts) if texts else 0,
            "language": lang,
            "modes": modes
        }

        cache_stats = self.cache.get_stats()

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "results": results,
            "cache_stats": cache_stats
        }

    async def _analyze_single(self, text: str, lang: str, modes: str) -> Dict[str, Any]:
        skill = MorphologicalAnalysisSkill(self.analyzer, self.cache)
        return await skill.execute(text, lang, modes, use_cache=True, detailed=False)

    def _create_error_response(self, message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        response = {
            "success": False,
            "error": message,
            "timestamp": datetime.now().isoformat(),
            "processing_time": 0.0
        }

        if details:
            response["details"] = details

        return response

__all__ = [
    "MorphologicalAnalysisSkill",
    "LanguageDetectionSkill", 
    "BatchAnalysisSkill"
]
