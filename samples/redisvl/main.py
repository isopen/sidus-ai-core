import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.redisvl import create_redisvl_agent
import random
import json

def generate_meaningful_vector(base_vector, variation=0.3):
    return [val + random.uniform(-variation, variation) for val in base_vector]

def main():
    print("RedisVL Vector Database Plugin")
    print("=" * 50)

    agent = create_redisvl_agent(os.environ.get('REDISVL_URL'))

    print("\n1. Redis connection test:")
    print("-" * 30)

    try:
        if agent.redisvl_client.test_connection():
            print("✅ Successfully connected to Redis")
        else:
            print("❌ Failed to connect to Redis")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    print("\n2. Creating vector index:")
    print("-" * 30)

    vector_schema = {
        "vector_fields": [{
            "name": "embedding",
            "dims": 384,
            "distance_metric": "COSINE"
        }]
    }

    result = agent.create_index(
        index_name="documents",
        vector_schema=vector_schema,
        prefix="doc:",
        index_type="HNSW"
    )

    if result.get('success'):
        print(f"✅ Index created: {result.get('index_name')}")
        print(f"   Vector dimensions: {result['vector_dimensions']}")
        print(f"   Distance metric: {result['distance_metric']}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n3. Storing sample documents:")
    print("-" * 30)

    biography_vector = [0.8] * 96 + [0.2] * 96 + [0.5] * 96 + [0.1] * 96
    career_vector = generate_meaningful_vector(biography_vector, 0.2)
    telegram_vector = generate_meaningful_vector(biography_vector, 0.15)
    wealth_vector = generate_meaningful_vector(biography_vector, 0.4)
    recognition_vector = generate_meaningful_vector(biography_vector, 0.3)

    sample_documents = [
        {
            "id": "durov_bio",
            "text": "Pavel Valeryevich Durov (Russian: Павел Валерьевич Дуров; born 10 October 1984) is a technology entrepreneur. He is best known as the chief executive officer (CEO) of Telegram.",
            "embedding": biography_vector,
            "metadata": {"category": "biography", "person": "Pavel Durov", "year": "1984"}
        },
        {
            "id": "durov_vk", 
            "text": "Durov was born in Russia, where he co-founded the social networking site VKontakte (VK) in 2006. He was forced out of VK in 2014 following disputes with the company's new owners and increased pressure from Russian authorities, which also led him to leave the country.",
            "embedding": career_vector,
            "metadata": {"category": "career", "person": "Pavel Durov", "company": "VKontakte", "years": "2006-2014"}
        },
        {
            "id": "durov_telegram",
            "text": "In 2013, he and his older brother, Nikolai Durov, developed Telegram, and in 2017, they moved to Dubai, United Arab Emirates, where its headquarters are now located.",
            "embedding": telegram_vector,
            "metadata": {"category": "career", "person": "Pavel Durov", "company": "Telegram", "years": "2013-present"}
        },
        {
            "id": "durov_wealth",
            "text": "Durov was listed on Forbes's billionaires list in 2023, with an estimated net worth of $11.5 billion. His fortune is largely driven by his ownership of Telegram. As of 19 July 2025, Durov was ranked the 118th richest person in the world, with an estimated net worth of $17.1 billion, according to Forbes.",
            "embedding": wealth_vector,
            "metadata": {"category": "wealth", "person": "Pavel Durov", "source": "Forbes", "net_worth": "$17.1B"}
        },
        {
            "id": "durov_recognition",
            "text": "In 2022, he was recognized by Forbes as the richest expat in the United Arab Emirates. In February 2023 Arabian Business named him the most powerful entrepreneur in Dubai. Durov publicly stands for Internet freedom and criticizes the establishment that tries to restrict it. Since 2021, he has held citizenship in Russia, Saint Kitts and Nevis, the United Arab Emirates, and France.",
            "embedding": recognition_vector,
            "metadata": {"category": "recognition", "person": "Pavel Durov", "awards": ["richest expat UAE", "most powerful entrepreneur Dubai"]}
        }
    ]

    stored_count = 0
    for doc in sample_documents:
        try:
            result = agent.store_document(
                index_name="documents",
                document_id=doc["id"],
                text=doc["text"],
                embedding=doc["embedding"],
                metadata=doc["metadata"]
            )

            if result.get('success'):
                print(f"✅ Stored: {doc['id']}")
                stored_count += 1
            else:
                print(f"❌ Failed to store {doc['id']}: {result.get('error')}")
        except Exception as e:
            print(f"❌ Error storing {doc['id']}: {e}")

    print(f"\nTotal stored: {stored_count}/{len(sample_documents)}")

    print("\n4. Getting index information:")
    print("-" * 30)

    result = agent.get_info(
        index_name="documents"
    )

    if result.get('success'):
        info = result.get('info_summary', {})
        print(f"✅ Index information:")
        print(f"   Documents: {info.get('num_docs', 0)}")
        print(f"   Indexed: {info.get('percent_indexed', '0')}%")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n5. Searching for similar documents:")
    print("-" * 30)

    if stored_count > 0:
        search_vector = generate_meaningful_vector(biography_vector, 0.1)

        result = agent.search_similar(
            index_name="documents",
            query_vector=search_vector,
            vector_field_name="embedding",
            limit=3
        )

        if result.get('success'):
            results = result.get('results', [])
            print(f"✅ Found {len(results)} similar documents")

            if results:
                for i, res in enumerate(results, 1):
                    full_id = res.get('id', '')
                    display_id = full_id.split(':')[-1] if ':' in full_id else full_id

                    metadata = res.get('metadata', {})
                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except:
                            metadata = {}

                    category = "Unknown"
                    if isinstance(metadata, dict):
                        category = metadata.get('category', 'Unknown')

                    print(f"   {i}. Score: {res.get('score', 0):.4f} - ID: {display_id}")
                    print(f"      Category: {category}")
        else:
            print(f"❌ Error: {result.get('error')}")
    else:
        print("⚠️  No documents stored, skipping search")

    print("\n6. Testing search with specific document embedding:")
    print("-" * 30)

    if stored_count > 0:
        result = agent.search_similar(
            index_name="documents",
            query_vector=biography_vector,
            vector_field_name="embedding",
            limit=2
        )

        if result.get('success'):
            results = result.get('results', [])
            print(f"✅ Found {len(results)} documents similar to durov_bio")

            if results:
                for i, res in enumerate(results, 1):
                    full_id = res.get('id', '')
                    display_id = full_id.split(':')[-1] if ':' in full_id else full_id
                    print(f"   {i}. ID: {display_id}, Score: {res.get('score', 0):.4f}")
        else:
            print(f"❌ Error: {result.get('error')}")

    print("\n7. Searching for documents about Telegram:")
    print("-" * 30)

    if stored_count > 0:
        result = agent.search_similar(
            index_name="documents",
            query_vector=telegram_vector,
            vector_field_name="embedding",
            limit=3
        )

        if result.get('success'):
            results = result.get('results', [])
            print(f"✅ Found {len(results)} documents about Telegram")

            if results:
                for i, res in enumerate(results, 1):
                    full_id = res.get('id', '')
                    display_id = full_id.split(':')[-1] if ':' in full_id else full_id

                    metadata = res.get('metadata', {})
                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except:
                            metadata = {}

                    company_info = ""
                    if isinstance(metadata, dict) and 'company' in metadata:
                        company_info = metadata['company']

                    print(f"   {i}. ID: {display_id}, Score: {res.get('score', 0):.4f}")
                    if company_info:
                        print(f"      Company: {company_info}")
        else:
            print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    main()
