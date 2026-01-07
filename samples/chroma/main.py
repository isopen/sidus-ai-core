import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
from sidusai.plugins.chroma import create_chroma_agent

def main():
    print("=" * 50)
    print("ChromaDB")
    print("=" * 50)

    agent = create_chroma_agent(
        persist_directory="./ton_teleport_db",
        embedding_model="all-MiniLM-L6-v2",
        host=os.environ.get('CHROMA_HOST'),
        port=os.environ.get('CHROMA_PORT'),
    )

    print("\n🔹 1. CREATE COLLECTION")
    print("-" * 50)

    result = agent.create_collection(
        collection_name="ton_teleport_btc",
        metadata={
            "category": "blockchain_bridges",
            "blockchain": "TON",
            "asset": "Bitcoin",
            "status": "testnet",
            "type": "trustless_bridge",
            "language": "english"
        }
    )

    if result.get("success"):
        print(f"✅ Collection created: {result.get('collection_name')}")
        print(f"   Metadata: {result.get('metadata')}")

    print("\n🔹 2. ADD TEXT DOCUMENTS")
    print("-" * 50)

    ton_teleport_documents = [
        {
            "id": "ton_teleport_intro",
            "document": "TON (The Open Network) was envisioned as a 'blockchain of blockchains,' aiming to integrate key Web3 services within a unified ecosystem. TON Teleport BTC is a significant step toward this goal — a trustless, decentralized bridge that brings Bitcoin directly into TON. TON Teleport BTC combines Bitcoin's renowned security with TON's speed and scalability. It's important to note that TON Teleport BTC is currently operating only in the Testnet phase. Do not send real tokens!",
            "metadata": {
                "section": "introduction",
                "topic": "overview",
                "phase": "testnet",
                "importance": "high",
                "word_count": 95
            }
        },
        {
            "id": "ton_teleport_security",
            "document": "TON Teleport BTC enables users to securely transfer BTC between the Bitcoin and TON networks without relying on central intermediaries. Inspired by Satoshi Nakamoto's ideal of a system based on 'cryptographic proof instead of trust,' TON Teleport BTC removes third-party control, ensuring each BTC on TON is fully backed by actual BTC on the Bitcoin network.",
            "metadata": {
                "section": "technical",
                "topic": "security_model",
                "key_feature": "trustless",
                "backing": "fully_backed",
                "word_count": 67
            }
        },
        {
            "id": "ton_teleport_defi",
            "document": "By integrating Bitcoin with TON's DeFi ecosystem, TON Teleport BTC transforms BTC from a store of value into a versatile financial tool. Users can utilize BTC within dApps, lending platforms, and decentralized exchanges, while the infrastructure sets the stage for broader cross-chain integrations.",
            "metadata": {
                "section": "use_cases",
                "topic": "defi_integration",
                "ecosystem": "TON DeFi",
                "transformation": "store_to_tool",
                "word_count": 53
            }
        },
        {
            "id": "ton_teleport_vision",
            "document": "TON Teleport BTC aims to make TON a central hub for blockchain assets, connecting Bitcoin to TON in a secure, decentralized way. This trustless bridge upholds TON's mission of censorship resistance and asset freedom, opening doors for seamless, user-controlled asset management across Web3.",
            "metadata": {
                "section": "vision",
                "topic": "ecosystem_growth",
                "goal": "blockchain_hub",
                "principles": "censorship_resistance",
                "word_count": 55
            }
        },
        {
            "id": "bridge_comparison",
            "document": "Unlike centralized bridges that require trust in custodians, TON Teleport BTC uses cryptographic proofs to verify asset backing. Similar to other decentralized bridges like Thorchain, it enables cross-chain swaps without intermediaries. However, TON Teleport specifically focuses on Bitcoin integration with TON's high-throughput blockchain.",
            "metadata": {
                "section": "comparative",
                "topic": "bridge_technology",
                "type": "decentralized",
                "comparison": "vs_centralized",
                "word_count": 56
            }
        },
        {
            "id": "testnet_warning",
            "document": "Warning: TON Teleport BTC is currently in Testnet phase. This means all transactions are using test tokens with no real value. Users should not send actual Bitcoin to testnet addresses. The mainnet launch will be announced officially with proper security audits and testing completion.",
            "metadata": {
                "section": "warning",
                "topic": "testnet_phase",
                "severity": "high",
                "action": "do_not_send_real_btc",
                "word_count": 54
            }
        }
    ]

    result = agent.add_documents(
        collection_name="ton_teleport_btc",
        documents=[doc["document"] for doc in ton_teleport_documents],
        ids=[doc["id"] for doc in ton_teleport_documents],
        metadatas=[doc["metadata"] for doc in ton_teleport_documents]
    )

    if result.get("success"):
        count = result.get("count", 0)
        data_type = result.get("data_type", "documents")
        print(f"✅ Added {count} {data_type} to collection")
        for doc in ton_teleport_documents:
            print(f"   • {doc['id']}: {doc['metadata']['topic']}")

    print("\n🔹 3. SEMANTIC SEARCH EXAMPLES")
    print("-" * 50)

    search_queries = [
        "secure Bitcoin transfer between blockchains",
        "TON DeFi ecosystem integration with Bitcoin",
        "trustless bridge technology without intermediaries",
        "testnet phase warnings and limitations"
    ]

    for query in search_queries:
        print(f"\n🔍 Searching for: '{query}'")
        result = agent.query_collection(
            collection_name="ton_teleport_btc",
            query_texts=[query],
            n_results=2
        )

        if result.get("success"):
            total_results = result.get('total_results', 0)
            print(f"   Found {total_results} relevant documents")

            if result.get("sample_documents"):
                for i, sample in enumerate(result["sample_documents"], 1):
                    doc_preview = sample.get('document_preview', 'No preview available')
                    query_idx = sample.get('query_index', 0)
                    result_idx = sample.get('result_index', 0)
                    print(f"   Result {i} (Query {query_idx}, Result {result_idx}):")
                    print(f"      {doc_preview}")

    print("\n🔹 4. METADATA FILTERING")
    print("-" * 50)

    filter_cases = [
        {
            "name": "High importance documents",
            "where": {"importance": "high"},
            "limit": 5
        },
        {
            "name": "Technical documentation about security",
            "where": {"section": "technical", "topic": "security_model"},
            "limit": 3
        },
        {
            "name": "Testnet-related content",
            "where": {"phase": "testnet"},
            "limit": 5
        }
    ]

    for case in filter_cases:
        print(f"\n📊 Filter: {case['name']}")
        result = agent.search_documents(
            collection_name="ton_teleport_btc",
            where=case["where"],
            limit=case["limit"]
        )

        if result.get("success"):
            found_count = result.get("found_count", 0)
            print(f"   Documents matching filter: {found_count}")

            if result.get("sample_documents"):
                for sample in result["sample_documents"]:
                    doc_id = sample.get('id', 'Unknown ID')
                    doc_preview = sample.get('document_preview', 'No preview')
                    print(f"   • Document ID: {doc_id}")
                    print(f"     Preview: {doc_preview}")

    print("\n🔹 5. COLLECTION STATISTICS")
    print("-" * 50)

    result = agent.get_collection_info("ton_teleport_btc")
    if result.get("success"):
        collection_name = result.get("collection_name")
        document_count = result.get("document_count", 0)
        metadata = result.get("metadata", {})
        sample_ids = result.get("sample_ids", [])

        print(f"📊 Collection: {collection_name}")
        print(f"   Total documents: {document_count}")
        print(f"   Collection metadata: {metadata}")
        print(f"   Sample document IDs: {sample_ids}")

        print(f"\n   Document topics in collection:")
        for doc in ton_teleport_documents:
            print(f"   • {doc['metadata']['topic']} ({doc['metadata']['section']})")

    print("\n🔹 6. UPDATE DOCUMENT")
    print("-" * 50)

    new_document = {
        "id": "testnet_details",
        "document": "TON Teleport BTC Testnet provides developers with a sandbox environment to test cross-chain transactions without financial risk. Testnet BTC has no monetary value and is freely available from faucets. This phase allows for rigorous security testing, smart contract audits, and user interface refinement before mainnet deployment.",
        "metadata": {
            "section": "technical",
            "topic": "testnet_environment",
            "phase": "testnet",
            "purpose": "development_testing",
            "audience": "developers",
            "word_count": 62
        }
    }

    result = agent.upsert_documents(
        collection_name="ton_teleport_btc",
        documents=[new_document["document"]],
        ids=[new_document["id"]],
        metadatas=[new_document["metadata"]]
    )

    if result.get("success"):
        print(f"✅ Document updated/added successfully")
        print(f"   Operation: {result.get('operation')}")
        print(f"   Document ID: {new_document['id']}")
        print(f"   Topic: {new_document['metadata']['topic']}")

    print("\n🔹 7. FINAL SEARCH")
    print("-" * 50)

    final_queries = [
        "How does Bitcoin integrate with TON blockchain?",
        "What makes TON Teleport BTC trustless and secure?",
        "Future potential of Bitcoin in TON DeFi"
    ]

    for i, query in enumerate(final_queries, 1):
        print(f"\nQuery {i}: '{query}'")
        result = agent.query_collection(
            collection_name="ton_teleport_btc",
            query_texts=[query],
            n_results=1
        )

        if result.get("success") and result.get("sample_documents"):
            sample = result["sample_documents"][0]
            print(f"   Most relevant document:")
            print(f"   {sample.get('document_preview')}")

if __name__ == "__main__":
    main()
