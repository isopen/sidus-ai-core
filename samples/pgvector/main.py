import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
from sidusai.plugins.pgvector import create_pgvector_agent
import numpy as np

def generate_dummy_embedding(dim=384, seed=None):
    if seed is not None:
        np.random.seed(seed)
    vector = np.random.randn(dim) * 0.1
    return (vector / np.linalg.norm(vector)).tolist()

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def print_result(operation, result, show_details=False):
    success = result.get('success', False)
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"\n{status} - {operation}")

    if not success:
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return

    if show_details:
        for key, value in result.items():
            if key not in ['success', 'timestamp', 'operation']:
                print(f"   {key}: {value}")

def print_search_results(result, limit=2):
    if not result.get('success'):
        return

    print(f"\nSearch Results:")
    print(f"   Found: {result.get('found_count', 0)} documents")

    if result.get('sample_results'):
        print(f"\n   Top {min(limit, len(result['sample_results']))} matches:")
        for i, doc in enumerate(result['sample_results'][:limit], 1):
            print(f"\n   Result {i}:")
            print(f"       ID: {doc.get('id')}")
            if 'distance' in doc:
                print(f"       Distance: {doc.get('distance'):.6f}")
            if 'combined_score' in doc:
                print(f"       Combined Score: {doc.get('combined_score'):.6f}")
            print(f"       Content: {doc.get('content', '')}")
            if doc.get('metadata'):
                print(f"       Metadata: {doc.get('metadata')}")

