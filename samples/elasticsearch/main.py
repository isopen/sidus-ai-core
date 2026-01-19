import os
import sys
import numpy as np
from typing import List
import hashlib

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.elasticsearch import create_elasticsearch_agent

class ElasticEmbeddingGenerator:
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

            cocoon_keywords = [
                'cocoon', 'tee', 'gpu', 'ton', 'blockchain', 'proxy',
                'worker', 'client', 'attestation', 'confidential',
                'inference', 'ai', 'model', 'decentralized', 'payment',
                'security', 'verification', 'contract', 'hardware',
                'privacy', 'compute', 'image', 'hash', 'network',
                'architecture', 'documentation', 'component', 'system'
            ]

            feature_index = 3
            for keyword in cocoon_keywords:
                if keyword in text.lower():
                    vector[feature_index] = 1.0
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
        return ElasticEmbeddingGenerator.generate_embeddings([query], dimension)[0]

def main():
    print("=" * 70)
    print("ELASTICSEARCH VECTOR SEARCH DEMO - COCOON Architecture Documentation")
    print("=" * 70)

    try:
        print("\n1. 📡 Creating Elasticsearch Agent...")
        agent = create_elasticsearch_agent(
            host=os.environ.get('ELASTIC_HOST', 'localhost'),
            port=os.environ.get('ELASTIC_PORT', 9200),
            timeout=30
        )
        print("   ✅ Agent created successfully")

        print("\n2. 🔍 Checking cluster status...")
        health = agent.cluster_health()
        if health.get('success'):
            status = health.get('status')
            nodes = health.get('number_of_nodes', 0)
            print(f"   🟢 Cluster status: {status}")
            print(f"   🖥️  Nodes: {nodes}")
            print(f"   📦 Active shards: {health.get('active_shards', 0)}")

        print("\n3. 🗑️  Cleaning up old index...")
        try:
            delete_result = agent.delete_index(index_name="cocoon-docs")
            if delete_result.get('success'):
                print("   ✅ Removed old index")
            elif "index_not_found_exception" in str(delete_result.get('error', '')):
                print("   ℹ️  No existing index found")
            else:
                print(f"   ⚠️  Could not delete: {delete_result.get('error')}")
        except Exception as e:
            print(f"   ⚠️  Cleanup warning: {e}")

        print("\n4. 🏗️  Creating new index with dense vector field...")

        index_config = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "category": {"type": "keyword"},
                    "version": {"type": "keyword"},
                    "date": {"type": "date"},
                    "keywords": {"type": "keyword"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            },
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "refresh_interval": "1s"
                }
            }
        }

        result = agent.create_index(
            index_name="cocoon-docs",
            mappings=index_config["mappings"],
            settings=index_config["settings"]
        )

        if result.get('success'):
            print("   ✅ Index 'cocoon-docs' created")
            print(f"   📏 Vector dimension: 384")
            print(f"   🔍 Similarity metric: cosine")
        else:
            print(f"   ❌ Failed to create index: {result.get('error')}")
            return

        print("\n5. 📝 Preparing COCOON Architecture documentation...")

        cocoon_docs = [
            {
                "title": "COCOON Architecture Overview",
                "content": "COCOON is a decentralized AI inference platform on TON that securely connects GPU owners who provide compute with privacy-conscious applications that need to run AI models. For GPU Providers, it defines how suitable hardware can become part of a confidential, attested compute layer – for Developers, it is the backend that executes model requests and settles payments on-chain.",
                "category": "Introduction",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["cocoon", "architecture", "overview", "decentralized", "platform"]
            },
            {
                "title": "COCOON Key Goals",
                "content": "Anyone with a GPU server can rent it out and earn money. Requests and responses remain private, known only to the client. Clients can verify that responses come from the requested model. Payment happens through TON blockchain.",
                "category": "Introduction",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["goals", "gpu", "privacy", "payment", "verification"]
            },
            {
                "title": "Worker Component",
                "content": "Executes AI inference requests inside TEE-protected VMs. Runs AI models (e.g., LLMs via vllm) inside confidential virtual machines. Protected by TEE (currently Intel TDX). Ensures all requests are kept private and the correct model is used. Receives payment from proxies for completed work.",
                "category": "Components",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["worker", "tee", "vm", "inference", "confidential"]
            },
            {
                "title": "Proxy Component",
                "content": "Routes requests from clients to workers. Protected by TEE (currently Intel TDX). Selects appropriate workers based on model type, load, and reputation. Accepts payment from clients. Pays workers for completed requests. Takes commission on each transaction.",
                "category": "Components",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["proxy", "routing", "payment", "commission", "load-balancing"]
            },
            {
                "title": "Client Component",
                "content": "Library for sending inference requests. Sends requests to proxies. Validates proxy TEE attestations to ensure requests are sent only to trusted proxies. Pays proxies for completed requests. Designed to run on servers (backend infrastructure).",
                "category": "Components",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["client", "library", "attestation", "validation", "requests"]
            },
            {
                "title": "Smart Contracts",
                "content": "Root Contract (On-Chain Registry): Stores allowed image and model hashes, addresses of proxies, and other network-wide settings. Payment Contracts: Stores payment information for clients and proxies. Similar to payment channels.",
                "category": "Blockchain",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["smart contracts", "root contract", "payment", "registry", "on-chain"]
            },
            {
                "title": "Request Workflow",
                "content": "Client establishes RA-TLS connection with proxy, verifying proxy's TEE attestation against root contract. Proxy establishes RA-TLS connection with selected worker, verifying worker's TEE attestation. Client sends inference request (with prepayment) → Proxy forwards to worker → Worker processes in TEE. Worker returns response → Proxy pays worker via smart contract → Proxy returns response to client.",
                "category": "Workflow",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["workflow", "ra-tls", "attestation", "payment", "process"]
            },
            {
                "title": "Security Properties",
                "content": "COCOON enforces security through static measurements, on-chain registries and runtime hardware verification. Image Verification: Each TEE VM's identity is defined by its image hash. Root Contract: The root smart contract on TON blockchain serves as the trusted registry. Attestation and Communication: RA-TLS ensures we communicate with correct VMs. GPU Verification: GPU is verified by the VM itself during boot.",
                "category": "Security",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["security", "attestation", "verification", "tee", "gpu"]
            },
            {
                "title": "Image Verification",
                "content": "Each TEE VM's identity is defined by its image hash, which includes: Base image - The root filesystem and all binaries (measured by TEE). Static config - Configuration that affects security/correctness (measured by TEE). Runtime config (not measured) affects behavior but not safety or correctness.",
                "category": "Security",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["image", "verification", "hash", "tee", "measurement"]
            },
            {
                "title": "Root Contract Details",
                "content": "The root smart contract on TON blockchain serves as the trusted registry containing: List of proxy IPs - Known proxy endpoints. Allowed image hashes - Valid proxy and worker TEE measurements. Supported model hashes - Verified AI model hashes. Config parameters - Network-wide settings (pricing, limits, etc.). Smart contract code - Code for worker and proxy contracts.",
                "category": "Security",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["root contract", "registry", "blockchain", "ton", "smart contract"]
            },
            {
                "title": "Network Topology",
                "content": "Multiple Clients → Few Proxies (e.g., 10-100) → Many Workers (e.g., 1000+). Workers connect to proxies. Proxies track worker reputation and load-balance requests.",
                "category": "Architecture",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["network", "topology", "clients", "proxies", "workers"]
            },
            {
                "title": "Performance and Availability",
                "content": "TEE does not guarantee performance. Slow or hanging workers are handled via reputation system. Proxies track worker response times and success rates. Clients can choose proxies and verify service quality. Reputation scores stored on-chain for transparency.",
                "category": "Operations",
                "version": "v1.0",
                "date": "2024-01-01",
                "keywords": ["performance", "availability", "reputation", "monitoring", "quality"]
            }
        ]

        print(f"   📄 Prepared {len(cocoon_docs)} documents")

        print("   🧠 Generating semantic embeddings...")
        texts = [doc["content"] for doc in cocoon_docs]
        embeddings = ElasticEmbeddingGenerator.generate_embeddings(texts)

        for i, doc in enumerate(cocoon_docs):
            doc["embedding"] = embeddings[i]

        print(f"   ✅ Generated {len(embeddings)} vectors (384 dimensions)")

        print("\n6. 📤 Indexing documents...")
        result = agent.bulk_insert(
            index_name="cocoon-docs",
            documents=cocoon_docs,
            batch_size=5,
            refresh=True
        )

        if result.get('success'):
            success_count = result.get('success_count', 0)
            print(f"   ✅ Indexed {success_count} documents successfully")

            if result.get('failed_count', 0) > 0:
                print(f"   ⚠️  Failed to index {result.get('failed_count')} documents")
        else:
            print(f"   ❌ Bulk insert failed: {result.get('error')}")
            return

        print("\n7. 📊 Checking index statistics...")
        info = agent.get_info(index_name="cocoon-docs")
        if info.get('success'):
            summary = info.get('info_summary', {})
            print(f"   📈 Documents: {summary.get('docs_count', 0)}")
            print(f"   💾 Storage: {summary.get('store_size', 0) / 1024:.2f} KB")

        print("\n" + "=" * 70)
        print("🧪 TESTING SEARCH CAPABILITIES")
        print("=" * 70)

        print("\n🔍 Test 1: Traditional Text Search")
        print("-" * 40)

        text_query = {
            "multi_match": {
                "query": "GPU payment security",
                "fields": ["title^2", "content", "keywords"],
                "type": "best_fields"
            }
        }

        text_result = agent.search_text(
            index_name="cocoon-docs",
            query=text_query,
            size=3
        )

        if text_result.get('success') and text_result.get('results_count', 0) > 0:
            results = text_result.get('results', [])
            print(f"📝 Found {len(results)} results:")
            for i, res in enumerate(results, 1):
                source = res.get('_source', {})
                title = source.get('title', '')
                category = source.get('category', '')
                score = res.get('_score', 0)
                print(f"   {i}. {title}")
                print(f"      Category: {category}, Score: {score:.4f}")

        print("\n🔢 Test 2: Vector Similarity Search")
        print("-" * 40)

        query_text = "How does COCOON ensure privacy and security?"
        print(f"   Query: '{query_text}'")

        query_vector = ElasticEmbeddingGenerator.generate_query_embedding(query_text)

        vector_result = agent.search_dense_vector(
            index_name="cocoon-docs",
            vector_field="embedding",
            vector=query_vector,
            k=3,
            num_candidates=50
        )

        if vector_result.get('success') and vector_result.get('results_count', 0) > 0:
            results = vector_result.get('results', [])
            print(f"   🧮 Found {len(results)} similar documents:")
            for i, res in enumerate(results, 1):
                source = res.get('_source', {})
                title = source.get('title', '')
                similarity = res.get('_score', 0)
                print(f"      {i}. {title}")
                print(f"         Similarity: {similarity:.4f}")

        print("\n⚡ Test 3: Hybrid Search (Text + Vector)")
        print("-" * 40)

        hybrid_query = "TEE attestation and verification"
        print(f"   Query: '{hybrid_query}'")

        hybrid_vector = ElasticEmbeddingGenerator.generate_query_embedding(hybrid_query)

        correct_text_query = {
            "multi_match": {
                "query": hybrid_query,
                "fields": ["title", "content", "keywords"]
            }
        }

        hybrid_result = agent.search_hybrid_vector(
            index_name="cocoon-docs",
            vector_field="embedding",
            vector=hybrid_vector,
            text_query=correct_text_query,
            k=2,
            vector_weight=0.6,
            text_weight=0.4
        )

        if hybrid_result.get('success') and hybrid_result.get('results_count', 0) > 0:
            results = hybrid_result.get('results', [])
            print(f"   🔀 Found {len(results)} hybrid results:")
            for i, res in enumerate(results, 1):
                source = res.get('_source', {})
                title = source.get('title', '')
                version = source.get('version', '')
                score = res.get('_score', 0)
                print(f"      {i}. {title} (v{version})")
                print(f"         Hybrid score: {score:.4f}")
        else:
            print(f"   ❌ Hybrid search failed: {hybrid_result.get('error')}")

        print("\n🎯 Test 4: Filtered Vector Search")
        print("-" * 40)

        print("   Searching for 'security' in Security category only")

        filter_vector = ElasticEmbeddingGenerator.generate_query_embedding("security mechanisms")

        filtered_result = agent.search_dense_vector(
            index_name="cocoon-docs",
            vector_field="embedding",
            vector=filter_vector,
            k=2,
            filter_query={
                "term": {
                    "category": "Security"
                }
            }
        )

        if filtered_result.get('success') and filtered_result.get('results_count', 0) > 0:
            results = filtered_result.get('results', [])
            print(f"   🎯 Found {len(results)} results in Security category:")
            for i, res in enumerate(results, 1):
                source = res.get('_source', {})
                print(f"      {i}. {source.get('title')}")

        print("\n📊 Test 5: Aggregations")
        print("-" * 40)

        agg_result = agent.aggregate(
            index_name="cocoon-docs",
            aggs={
                "categories": {
                    "terms": {
                        "field": "category",
                        "size": 5
                    }
                },
                "versions": {
                    "terms": {
                        "field": "version",
                        "size": 5
                    }
                }
            },
            size=0
        )

        if agg_result.get('success'):
            aggs = agg_result.get('aggregations', {})

            categories = aggs.get('categories', {}).get('buckets', [])
            print("   📂 Categories distribution:")
            for bucket in categories:
                print(f"      • {bucket.get('key')}: {bucket.get('doc_count')} docs")

            versions = aggs.get('versions', {}).get('buckets', [])
            print("\n   🏷️  Versions distribution:")
            for bucket in versions:
                print(f"      • {bucket.get('key')}: {bucket.get('doc_count')} docs")

        print("\n⚡ Test 6: Performance Benchmark")
        print("-" * 40)

        test_queries = [
            "GPU compute",
            "blockchain payment",
            "TEE security",
            "network topology"
        ]

        print("   Running performance tests...")
        for i, query in enumerate(test_queries, 1):
            vector = ElasticEmbeddingGenerator.generate_query_embedding(query)

            result = agent.search_dense_vector(
                index_name="cocoon-docs",
                vector_field="embedding",
                vector=vector,
                k=3,
                num_candidates=30
            )

            if result.get('success'):
                took_ms = result.get('took_ms', 0)
                count = result.get('results_count', 0)
                if count > 0:
                    top_score = result.get('results', [{}])[0].get('_score', 0)
                    print(f"      Query {i}: {took_ms}ms, {count} results, score: {top_score:.4f}")

        print("\n" + "=" * 70)
        print("📈 FINAL STATISTICS")
        print("=" * 70)

        final_info = agent.get_info(index_name="cocoon-docs")
        if final_info.get('success'):
            final_summary = final_info.get('info_summary', {})
            print(f"\n📊 Index: cocoon-docs")
            print(f"   📄 Documents: {final_summary.get('docs_count', 0)}")
            print(f"   💾 Size: {final_summary.get('store_size', 0) / 1024:.2f} KB")
            print(f"   🔧 Segments: {final_summary.get('segments_count', 0)}")

        cluster_info = agent.cluster_health()
        if cluster_info.get('success'):
            print(f"\n🏢 Cluster: {cluster_info.get('cluster_name')}")
            print(f"   🟢 Status: {cluster_info.get('status')}")
            print(f"   🖥️  Nodes: {cluster_info.get('number_of_nodes', 0)}")

        agent.plugin.elasticsearch_client.close()

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   Make sure SIDUS_AI_CORE_PATH is set correctly")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
