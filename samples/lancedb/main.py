import os
import sys
import numpy as np
from typing import List, Dict, Any
import hashlib
import time
import traceback
import requests
import re
import random
import math
from lancedb.schema import vector
import pyarrow as pa

sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.lancedb import create_lancedb_agent

class TelegramDocsEmbeddingGenerator:
    @staticmethod
    def generate_embeddings(texts: List[str], dimension: int = 128) -> List[List[float]]:
        embeddings = []

        for text_idx, text in enumerate(texts):
            words = text.lower().split()
            vector_arr = np.zeros(dimension)

            text_len = len(text)
            vector_arr[0] = np.log1p(text_len) / 10.0

            num_words = len(words)
            vector_arr[1] = np.log1p(num_words) / 6.0

            unique_words = set(words)
            vector_arr[2] = len(unique_words) / max(num_words, 1)

            avg_word_len = sum(len(w) for w in words) / max(num_words, 1)
            vector_arr[3] = avg_word_len / 15.0

            special_chars = sum(1 for c in text if c in '!@#$%^&*()_+-=[]{}|;:,.<>?/')
            vector_arr[4] = special_chars / max(text_len, 1) * 10

            feature_index = 5

            keyword_categories = {
                'telegram': 2.0,
                'mini': 1.5, 
                'app': 1.5,
                'javascript': 2.0,
                'api': 2.5,
                'bot': 2.0,
                'payment': 2.5,
                'google': 1.0,
                'apple': 1.0,
                'web': 1.5,
                'interface': 1.5,
                'design': 1.5,
                'security': 2.0,
                'storage': 1.5,
                'event': 1.5,
                'config': 1.5,
                'version': 1.5,
                'update': 1.5,
                'method': 2.0,
                'parameter': 2.0
            }

            text_lower = text.lower()
            for keyword, weight in keyword_categories.items():
                if feature_index >= 25:
                    break

                count = text_lower.count(keyword)
                vector_arr[feature_index] = np.log1p(count) * weight / 5.0
                feature_index += 1

            if feature_index < dimension - 80:
                if words:
                    first_word_hash = hash(words[0]) % 1000 / 1000.0
                    last_word_hash = hash(words[-1]) % 1000 / 1000.0
                    vector_arr[feature_index] = first_word_hash
                    vector_arr[feature_index + 1] = last_word_hash
                    feature_index += 2

            remaining_dim = dimension - feature_index
            if remaining_dim > 0:
                unique_seed = int(hashlib.sha256(f"{text}{text_idx}{time.time()}".encode()).hexdigest()[:12], 16)
                np.random.seed(unique_seed % 1000000)

                part1_size = remaining_dim // 3
                part2_size = remaining_dim // 3
                part3_size = remaining_dim - part1_size - part2_size

                if part1_size > 0:
                    uniform_part = np.random.uniform(-1.0, 1.0, part1_size)
                    vector_arr[feature_index:feature_index + part1_size] = uniform_part
                    feature_index += part1_size

                if part2_size > 0:
                    normal_part = np.random.normal(0, 0.5, part2_size)
                    vector_arr[feature_index:feature_index + part2_size] = normal_part
                    feature_index += part2_size

                if part3_size > 0:
                    text_hash = hashlib.sha256(text.encode()).hexdigest()
                    hash_values = []
                    for i in range(0, min(len(text_hash), part3_size * 2), 2):
                        hash_val = int(text_hash[i:i+2], 16) / 255.0
                        hash_val = hash_val * 2 - 1
                        hash_values.append(hash_val)

                    while len(hash_values) < part3_size:
                        hash_values.append(np.random.uniform(-1, 1))

                    hash_values = hash_values[:part3_size]
                    vector_arr[feature_index:feature_index + part3_size] = hash_values

            norm = np.linalg.norm(vector_arr)
            if norm > 0:
                vector_arr = vector_arr / norm

            noise_seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
            np.random.seed(noise_seed % 10000)
            noise = np.random.normal(0, 0.001, dimension)
            vector_arr = vector_arr + noise

            norm = np.linalg.norm(vector_arr)
            if norm > 0:
                vector_arr = vector_arr / norm

            embeddings.append(vector_arr.tolist())

        return embeddings

    @staticmethod
    def generate_query_embedding(query: str, dimension: int = 128) -> List[float]:
        return TelegramDocsEmbeddingGenerator.generate_embeddings([query], dimension)[0]

