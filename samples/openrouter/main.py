import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
from datetime import datetime
from sidusai.plugins.openrouter import create_openrouter_agent

def print_model_info(model):
    if not model:
        print("No model found")
        return

    print(f"Model: {model.get('name', model['id'])}")
    print(f"ID: {model['id']}")
    print(f"Category: {model.get('category', 'Unknown')}")
    print(f"Context Length: {model.get('context_length', 0)} tokens")
    print(f"Is Free: {model.get('is_free', False)}")

    if not model.get('is_free', False):
        pricing = model.get('pricing', {})
        prompt_price = float(pricing.get('prompt', 0))
        completion_price = float(pricing.get('completion', 0))
        total = prompt_price + completion_price
        print(f"Total Price per 1K: ${total:.6f} USD")

def main():
    print("Testing cheapest model finding")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("\nERROR: No API key found!")
        print("Set: export OPENROUTER_API_KEY='your_key_here'")
        return

    agent = create_openrouter_agent(api_key=api_key)

    print("\nTesting connection...")
    models_result = agent.get_available_models(free_only=True)
    if models_result.get('success') and len(models_result.get('models', [])) > 0:
        print("Connection successful")
    else:
        print("Connection failed")
        return

    print("\n" + "=" * 70)
    print("Test 1: Find cheapest overall model")
    print("=" * 70)

    models_result = agent.get_available_models(free_only=True)
    if models_result.get('success'):
        free_models = models_result.get('models', [])
        if free_models:
            cheapest = free_models[0]
            print_model_info(cheapest)
        else:
            print("No free models found")

    print("\n" + "=" * 70)
    print("Test 2: Top 5 cheapest models")
    print("=" * 70)

    models_result = agent.get_available_models(free_only=False)
    if models_result.get('success'):
        all_models = models_result.get('models', [])

        def get_model_cost(model):
            if model.get('is_free'):
                return 0
            pricing = model.get('pricing', {})
            prompt_price = float(pricing.get('prompt', 0))
            completion_price = float(pricing.get('completion', 0))
            return prompt_price + completion_price

        sorted_models = sorted(all_models, key=get_model_cost)

        for i, model in enumerate(sorted_models[:5], 1):
            print(f"\n#{i}:")
            print_model_info(model)

    print("\n" + "=" * 70)
    print("Test 4: Find cheapest model with minimum 4K context")
    print("=" * 70)

    models_result = agent.get_available_models(free_only=False)
    if models_result.get('success'):
        all_models = models_result.get('models', [])

        filtered_models = [m for m in all_models if m.get('context_length', 0) >= 4096]

        if filtered_models:
            def get_model_cost(model):
                if model.get('is_free'):
                    return 0
                pricing = model.get('pricing', {})
                prompt_price = float(pricing.get('prompt', 0))
                completion_price = float(pricing.get('completion', 0))
                return prompt_price + completion_price

            filtered_models.sort(key=get_model_cost)
            cheapest_4k = filtered_models[0]
            print_model_info(cheapest_4k)

    print("\n" + "=" * 70)
    print("Test 5: Cost analysis")
    print("=" * 70)

    models_result = agent.get_available_models(free_only=False)
    if models_result.get('success'):
        all_models = models_result.get('models', [])

        total_models = len(all_models)
        free_models = len([m for m in all_models if m.get('is_free', False)])
        paid_models = total_models - free_models

        print(f"Total Models: {total_models}")
        print(f"Free Models: {free_models}")
        print(f"Paid Models: {paid_models}")

        paid_only = [m for m in all_models if not m.get('is_free', False)]

        price_ranges = {
            "free": free_models,
            "ultra_low": 0,
            "low": 0,
            "medium": 0,
            "high": 0,
            "very_high": 0
        }

        for model in paid_only:
            pricing = model.get('pricing', {})
            total_price = float(pricing.get('prompt', 0)) + float(pricing.get('completion', 0))

            if total_price < 0.001:
                price_ranges["ultra_low"] += 1
            elif total_price < 0.01:
                price_ranges["low"] += 1
            elif total_price < 0.1:
                price_ranges["medium"] += 1
            elif total_price < 1.0:
                price_ranges["high"] += 1
            else:
                price_ranges["very_high"] += 1

        print("\nPrice Ranges:")
        for range_name, count in price_ranges.items():
            if count > 0:
                print(f"  {range_name}: {count} models")

        if paid_only:
            prompt_prices = []
            completion_prices = []
            total_prices = []

            for model in paid_only:
                pricing = model.get('pricing', {})
                prompt_prices.append(float(pricing.get('prompt', 0)))
                completion_prices.append(float(pricing.get('completion', 0)))
                total_prices.append(float(pricing.get('prompt', 0)) + float(pricing.get('completion', 0)))

            def safe_average(values):
                return sum(values) / len(values) if values else 0

            print("\nAverage Costs:")
            avg = safe_average(total_prices)
            print(f"  Total per 1K: ${avg:.6f} USD")

            print("\nMinimum Costs:")
            min_total = min(total_prices) if total_prices else 0
            print(f"  Total per 1K: ${min_total:.6f} USD")

            print("\nMaximum Costs:")
            max_total = max(total_prices) if total_prices else 0
            print(f"  Total per 1K: ${max_total:.6f} USD")

    print("\n" + "=" * 70)
    print("Test 6: Compare specific models")
    print("=" * 70)

    test_models = [
        "google/gemma-7b-it",
        "microsoft/phi-3-mini-4k-instruct", 
        "mistralai/mistral-7b-instruct",
        "amazon/nova-2-lite-v1:free"
    ]

    for model_id in test_models:
        model_info = agent.get_model_info(model_id)
        if model_info.get('success'):
            model_data = model_info['model_info']
            print(f"\n{model_data['id']}:")
            print(f"  Total per 1K: ${model_data.get('total_per_1k', 0):.6f} USD" if 'total_per_1k' in model_data else "  Total per 1K: Calculating...")
            print(f"  Is Free: {model_data.get('is_free', False)}")
            print(f"  Context: {model_data.get('context_length', 0):,} tokens")

    print("\n" + "=" * 70)
    print("Test 7: Calculate usage cost")
    print("=" * 70)

    models_result = agent.get_available_models(free_only=True)
    if models_result.get('success'):
        free_models = models_result.get('models', [])
        if free_models:
            cheapest_id = free_models[0]['id']

            cost_result = agent.calculate_cost(
                model=cheapest_id,
                prompt_tokens=1000,
                completion_tokens=500
            )

            if cost_result.get('success'):
                usage = cost_result['cost_info']
                print(f"Model: {usage['model_name']}")
                print(f"Total Tokens: {usage['total_tokens']:,}")
                print(f"Total Cost: ${usage['total_cost']:.6f} USD")
                print(f"Is Free: {usage['is_free']}")

    print("\n" + "=" * 70)
    print("Test 8: Find cheapest paid-only model")
    print("=" * 70)

    models_result = agent.get_available_models(free_only=False)
    if models_result.get('success'):
        all_models = models_result.get('models', [])

        paid_models = [m for m in all_models if not m.get('is_free', False)]

        if paid_models:
            def get_model_cost(model):
                pricing = model.get('pricing', {})
                prompt_price = float(pricing.get('prompt', 0))
                completion_price = float(pricing.get('completion', 0))
                return prompt_price + completion_price

            paid_models.sort(key=get_model_cost)
            cheapest_paid = paid_models[0]
            print_model_info(cheapest_paid)

    print("\n" + "=" * 70)
    print("Test 3: Testing Amazon Nova 2 Lite model specifically")
    print("=" * 70)

    amazon_model_id = "amazon/nova-2-lite-v1:free"
    print(f"\nLooking for model: {amazon_model_id}")

    model_info = agent.get_model_info(amazon_model_id)
    if model_info.get('success'):
        amazon_model = model_info['model_info']
        print("✓ Found Amazon Nova 2 Lite model!")
        print_model_info(amazon_model)

        print("\nTesting chat with Amazon Nova 2 Lite...")
        messages = [
            {
                "role": "system", 
                "content": "You are Amazon Nova 2 Lite, a helpful AI assistant with 1M token context. Be concise."
            },
            {
                "role": "user", 
                "content": "Reply simply OK if you received this message"
            }
        ]

        response = agent.chat_completion(
            messages=messages,
            model=amazon_model_id,
            temperature=0.7,
            max_tokens=30
        )

        if response.get('success'):
            print("\n✅ Amazon Nova 2 Lite response:")
            print("-" * 50)
            print(response.get('content', ''))
            print("-" * 50)

            usage = response.get('usage', {})
            if usage:
                print(f"\nToken usage: {usage.get('total_tokens', 0)} tokens")

            print(f"\n🆓 This model is FREE!")
        else:
            print(f"\n❌ Chat failed: {response.get('error')}")
    else:
        print(f"\n❌ Amazon Nova 2 Lite model not found")
        print("Checking all available free models...")
        free_models_result = agent.get_available_models(free_only=True)
        if free_models_result.get('success'):
            free_models = free_models_result.get('models', [])
            print(f"\nFound {len(free_models)} free models:")
            for i, model in enumerate(free_models[:10], 1):
                print(f"{i}. {model['id']} - {model.get('name', 'Unknown')}")

    print("\n" + "=" * 70)
    print("All tests completed!")
    print("=" * 70)

if __name__ == "__main__":
    main()
