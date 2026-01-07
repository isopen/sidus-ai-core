from typing import Dict, Any
from datetime import datetime
from .components import ChromaDBClientComponent

class ChromaDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def create_collection_skill(context: Dict[str, Any]) -> ChromaDataValue:
    collection_name = context.get('collection_name', 'default_collection')
    metadata = context.get('metadata')

    try:
        client: ChromaDBClientComponent = context.get('chroma_client')

        if not client:
            result = {"success": False, "error": "ChromaDB client not available"}
            return ChromaDataValue(result)

        collection = client.get_or_create_collection(
            name=collection_name,
            metadata=metadata
        )

        result = {
            "success": True,
            "collection_name": collection_name,
            "operation": "get_or_create",
            "metadata": collection.metadata,
            "timestamp": datetime.now().isoformat()
        }

        return ChromaDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "collection_name": collection_name,
            "timestamp": datetime.now().isoformat()
        }
        return ChromaDataValue(result)

def add_documents_skill(context: Dict[str, Any]) -> ChromaDataValue:

    collection_name = context.get('collection_name', 'default_collection')
    documents = context.get('documents', [])
    ids = context.get('ids', [])
    metadatas = context.get('metadatas')
    embeddings = context.get('embeddings')
    images = context.get('images')
    uris = context.get('uris')

    try:
        client: ChromaDBClientComponent = context.get('chroma_client')

        if not client:
            result = {"success": False, "error": "ChromaDB client not available"}
            return ChromaDataValue(result)

        if not documents and not images and not embeddings and not uris:
            result = {"success": False, "error": "No data provided"}
            return ChromaDataValue(result)

        add_result = client.add_documents(
            collection_name=collection_name,
            documents=documents,
            ids=ids,
            metadatas=metadatas,
            embeddings=embeddings,
            images=images,
            uris=uris
        )

        if add_result["success"]:
            data_type = "documents" if documents else "images" if images else "embeddings" if embeddings else "uris"
            result = {
                "success": True,
                "collection_name": collection_name,
                "data_type": data_type,
                "count": add_result["count"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "success": False,
                "error": add_result.get("error", "Unknown error"),
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }

        return ChromaDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "collection_name": collection_name,
            "timestamp": datetime.now().isoformat()
        }
        return ChromaDataValue(result)

def query_collection_skill(context: Dict[str, Any]) -> ChromaDataValue:

    collection_name = context.get('collection_name', 'default_collection')
    query_texts = context.get('query_texts')
    query_embeddings = context.get('query_embeddings')
    query_images = context.get('query_images')
    query_uris = context.get('query_uris')
    n_results = context.get('n_results', 10)
    where = context.get('where')
    where_document = context.get('where_document')

    try:
        client: ChromaDBClientComponent = context.get('chroma_client')

        if not client:
            result = {"success": False, "error": "ChromaDB client not available"}
            return ChromaDataValue(result)

        if not query_texts and not query_embeddings and not query_images and not query_uris:
            result = {"success": False, "error": "No query data provided"}
            return ChromaDataValue(result)

        query_result = client.query(
            collection_name=collection_name,
            query_texts=query_texts,
            query_embeddings=query_embeddings,
            query_images=query_images,
            query_uris=query_uris,
            n_results=n_results,
            where=where,
            where_document=where_document
        )

        if query_result["success"]:
            results = query_result["results"]

            analysis = {
                "success": True,
                "collection_name": collection_name,
                "query_count": query_result["query_count"],
                "n_results": n_results,
                "total_results": len(results.get('ids', [])),
                "distances_summary": {},
                "timestamp": datetime.now().isoformat()
            }

            if results.get('distances'):
                all_distances = [d for sublist in results['distances'] for d in sublist]
                if all_distances:
                    analysis["distances_summary"] = {
                        "min": min(all_distances),
                        "max": max(all_distances),
                        "avg": sum(all_distances) / len(all_distances)
                    }

            if results.get('documents'):
                sample_docs = []
                for i, doc_list in enumerate(results['documents'][:3]):
                    for j, doc in enumerate(doc_list[:2]):
                        if doc:
                            document_preview = doc
                            sample_docs.append({
                                "query_index": i,
                                "result_index": j,
                                "document_preview": document_preview
                            })
                analysis["sample_documents"] = sample_docs

            return ChromaDataValue(analysis)
        else:
            result = {
                "success": False,
                "error": query_result.get("error", "Query failed"),
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }
            return ChromaDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "collection_name": collection_name,
            "timestamp": datetime.now().isoformat()
        }
        return ChromaDataValue(result)

def get_collection_info_skill(context: Dict[str, Any]) -> ChromaDataValue:

    collection_name = context.get('collection_name', 'default_collection')

    try:
        client: ChromaDBClientComponent = context.get('chroma_client')

        if not client:
            result = {"success": False, "error": "ChromaDB client not available"}
            return ChromaDataValue(result)

        info_result = client.get_collection_info(collection_name)

        if info_result["success"]:
            result = {
                "success": True,
                "collection_name": collection_name,
                "document_count": info_result["count"],
                "metadata": info_result["metadata"],
                "sample_ids": info_result.get("sample_ids", []),
                "sample_documents": info_result.get("sample_documents", []),
                "timestamp": datetime.now().isoformat()
            }

            return ChromaDataValue(result)
        else:
            result = {
                "success": False,
                "error": info_result.get("error", "Failed to get info"),
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }
            return ChromaDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "collection_name": collection_name,
            "timestamp": datetime.now().isoformat()
        }
        return ChromaDataValue(result)