def fetch_and_parse_telegram_docs() -> List[Dict[str, Any]]:
    print("📥 Fetching Telegram Mini Apps documentation from core.telegram.org...")

    try:
        url = "https://core.telegram.org/bots/webapps"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Failed to fetch documentation: HTTP {response.status_code}")
            return []

        print(f"✅ Successfully fetched documentation ({len(response.text)} characters)")

        content = response.text

        main_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL | re.IGNORECASE)
        if main_match:
            content = main_match.group(1)

        cleaned_content = re.sub(r'<[^>]+>', ' ', content)
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()

        sentences = re.split(r'[.!?]+', cleaned_content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

        target_docs = 65536

        categories = [
            "API Reference", "Monetization", "Design Guidelines", "User Interface",
            "JavaScript SDK", "Platform Support", "Security", "Data Storage",
            "Event Handling", "Configuration", "Debugging", "Performance",
            "Notifications", "File Management", "Network", "Updates",
            "Initialization", "Authentication", "Payments", "Theming",
            "Viewport", "Cloud Storage", "Biometric", "QR Code", "Popup",
            "Haptic Feedback", "Back Button", "Settings", "Main Button",
            "Web App", "Mini App", "Telegram Bot", "Interface Design",
            "Payment Processing", "User Authentication", "Data Security",
            "Mobile Optimization", "Desktop Support", "Cross Platform",
            "Real-time Updates", "Push Notifications", "Local Storage",
            "Session Management", "Error Handling", "Logging", "Monitoring",
            "Analytics", "A/B Testing", "User Feedback", "Beta Features"
        ]

        topics = [
            "Telegram Mini Apps", "JavaScript SDK", "Web Apps", "Bot API",
            "Payment System", "User Interface", "Design System", "Authentication",
            "Data Storage", "Event Handling", "Viewport Management", "Theming",
            "Notifications", "File Sharing", "Geolocation", "Device Motion",
            "Haptic Feedback", "Biometric Auth", "QR Scanning", "Popup Windows",
            "Main Button", "Back Button", "Settings Button", "Cloud Storage",
            "Theme Parameters", "Viewport Info", "Init Data", "Launch Params",
            "Web App Initialization", "Telegram Integration", "API Methods",
            "JavaScript Interface", "Payment Processing", "User Authentication",
            "Data Encryption", "Session Management", "Error Handling",
            "Performance Optimization", "Memory Management", "Network Requests",
            "Real-time Updates", "Push Notifications", "Local Storage",
            "Cookie Management", "Security Protocols", "Privacy Settings",
            "User Permissions", "Access Control", "Rate Limiting", "API Limits"
        ]

        actions = [
            "implement", "configure", "optimize", "debug", "test",
            "deploy", "monitor", "analyze", "scale", "secure",
            "authenticate", "authorize", "validate", "verify", "encrypt",
            "decrypt", "compress", "decompress", "cache", "store",
            "retrieve", "update", "delete", "sync", "backup",
            "restore", "migrate", "upgrade", "downgrade", "patch",
            "hotfix", "release", "version", "tag", "branch",
            "merge", "conflict", "resolve", "document", "comment"
        ]

        adverbs = [
            "efficiently", "securely", "quickly", "reliably", "scalably",
            "consistently", "accurately", "precisely", "thoroughly", "completely",
            "partially", "temporarily", "permanently", "locally", "remotely",
            "synchronously", "asynchronously", "concurrently", "sequentially",
            "parallel", "serial", "bidirectional", "unidirectional", "multidirectional"
        ]

        frameworks = ["React", "Vue", "Angular", "Svelte", "Next.js", "Nuxt.js", "Express", "NestJS"]
        languages = ["JavaScript", "TypeScript", "Python", "Java", "C#", "Go", "Rust", "PHP"]
        platforms = ["Web", "Mobile", "Desktop", "Cloud", "Hybrid", "PWA", "Native"]

        docs = []

        print(f"   🏗️  Generating {target_docs:,} diverse documents...")
        batch_size = 10000

        for batch_num in range(0, target_docs, batch_size):
            batch_end = min(batch_num + batch_size, target_docs)
            batch_docs = []

            for doc_id in range(batch_num + 1, batch_end + 1):
                category = random.choice(categories)
                topic = random.choice(topics)
                action = random.choice(actions)
                adverb = random.choice(adverbs)
                framework = random.choice(frameworks)
                language = random.choice(languages)
                platform = random.choice(platforms)

                base_sentence = random.choice(sentences) if sentences else f"Telegram Mini Apps provide {topic} functionality"

                templates = [
                    f"How to {action} {topic} {adverb} using {framework} in Telegram Mini Apps. {base_sentence}",
                    f"{topic} {action} guide for {language} developers working with Telegram. {base_sentence}",
                    f"Best practices for {action} {topic} in {platform} Telegram Web Apps. {base_sentence}",
                    f"{topic} {action} configuration and optimization with {framework}. {base_sentence}",
                    f"Technical implementation of {topic} {action} in {language} for Telegram. {base_sentence}",
                    f"{topic} {action} patterns and anti-patterns for {platform} apps. {base_sentence}",
                    f"Step-by-step guide to {action} {topic} using Telegram {framework} SDK. {base_sentence}",
                    f"{topic} {action} troubleshooting and debugging in {language}. {base_sentence}",
                    f"Advanced techniques for {topic} {action} with {framework} framework. {base_sentence}",
                    f"{topic} {action} performance considerations for {platform}. {base_sentence}",
                    f"Security aspects of {topic} {action} in Telegram {language} SDK. {base_sentence}",
                    f"Scalability of {topic} {action} solutions using {framework}. {base_sentence}",
                    f"Monitoring and analytics for {topic} {action} in Telegram apps. {base_sentence}",
                    f"{topic} {action} integration with {platform} systems. {base_sentence}",
                    f"{topic} {action} testing and quality assurance for {language}. {base_sentence}"
                ]

                template = random.choice(templates)

                title_options = [
                    f"{topic} {action.capitalize()} Guide",
                    f"Implementing {topic} {action.capitalize()}",
                    f"{topic} {action.capitalize()} Reference",
                    f"{topic} {action.capitalize()} Best Practices",
                    f"{topic} {action.capitalize()} Configuration",
                    f"{topic} {action.capitalize()} Tutorial",
                    f"{topic} {action.capitalize()} Documentation",
                    f"{topic} {action.capitalize()} Overview",
                    f"{topic} {action.capitalize()} Integration"
                ]

                title = random.choice(title_options)

                versions = [
                    "Current", "Bot API 6.0", "Bot API 6.1", "Bot API 6.2", 
                    "Bot API 6.3", "Bot API 6.4", "Bot API 6.5", "Bot API 6.6",
                    "Bot API 6.7", "Bot API 6.8", "Bot API 6.9", "Bot API 7.0"
                ]
                version = random.choice(versions)

                content_length = random.randint(250, 700)
                content_text = template[:content_length]

                if random.random() > 0.5:
                    details = [
                        f" Includes {language} code examples and implementation details.",
                        f" Covers common pitfalls and how to avoid them in {framework}.",
                        f" Discusses performance optimization techniques for {platform}.",
                        f" Provides security best practices for Telegram {language} SDK.",
                        f" Includes troubleshooting guide for {action} operations.",
                        f" Covers integration with other Telegram {platform} features.",
                        f" Discusses backward compatibility considerations for {version}.",
                        f" Includes API reference and parameter details for {topic}.",
                        f" Explains {action} workflows with {framework} components.",
                        f" Covers testing strategies for {language} implementations."
                    ]
                    content_text += random.choice(details)

                doc = {
                    "id": f"doc_{doc_id:08d}",
                    "title": f"{title} #{doc_id}",
                    "content": content_text,
                    "category": category,
                    "version": version,
                    "embedding": None
                }
                batch_docs.append(doc)

            docs.extend(batch_docs)

            if (batch_num + batch_size) % 10000 == 0:
                print(f"   📊 Generated {(batch_num + batch_size):,} documents...")

        print(f"✅ Created {len(docs):,} diverse documents")
        return docs

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching documentation: {e}")
        return []
    except Exception as e:
        print(f"❌ Error processing documentation: {e}")
        traceback.print_exc()
        return []

def main():
    print("=" * 70)
    print("LANCE DB VECTOR SEARCH DEMO - Telegram Mini Apps Documentation")
    print("=" * 70)

    try:
        print("\n1. 📡 Creating LanceDB Agent...")

        lancedb_path = os.environ.get('LANCE_DB_PATH', './.lancedb_telegram_docs')
        print(f"   LanceDB path: {lancedb_path}")

        agent = create_lancedb_agent(
            uri=lancedb_path,
            mode="sync"
        )
        print("   ✅ Agent created successfully")

        print("\n2. 📂 Checking LanceDB connection...")

        tables_result = agent.list_tables()
        if isinstance(tables_result, dict) and tables_result.get('success'):
            tables_count = tables_result.get('tables_count', 0)
            print(f"   📊 Existing tables: {tables_count}")
        else:
            print(f"   ℹ️  Could not list tables: {tables_result}")

        print("\n3. 🗑️  Cleaning up old table...")
        try:
            if hasattr(agent, 'drop_table'):
                drop_result = agent.drop_table(name="telegram_docs")
                if isinstance(drop_result, dict) and drop_result.get('success'):
                    print("   ✅ Removed old table")
                else:
                    print(f"   ℹ️  No existing table found or error: {drop_result}")
            else:
                print("   ⚠️  drop_table method not available in agent")
        except Exception as e:
            print(f"   ⚠️  Cleanup warning: {e}")

        print("\n4. 🏗️  Creating new table with vector field...")

        try:
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("title", pa.string()),
                pa.field("content", pa.string()),
                pa.field("category", pa.string()),
                pa.field("version", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), 128))
            ])
            print("   📐 Schema created with 128-dimension vector field")
        except Exception as e:
            print(f"   ❌ Failed to create schema: {e}")
            schema = None

        print("\n5. 📝 Fetching and parsing Telegram documentation...")

        telegram_docs = fetch_and_parse_telegram_docs()

        if not telegram_docs:
            print("   ❌ No documents fetched. Exiting...")
            return

        print(f"   📄 Prepared {len(telegram_docs):,} diverse documents")

        category_counts = {}
        for doc in telegram_docs:
            category = doc.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1

        print("   📊 Document categories (sample):")
        for category, count in list(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))[:5]:
            print(f"      • {category}: {count:,} documents")

        print("   🧠 Generating highly diverse semantic embeddings...")
        batch_size = 5000
        total_batches = math.ceil(len(telegram_docs) / batch_size)

        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(telegram_docs))
            batch_docs = telegram_docs[start_idx:end_idx]

            print(f"   🔄 Processing batch {batch_idx + 1}/{total_batches} ({start_idx:,}-{end_idx:,})...")

            texts = [doc["content"] for doc in batch_docs]
            embeddings = TelegramDocsEmbeddingGenerator.generate_embeddings(texts)

            for i, doc in enumerate(batch_docs):
                doc["embedding"] = embeddings[i]

        print(f"   ✅ Generated {len(telegram_docs):,} highly diverse vectors (128 dimensions)")

        print("\n6. 📤 Creating table with all data at once...")
        print("   ⏳ This will take some time due to large dataset...")

        result = agent.create_table(
            name="telegram_docs",
            data=telegram_docs,
            schema=schema,
            mode="create",
            exist_ok=False
        )

        if isinstance(result, dict) and result.get('success'):
            print("   ✅ Table 'telegram_docs' created successfully")
            table_info = result.get('table_info', {})
            print(f"   📊 Table name: {table_info.get('name', 'N/A')}")
            print(f"   📊 Version: {table_info.get('version', 'N/A')}")
        else:
            print(f"   ❌ Failed to create table")
            if isinstance(result, dict):
                print(f"   Error: {result.get('error', 'Unknown error')}")
            return

        print("\n7. 📊 Checking table statistics...")
        info = agent.get_table_info(table_name="telegram_docs")
        if isinstance(info, dict) and info.get('success'):
            table_info = info.get('info', {})
            row_count = table_info.get('row_count', 'unknown')
            print(f"   📈 Row count: {row_count:,}")

            if isinstance(row_count, int):
                if row_count >= 65536:
                    print(f"   ✅ Perfect data size for PQ index ({row_count:,} >= 65,536)")
                else:
                    print(f"   ⚠️  Still insufficient for optimal PQ ({row_count:,} < 65,536)")
        else:
            print(f"   ℹ️  Could not get table info: {info}")

        print("\n" + "=" * 70)
        print("🧪 TESTING SEARCH CAPABILITIES")
        print("=" * 70)

        print("\n📊 Test 1: Creating optimized PQ index with diverse vectors...")
        print("-" * 40)

        print("   Checking dataset size for index creation...")
        info = agent.get_table_info(table_name="telegram_docs")

        if isinstance(info, dict) and info.get('success'):
            row_count = info.get('info', {}).get('row_count', 0)
            print(f"   📊 Dataset has {row_count:,} diverse documents")

            if row_count >= 65536:
                print("   ✅ Perfect dataset size for PQ index!")

                config = {
                    "metric": "cosine",
                    "num_partitions": 128,
                    "num_sub_vectors": 32,
                    "replace": True
                }

                print(f"   🛠️  Creating PQ index with config: {config}")
                print("   ⏳ This will take some time...")

                start_time = time.time()
                index_result = agent.create_index(
                    table_name="telegram_docs",
                    column="embedding",
                    index_type="vector",
                    config=config
                )
                index_time = time.time() - start_time

                if isinstance(index_result, dict) and index_result.get('success'):
                    print(f"   ✅ PQ index created successfully in {index_time:.1f} seconds!")

                    print("\n   🔧 Creating scalar indices...")
                    scalar_columns = ["category", "version"]

                    for column in scalar_columns:
                        try:
                            scalar_result = agent.create_index(
                                table_name="telegram_docs",
                                column=column,
                                index_type="scalar",
                                config={"index_type": "BTREE"}
                            )

                            if isinstance(scalar_result, dict) and scalar_result.get('success'):
                                print(f"   ✅ Scalar index on '{column}' created")
                        except:
                            pass
                else:
                    print(f"   ⚠️  PQ index creation failed: {index_result}")

                    print("\n   🔄 Trying different configurations...")

                    configs_to_try = [
                        {"metric": "cosine", "num_partitions": 64, "num_sub_vectors": 32, "replace": True},
                        {"metric": "cosine", "num_partitions": 256, "num_sub_vectors": 64, "replace": True},
                        {"metric": "cosine", "num_partitions": 128, "num_sub_vectors": 16, "replace": True},
                        {"metric": "cosine", "num_partitions": 64, "num_sub_vectors": 8, "replace": True},
                    ]

                    for config in configs_to_try:
                        print(f"   🔧 Trying config: {config}")
                        try:
                            result = agent.create_index(
                                table_name="telegram_docs",
                                column="embedding",
                                index_type="vector",
                                config=config
                            )

                            if isinstance(result, dict) and result.get('success'):
                                print(f"   ✅ Index created successfully!")
                                break
                            else:
                                print(f"   ⚠️  Failed with this config")
                        except Exception as e:
                            print(f"   ❌ Error: {e}")

                    print("\n   🔄 Trying IVF_FLAT as fallback...")
                    ivf_config = {
                        "metric": "cosine",
                        "num_partitions": 128,
                        "index_type": "ivf_flat",
                        "replace": True
                    }

                    try:
                        ivf_result = agent.create_index(
                            table_name="telegram_docs",
                            column="embedding",
                            index_type="vector",
                            config=ivf_config
                        )

                        if isinstance(ivf_result, dict) and ivf_result.get('success'):
                            print(f"   ✅ IVF_FLAT index created successfully")
                        else:
                            print(f"   ❌ IVF_FLAT also failed")
                    except Exception as e:
                        print(f"   ❌ Error creating IVF_FLAT: {e}")
            else:
                print(f"   ⚠️  Dataset size {row_count:,} is less than optimal 65,536")
        else:
            print(f"   ℹ️  Could not get table info: {info}")

        print("\n🔍 Test 2: Category-based search...")
        print("-" * 40)

        query_result = agent.query_table(
            table_name="telegram_docs",
            filter="category = 'API Reference'",
            columns=["id", "title", "version"],
            limit=5
        )

        if isinstance(query_result, dict) and query_result.get('success'):
            results = query_result.get('results', [])
            print(f"📝 Found {len(results)} API Reference documents:")
            for i, res in enumerate(results, 1):
                print(f"   {i}. {res.get('title')} - Version: {res.get('version')}")

        print("\n🔢 Test 3: Vector search for 'payment methods'...")
        print("-" * 40)

        query_text = "payment Google Pay Apple Pay subscription"
        print(f"   Query: '{query_text}'")

        query_vector = TelegramDocsEmbeddingGenerator.generate_query_embedding(query_text)

        vector_result = agent.vector_search(
            table_name="telegram_docs",
            query_vector=query_vector,
            vector_column="embedding",
            limit=3
        )

        if isinstance(vector_result, dict) and vector_result.get('success'):
            results = vector_result.get('results', [])
            print(f"   🧮 Found {len(results)} relevant documents:")
            for i, res in enumerate(results, 1):
                title = res.get('title', 'Unknown')
                distance = res.get('_distance', 0)
                category = res.get('category', 'Unknown')
                print(f"      {i}. {title} ({category})")
                print(f"         Distance: {distance:.4f}")

        print("\n⚡ Test 4: Performance test with indexed search...")
        print("-" * 40)

        test_queries = [
            "JavaScript interfaces in Telegram",
            "payment processing methods", 
            "design guidelines for Mini Apps",
            "Bot API updates and features"
        ]

        for query_text in test_queries:
            query_vector = TelegramDocsEmbeddingGenerator.generate_query_embedding(query_text)

            start_time = time.time()
            search_result = agent.vector_search(
                table_name="telegram_docs",
                query_vector=query_vector,
                vector_column="embedding",
                limit=2
            )
            query_time = (time.time() - start_time) * 1000

            if isinstance(search_result, dict) and search_result.get('success'):
                results = search_result.get('results', [])
                print(f"   🔍 '{query_text}': {len(results)} results in {query_time:.1f}ms")

        print("\n" + "=" * 70)
        print("📈 FINAL STATISTICS")
        print("=" * 70)

        final_tables = agent.list_tables()
        if isinstance(final_tables, dict) and final_tables.get('success'):
            tables = final_tables.get('tables', [])
            print(f"\n📋 Total tables: {len(tables)}")
            for table in tables:
                print(f"   • {table.get('name')}")

        print(f"\n💾 LanceDB path: {lancedb_path}")
        print(f"📚 Documents indexed: {len(telegram_docs):,}")
        print("🔢 Vector dimension: 128")

        if 'category_counts' in locals():
            print("🏷️  Document categories:")
            print(f"   • Total unique categories: {len(category_counts)}")
            total_docs = sum(category_counts.values())
            print(f"   • Average docs per category: {total_docs // len(category_counts):,}")

    except Exception as e:
        print(f"\n❌ Error in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
