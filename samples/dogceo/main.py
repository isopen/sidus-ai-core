import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
from sidusai.plugins.dogceo import create_dogceo_agent

def main():
    print("=" * 60)
    print("🐶 DOG CEO IMAGE GENERATOR EXAMPLE")
    print("=" * 60)

    print("\nCreating Dog CEO Agent...")
    agent = create_dogceo_agent()

    print("\n1. Getting all dog breeds...")
    breeds_result = agent.get_all_breeds()

    if breeds_result.get('success'):
        breeds = breeds_result.get('breeds', [])
        categories = breeds_result.get('categories', {})

        print(f"✅ Found {len(breeds)} dog breeds")
        print("\nCategories:")
        for category, category_breeds in categories.items():
            print(f"  • {category}: {len(category_breeds)} breeds")
    else:
        print(f"❌ Error: {breeds_result.get('error')}")

    print("\n2. Getting random dog image...")
    random_result = agent.get_random_dog()

    if random_result.get('success'):
        images = random_result.get('images', [])
        if images:
            print(f"✅ Random dog image URL: {images[0]}")
    else:
        print(f"❌ Error: {random_result.get('error')}")

    print("\n3. Getting Labrador images...")
    labrador_result = agent.get_breed_images("labrador", 3)

    if labrador_result.get('success'):
        images = labrador_result.get('images', [])
        print(f"✅ Found {len(images)} Labrador images")
        for i, img_url in enumerate(images[:2], 1):
            print(f"  {i}. {img_url}")
    else:
        print(f"❌ Error: {labrador_result.get('error')}")

    print("\n4. Getting Bulldog sub-breeds...")
    sub_result = agent.get_sub_breeds("bulldog")

    if sub_result.get('success'):
        sub_breeds = sub_result.get('sub_breeds', [])
        print(f"✅ Bulldog has {len(sub_breeds)} sub-breeds:")
        for sub in sub_breeds:
            print(f"  • {sub}")
    else:
        print(f"❌ Error: {sub_result.get('error')}")

    print("\n5. Testing chat interface...")
    chat_response = agent.chat("breeds")
    print(f"🤖 Agent response: {chat_response[:200]}...")

    print("\n" + "=" * 60)
    print("✅ Example completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
