import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH', '.'))
from sidusai.plugins.weaviate import create_weaviate_agent

def main():
    print("WEAVIATE VECTOR DATABASE DEMO")
    print("=" * 50)

    agent = create_weaviate_agent(
        weaviate_url=os.environ.get('WEAVIATE_URL'),
        grpc_enabled=True
    )

    print("\n1. Connecting to Weaviate:")
    print("-" * 30)

    result = agent.list_collections()
    if result.get('success'):
        print(f"✅ Connection successful!")
        collections_count = result.get('collections_count', 0)
        print(f"   Collections in database: {collections_count}")

        if collections_count > 0:
            collections = result.get('collections', [])[:3]
            print(f"   First 3 collections:")
            for i, coll in enumerate(collections, 1):
                objects_count = coll.get('total_objects', 0)
                vectorizer = coll.get('vectorizer', 'None')
                print(f"   {i}. {coll.get('name')} (objects: {objects_count}, vectorizer: {vectorizer})")
    else:
        print(f"❌ Error: {result.get('error')}")
        return

    print("\n2. Creating TDLib documentation collection:")
    print("-" * 30)

    try:
        delete_result = agent.delete_collection(collection_name="TDLibDocs")
        if delete_result.get('success'):
            print("Cleaned up existing collection")
    except:
        pass

    result = agent.create_collection(
        collection_name="TDLibDocs",
        properties=[
            {
                "name": "title",
                "dataType": "text",
                "description": "Documentation section title"
            },
            {
                "name": "content",
                "dataType": "text", 
                "description": "Documentation content"
            },
            {
                "name": "section",
                "dataType": "text",
                "description": "Documentation section"
            },
            {
                "name": "keywords",
                "dataType": "text[]",
                "description": "Keywords"
            }
        ],
        vectorizer="text2vec-transformers"
    )

    if result.get('success'):
        print(f"✅ Collection created: {result.get('collection_name')}")
        print(f"   Vectorizer: {result.get('vectorizer')}")
        print(f"   Properties count: {result.get('properties_count')}")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n3. Adding TDLib documentation sections:")
    print("-" * 30)

    tdlib_docs = [
        {
            "title": "Getting started with TDLib",
            "content": "TDLib is a fully functional Telegram client which takes care of all networking, local storage and data consistency details. In this tutorial we describe the main concepts understanding of which is required for efficient TDLib usage.",
            "section": "Introduction",
            "keywords": ["tdlib", "telegram", "client", "tutorial", "getting started", "basics", "introduction"]
        },
        {
            "title": "TDLib interface and API",
            "content": "The main TDLib API is fully-asynchronous. An Application can send a request to TDLib through ClientManager.send method and receive a response asynchronously through the ClientManager.receive method when it becomes available. The exact naming of these methods is different for different TDLib interfaces.",
            "section": "Architecture", 
            "keywords": ["interface", "api", "asynchronous", "client", "application", "requests", "responses"]
        },
        {
            "title": "TDLib glossary and terminology",
            "content": "This section describes the basic notions required for understanding the TDLib API. Telegram is a messenger, so the main object is a message. Each message belongs to some chat and has a unique identifier. Currently there are 4 different types of chats on Telegram: private chats, basic groups, supergroups, and secret chats.",
            "section": "Concepts",
            "keywords": ["glossary", "terminology", "message", "chat", "user", "bot", "concepts", "definitions"]
        },
        {
            "title": "User authorization and authentication",
            "content": "Authorization is controlled by TDLib through updates. Whenever an action is required to proceed with user authorization, the Application receives an updateAuthorizationState. The Application only needs to handle this update appropriately to correctly implement user authorization.",
            "section": "Authentication",
            "keywords": ["authorization", "authentication", "updates", "state", "login", "credentials", "security"]
        },
        {
            "title": "Sending messages with TDLib",
            "content": "To send any kind of message, the Application needs to call the method sendMessage providing a chat identifier and the content of the message to be sent. The Application can send a text message using inputMessageText, a photo using inputMessagePhoto, or a location using inputMessageLocation.",
            "section": "Messaging",
            "keywords": ["sending", "message", "content", "photo", "location", "api", "sendmessage", "messaging"]
        },
        {
            "title": "Handling updates and events",
            "content": "All updates and responses to requests must be handled in the order they are received. Important updates include: updateAuthorizationState, updateNewChat, updateUser, updateBasicGroup, updateSupergroup, updateSecretChat, updateNewMessage, updateMessageSendSucceeded, updateMessageContent, updateFile.",
            "section": "Updates",
            "keywords": ["updates", "events", "handling", "real-time", "notifications", "listeners", "callbacks"]
        },
        {
            "title": "Managing chat lists",
            "content": "Currently there are 3 different types of chat lists: Main chat list, Archive chat list, and folder chat lists. The positions of chats in chat lists are managed by TDLib. The Application only needs to listen to updates that change the chat.positions field and maintain sorted lists.",
            "section": "Chat Management",
            "keywords": ["chats", "lists", "main", "archive", "folders", "sorting", "management", "organization"]
        },
        {
            "title": "Retrieving chat message history",
            "content": "The Application can use the method getChatHistory to get messages in a chat. The messages will be returned in the reverse chronological order. To get more messages than can be returned in one response, the Application needs to pass the identifier of the last message it has received as from_message_id to next request.",
            "section": "Messages",
            "keywords": ["messages", "history", "chronological", "pagination", "retrieval", "gethistory", "chat history"]
        },
        {
            "title": "Working with files in TDLib",
            "content": "Messages with media content like photos or videos can have files. Each file has an identifier and may be available locally or remotely. Files can be downloaded to local storage or uploaded to Telegram cloud servers. The updateFile update tracks file transfer progress.",
            "section": "Files",
            "keywords": ["files", "media", "download", "upload", "storage", "transfer", "progress", "updatefile"]
        },
        {
            "title": "Error handling in TDLib",
            "content": "TDLib provides detailed error information through error objects. Each error has a code and message. Common errors include network issues, authorization problems, and invalid parameters. Applications should implement proper error handling for robust operation.",
            "section": "Errors",
            "keywords": ["errors", "error handling", "exceptions", "debugging", "troubleshooting", "validation"]
        }
    ]

    for i, doc in enumerate(tdlib_docs, 1):
        result = agent.store_document(
            collection_name="TDLibDocs",
            properties=doc
        )

        if result.get('success'):
            print(f"✅ Section {i}: {doc['title']}")
        else:
            print(f"❌ Error: {result.get('error')}")

    print("\n4. Testing search accuracy:")
    print("-" * 30)

    test_cases = [
        {
            "query": "How do I authenticate users in TDLib?",
            "expected": ["User authorization and authentication", "Getting started with TDLib"],
            "description": "Authentication query"
        },
        {
            "query": "What are the basic concepts I need to know?",
            "expected": ["TDLib glossary and terminology", "Getting started with TDLib"],
            "description": "Basic concepts query"
        },
        {
            "query": "How to send photos and messages?",
            "expected": ["Sending messages with TDLib", "Working with files in TDLib"],
            "description": "Messaging query"
        },
        {
            "query": "How to handle real-time notifications?",
            "expected": ["Handling updates and events", "Managing chat lists"],
            "description": "Updates query"
        },
        {
            "query": "How to retrieve old messages from chat?",
            "expected": ["Retrieving chat message history", "Managing chat lists"],
            "description": "History query"
        }
    ]

    for test in test_cases:
        print(f"\nQuery: '{test['query']}'")
        print(f"Expected topics: {', '.join(test['expected'])}")

        result = agent.near_text_search(
            collection_name="TDLibDocs",
            query=test['query'],
            limit=3
        )

        if result.get('success') and result.get('results_count', 0) > 0:
            results = result.get('results', [])
            found_titles = [r.get('properties', {}).get('title', '') for r in results]

            matches = 0
            for expected in test['expected']:
                for found in found_titles:
                    if expected.lower() in found.lower():
                        matches += 1
                        break

            if matches > 0:
                print(f"✅ Found {matches}/{len(test['expected'])} expected topics")
            else:
                print(f"⚠️  No exact matches found")

            print(f"Actual results:")
            for i, title in enumerate(found_titles, 1):
                print(f"  {i}. {title}")
        else:
            print(f"❌ No results found")

    print("\n5. Comparing search methods:")
    print("-" * 30)

    comparison_query = "working with chat messages and files"

    print(f"Query: '{comparison_query}'")

    print("\nSemantic search results:")
    semantic_result = agent.near_text_search(
        collection_name="TDLibDocs",
        query=comparison_query,
        limit=3
    )

    if semantic_result.get('success'):
        semantic_titles = [r.get('properties', {}).get('title', '') for r in semantic_result.get('results', [])]
        for i, title in enumerate(semantic_titles, 1):
            print(f"  {i}. {title}")

    print("\nKeyword search (BM25) results:")
    bm25_result = agent.bm25_search(
        collection_name="TDLibDocs", 
        query=comparison_query,
        limit=3
    )

    if bm25_result.get('success'):
        bm25_titles = [r.get('properties', {}).get('title', '') for r in bm25_result.get('results', [])]
        for i, title in enumerate(bm25_titles, 1):
            print(f"  {i}. {title}")

    print("\nHybrid search results:")
    hybrid_result = agent.hybrid_search(
        collection_name="TDLibDocs",
        query=comparison_query,
        alpha=0.5,
        limit=3
    )

    if hybrid_result.get('success'):
        hybrid_titles = [r.get('properties', {}).get('title', '') for r in hybrid_result.get('results', [])]
        for i, title in enumerate(hybrid_titles, 1):
            print(f"  {i}. {title}")

    print("\n6. Collection statistics:")
    print("-" * 30)

    result = agent.get_info(
        collection_name="TDLibDocs"
    )

    if result.get('success'):
        summary = result.get('info_summary', {})
        print(f"Total documents: {summary.get('total_objects', 0)}")
        print(f"Vectorizer: {summary.get('vectorizer')}")

        detailed = result.get('detailed_info', {})
        if detailed and 'properties' in detailed:
            print(f"Properties: {len(detailed['properties'])}")

    print("\n7. Filtered search examples:")
    print("-" * 30)

    filter_tests = [
        {
            "query": "authentication",
            "filter": {"property": "section", "operator": "equal", "value": "Authentication"},
            "description": "Authentication section only"
        },
        {
            "query": "messages",
            "filter": {"property": "section", "operator": "equal", "value": "Messaging"},
            "description": "Messaging section only"
        }
    ]

    for test in filter_tests:
        print(f"\n{test['description']}:")
        print(f"Query: '{test['query']}'")

        result = agent.near_text_search(
            collection_name="TDLibDocs",
            query=test['query'],
            filters=test['filter'],
            limit=2
        )

        if result.get('success') and result.get('results_count', 0) > 0:
            results = result.get('results', [])
            for i, res in enumerate(results, 1):
                props = res.get('properties', {})
                print(f"  {i}. {props.get('title')} (Section: {props.get('section')})")
        else:
            print("  No results found with filter")

    #result = agent.delete_collection(
    #    collection_name="TDLibDocs"
    #)

    #if result.get('success'):
    #    print(f"✅ Collection deleted")

    agent.plugin.weaviate_client.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted")
    except Exception as e:
        print(f"\nError: {e}")
