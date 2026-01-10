from typing import Dict, Any
from datetime import datetime
from .models import Document

class QdrantDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def create_collection_skill(context: Dict[str, Any]) -> QdrantDataValue:
    print("Starting create_collection_skill...")

    collection_name = context.get('collection_name', '')
    vector_size = context.get('vector_size', 384)
    distance = context.get('distance', 'COSINE')
    sparse_vectors = context.get('sparse_vectors', False)

    try:
        client = context.get('qdrant_client')

        if not client:
            result = {"success": False, "error": "Qdrant client not available"}
            return QdrantDataValue(result)

        result = client.create_collection(
            collection_name=collection_name,
            vector_size=vector_size,
            distance=distance,
            sparse_vectors=sparse_vectors
        )

        if result.get('success'):
            result['skill'] = 'create_collection'
            result['parameters'] = {
                'collection_name': collection_name,
                'vector_size': vector_size,
                'distance': distance
            }
            print(f"✅ Collection '{collection_name}' created successfully")
        else:
            print(f"❌ Failed to create collection: {result.get('error')}")

        return QdrantDataValue(result)

    except Exception as e:
        print(f"Error in create_collection_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "skill": "create_collection",
            "timestamp": datetime.now().isoformat()
        }
        return QdrantDataValue(result)

def upload_points_skill(context: Dict[str, Any]) -> QdrantDataValue:
    print("Starting upload_points_skill...")

    collection_name = context.get('collection_name', '')
    vectors = context.get('vectors', [])
    payloads = context.get('payloads', [])
    ids = context.get('ids')

    try:
        client = context.get('qdrant_client')

        if not client:
            result = {"success": False, "error": "Qdrant client not available"}
            return QdrantDataValue(result)

        if not vectors:
            result = {"success": False, "error": "No vectors provided"}
            return QdrantDataValue(result)

        if len(vectors) != len(payloads):
            result = {"success": False, "error": f"Vectors count ({len(vectors)}) doesn't match payloads count ({len(payloads)})"}
            return QdrantDataValue(result)

        result = client.upload_points(
            collection_name=collection_name,
            vectors=vectors,
            payloads=payloads,
            ids=ids
        )

        if result.get('success'):
            result['skill'] = 'upload_points'
            result['statistics'] = {
                'vectors_count': len(vectors),
                'payloads_count': len(payloads),
                'collection': collection_name
            }

            print(f"✅ Uploaded {len(vectors)} points to '{collection_name}'")

            if payloads and len(payloads) > 0:
                print(f"   Sample payload keys: {list(payloads[0].keys())}")
        else:
            print(f"❌ Failed to upload points: {result.get('error')}")

        return QdrantDataValue(result)

    except Exception as e:
        print(f"Error in upload_points_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "skill": "upload_points",
            "timestamp": datetime.now().isoformat()
        }
        return QdrantDataValue(result)

def upload_documents_skill(context: Dict[str, Any]) -> QdrantDataValue:
    print("Starting upload_documents_skill...")

    collection_name = context.get('collection_name', '')
    documents = context.get('documents', [])
    vectors = context.get('vectors', [])
    ids = context.get('ids')

    try:
        client = context.get('qdrant_client')

        if not client:
            result = {"success": False, "error": "Qdrant client not available"}
            return QdrantDataValue(result)

        if not documents:
            result = {"success": False, "error": "No documents provided"}
            return QdrantDataValue(result)

        if not vectors:
            result = {"success": False, "error": "No vectors provided"}
            return QdrantDataValue(result)

        if len(documents) != len(vectors):
            result = {"success": False, "error": f"Documents count ({len(documents)}) doesn't match vectors count ({len(vectors)})"}
            return QdrantDataValue(result)

        payloads = []
        for doc in documents:
            if isinstance(doc, Document):
                payload = doc.metadata.copy()
                payload["text"] = doc.text
            else:
                payload = doc.copy()
            payloads.append(payload)

        result = client.upload_points(
            collection_name=collection_name,
            vectors=vectors,
            payloads=payloads,
            ids=ids
        )

        if result.get('success'):
            result['skill'] = 'upload_documents'
            result['statistics'] = {
                'documents_count': len(documents),
                'vectors_count': len(vectors),
                'collection': collection_name
            }

            print(f"✅ Uploaded {len(documents)} documents to '{collection_name}'")

            if documents and len(documents) > 0:
                if isinstance(documents[0], Document):
                    print(f"   Document type: Document objects")
                    print(f"   First document text preview: {documents[0].text[:50]}...")
                else:
                    print(f"   Document type: Dict objects")
                    print(f"   First document keys: {list(documents[0].keys())}")
        else:
            print(f"❌ Failed to upload documents: {result.get('error')}")

        return QdrantDataValue(result)

    except Exception as e:
        print(f"Error in upload_documents_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "skill": "upload_documents",
            "timestamp": datetime.now().isoformat()
        }
        return QdrantDataValue(result)

