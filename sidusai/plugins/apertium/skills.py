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

        words = [w.strip('.,!?;:"\'()[]{}') for w in text.split()]
        words = [w for w in words if w]

        language_character_patterns = {
            "eng": [(" the ", 5), (" and ", 4), ("ing ", 3), (" of ", 3), (" to ", 3), (" a ", 2)],
            "spa": [(" el ", 5), (" la ", 5), (" y ", 4), (" de ", 4), (" que ", 4), (" en ", 3)],
            "fra": [(" le ", 5), (" la ", 5), (" et ", 4), (" de ", 4), (" que ", 4), (" est ", 3)],
            "por": [(" o ", 5), (" a ", 5), (" e ", 4), (" de ", 4), (" que ", 4), (" do ", 3)],
            "tur": [(" ve ", 5), (" bir ", 4), (" için ", 4), (" ama ", 3), (" ile ", 3)],
        }

        for lang in valid_langs:
            try:
                print(f"  Testing language: {lang} ({self.analyzer.supported_morph_languages.get(lang, 'Unknown')})")
                result = await self.analyzer.analyse_text(text, lang, "morph")

                score = 0.0
                is_valid_analysis = False
                meaningful_analyses = 0
                total_analyses = 0

                if "error" not in result:
                    if "analyses" in result and result["analyses"]:
                        analyses = result["analyses"]
                        total_analyses = len(analyses)

                        if analyses:
                            for analysis in analyses:
                                if isinstance(analysis, dict):
                                    lemma = analysis.get("lemma", "")
                                    tags = analysis.get("tags", [])

                                    if lemma and lemma != "*" and lemma != text.lower() and lemma != "?":
                                        if tags and len(tags) > 0:
                                            meaningful_analyses += 1
                                            is_valid_analysis = True

                            if is_valid_analysis and meaningful_analyses > 0:
                                if len(words) == 1:
                                    word_score = 1.0 if meaningful_analyses == 1 else 0.5
                                else:
                                    word_score = min(1.0, meaningful_analyses / len(words))

                                tag_counts = []
                                for analysis in analyses:
                                    if isinstance(analysis, dict):
                                        lemma = analysis.get("lemma", "")
                                        if lemma and lemma != "*" and lemma != text.lower():
                                            tags = analysis.get("tags", [])
                                            if tags:
                                                tag_counts.append(len(tags))

                                avg_tags = sum(tag_counts) / len(tag_counts) if tag_counts else 0
                                tag_score = min(0.4, avg_tags * 0.1)

                                quality_ratio = meaningful_analyses / total_analyses if total_analyses > 0 else 0
                                quality_score = min(0.6, quality_ratio * 0.6)

                                base_score = word_score * 0.4 + tag_score * 0.3 + quality_score * 0.3

                                pattern_score = 0
                                text_lower = " " + text.lower() + " "
                                if lang in language_character_patterns:
                                    for pattern, weight in language_character_patterns[lang]:
                                        if pattern in text_lower:
                                            pattern_score += weight

                                pattern_bonus = min(0.2, pattern_score * 0.05)

                                score = base_score + pattern_bonus

                                if lang in ["eng", "spa", "fra"]:
                                    score *= 1.05
                            else:
                                score = 0.1
                        else:
                            score = 0.05
                    else:
                        score = 0.05
                else:
                    score = 0.0

                results.append({
                    "language": lang,
                    "language_name": self.analyzer.supported_morph_languages.get(lang, lang),
                    "score": round(score, 3),
                    "analysis_count": total_analyses,
                    "meaningful_analyses": meaningful_analyses,
                    "valid_analysis": is_valid_analysis,
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
                    "success": False,
                    "valid_analysis": False,
                    "meaningful_analyses": 0,
                    "analysis_count": 0
                })

        results.sort(key=lambda x: x["score"], reverse=True)

        processing_time = (datetime.now() - start_time).total_seconds()

        detected_lang = None
        confidence = 0.0

        if results:
            top_result = results[0]
            second_result = results[1] if len(results) > 1 else None

            threshold = 0.4 if len(words) > 2 else 0.5

            if top_result["score"] > threshold:
                detected_lang = top_result["language"]
                confidence = top_result["score"]

                if second_result:
                    score_diff = top_result["score"] - second_result["score"]
                    if score_diff < 0.15:
                        confidence *= 0.85
                    elif score_diff > 0.3:
                        confidence = min(confidence * 1.2, 1.0)

            print(f"\nTop 5 candidates:")
            for i, result in enumerate(results[:5], 1):
                print(f"  {i}. {result['language']} ({result['language_name']}): {result['score']:.3f} (meaningful: {result['meaningful_analyses']}/{result['analysis_count']})")

        top_candidates = []
        for result in results[:5]:
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
            "word_count": len(words),
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
