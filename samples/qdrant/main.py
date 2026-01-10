import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.qdrant import create_qdrant_agent
from sidusai.plugins.qdrant.models import Document

def main():
    print("QDrant VECTOR DATABASE")
    print("=" * 50)

    agent = create_qdrant_agent(
        host=os.environ.get('QDRANT_HOST'),
        port=os.environ.get('QDRANT_PORT'),
    )

    print("\n1. Creating Telegram information collection:")
    print("-" * 30)

    result = agent.create_collection(
        collection_name="telegram_info",
        vector_size=10,
        distance="COSINE"
    )

    if result.get('success'):
        parameters = result.get('parameters')
        print(f"Collection '{result.get('collection_name')}' created")
        print(f"   Vector size: {parameters.get('vector_size')}")
        print(f"   Distance metric: {parameters.get('distance')}")
    else:
        print(f"Note: {result.get('message', result.get('error', 'Unknown'))}")

    print("\n2. Loading Telegram information with vector representations:")
    print("-" * 30)

    telegram_info = [
        Document(
            text="Telegram (also known as Telegram Messenger) is a cloud-based, cross-platform social media and instant messaging (IM) service.",
            metadata={
                "topic": "introduction",
                "category": "overview",
                "year": 2013,
                "importance": "high"
            }
        ),
        Document(
            text="It launched for iOS on 14 August 2013 and Android on 20 October 2013.",
            metadata={
                "topic": "launch dates",
                "category": "history",
                "year": 2013,
                "importance": "medium"
            }
        ),
        Document(
            text="It allows users to exchange messages, share media and files, and hold private and group voice or video calls as well as public livestreams.",
            metadata={
                "topic": "features",
                "category": "functionality",
                "year": 2013,
                "importance": "high"
            }
        ),
        Document(
            text="It is available for Android, iOS, Windows, macOS, Linux, and web browsers.",
            metadata={
                "topic": "platforms",
                "category": "availability",
                "year": 2013,
                "importance": "medium"
            }
        ),
        Document(
            text="Telegram offers end-to-end encryption in voice and video calls, and optionally in private chats if both participants use a mobile device.",
            metadata={
                "topic": "encryption",
                "category": "security",
                "year": 2013,
                "importance": "high"
            }
        ),
        Document(
            text="Telegram also has social networking features, allowing users to post stories, create public groups with up to 200,000 members, and share one-way updates to unlimited audiences in so-called channels.",
            metadata={
                "topic": "social features",
                "category": "functionality",
                "year": 2013,
                "importance": "medium"
            }
        ),
        Document(
            text="Telegram was founded in 2013 by Pavel and Nikolai Durov.",
            metadata={
                "topic": "founders",
                "category": "history",
                "year": 2013,
                "importance": "high"
            }
        )
    ]

    info_vectors = [
        [0.8, 0.1, 0.2, 0.3, 0.4, 0.1, 0.2, 0.1, 0.3, 0.1],
        [0.7, 0.2, 0.3, 0.4, 0.5, 0.2, 0.3, 0.2, 0.4, 0.2],
        [0.6, 0.3, 0.4, 0.5, 0.6, 0.1, 0.1, 0.1, 0.2, 0.3],
        [0.9, 0.4, 0.5, 0.6, 0.7, 0.3, 0.4, 0.3, 0.5, 0.4],
        [0.8, 0.5, 0.6, 0.7, 0.8, 0.2, 0.2, 0.2, 0.3, 0.5],
        [0.7, 0.6, 0.7, 0.8, 0.9, 0.1, 0.1, 0.1, 0.2, 0.6],
        [0.6, 0.7, 0.8, 0.9, 1.0, 0.4, 0.5, 0.4, 0.6, 0.7]
    ]

    result = agent.upload_documents(
        collection_name="telegram_info",
        documents=telegram_info,
        vectors=info_vectors
    )

    if result.get('success'):        
        stats = result.get('statistics', {})
        print(f"Loaded {stats.get('documents_count', 0)} information items")
        print(f"   Vectors: {stats.get('vectors_count', 0)}")
        print(f"   Collection: {stats.get('collection')}")

        if telegram_info and len(telegram_info) > 0:
            print(f"   Sample information:")
            print(f"   Topic: {telegram_info[0].metadata.get('topic')}")
            print(f"   Category: {telegram_info[0].metadata.get('category')}")
            print(f"   Text: {telegram_info[0].text}")
    else:
        print(f"Error: {result.get('error')}")

    print("\n3. Searching similar information:")
    print("-" * 30)

    print("a) Search for messaging service information:")

    messaging_vector = [0.85, 0.15, 0.25, 0.35, 0.45, 0.15, 0.25, 0.15, 0.35, 0.15]

    result = agent.search_similar(
        collection_name="telegram_info",
        query_vector=messaging_vector,
        limit=3
    )

    if result.get('success'):
        results = result.get('results', [])
        print(f"Found {len(results)} similar items")

        analysis = result.get('results_analysis', {})
        if analysis:
            score_range = analysis.get('score_range', {})
            print(f"   Score range: {score_range.get('min', 0):.4f} - {score_range.get('max', 0):.4f}")

        for i, res in enumerate(results, 1):
            payload = res.get('payload', {})
            print(f"   {i}. Score: {res.get('score'):.4f}")
            print(f"      Topic: {payload.get('topic')}")
            print(f"      Category: {payload.get('category')}")
            print(f"      Year: {payload.get('year')}")
            print(f"      Importance: {payload.get('importance')}")
            print(f"      Text: {payload.get('text', '')}")
    else:
        print(f"Error: {result.get('error')}")

    print("\nb) Search for security features with filters:")

    security_vector = [0.75, 0.25, 0.35, 0.45, 0.55, 0.2, 0.3, 0.2, 0.4, 0.25]

    result = agent.search_similar(
        collection_name="telegram_info",
        query_vector=security_vector,
        limit=3,
        filters={"category": "security"}
    )

    if result.get('success'):
        results = result.get('results', [])
        print(f"Found {len(results)} security items")

        for i, res in enumerate(results, 1):
            payload = res.get('payload', {})
            print(f"   {i}. {payload.get('topic')} ({payload.get('year')}) - Score: {res.get('score'):.4f}")
    else:
        print(f"Error: {result.get('error')}")

    print("\nc) Search for high importance information:")

    high_importance_vector = [0.7, 0.3, 0.4, 0.5, 0.6, 0.3, 0.4, 0.3, 0.5, 0.35]

    result = agent.search_similar(
        collection_name="telegram_info",
        query_vector=high_importance_vector,
        limit=3,
        filters={"importance": "high"}
    )

    if result.get('success'):
        results = result.get('results', [])
        print(f"Found {len(results)} high importance items")

        for i, res in enumerate(results, 1):
            payload = res.get('payload', {})
            print(f"   {i}. {payload.get('topic')} ({payload.get('year')}) - {payload.get('category')}")
    else:
        print(f"Error: {result.get('error')}")

    print("\n4. Telegram information collection details:")
    print("-" * 30)

    result = agent.get_collection_info("telegram_info")

    if result.get('success'):
        info = result.get('collection_info', {})
        analysis = result.get('collection_analysis', {})

        print(f"Collection: {info.get('name')}")
        print(f"Status: {analysis.get('health', 'Unknown')}")

        stats = analysis.get('statistics', {})
        print(f"Total items: {stats.get('total_points', 0)}")
        print(f"Vectors: {stats.get('vectors_count', 0)}")
        print(f"Segments: {stats.get('segments', 0)}")

        if info.get('config'):
            print(f"Configuration: {info.get('config')}")
    else:
        print(f"Error: {result.get('error')}")

    print("\n5. View all information in collection:")
    print("-" * 30)

    result = agent.scroll_points(
        collection_name="telegram_info",
        limit=5
    )

    if result.get('success'):
        points = result.get('points', [])
        print(f"Retrieved {len(points)} items from collection")

        for i, point in enumerate(points, 1):
            payload = point.get('payload', {})
            print(f"   {i}. ID: {point.get('id')}")
            print(f"      Topic: {payload.get('topic')}")
            print(f"      Category: {payload.get('category')}")
            print(f"      Importance: {payload.get('importance')}")
    else:
        print(f"Error: {result.get('error')}")

    print("\n6. Creating additional information collection:")
    print("-" * 30)

    result = agent.create_collection(
        collection_name="additional_info",
        vector_size=8,
        distance="COSINE"
    )

    if result.get('success'):
        print(f"Additional collection created")

        additional_items = [
            {"text": "Telegram servers are distributed worldwide with several data centers, and its headquarters are in Dubai, United Arab Emirates.", "topic": "infrastructure", "date": "2013"},
            {"text": "It was the most downloaded app worldwide in January 2021, with 1 billion downloads globally as of late August 2021.", "topic": "popularity", "date": "2021"},
            {"text": "As of 2024, registration to Telegram requires either a phone number and a smartphone or one of a limited number of non-fungible tokens (NFTs) issued in 2022.", "topic": "registration", "date": "2024"},
            {"text": "As of March 2025, Telegram has more than 1 billion monthly active users, with India as the country with the most users.", "topic": "usage stats", "date": "2025"},
            {"text": "Telegram allows users to exchange messages, share media and files, and hold private and group voice or video calls.", "topic": "core features", "date": "2013"}
        ]

        item_vectors = [
            [0.9, 0.1, 0.2, 0.1, 0.3, 0.1, 0.2, 0.1],
            [0.8, 0.2, 0.3, 0.2, 0.4, 0.2, 0.3, 0.2],
            [0.7, 0.3, 0.4, 0.3, 0.5, 0.3, 0.4, 0.3],
            [0.6, 0.4, 0.5, 0.4, 0.6, 0.4, 0.5, 0.4],
            [0.5, 0.5, 0.6, 0.5, 0.7, 0.5, 0.6, 0.5]
        ]

        result = agent.upload_points(
            collection_name="additional_info",
            vectors=item_vectors,
            payloads=additional_items
        )

        if result.get('success'):
            print(f"Loaded {result.get('points_count', 0)} additional items")

            features_vector = [0.85, 0.15, 0.25, 0.15, 0.35, 0.15, 0.25, 0.15]
            result = agent.search_similar("additional_info", features_vector, limit=2)

            if result.get('success'):
                print(f"   Similar feature items:")
                for res in result.get('results', []):
                    payload = res.get('payload', {})
                    print(f"   - {payload.get('topic')}: {payload.get('text', '')}")
        else:
            print(f"Additional items load error: {result.get('error')}")
    else:
        print(f"Note: {result.get('message', result.get('error', 'Unknown'))}")

if __name__ == "__main__":
    main()
