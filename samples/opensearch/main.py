import os
import sys
import numpy as np
from typing import List
import hashlib

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.opensearch import create_opensearch_agent

class BetterEmbeddingGenerator:
    @staticmethod
    def generate_embeddings(texts: List[str], dimension: int = 384) -> List[List[float]]:
        embeddings = []

        for text in texts:
            words = text.lower().split()
            vector = np.zeros(dimension)

            text_len = len(text)
            vector[0] = min(text_len / 1000.0, 1.0)

            num_words = len(words)
            vector[1] = min(num_words / 50.0, 1.0)

            unique_words = set(words)
            vector[2] = len(unique_words) / max(num_words, 1)

            seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
            np.random.seed(seed % 10000)

            important_features = [
                'api', 'bot', 'telegram', 'message', 'chat', 'user',
                'method', 'field', 'class', 'parameter', 'added',
                'send', 'get', 'update', 'topic', 'gift', 'checklist'
            ]

            feature_index = 3
            for feature in important_features:
                if feature in text.lower():
                    vector[feature_index] = 1.0
                feature_index += 1
                if feature_index >= dimension:
                    break

            semantic_features = [
                ('http', 0.8), ('https', 0.8), ('token', 0.7),
                ('webhook', 0.6), ('json', 0.5), ('request', 0.7),
                ('response', 0.7), ('error', 0.6), ('star', 0.6),
                ('price', 0.5), ('payment', 0.5), ('file', 0.6),
                ('upload', 0.6), ('download', 0.6), ('server', 0.5)
            ]

            for keyword, weight in semantic_features:
                if keyword in text.lower():
                    vector[feature_index] = weight
                    feature_index += 1
                    if feature_index >= dimension:
                        break

            remaining_dim = dimension - feature_index
            if remaining_dim > 0:
                random_part = np.random.normal(0, 0.1, remaining_dim)
                vector[feature_index:] = random_part

            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm

            embeddings.append(vector.tolist())

        return embeddings

    @staticmethod
    def generate_query_embedding(query: str, dimension: int = 384) -> List[float]:
        return BetterEmbeddingGenerator.generate_embeddings([query], dimension)[0]