def main():
    print_section("PGVECTOR COMPREHENSIVE TEST")

    agent = create_pgvector_agent(
        host=os.environ.get('PGVECTOR_HOST', 'localhost'),
        port=int(os.environ.get('PGVECTOR_PORT', 5432)),
        database=os.environ.get('PGVECTOR_DATABASE', 'postgres'),
        user=os.environ.get('PGVECTOR_USER', 'postgres'),
        password=os.environ.get('PGVECTOR_PASSWORD', 'your_password'),
        schema='public',
        table_prefix='ton_'
    )

    print_section("1. CONNECTION TEST")
    result = agent.test_connection()
    if result.get('success') and result.get('connected'):
        print("✅ Database Connection: ACTIVE")
        print(f"   Host: {result.get('host')}:{result.get('port')}")
        print(f"   Database: {result.get('database')}")
        print(f"   Schema: {result.get('schema')}")
        print(f"   Connection Pool: {result.get('connection_pool_size')} connections")
    else:
        print("❌ Database Connection: FAILED")
        return

    print_section("2. TABLE MANAGEMENT")

    print_result("Try to cleanup existing table", 
                 agent.delete_vectors(table_name="blockchain_documents", ids=[99999]))

    result = agent.create_table(
        table_name="blockchain_documents",
        vector_dimension=384,
        metadata_columns={
            "category": "VARCHAR(50)",
            "importance": "VARCHAR(20)",
            "tags": "TEXT[]",
            "rating": "INTEGER"
        },
        with_hnsw=True
    )

    if result.get('success'):
        print_result("Create vector table", result)
        print(f"   Table Name: {result.get('table_name')}")
        print(f"   Vector Dimension: {result.get('vector_dimension')}")
        print(f"   HNSW Index: {'ENABLED' if result.get('has_hnsw_index') else 'DISABLED'}")
        print(f"   Metadata Columns: {result.get('metadata_columns_count', 0)}")

    print_section("3. DATA INSERTION")

    documents = [
        {
            "id": 101,
            "content": "TON Teleport BTC enables trustless Bitcoin transfers between TON and Bitcoin networks using cryptographic proofs and decentralized bridge technology.",
            "embedding": generate_dummy_embedding(384, 101),
            "metadata": {
                "category": "bridge_technology",
                "importance": "critical",
                "tags": ["bitcoin", "ton", "bridge", "defi"],
                "rating": 9
            }
        },
        {
            "id": 102,
            "content": "Bitcoin is the first decentralized digital currency that operates without central authority using blockchain technology.",
            "embedding": generate_dummy_embedding(384, 102),
            "metadata": {
                "category": "cryptocurrency",
                "importance": "high",
                "tags": ["bitcoin", "crypto", "currency", "blockchain"],
                "rating": 10
            }
        },
        {
            "id": 103,
            "content": "Ethereum smart contracts enable decentralized applications and automated agreements on blockchain networks.",
            "embedding": generate_dummy_embedding(384, 103),
            "metadata": {
                "category": "smart_contracts",
                "importance": "high",
                "tags": ["ethereum", "smart-contracts", "dapps", "blockchain"],
                "rating": 8
            }
        },
        {
            "id": 104,
            "content": "Blockchain consensus mechanisms ensure network security and transaction validation through distributed protocols.",
            "embedding": generate_dummy_embedding(384, 104),
            "metadata": {
                "category": "consensus",
                "importance": "medium",
                "tags": ["blockchain", "consensus", "security", "validation"],
                "rating": 7
            }
        },
        {
            "id": 105,
            "content": "Cryptocurrency mining involves solving complex mathematical problems to validate transactions on blockchain networks.",
            "embedding": generate_dummy_embedding(384, 105),
            "metadata": {
                "category": "mining",
                "importance": "medium",
                "tags": ["cryptocurrency", "mining", "blockchain", "transactions"],
                "rating": 6
            }
        },
        {
            "id": 106,
            "content": "Decentralized finance platforms provide financial services without intermediaries using blockchain technology.",
            "embedding": generate_dummy_embedding(384, 106),
            "metadata": {
                "category": "defi",
                "importance": "high",
                "tags": ["defi", "finance", "blockchain", "decentralized"],
                "rating": 9
            }
        }
    ]

    result = agent.insert_vectors(
        table_name="blockchain_documents",
        vectors=[doc["embedding"] for doc in documents],
        metadata_list=[doc["metadata"] for doc in documents],
        ids=[doc["id"] for doc in documents],
        content_list=[doc["content"] for doc in documents]
    )

    if result.get('success'):
        print_result("Insert documents", result)
        print(f"   Inserted: {result.get('vector_count', 0)} documents")
        print(f"   Document IDs: {', '.join(str(doc['id']) for doc in documents)}")

    print_section("4. VECTOR SEARCH OPERATIONS")

    query_vector = generate_dummy_embedding(384, 500)

    result = agent.query_vectors(
        table_name="blockchain_documents",
        query_vector=query_vector,
        limit=3,
        distance_metric="cosine"
    )

    print_result("Vector Similarity Search", result)
    print_search_results(result, limit=3)

    if result.get('distances_summary'):
        dist = result['distances_summary']
        print(f"\nDistance Statistics:")
        print(f"   Min Distance: {dist.get('min', 0):.6f}")
        print(f"   Max Distance: {dist.get('max', 0):.6f}")
        print(f"   Avg Distance: {dist.get('avg', 0):.6f}")

    print_section("5. FILTERED SEARCH")

    result = agent.search_with_filter(
        table_name="blockchain_documents",
        query_vector=query_vector,
        filter_conditions={"importance": "high"},
        limit=3,
        distance_metric="cosine"
    )

    print_result("Filtered Vector Search", result)
    print_search_results(result)

    if result.get('filter_conditions'):
        print(f"\nApplied Filters:")
        for key, value in result['filter_conditions'].items():
            print(f"   {key}: {value}")

    print_section("6. HYBRID SEARCH TESTS")

    hybrid_queries = [
        {"query_text": "blockchain", "limit": 5, "text_weight": 0.5, "vector_weight": 0.5},
        {"query_text": "bitcoin transfers", "limit": 5, "text_weight": 0.4, "vector_weight": 0.6},
        {"query_text": "decentralized technology", "limit": 5, "text_weight": 0.3, "vector_weight": 0.7},
        {"query_text": "smart contracts", "limit": 5, "text_weight": 0.6, "vector_weight": 0.4}
    ]

    for query in hybrid_queries:
        result = agent.hybrid_search(
            table_name="blockchain_documents",
            query_text=query["query_text"],
            query_vector=query_vector,
            limit=query["limit"],
            text_weight=query["text_weight"],
            vector_weight=query["vector_weight"],
            distance_metric="cosine"
        )

        if result.get('success'):
            print_result(f"Hybrid Search: '{query['query_text']}'", result)
            print_search_results(result, limit=2)

            if result.get('found_count', 0) == 0:
                print(f"   Note: No results found for query '{query['query_text']}'")
        else:
            print_result(f"Hybrid Search: '{query['query_text']}'", result)

    print_section("7. DATABASE METADATA")

    result = agent.get_table_info("blockchain_documents")
    if result.get('success'):
        print_result("Table Information", result)
        print(f"   Total Rows: {result.get('row_count', 0)}")
        print(f"   Oldest Record: {result.get('oldest_record', 'N/A')}")
        print(f"   Newest Record: {result.get('newest_record', 'N/A')}")
        print(f"   Columns Count: {result.get('columns_count', 0)}")
        print(f"   Indexes Count: {result.get('indexes_count', 0)}")

    result = agent.get_vector_statistics("blockchain_documents")
    if result.get('success'):
        print_result("Vector Statistics", result)
        print(f"   Total Vectors: {result.get('total_vectors', 0)}")
        print(f"   Avg Dimensions: {result.get('avg_dimensions', 0):.2f}")
        print(f"   Norm Range: {result.get('min_norm', 0):.4f} - {result.get('max_norm', 0):.4f}")
        print(f"   Avg Norm: {result.get('avg_norm', 0):.4f}")

    result = agent.list_tables()
    if result.get('success'):
        print_result("List All Tables", result)
        print(f"   Tables Found: {result.get('total_count', 0)}")
        for table in result.get('tables', []):
            print(f"      • {table}")

    print_section("8. DATA MODIFICATION")

    result = agent.update_vectors(
        table_name="blockchain_documents",
        ids=[101],
        content_list=["TON Teleport BTC: Advanced trustless bridge for Bitcoin↔TON transfers with enhanced security features."],
        metadata_list=[{"importance": "critical", "rating": 10, "updated": True, "version": "2.0"}]
    )

    if result.get('success'):
        print_result("Update Document", result)
        print(f"   Updated: {result.get('updated_count', 0)} documents")
        print(f"   Document ID 101 updated")

    print_section("9. BULK OPERATIONS")

    bulk_docs = [
        {
            "embedding": generate_dummy_embedding(384, 201),
            "content": "DeFi applications provide financial services without intermediaries using blockchain technology.",
            "metadata": {"category": "defi", "importance": "high", "rating": 8}
        },
        {
            "embedding": generate_dummy_embedding(384, 202),
            "content": "NFTs represent unique digital assets on blockchain networks with proof of ownership.",
            "metadata": {"category": "nft", "importance": "medium", "rating": 7}
        }
    ]

    result = agent.bulk_insert(
        table_name="blockchain_documents",
        vectors=[doc["embedding"] for doc in bulk_docs],
        metadata_list=[doc["metadata"] for doc in bulk_docs],
        content_list=[doc["content"] for doc in bulk_docs],
        batch_size=1000
    )

    if result.get('success'):
        print_result("Bulk Insert", result)
        print(f"   Inserted: {result.get('total_inserted', 0)} documents")
        print(f"   Performance: {result.get('vectors_per_second', 0):.1f} vectors/sec")
        print(f"   Time: {result.get('time_seconds', 0):.3f} seconds")

    print_section("10. TABLE MODIFICATION")

    result = agent.modify_table(
        table_name="blockchain_documents",
        add_columns={
            "source_url": "VARCHAR(255)",
            "language": "VARCHAR(10) DEFAULT 'en'"
        }
    )

    if result.get('success'):
        print_result("Modify Table Structure", result)
        print(f"   Operations: {result.get('total_operations', 0)} modifications")

    print_section("11. CLEANUP OPERATIONS")

    result = agent.delete_vectors(
        table_name="blockchain_documents",
        ids=[102]
    )

    if result.get('success'):
        print_result("Delete Operation", result)
        print(f"   Deleted: {result.get('deleted_count', 0)} documents")
        print(f"   Document ID 102 deleted")

    print_section("12. FINAL VERIFICATION")

    result = agent.query_vectors(
        table_name="blockchain_documents",
        query_vector=generate_dummy_embedding(384, 999),
        limit=50,
        distance_metric="cosine",
        return_columns=["id", "content", "metadata", "created_at"]
    )

    if result.get('success'):
        print_result("Final Verification Search", result)
        print(f"   Total documents in table: {result.get('found_count', 0)}")
        if result.get('results'):
            print(f"\n   Sample documents:")
            for i, doc in enumerate(result['results'][:2], 1):
                print(f"\n   Result {i}:")
                print(f"       ID: {doc.get('id')}")
                metadata = doc.get('metadata', {})
                if metadata:
                    categories = [v for k, v in metadata.items() if 'category' in k or 'type' in k]
                    if categories:
                        print(f"       Type: {categories[0]}")
                print(f"       Created: {doc.get('created_at', 'N/A')}")

    print_section("TEST SUMMARY")

    print("OPERATIONS PERFORMED:")
    print("   ✓ Database Connection Test")
    print("   ✓ Table Creation with Metadata")
    print("   ✓ Document Insertion (Individual & Bulk)")
    print("   ✓ Vector Similarity Search")
    print("   ✓ Filtered Vector Search")
    print("   ✓ Hybrid Text+Vector Search")
    print("   ✓ Table Metadata Inspection")
    print("   ✓ Vector Statistics Analysis")
    print("   ✓ Document Updates")
    print("   ✓ Table Structure Modification")
    print("   ✓ Data Deletion")

if __name__ == "__main__":
    main()
