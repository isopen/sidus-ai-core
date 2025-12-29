import json
import sys
import os
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
from sidusai.plugins.apertium import create_apertium_agent

def main():
    agent = create_apertium_agent()

    print("1. Analysis of English word 'running':")
    result = agent.analyse("running", lang="eng")
    if result.get("success"):
        if "data" in result and "analyses" in result["data"]:
            print(f"   Analyses found: {len(result['data']['analyses'])}")
            if result["data"]["analyses"]:
                print(f"   First analysis: {json.dumps(result['data']['analyses'][0], indent=2, ensure_ascii=False)}")
    else:
        print(f"   Error: {result.get('error')}")

    print("\n2. Analysis of Spanish word 'corriendo':")
    result = agent.analyse("corriendo", lang="spa")
    if result.get("success"):
        if "data" in result and "analyses" in result["data"]:
            print(f"   Analyses found: {len(result['data']['analyses'])}")
            if result["data"]["analyses"]:
                print(f"   First analysis: {json.dumps(result['data']['analyses'][0], indent=2, ensure_ascii=False)}")
    else:
        print(f"   Error: {result.get('error')}")

    print("\n3. Language detection for English text:")
    result = agent.detect_language("I am reading a book")
    if result.get("success"):
        print(f"   Detected: {result.get('detected_language')} (confidence: {result.get('confidence')})")
    else:
        print(f"   Error: {result.get('error')}")

    print("\n4. Language detection for Spanish text:")
    result = agent.detect_language("Estoy leyendo un libro")
    if result.get("success"):
        print(f"   Detected: {result.get('detected_language')} (confidence: {result.get('confidence')})")
    else:
        print(f"   Error: {result.get('error')}")

    print("\n5. Batch analysis of multiple words:")
    words = ["running", "corriendo", "читаю", "okuyorum"]
    result = agent.batch_analyse(words, lang="eng", max_concurrent=2)
    if result.get("success"):
        summary = result.get("summary", {})
        print(f"   Total texts: {summary.get('total_texts')}")
        print(f"   Successful: {summary.get('successful')}")
        print(f"   Failed: {summary.get('failed')}")
    else:
        print(f"   Error: {result.get('error')}")

    print("\n6. Supported languages:")
    result = agent.get_supported_morph_languages()
    if result.get("success"):
        languages = result.get("data", {})
        print(f"   For morphological analysis: {len(languages)} languages")
        print(f"   First 5: {list(languages.keys())[:5]}")
    else:
        print(f"   Error: {result.get('error')}")

    print("\n7. Language info:")
    for lang in ["eng", "spa", "fra", "rus"]:
        result = agent.get_language_info(lang)
        if result.get("success"):
            info = result.get("data", {})
            status = "✓" if info.get('morph_supported') else "✗"
            print(f"   {status} {lang}: {info.get('name')}")
        else:
            print(f"   ✗ {lang}: Error - {result.get('error')}")

    print("\n8. Metadata:")
    result = agent.get_metadata()
    if result.get("success"):
        metadata = result.get("data", {})
        print(f"   Plugin: {metadata.get('name')} v{metadata.get('version')}")
        print(f"   Base URL: {metadata.get('base_url')}")
    else:
        print(f"   Error: {result.get('error')}")

    print("\n9. Cache stats:")
    result = agent.get_cache_stats()
    if result.get("success"):
        stats = result.get("data", {})
        print(f"   Cache size: {stats.get('size')}/{stats.get('max_size')}")
    else:
        print(f"   Error: {result.get('error')}")

    print("\n✓ Test completed")

if __name__ == "__main__":
    main()
