import asyncio
import json
import sys
import os
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
from sidusai.plugins.apertium import ApertiumPlugin

async def main():
    plugin = ApertiumPlugin()

    config = {
        "base_url": "https://beta.apertium.org/apy",
        "cache_size": 500
    }

    if await plugin.initialize(config):
        print("✓ Plugin successfully initialized")
    else:
        print("✗ Plugin initialization error")
        return

    try:
        print("\n1. Analysis of English word 'running':")
        result = await plugin.analyse("running", lang="eng")
        print(f"   Analyses found: {result['summary']['analysis_count']}")
        if result['data']['analyses']:
            print(f"   First analysis: {json.dumps(result['data']['analyses'][0], indent=2, ensure_ascii=False)}")

        print("\n2. Analysis of Spanish word 'corriendo':")
        result = await plugin.analyse("corriendo", lang="spa")
        print(f"   Analyses found: {result['summary']['analysis_count']}")
        if result['data']['analyses']:
            print(f"   First analysis: {json.dumps(result['data']['analyses'][0], indent=2, ensure_ascii=False)}")

        print("\n3. Language detection for English text:")
        result = await plugin.detect_language("I am reading a book")
        print(f"   Detected: {result['detected_language']} (confidence: {result['confidence']})")

        print("\n4. Language detection for Spanish text:")
        result = await plugin.detect_language("Estoy leyendo un libro")
        print(f"   Detected: {result['detected_language']} (confidence: {result['confidence']})")

        print("\n5. Batch analysis of multiple words:")
        words = ["running", "corriendo", "читаю", "okuyorum"]
        result = await plugin.batch_analyse(words, lang="eng", max_concurrent=2)
        print(f"   Total texts: {result['summary']['total_texts']}")
        print(f"   Successful: {result['summary']['successful']}")
        print(f"   Failed: {result['summary']['failed']}")

        print("\n6. Supported languages:")
        morph_langs = plugin.get_supported_morph_languages()
        print(f"   For morphological analysis: {len(morph_langs)} languages")

        print("\n7. Language info:")
        for lang in ["eng", "spa", "fra", "rus"]:
            info = plugin.get_language_info(lang)
            status = "✓" if info.get('morph_supported') else "✗"
            print(f"   {status} {lang}: {info.get('name')}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await plugin.shutdown()
        print("\n✓ Plugin shutdown completed")

if __name__ == "__main__":
    asyncio.run(main())