def main():
    print("TELEGRAM BOT API DOCUMENTATION SEARCH DEMO")
    print("=" * 60)

    host = os.environ.get('OPENSEARCH_HOST', 'localhost')
    port = int(os.environ.get('OPENSEARCH_PORT', '9200'))

    agent = create_opensearch_agent(
        host=host,
        port=port,
        use_ssl=False,
        timeout=30
    )

    print(f"\n1. Connecting to OpenSearch {host}:{port}:")
    print("-" * 40)

    result = agent.list_indices()
    if result.get('success'):
        indices = result.get('indices', [])
        print(f"✅ Connected to OpenSearch")
        print(f"   Found {len(indices)} indices")
    else:
        print(f"❌ Error: {result.get('error')}")
        return

    print("\n2. Creating Telegram Bot API documentation index:")
    print("-" * 40)

    try:
        agent.delete_index(index_name="telegram-bot-api")
        print("Cleaned existing index")
    except:
        pass

    result = agent.create_index(
        index_name="telegram-bot-api",
        mappings={
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"},
                "category": {"type": "keyword"},
                "version": {"type": "keyword"},
                "date": {"type": "date"},
                "keywords": {"type": "keyword"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 384,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "faiss",
                        "parameters": {
                            "ef_construction": 256,
                            "m": 16
                        }
                    }
                }
            }
        },
        settings={
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 200,
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
    )

    if result.get('success'):
        print(f"✅ Index created: telegram-bot-api")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n3. Indexing Telegram Bot API documentation:")
    print("-" * 40)

    telegram_docs = [
        {
            "title": "Introduction to Telegram Bot API",
            "content": "The Bot API is an HTTP-based interface created for developers keen on building bots for Telegram. To learn how to create and set up a bot, please consult our Introduction to Bots and Bot FAQ.",
            "category": "Introduction",
            "version": "General",
            "date": "2024-01-01",
            "keywords": ["api", "bot", "telegram", "introduction", "basics"]
        },
        {
            "title": "Bot API 9.3 - December 31, 2025",
            "content": "Added the field has_topics_enabled to the class User. Added the method sendMessageDraft. Supported the fields message_thread_id and is_topic_message in the class Message. Added gifts support with getUserGifts and getChatGifts methods. Increased maximum price for paid media to 25000 Telegram Stars.",
            "category": "Release Notes",
            "version": "9.3",
            "date": "2025-12-31",
            "keywords": ["9.3", "topics", "gifts", "stars", "paid media"]
        },
        {
            "title": "Bot API 9.2 - August 15, 2025",
            "content": "Added checklists support with checklist_task_id field. Added gifts with publisher_chat field. Added direct messages in channels with is_direct_messages field. Added suggested posts with SuggestedPostParameters class.",
            "category": "Release Notes",
            "version": "9.2",
            "date": "2025-08-15",
            "keywords": ["9.2", "checklists", "direct messages", "suggested posts"]
        },
        {
            "title": "Bot API 9.1 - July 3, 2025",
            "content": "Added Checklist and ChecklistTask classes. Added gift transfer date fields. Increased maximum poll options to 12. Added getMyStarBalance method for checking Telegram Stars balance.",
            "category": "Release Notes",
            "version": "9.1",
            "date": "2025-07-03",
            "keywords": ["9.1", "checklist", "poll", "stars", "balance"]
        },
        {
            "title": "Authorizing Your Bot",
            "content": "Each bot is given a unique authentication token when created. Tokens look like 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11. All queries must be served over HTTPS in form: https://api.telegram.org/bot<token>/METHOD_NAME",
            "category": "Authentication",
            "version": "General",
            "date": "2024-01-01",
            "keywords": ["authentication", "token", "https", "api", "security"]
        },
        {
            "title": "Making Requests",
            "content": "Support GET and POST HTTP methods. Four ways of passing parameters: URL query string, application/x-www-form-urlencoded, application/json, multipart/form-data for file uploads. Response contains JSON with boolean 'ok' field and optional 'description'.",
            "category": "API Basics",
            "version": "General",
            "date": "2024-01-01",
            "keywords": ["requests", "http", "json", "parameters", "response"]
        },
        {
            "title": "Getting Updates",
            "content": "Two ways: getUpdates method or webhooks. Updates stored for 24 hours. Receive JSON-serialized Update objects. Webhooks allow requests while sending answer using application/json or form-data content types.",
            "category": "Updates",
            "version": "General",
            "date": "2024-01-01",
            "keywords": ["updates", "webhooks", "getupdates", "json", "real-time"]
        },
        {
            "title": "Local Bot API Server",
            "content": "Server source code available at telegram-bot-api. Local server features: download files without size limit, upload up to 2000 MB files, use local paths, any webhook URL/port, receive absolute local file paths.",
            "category": "Deployment",
            "version": "General",
            "date": "2024-01-01",
            "keywords": ["local", "server", "deployment", "webhook", "files"]
        },
        {
            "title": "Gifts System",
            "content": "Added in API 9.3. Methods: getUserGifts, getChatGifts. Unique gifts have colors, backgrounds, premium status. Gifts can be resold, have blockchain origin. Maximum price increased to 25000 Stars.",
            "category": "Features",
            "version": "9.3",
            "date": "2025-12-31",
            "keywords": ["gifts", "stars", "premium", "blockchain", "resale"]
        },
        {
            "title": "Topics in Private Chats",
            "content": "Forum topic mode for bots in private chats. sendMessageDraft for streaming partial messages. Support message_thread_id in all send methods. Manage topics with editForumTopic, deleteForumTopic methods.",
            "category": "Features",
            "version": "9.3",
            "date": "2025-12-31",
            "keywords": ["topics", "forum", "private", "thread", "messages"]
        },
        {
            "title": "Checklists Feature",
            "content": "Added in API 9.2. ChecklistTask and Checklist classes. sendChecklist and editMessageChecklist methods. Tasks can be marked done/not done. Business account integration.",
            "category": "Features",
            "version": "9.2",
            "date": "2025-08-15",
            "keywords": ["checklist", "tasks", "business", "organization"]
        },
        {
            "title": "Direct Messages in Channels",
            "content": "Supergroups for channel direct messages. DirectMessagesTopic class. Suggested posts with approval system. Paid posts cannot be deleted for 24 hours. Price management for direct messages.",
            "category": "Features",
            "version": "9.2",
            "date": "2025-08-15",
            "keywords": ["direct messages", "channels", "suggested posts", "paid"]
        },
        {
            "title": "Error Handling",
            "content": "Response includes error_code and description fields. Optional parameters field for automatic error handling. All methods case-insensitive. All queries use UTF-8 encoding.",
            "category": "API Basics",
            "version": "General",
            "date": "2024-01-01",
            "keywords": ["errors", "handling", "response", "utf8", "debugging"]
        }
    ]

    print("Generating semantic embeddings...")
    texts = [doc["content"] for doc in telegram_docs]
    embeddings = BetterEmbeddingGenerator.generate_embeddings(texts)

    for i, doc in enumerate(telegram_docs):
        doc["embedding"] = embeddings[i]

    print(f"Generated {len(embeddings)} embeddings")

    result = agent.bulk_insert(
        index_name="telegram-bot-api",
        documents=telegram_docs,
        batch_size=10,
        refresh=True
    )

    if result.get('success'):
        print(f"✅ Added {result.get('total_documents', 0)} documents")
    else:
        print(f"❌ Error: {result.get('error')}")
        return

    print("\n4. Testing semantic search on Bot API:")
    print("-" * 40)

    test_queries = [
        {
            "text": "How to authenticate bot with token?",
            "expected_categories": ["Authentication"]
        },
        {
            "text": "What's new in API version 9.3?",
            "expected_categories": ["Release Notes"]
        },
        {
            "text": "How to handle gifts and stars?",
            "expected_categories": ["Features"]
        },
        {
            "text": "How to get updates from users?",
            "expected_categories": ["Updates"]
        },
        {
            "text": "How to upload large files?",
            "expected_categories": ["Deployment"]
        }
    ]

    for test in test_queries:
        print(f"\n🔍 Query: '{test['text']}'")

        query_embedding = BetterEmbeddingGenerator.generate_query_embedding(test["text"])

        result = agent.search_knn(
            index_name="telegram-bot-api",
            vector_field="embedding",
            vector=query_embedding,
            k=3,
            method_parameters={"ef_search": 100}
        )

        if result.get('success') and result.get('results_count', 0) > 0:
            results = result.get('results', [])

            for i, res in enumerate(results, 1):
                source = res.get('_source', {})
                title = source.get('title', '')
                category = source.get('category', '')
                version = source.get('version', '')
                score = res.get('_score', 0)

                is_expected = category in test['expected_categories']
                match_mark = "✅" if is_expected else "  "

                print(f"{match_mark} {i}. {title}")
                print(f"     Category: {category}, Version: {version}, Score: {score:.4f}")

                if i == 1 and score > 0.6:
                    print(f"     🎯 Top match confidence: {'HIGH' if score > 0.7 else 'MEDIUM'}")
        else:
            print("❌ No results found")

    print("\n5. Comparing keyword vs vector search:")
    print("-" * 40)

    comparison_query = "bot authentication token and api requests"

    print(f"Query: '{comparison_query}'")

    print("\n📝 Keyword search:")
    keyword_result = agent.search_text(
        index_name="telegram-bot-api",
        query={
            "multi_match": {
                "query": comparison_query,
                "fields": ["title^2", "content", "keywords"],
                "type": "best_fields"
            }
        },
        size=3
    )

    if keyword_result.get('success'):
        results = keyword_result.get('results', [])
        for i, res in enumerate(results, 1):
            title = res.get('_source', {}).get('title', '')
            score = res.get('_score', 0)
            print(f"  {i}. {title} (score: {score:.4f})")

    print("\n🔢 Vector search:")
    vector_result = agent.search_knn(
        index_name="telegram-bot-api",
        vector_field="embedding",
        vector=BetterEmbeddingGenerator.generate_query_embedding(comparison_query),
        k=3
    )

    if vector_result.get('success'):
        results = vector_result.get('results', [])
        for i, res in enumerate(results, 1):
            title = res.get('_source', {}).get('title', '')
            score = res.get('_score', 0)
            print(f"  {i}. {title} (similarity: {score:.4f})")

    print("\n6. Filtering by API version:")
    print("-" * 40)

    print("Searching for features in API 9.3 only:")

    result = agent.search_knn(
        index_name="telegram-bot-api",
        vector_field="embedding",
        vector=BetterEmbeddingGenerator.generate_query_embedding("gifts and topics"),
        k=3,
        filter_query={
            "term": {
                "version": "9.3"
            }
        }
    )

    if result.get('success'):
        results = result.get('results', [])
        print(f"Found {len(results)} results in API 9.3:")
        for i, res in enumerate(results, 1):
            source = res.get('_source', {})
            print(f"  {i}. {source.get('title')}")

    print("\n7. Finding related features:")
    print("-" * 40)

    feature_query = "How to implement checklists and direct messages?"

    print(f"Query: '{feature_query}'")

    result = agent.search_knn(
        index_name="telegram-bot-api",
        vector_field="embedding",
        vector=BetterEmbeddingGenerator.generate_query_embedding(feature_query),
        k=4,
        filter_query={
            "bool": {
                "should": [
                    {"term": {"category": "Features"}},
                    {"term": {"category": "Release Notes"}}
                ]
            }
        }
    )

    if result.get('success'):
        results = result.get('results', [])
        print(f"Found {len(results)} feature-related results:")
        for i, res in enumerate(results, 1):
            source = res.get('_source', {})
            title = source.get('title', '')
            version = source.get('version', '')
            score = res.get('_score', 0)
            print(f"  {i}. {title} (v{version}, similarity: {score:.4f})")

    print("\n8. Index statistics:")
    print("-" * 40)

    result = agent.get_info(index_name="telegram-bot-api")
    if result.get('success'):
        summary = result.get('info_summary', {})
        print(f"📊 Total documents: {summary.get('docs_count', 0)}")
        print(f"💾 Storage size: {summary.get('store_size', 0) / 1024:.2f} KB")

        print("\n📂 Distribution by category:")
        agg_result = agent.aggregate(
            index_name="telegram-bot-api",
            aggs={
                "categories": {
                    "terms": {
                        "field": "category",
                        "size": 10
                    }
                }
            },
            size=0
        )

        if agg_result.get('success'):
            aggs = agg_result.get('aggregations', {})
            categories = aggs.get('categories', {}).get('buckets', [])
            for bucket in categories:
                category = bucket.get('key', '')
                count = bucket.get('doc_count', 0)
                print(f"  • {category}: {count} documents")

    print("\n9. Performance benchmark:")
    print("-" * 40)

    queries = [
        "bot setup and authentication",
        "api version 9.3 features",
        "file upload limits",
        "error handling best practices"
    ]

    print("Running search performance test...")
    for i, query in enumerate(queries, 1):
        vector = BetterEmbeddingGenerator.generate_query_embedding(query)
        result = agent.search_knn(
            index_name="telegram-bot-api",
            vector_field="embedding",
            vector=vector,
            k=5
        )

        if result.get('success'):
            took_ms = result.get('took_ms', 0)
            count = result.get('results_count', 0)
            if count > 0:
                top_score = result.get('results', [{}])[0].get('_score', 0)
                print(f"  Query {i}: {took_ms}ms, {count} results, top score: {top_score:.4f}")

    agent.plugin.opensearch_client.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted")
    except Exception as e:
        print(f"\nError: {e}")
