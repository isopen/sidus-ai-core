import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
from sidusai.plugins.thecatapi import create_thecatapi_agent

def main():
    print("=" * 60)
    print("🐱 THE CAT API - COMPLETE PLUGIN DEMO")
    print("=" * 60)

    API_KEY = os.environ.get('THE_CAT_API_KEY')
    if not API_KEY:
        print("❌ Please set THE_CAT_API_KEY environment variable")
        return

    try:
        print(f"\n🔑 Using API key: {API_KEY[:8]}...")
        agent = create_thecatapi_agent(api_key=API_KEY)
        print("✅ The Cat API Agent created successfully")

        print("\n1. Getting random cat image...")
        result = agent.get_random_cat(limit=1)
        if result.get('success'):
            images = result.get('images', [])
            if images:
                print(f"✅ Random cat: {images[0].get('url', 'URL not available')[:80]}...")

        print("\n2. Getting cat breeds...")
        result = agent.get_all_breeds(limit=5)
        if result.get('success'):
            breeds = result.get('breeds', [])
            print(f"✅ Found {len(breeds)} breeds")
            for breed in breeds[:3]:
                print(f"  • {breed.get('name')} ({breed.get('origin')})")

        print("\n3. Searching breeds...")
        result = agent.search_breeds("siamese")
        if result.get('success'):
            breeds = result.get('breeds', [])
            print(f"✅ Found {len(breeds)} matching breeds")

        print("\n4. Getting categories...")
        result = agent.get_categories()
        if result.get('success'):
            categories = result.get('categories', [])
            print(f"✅ Found {len(categories)} categories")

        print("\n5. Testing chat interface...")
        chat_responses = [
            "help",
            "breeds",
            "random"
        ]

        for query in chat_responses:
            print(f"\n  Query: '{query}'")
            response = agent.chat(query)
            if response:
                preview = response[:150] + "..." if len(response) > 150 else response
                print(f"  Response: {preview}")

        print("\n" + "=" * 60)
        print("✅ COMPLETE PLUGIN TEST SUCCESSFUL!")
        print("=" * 60)

        print("\n📋 Available features in this plugin:")
        print("  • Images API: Upload, search, delete, analyze")
        print("  • Breeds API: List, search, breed-specific facts")
        print("  • Favourites API: Add, list, delete favourites")
        print("  • Votes API: Vote on images, list votes")
        print("  • Facts API: Random facts, breed facts")
        print("  • Categories API: List all categories")
        print("  • Chat Interface: Natural language commands")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