def search_similar_skill(context: Dict[str, Any]) -> QdrantDataValue:
    print("Starting search_similar_skill...")

    collection_name = context.get('collection_name', '')
    query_vector = context.get('query_vector', [])
    limit = context.get('limit', 10)
    filters = context.get('filters')

    try:
        client = context.get('qdrant_client')

        if not client:
            result = {"success": False, "error": "Qdrant client not available"}
            return QdrantDataValue(result)

        if not query_vector:
            result = {"success": False, "error": "No query vector provided"}
            return QdrantDataValue(result)

        result = client.search_similar(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            filters=filters
        )

        if result.get('success'):
            result['skill'] = 'search_similar'
            result['query_analysis'] = {
                'vector_dimensions': len(query_vector),
                'search_parameters': {
                    'collection': collection_name,
                    'limit': limit,
                    'filters_applied': bool(filters)
                }
            }

            results = result.get('results', [])
            if results:
                scores = [r.get('score', 0) for r in results]
                result['results_analysis'] = {
                    'total_results': len(results),
                    'score_range': {
                        'min': min(scores),
                        'max': max(scores),
                        'avg': sum(scores) / len(scores)
                    },
                    'top_result': {
                        'id': results[0].get('id'),
                        'score': results[0].get('score'),
                        'payload_preview': str(results[0].get('payload', {}))[:200]
                    }
                }

            print(f"✅ Found {len(results)} similar vectors")

            if results:
                print(f"Top {min(3, len(results))} results:")
                for i, res in enumerate(results[:3]):
                    print(f"  {i+1}. Score: {res.get('score'):.4f}, ID: {res.get('id')}")
                    payload = res.get('payload', {})
                    if 'text' in payload:
                        print(f"     Text: {payload['text'][:80]}...")
                    elif 'title' in payload:
                        print(f"     Title: {payload['title']}")
        else:
            print(f"❌ Search failed: {result.get('error')}")

        return QdrantDataValue(result)

    except Exception as e:
        print(f"Error in search_similar_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "skill": "search_similar",
            "timestamp": datetime.now().isoformat()
        }
        return QdrantDataValue(result)

def get_collection_info_skill(context: Dict[str, Any]) -> QdrantDataValue:
    print("Starting get_collection_info_skill...")

    collection_name = context.get('collection_name', '')

    try:
        client = context.get('qdrant_client')

        if not client:
            result = {"success": False, "error": "Qdrant client not available"}
            return QdrantDataValue(result)

        result = client.get_collection_info(collection_name)

        if result.get('success'):
            result['skill'] = 'get_collection_info'

            collection_info = result.get('collection_info', {})

            result['collection_analysis'] = {
                'collection_name': collection_info.get('name'),
                'status': collection_info.get('status'),
                'statistics': {
                    'total_points': collection_info.get('points_count', 0),
                    'vectors_count': collection_info.get('vectors_count', 0),
                    'segments': collection_info.get('segments_count', 0)
                },
                'health': '✅ Healthy' if collection_info.get('status') == 'green' else '⚠️ Issues'
            }

            print(f"✅ Retrieved info for collection '{collection_name}'")
            print(f"  Status: {collection_info.get('status')}")
            print(f"  Points: {collection_info.get('points_count')}")
            print(f"  Segments: {collection_info.get('segments_count', 0)}")
        else:
            print(f"❌ Failed to get collection info: {result.get('error')}")

        return QdrantDataValue(result)

    except Exception as e:
        print(f"Error in get_collection_info_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "skill": "get_collection_info",
            "timestamp": datetime.now().isoformat()
        }
        return QdrantDataValue(result)

def scroll_points_skill(context: Dict[str, Any]) -> QdrantDataValue:
    print("Starting scroll_points_skill...")

    collection_name = context.get('collection_name', '')
    limit = context.get('limit', 100)
    offset = context.get('offset')

    try:
        client = context.get('qdrant_client')

        if not client:
            result = {"success": False, "error": "Qdrant client not available"}
            return QdrantDataValue(result)

        result = client.scroll_points(
            collection_name=collection_name,
            limit=limit,
            offset=offset
        )

        if result.get('success'):
            result['skill'] = 'scroll_points'

            points = result.get('points', [])
            result['statistics'] = {
                'points_returned': len(points),
                'has_more': bool(result.get('next_offset')),
                'collection': collection_name
            }

            print(f"✅ Scrolled {len(points)} points from '{collection_name}'")

            if points:
                print(f"  First point ID: {points[0].get('id')}")
                print(f"  First point payload keys: {list(points[0].get('payload', {}).keys())}")
        else:
            print(f"❌ Failed to scroll points: {result.get('error')}")

        return QdrantDataValue(result)

    except Exception as e:
        print(f"Error in scroll_points_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "skill": "scroll_points",
            "timestamp": datetime.now().isoformat()
        }
        return QdrantDataValue(result)
