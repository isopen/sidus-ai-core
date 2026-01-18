import os
import sys
import numpy as np
from typing import List
import hashlib
import time

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.milvus import create_milvus_agent

class MTProtoEmbeddingGenerator:
    @staticmethod
    def generate_embeddings(texts: List[str], dimension: int = 384) -> List[List[float]]:
        embeddings = []
        for text in texts:
            words = text.lower().split()
            vector = np.zeros(dimension)

            vector[0] = min(len(text) / 5000.0, 1.0)
            vector[1] = min(len(words) / 100.0, 1.0)
            vector[2] = len(set(words)) / max(len(words), 1)

            seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
            np.random.seed(seed % 10000)

            protocol_features = ['mtproto', 'protocol', 'encryption', 'telegram', 'client', 'server', 'auth', 'key', 'message', 'session', 'rpc', 'security', 'crypto', 'layer', 'transport', 'api', 'cloud', 'chat', 'secret', 'mobile', 'end-to-end', 'tls', 'schema', 'binary', 'serialization', 'http', 'https', 'websocket', 'tcp', 'udp']

            idx = 3
            text_lower = text.lower()
            for feature in protocol_features:
                if feature in text_lower:
                    vector[idx] = 1.0
                idx += 1
                if idx >= dimension:
                    break

            if idx < dimension:
                vector[idx:] = np.random.normal(0, 0.05, dimension - idx)

            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm

            embeddings.append(vector.tolist())

        return embeddings

    @staticmethod
    def generate_query_embedding(query: str, dimension: int = 384) -> List[float]:
        return MTProtoEmbeddingGenerator.generate_embeddings([query], dimension)[0]

def extract_entity_data(res):
    if not isinstance(res, dict):
        return {}

    entity_wrapper = res.get('entity', {})

    if not entity_wrapper or not isinstance(entity_wrapper, dict):
        return {}

    entity = entity_wrapper.get('entity', {})

    if not entity:
        return {}

    return {
        'title': entity.get('title', 'No title'),
        'category': entity.get('category', 'No category'),
        'topic': entity.get('topic', 'No topic'),
        'complexity': entity.get('complexity', 'Unknown')
    }

