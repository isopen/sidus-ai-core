from typing import Dict, Any
from datetime import datetime

class MilvusDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def create_collection_skill(context: Dict[str, Any]) -> MilvusDataValue:
    print("Starting create_collection_skill...")

    collection_name = context.get('collection_name', 'Documents')
    dimension = context.get('dimension', 384)
    metric_type = context.get('metric_type', 'COSINE')

    try:
        client = context.get('milvus_client')

        if not client:
            result = {"success": False, "error": "Milvus client not available"}
            return MilvusDataValue(result)

        try:
            response = client.create_collection(
                collection_name=collection_name,
                dimension=dimension,
                metric_type=metric_type
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "dimension": dimension,
                    "metric_type": metric_type,
                    "status": "created",
                    "summary": {
                        "metric_type": metric_type,
                        "dimension": dimension
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Collection created: {collection_name}")
                print(f"Dimension: {dimension}")
                print(f"Metric type: {metric_type}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Collection creation failed: {response.get('error')}")

            return MilvusDataValue(analysis_result)

        except Exception as e:
            print(f"Error creating collection: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to create collection: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return MilvusDataValue(analysis_result)

    except Exception as e:
        print(f"Error in create_collection_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MilvusDataValue(result)

def search_similar_skill(context: Dict[str, Any]) -> MilvusDataValue:
    print("Starting search_similar_skill...")

    collection_name = context.get('collection_name', 'Documents')
    data = context.get('data', [])
    limit = context.get('limit', 10)
    output_fields = context.get('output_fields', [])
    filter = context.get('filter')

    try:
        client = context.get('milvus_client')

        if not client:
            result = {"success": False, "error": "Milvus client not available"}
            return MilvusDataValue(result)

        if not data:
            result = {"success": False, "error": "Search data is required"}
            return MilvusDataValue(result)

        try:
            response = client.search_similar(
                collection_name=collection_name,
                data=data,
                limit=limit,
                output_fields=output_fields,
                filter=filter
            )

            if response.get('success'):
                results = response.get('results', [])

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "queries_count": len(data),
                    "results_per_query": limit,
                    "total_results": len(results),
                    "results": results,
                    "summary": {
                        "average_distance": 0,
                        "min_distance": float('inf'),
                        "max_distance": 0,
                        "unique_ids": set()
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    distances = []
                    for r in results:
                        distance = r.get('distance')
                        if distance is not None:
                            distances.append(distance)
                        analysis_result['summary']['unique_ids'].add(r.get('id'))

                    if distances:
                        analysis_result['summary']['average_distance'] = sum(distances) / len(distances)
                        analysis_result['summary']['min_distance'] = min(distances)
                        analysis_result['summary']['max_distance'] = max(distances)

                    analysis_result['summary']['unique_ids'] = list(analysis_result['summary']['unique_ids'])

                print(f"Vector search completed: Found {len(results)} total results")
                print(f"Collection: {collection_name}")
                print(f"Queries: {len(data)}")
                print(f"Limit per query: {limit}")

                if results and distances:
                    print(f"Average distance: {analysis_result['summary']['average_distance']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        id_str = str(result.get('id', ''))
                        distance = result.get('distance', 0)
                        entity = result.get('entity', {})
                        print(f"{i+1}. Distance: {distance:.4f} - ID: {id_str}")
                        if entity:
                            for key, value in list(entity.items())[:2]:
                                if isinstance(value, str) and len(value) > 50:
                                    print(f"   {key}: {value[:50]}...")
                                else:
                                    print(f"   {key}: {value}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Search failed: {response.get('error')}")

            return MilvusDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return MilvusDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_similar_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MilvusDataValue(result)

def store_document_skill(context: Dict[str, Any]) -> MilvusDataValue:
    print("Starting store_document_skill...")

    collection_name = context.get('collection_name', 'Documents')
    data = context.get('data', [])

    try:
        client = context.get('milvus_client')

        if not client:
            result = {"success": False, "error": "Milvus client not available"}
            return MilvusDataValue(result)

        if not data:
            result = {"success": False, "error": "Data is required"}
            return MilvusDataValue(result)

        try:
            response = client.store_document(
                collection_name=collection_name,
                data=data
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "insert_count": response.get('insert_count', 0),
                    "ids": response.get('ids', []),
                    "collection_name": collection_name,
                    "summary": {
                        "data_count": len(data),
                        "has_vectors": any('vector' in d for d in data),
                        "fields_in_first": list(data[0].keys()) if data else []
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Documents stored in collection: {collection_name}")
                print(f"Insert count: {analysis_result['insert_count']}")
                print(f"First ID: {analysis_result['ids'][0] if analysis_result['ids'] else 'N/A'}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to store document: {response.get('error')}")

            return MilvusDataValue(analysis_result)

        except Exception as e:
            print(f"Error storing document: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to store document: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return MilvusDataValue(analysis_result)

    except Exception as e:
        print(f"Error in store_document_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MilvusDataValue(result)

def batch_insert_skill(context: Dict[str, Any]) -> MilvusDataValue:
    print("Starting batch_insert_skill...")

    collection_name = context.get('collection_name', 'Documents')
    data = context.get('data', [])

    try:
        client = context.get('milvus_client')

        if not client:
            result = {"success": False, "error": "Milvus client not available"}
            return MilvusDataValue(result)

        if not data:
            result = {"success": False, "error": "Data is required"}
            return MilvusDataValue(result)

        try:
            response = client.batch_insert(
                collection_name=collection_name,
                data=data
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "insert_count": response.get('insert_count', 0),
                    "ids": response.get('ids', []),
                    "collection_name": collection_name,
                    "batch_size": len(data),
                    "summary": {
                        "data_count": len(data),
                        "has_vectors": any('vector' in d for d in data)
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Batch insert completed")
                print(f"Collection: {collection_name}")
                print(f"Batch size: {len(data)}")
                print(f"Inserted: {analysis_result['insert_count']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Batch insert failed: {response.get('error')}")

            return MilvusDataValue(analysis_result)

        except Exception as e:
            print(f"Error in batch insert: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform batch insert: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return MilvusDataValue(analysis_result)

    except Exception as e:
        print(f"Error in batch_insert_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MilvusDataValue(result)

def get_info_skill(context: Dict[str, Any]) -> MilvusDataValue:
    print("Starting get_info_skill...")

    collection_name = context.get('collection_name', 'Documents')

    try:
        client = context.get('milvus_client')

        if not client:
            result = {"success": False, "error": "Milvus client not available"}
            return MilvusDataValue(result)

        try:
            response = client.get_info(collection_name=collection_name)

            if response.get('success'):
                info = response.get('info', {})

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "info_summary": {
                        "description": info.get('description', ''),
                        "auto_id": info.get('auto_id', False)
                    },
                    "detailed_info": info,
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Collection info retrieved: {collection_name}")
                print(f"Description: {analysis_result['info_summary']['description']}")
                print(f"Auto ID: {analysis_result['info_summary']['auto_id']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to get collection info: {response.get('error')}")

            return MilvusDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting collection info: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get collection info: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return MilvusDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_info_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MilvusDataValue(result)

def delete_collection_skill(context: Dict[str, Any]) -> MilvusDataValue:
    print("Starting delete_collection_skill...")

    collection_name = context.get('collection_name', 'Documents')

    try:
        client = context.get('milvus_client')

        if not client:
            result = {"success": False, "error": "Milvus client not available"}
            return MilvusDataValue(result)

        try:
            response = client.delete_collection(collection_name=collection_name)

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "status": "deleted",
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Collection deleted: {collection_name}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to delete collection: {response.get('error')}")

            return MilvusDataValue(analysis_result)

        except Exception as e:
            print(f"Error deleting collection: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to delete collection: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return MilvusDataValue(analysis_result)

    except Exception as e:
        print(f"Error in delete_collection_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MilvusDataValue(result)

def list_collections_skill(context: Dict[str, Any]) -> MilvusDataValue:
    print("Starting list_collections_skill...")

    try:
        client = context.get('milvus_client')

        if not client:
            result = {"success": False, "error": "Milvus client not available"}
            return MilvusDataValue(result)

        try:
            response = client.list_collections()

            if response.get('success'):
                collections = response.get('collections', [])

                analysis_result = {
                    "success": True,
                    "collections_count": len(collections),
                    "collections": collections,
                    "summary": {
                        "collection_names": [],
                        "collections_with_auto_id": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                for collection in collections:
                    analysis_result['summary']['collection_names'].append(collection.get('name', ''))
                    if collection.get('auto_id'):
                        analysis_result['summary']['collections_with_auto_id'] += 1

                print(f"Found {len(collections)} collections")
                print(f"Collections with auto ID: {analysis_result['summary']['collections_with_auto_id']}")

                if collections:
                    print(f"First 5 collections:")
                    for i, collection in enumerate(collections[:5]):
                        print(f"{i+1}. {collection.get('name')} - Auto ID: {collection.get('auto_id', False)}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to list collections: {response.get('error')}")

            return MilvusDataValue(analysis_result)

        except Exception as e:
            print(f"Error listing collections: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to list collections: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return MilvusDataValue(analysis_result)

    except Exception as e:
        print(f"Error in list_collections_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MilvusDataValue(result)

def fetch_object_skill(context: Dict[str, Any]) -> MilvusDataValue:
    print("Starting fetch_object_skill...")

    collection_name = context.get('collection_name', 'Documents')
    ids = context.get('ids', [])
    output_fields = context.get('output_fields', [])

    try:
        client = context.get('milvus_client')

        if not client:
            result = {"success": False, "error": "Milvus client not available"}
            return MilvusDataValue(result)

        if not ids:
            result = {"success": False, "error": "IDs are required"}
            return MilvusDataValue(result)

        try:
            response = client.fetch_object(
                collection_name=collection_name,
                ids=ids,
                output_fields=output_fields
            )

            if response.get('success'):
                results = response.get('results', [])

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "ids_requested": ids,
                    "ids_found": response.get('ids_found', []),
                    "results": results,
                    "summary": {
                        "requested_count": len(ids),
                        "found_count": len(results),
                        "success_rate": len(results) / len(ids) if ids else 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Fetch completed: Found {len(results)} out of {len(ids)} requested")
                print(f"Collection: {collection_name}")
                print(f"Success rate: {analysis_result['summary']['success_rate']:.2%}")

                if results:
                    print("First 3 results:")
                    for i, result in enumerate(results[:3]):
                        print(f"{i+1}. ID: {result.get('id', 'N/A')}")
                        for key, value in list(result.items())[:3]:
                            if key != 'id':
                                print(f"   {key}: {value}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Fetch failed: {response.get('error')}")

            return MilvusDataValue(analysis_result)

        except Exception as e:
            print(f"Error fetching objects: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to fetch objects: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return MilvusDataValue(analysis_result)

    except Exception as e:
        print(f"Error in fetch_object_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MilvusDataValue(result)

def update_object_skill(context: Dict[str, Any]) -> MilvusDataValue:
    print("Starting update_object_skill...")

    collection_name = context.get('collection_name', 'Documents')
    data = context.get('data', [])

    try:
        client = context.get('milvus_client')

        if not client:
            result = {"success": False, "error": "Milvus client not available"}
            return MilvusDataValue(result)

        if not data:
            result = {"success": False, "error": "Data is required"}
            return MilvusDataValue(result)

        try:
            response = client.update_object(
                collection_name=collection_name,
                data=data
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "upsert_count": response.get('upsert_count', 0),
                    "ids": response.get('ids', []),
                    "collection_name": collection_name,
                    "summary": {
                        "data_count": len(data),
                        "fields_updated": list(data[0].keys()) if data else []
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Objects updated: {analysis_result['upsert_count']}")
                print(f"Collection: {collection_name}")
                print(f"First ID: {analysis_result['ids'][0] if analysis_result['ids'] else 'N/A'}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to update objects: {response.get('error')}")

            return MilvusDataValue(analysis_result)

        except Exception as e:
            print(f"Error updating objects: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to update objects: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return MilvusDataValue(analysis_result)

    except Exception as e:
        print(f"Error in update_object_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MilvusDataValue(result)

def delete_object_skill(context: Dict[str, Any]) -> MilvusDataValue:
    print("Starting delete_object_skill...")

    collection_name = context.get('collection_name', 'Documents')
    filter = context.get('filter', '')

    try:
        client = context.get('milvus_client')

        if not client:
            result = {"success": False, "error": "Milvus client not available"}
            return MilvusDataValue(result)

        if not filter:
            result = {"success": False, "error": "Filter is required"}
            return MilvusDataValue(result)

        try:
            response = client.delete_object(
                collection_name=collection_name,
                filter=filter
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "delete_count": response.get('delete_count', 0),
                    "collection_name": collection_name,
                    "summary": {
                        "filter": filter,
                        "successful_deletions": response.get('delete_count', 0)
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Objects deleted: {analysis_result['delete_count']}")
                print(f"Collection: {collection_name}")
                print(f"Filter: {filter}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to delete objects: {response.get('error')}")

            return MilvusDataValue(analysis_result)

        except Exception as e:
            print(f"Error deleting objects: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to delete objects: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return MilvusDataValue(analysis_result)

    except Exception as e:
        print(f"Error in delete_object_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MilvusDataValue(result)

def query_skill(context: Dict[str, Any]) -> MilvusDataValue:
    print("Starting query_skill...")

    collection_name = context.get('collection_name', 'Documents')
    filter = context.get('filter', '')
    output_fields = context.get('output_fields', [])
    limit = context.get('limit')
    offset = context.get('offset', 0)

    try:
        client = context.get('milvus_client')

        if not client:
            result = {"success": False, "error": "Milvus client not available"}
            return MilvusDataValue(result)

        if not filter:
            result = {"success": False, "error": "Filter is required"}
            return MilvusDataValue(result)

        try:
            response = client.query(
                collection_name=collection_name,
                filter=filter,
                output_fields=output_fields,
                limit=limit,
                offset=offset
            )

            if response.get('success'):
                results = response.get('results', [])

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "filter": filter,
                    "results_count": len(results),
                    "results": results,
                    "summary": {
                        "output_fields": output_fields,
                        "has_results": len(results) > 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Query completed: Found {len(results)} results")
                print(f"Collection: {collection_name}")
                print(f"Filter: {filter}")

                if results:
                    print("First 3 results:")
                    for i, result in enumerate(results[:3]):
                        print(f"{i+1}. ID: {result.get('id', 'N/A')}")
                        for key, value in list(result.items())[:3]:
                            if key != 'id':
                                if isinstance(value, str) and len(value) > 50:
                                    print(f"   {key}: {value[:50]}...")
                                else:
                                    print(f"   {key}: {value}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Query failed: {response.get('error')}")

            return MilvusDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing query: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform query: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return MilvusDataValue(analysis_result)

    except Exception as e:
        print(f"Error in query_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return MilvusDataValue(result)
