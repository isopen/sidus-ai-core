import os
import sys
import base64
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.gemini import create_gemini_agent

def save_base64_image(base64_data: str, filename: str) -> bool:
    try:
        image_data = base64.b64decode(base64_data)
        with open(filename, 'wb') as f:
            f.write(image_data)
        return True
    except Exception as e:
        print(f"   Error saving image: {e}")
        return False

def main():
    print("GEMINI API")
    print("=" * 50)

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY='your_api_key'")
        return

    agent = create_gemini_agent(api_key=api_key)

    print("\n1. Text generation test:")
    print("-" * 30)

    result = agent.generate_text(
        prompt="Tell me a short joke about programming",
        model='gemini-3-flash-preview',
        temperature=0.7,
        max_tokens=500
    )

    if result.get('success'):
        candidates = result.get('candidates', [])
        if candidates:
            print(f"✅ Generated text:")
            print(f"   {candidates[0]['text']}")
            print(f"   Finish reason: {candidates[0]['finish_reason']}")
            print(f"   Token count: {candidates[0]['token_count']}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n2. Content generation with structure:")
    print("-" * 30)

    contents = [{
        "parts": [{
            "text": "Find the race condition in this multi-threaded C++ snippet: \n"
                   "int counter = 0;\n"
                   "void increment() { counter++; }\n"
                   "// Two threads calling increment() simultaneously"
        }]
    }]

    result = agent.generate_content(
        contents=contents,
        model='gemini-3-flash-preview',
        generation_config={
            "temperature": 0.2,
            "maxOutputTokens": 500
        }
    )

    if result.get('success'):
        candidates = result.get('candidates', [])
        if candidates:
            print(f"✅ Generated analysis:")
            text = candidates[0]['text']
            print(f"   {text}" if len(text) > 200 else f"   {text}")

            usage = result.get('usage_metadata', {})
            print(f"   Tokens used: {usage.get('totalTokenCount', 0)}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n3. Text embedding:")
    print("-" * 30)

    result = agent.embed_content(
        text="What is the meaning of life?",
        model='gemini-embedding-001'
    )

    if result.get('success'):
        embedding = result.get('embedding', {})
        print(f"✅ Created embedding:")
        print(f"   Dimensions: {embedding.get('dimensions', 0)}")
        print(f"   First 5 values: {embedding.get('values_preview', [])}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n4. Batch text embeddings:")
    print("-" * 30)

    texts = [
        "What is the meaning of life?",
        "How much wood would a woodchuck chuck?",
        "How does the brain work?",
        "Explain quantum computing in simple terms",
        "What is machine learning?"
    ]

    result = agent.batch_embed_contents(
        texts=texts,
        model='gemini-embedding-001'
    )

    if result.get('success'):
        print(f"✅ Created {result.get('embeddings_count', 0)} embeddings")
        summary = result.get('summary', {})
        print(f"   Average dimensions: {summary.get('avg_dimensions', 0):.2f}")

        embeddings = result.get('embeddings', [])[:3]
        if embeddings:
            print(f"\n   First 3 embeddings:")
            for i, embed in enumerate(embeddings, 1):
                print(f"   {i}. '{embed['text_preview']}'")
                print(f"      Dimensions: {embed['dimensions']}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n6. Technical question:")
    print("-" * 30)

    result = agent.generate_content(
        contents=[{
            "parts": [{
                "text": "Explain the difference between supervised and unsupervised learning with one example each."
            }]
        }],
        model='gemini-3-flash-preview',
        generation_config={
            "temperature": 0.3,
            "maxOutputTokens": 300
        }
    )

    if result.get('success'):
        candidates = result.get('candidates', [])
        if candidates:
            text = candidates[0]['text']
            print(f"✅ Explanation:")
            lines = text.split('\n')
            for line in lines[:8]:
                if line.strip():
                    print(f"   {line}")
            if len(lines) > 8:
                print(f"   ...")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n7. Image generation with Imagen:")
    print("-" * 30)

    result = agent.generate_image(
        prompt="Robot holding a red skateboard in futuristic city, digital art style",
        model='imagen-4.0-generate-001',
        sample_count=1,
        parameters={
            "aspectRatio": "1:1",
            "negativePrompt": "blurry, low quality, distorted"
        }
    )

    if result.get('success'):
        predictions = result.get('predictions', [])
        print(f"✅ Generated {len(predictions)} images with Imagen model")
        for i, pred in enumerate(predictions, 1):
            print(f"   Image {i}: {pred['mimeType']}, Size: {pred['image_size']} bytes")

            if pred.get('bytes'):
                filename = f"imagen_robot_skateboard_{i}.png"
                if save_base64_image(pred['bytes'], filename):
                    print(f"      Saved to: {filename}")
                else:
                    print(f"      Failed to save image")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n8. Image generation - Cyberpunk style:")
    print("-" * 30)

    result = agent.generate_image(
        prompt="Create a picture of a futuristic banana with neon lights in a cyberpunk city, digital art style",
        model='imagen-4.0-generate-001',
        sample_count=1
    )

    if result.get('success'):
        predictions = result.get('predictions', [])
        if predictions:
            pred = predictions[0]
            print(f"✅ Generated cyberpunk banana image")
            print(f"   Format: {pred['mimeType']}")
            print(f"   Data size: {pred['image_size']} bytes")

            if pred.get('bytes'):
                filename = f"imagen_cyberpunk_banana.png"
                if save_base64_image(pred['bytes'], filename):
                    print(f"   Saved to: {filename}")
                else:
                    print(f"   Failed to save image")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n9. Robot skill - Image analysis (requires image file):")
    print("-" * 30)

    image_path = "test_image.png"
    if os.path.exists(image_path):
        result = agent.analyze_image(
            image_path=image_path,
            prompt="Point to no more than 10 items in the image. The label returned should be an identifying name for the object detected. The answer should follow the json format: [{\"point\": [y, x], \"label\": <label1>}, ...]. The points are in [y, x] format normalized to 0-1000.",
            model='gemini-3-flash-preview',
            temperature=0.5,
            thinking_budget=0
        )

        if result.get('success'):
            candidates = result.get('candidates', [])
            if candidates:
                candidate = candidates[0]
                print(f"✅ Image analysis complete")
                print(f"   Response: {candidate['text_response'][:150]}..." if len(candidate['text_response']) > 150 else f"   Response: {candidate['text_response']}")

                if candidate.get('is_valid_json'):
                    print(f"   Valid JSON detected")
                    parsed = candidate.get('parsed_json', [])
                    print(f"   Found {len(parsed)} objects")
                    for i, obj in enumerate(parsed[:3], 1):
                        if isinstance(obj, dict):
                            print(f"   Object {i}: {obj.get('label', 'Unknown')} at point {obj.get('point', [])}")
                else:
                    print(f"   Response is not valid JSON")
    else:
        print(f"⚠️  Skipping image analysis - test image not found at '{image_path}'")
        print(f"   Create a test image or specify your own image path")

    print("\n10. Test connection with simple prompt:")
    print("-" * 30)

    result = agent.generate_text(
        prompt="Hello, are you working?",
        model='gemini-3-flash-preview',
        temperature=0.1,
        max_tokens=10
    )

    if result.get('success'):
        print(f"✅ Connection test successful")
        candidates = result.get('candidates', [])
        if candidates:
            print(f"   Response: {candidates[0]['text']}")
    else:
        print(f"❌ Connection test failed: {result.get('error')}")

if __name__ == "__main__":
    main()