def list_collections_skill(context: Dict[str, Any]) -> ChromaDataValue:

    limit = context.get('limit', 100)
    offset = context.get('offset', 0)

    try:
        client: ChromaDBClientComponent = context.get('chroma_client')

        if not client:
            result = {"success": False, "error": "ChromaDB client not available"}
            return ChromaDataValue(result)

        list_result = client.list_collections(limit=limit, offset=offset)

        if list_result["success"]:
            result = {
                "success": True,
                "collections": list_result["collections"],
                "collection_info": list_result.get("collection_info", []),
                "total_count": list_result["count"],
                "limit": limit,
                "offset": offset,
                "timestamp": datetime.now().isoformat()
            }

            return ChromaDataValue(result)
        else:
            result = {
                "success": False,
                "error": list_result.get("error", "Failed to list collections"),
                "timestamp": datetime.now().isoformat()
            }
            return ChromaDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return ChromaDataValue(result)

def delete_collection_skill(context: Dict[str, Any]) -> ChromaDataValue:

    collection_name = context.get('collection_name')

    try:
        client: ChromaDBClientComponent = context.get('chroma_client')

        if not client:
            result = {"success": False, "error": "ChromaDB client not available"}
            return ChromaDataValue(result)

        if not collection_name:
            result = {"success": False, "error": "Collection name required"}
            return ChromaDataValue(result)

        success = client.delete_collection(collection_name)

        if success:
            result = {
                "success": True,
                "collection_name": collection_name,
                "message": "Collection deleted successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "success": False,
                "collection_name": collection_name,
                "error": "Failed to delete collection",
                "timestamp": datetime.now().isoformat()
            }

        return ChromaDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "collection_name": collection_name,
            "timestamp": datetime.now().isoformat()
        }
        return ChromaDataValue(result)

def upsert_documents_skill(context: Dict[str, Any]) -> ChromaDataValue:

    collection_name = context.get('collection_name', 'default_collection')
    documents = context.get('documents', [])
    ids = context.get('ids', [])
    metadatas = context.get('metadatas')
    embeddings = context.get('embeddings')
    images = context.get('images')
    uris = context.get('uris')

    try:
        client: ChromaDBClientComponent = context.get('chroma_client')

        if not client:
            result = {"success": False, "error": "ChromaDB client not available"}
            return ChromaDataValue(result)

        if not documents and not images and not embeddings and not uris:
            result = {"success": False, "error": "No data provided"}
            return ChromaDataValue(result)

        upsert_result = client.upsert_documents(
            collection_name=collection_name,
            documents=documents,
            ids=ids,
            metadatas=metadatas,
            embeddings=embeddings,
            images=images,
            uris=uris
        )

        if upsert_result["success"]:
            data_type = "documents" if documents else "images" if images else "embeddings" if embeddings else "uris"
            result = {
                "success": True,
                "collection_name": collection_name,
                "operation": "upsert",
                "data_type": data_type,
                "count": upsert_result["count"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "success": False,
                "error": upsert_result.get("error", "Unknown error"),
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }

        return ChromaDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "collection_name": collection_name,
            "timestamp": datetime.now().isoformat()
        }
        return ChromaDataValue(result)

def search_documents_skill(context: Dict[str, Any]) -> ChromaDataValue:

    collection_name = context.get('collection_name', 'default_collection')
    where = context.get('where')
    where_document = context.get('where_document')
    limit = context.get('limit', 100)
    offset = context.get('offset', 0)

    try:
        client: ChromaDBClientComponent = context.get('chroma_client')

        if not client:
            result = {"success": False, "error": "ChromaDB client not available"}
            return ChromaDataValue(result)

        get_result = client.get(
            collection_name=collection_name,
            where=where,
            where_document=where_document,
            limit=limit,
            offset=offset
        )

        if get_result["success"]:
            results = get_result["results"]

            analysis = {
                "success": True,
                "collection_name": collection_name,
                "search_criteria": {
                    "where": where,
                    "where_document": where_document
                },
                "found_count": get_result["count"],
                "limit": limit,
                "offset": offset,
                "sample_documents": [],
                "timestamp": datetime.now().isoformat()
            }

            if results.get('documents'):
                for i, doc in enumerate(results['documents'][:5]):
                    if doc:
                        document_preview = doc
                        analysis["sample_documents"].append({
                            "index": i,
                            "id": results['ids'][i] if i < len(results.get('ids', [])) else None,
                            "document_preview": document_preview
                        })

            return ChromaDataValue(analysis)
        else:
            result = {
                "success": False,
                "error": get_result.get("error", "Search failed"),
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }
            return ChromaDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "collection_name": collection_name,
            "timestamp": datetime.now().isoformat()
        }
        return ChromaDataValue(result)

def test_connection_skill(context: Dict[str, Any]) -> ChromaDataValue:

    try:
        client: ChromaDBClientComponent = context.get('chroma_client')

        if not client:
            result = {"success": False, "error": "ChromaDB client not available"}
            return ChromaDataValue(result)

        is_connected = client.test_connection()

        result = {
            "success": True,
            "connected": is_connected,
            "client_type": "HTTP" if client.host else "Persistent" if client.persist_directory else "In-memory",
            "host": client.host,
            "port": client.port,
            "persist_directory": client.persist_directory,
            "timestamp": datetime.now().isoformat()
        }

        return ChromaDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "connected": False,
            "timestamp": datetime.now().isoformat()
        }
        return ChromaDataValue(result)