def main():
    print("MTProto Protocol Documentation Search Demo with Milvus Server")
    print("=" * 70)

    agent = create_milvus_agent(uri="http://localhost:19530")

    print(f"\n1. Connecting to Milvus server...")
    print("-" * 45)

    result = agent.list_collections()

    if result.get('success'):
        collections = result.get('collections', [])
        print(f"✅ Connected to Milvus server")
        print(f"   Found collections: {len(collections)}")
    else:
        print(f"❌ Error: {result.get('error')}")
        return

    print("\n2. Creating MTProto documentation collection:")
    print("-" * 45)

    try:
        agent.delete_collection(collection_name="mtproto_docs")
        print("Cleaned existing collection")
        time.sleep(2)
    except:
        pass

    result = agent.create_collection(
        collection_name="mtproto_docs",
        dimension=384,
        metric_type="COSINE"
    )

    if result.get('success'):
        print(f"✅ Collection created: mtproto_docs")
    else:
        print(f"❌ Error: {result.get('error')}")
        return

    time.sleep(1)

    print("\n3. Indexing MTProto documentation:")
    print("-" * 45)

    mtproto_docs = [
        {
            "id": 1,
            "title": "MTProto Mobile Protocol Overview",
            "content": "The protocol is designed for access to a server API from applications running on mobile devices. It must be emphasized that a web browser is not such an application. The protocol is subdivided into three virtually independent components.",
            "category": "Overview",
            "topic": "Introduction",
            "complexity": "Basic",
            "date": "2024-01-01"
        },
        {
            "id": 2,
            "title": "High-Level Component (RPC Query Language/API)",
            "content": "From the standpoint of the high-level component, the client and the server exchange messages inside a session. The session is attached to the client device rather than a specific WebSocket/http/https/tcp connection.",
            "category": "Architecture",
            "topic": "Components",
            "complexity": "Intermediate",
            "date": "2024-01-01"
        },
        {
            "id": 3,
            "title": "Authorization and Encryption",
            "content": "Prior to a message being transmitted over a network, it is encrypted with AES-256. A 64-bit key identifier and a 128-bit message key are added. The message key defines an actual 256-bit key which encrypts the message using AES-256.",
            "category": "Security",
            "topic": "Encryption",
            "complexity": "Advanced",
            "date": "2024-01-01"
        },
        {
            "id": 4,
            "title": "MTProto 2.0 Server-Client Encryption",
            "content": "As of version 4.6, major Telegram clients are using MTProto 2.0. MTProto v1.0 is deprecated and is currently being phased out. This protocol is used for cloud chats with server-client encryption.",
            "category": "Security",
            "topic": "Versions",
            "complexity": "Intermediate",
            "date": "2024-01-01"
        },
        {
            "id": 5,
            "title": "Perfect Forward Secrecy in MTProto",
            "content": "To prevent attackers from decrypting messages post factum, MTProto supports Perfect Forward Secrecy in both cloud chats and secret chats. This prevents decryption even if authorization keys are compromised later.",
            "category": "Security",
            "topic": "PFS",
            "complexity": "Advanced",
            "date": "2024-01-01"
        },
        {
            "id": 6,
            "title": "Time Synchronization in MTProto",
            "content": "If client time diverges from server time, the server may ignore client messages. The server sends a special message containing correct time and 128-bit salt for synchronization.",
            "category": "Protocol",
            "topic": "Synchronization",
            "complexity": "Intermediate",
            "date": "2024-01-01"
        },
        {
            "id": 7,
            "title": "Message Types in MTProto",
            "content": "There are several types of messages: RPC calls (client to server), RPC responses (server to client), message acknowledgments, status queries, and multipart containers that can hold several messages.",
            "category": "Protocol",
            "topic": "Messages",
            "complexity": "Basic",
            "date": "2024-01-01"
        },
        {
            "id": 8,
            "title": "Transport Layer Components",
            "content": "Defines methods for client and server to transmit messages over existing network protocols such as HTTP, HTTPS, WS, WSS, TCP, UDP. Multiple connections can be open simultaneously.",
            "category": "Architecture",
            "topic": "Transport",
            "complexity": "Intermediate",
            "date": "2024-01-01"
        },
        {
            "id": 9,
            "title": "Secret Chats and End-to-End Encryption",
            "content": "MTProto also supports end-to-end encrypted secret chats separate from cloud chats. These use different encryption schemas and provide complete privacy between communicating parties.",
            "category": "Security",
            "topic": "E2EE",
            "complexity": "Advanced",
            "date": "2024-01-01"
        },
        {
            "id": 10,
            "title": "Binary Data Serialization in MTProto",
            "content": "All messages use binary data serialization with little endian format. Large numbers for RSA and DH use big endian as per OpenSSL. Messages have 64-bit IDs, 32-bit sequence numbers.",
            "category": "Protocol",
            "topic": "Serialization",
            "complexity": "Advanced",
            "date": "2024-01-01"
        }
    ]

    print("Generating vector embeddings...")
    texts = [doc["content"] for doc in mtproto_docs]
    embeddings = MTProtoEmbeddingGenerator.generate_embeddings(texts)

    for i, doc in enumerate(mtproto_docs):
        doc["vector"] = embeddings[i]

    print(f"Generated {len(embeddings)} embeddings")

    result = agent.batch_insert(
        collection_name="mtproto_docs",
        data=mtproto_docs
    )

    if result.get('success'):
        print(f"✅ Added {result.get('insert_count', 0)} documents")
        print(f"First IDs: {result.get('ids', [])[:3]}")
    else:
        print(f"❌ Error: {result.get('error')}")
        return

    time.sleep(2)

    print("\n4. Verifying data insertion:")
    print("-" * 45)

    result = agent.query(
        collection_name="mtproto_docs",
        filter='id >= 1',
        output_fields=["title", "category", "complexity"],
        limit=3
    )

    if result.get('success'):
        results = result.get('results', [])
        print(f"✅ Data verification: Found {len(results)} documents")
        for res in results:
            print(f"  • {res.get('title')} ({res.get('category')})")
    else:
        print(f"❌ Verification failed: {result.get('error')}")

    print("\n5. Testing vector search with simple query:")
    print("-" * 45)

    simple_query = "telegram encryption"
    print(f"🔍 Simple query: '{simple_query}'")

    query_embedding = MTProtoEmbeddingGenerator.generate_query_embedding(simple_query)

    result = agent.search_similar(
        collection_name="mtproto_docs",
        data=[query_embedding],
        limit=5,
        output_fields=["title", "category", "complexity"]
    )

    if result.get('success'):
        results = result.get('results', [])
        print(f"✅ Vector search results: {len(results)}")

        for i, res in enumerate(results, 1):
            entity_data = extract_entity_data(res)
            distance = res.get('distance', 0)
            similarity = 1.0 - distance if distance else 0

            print(f"   {i}. {entity_data['title']}")
            print(f"      Category: {entity_data['category']}")
            print(f"      Similarity: {similarity:.4f}")
    else:
        print(f"❌ Vector search failed: {result.get('error')}")

    print("\n6. Testing hybrid search with metadata filter:")
    print("-" * 45)

    result = agent.search_similar(
        collection_name="mtproto_docs",
        data=[MTProtoEmbeddingGenerator.generate_query_embedding("security")],
        limit=3,
        output_fields=["title", "category", "complexity"],
        filter='category == "Security"'
    )

    if result.get('success'):
        results = result.get('results', [])
        print(f"✅ Hybrid search results: {len(results)}")

        for i, res in enumerate(results, 1):
            entity_data = extract_entity_data(res)
            distance = res.get('distance', 0)
            similarity = 1.0 - distance if distance else 0

            print(f"   {i}. {entity_data['title']}")
            print(f"      Complexity: {entity_data['complexity']}")
            print(f"      Similarity: {similarity:.4f}")
    else:
        print(f"❌ Hybrid search failed: {result.get('error')}")

    print("\n7. Testing metadata-only queries:")
    print("-" * 45)

    complexities = ["Basic", "Intermediate", "Advanced"]

    for complexity in complexities:
        result = agent.query(
            collection_name="mtproto_docs",
            filter=f'complexity == "{complexity}"',
            output_fields=["title", "topic"],
            limit=2
        )

        if result.get('success'):
            results = result.get('results', [])
            print(f"\n📚 {complexity} level ({len(results)}):")
            for res in results:
                print(f"  • {res.get('title')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted")
    except Exception as e:
        print(f"\nError: {e}")
