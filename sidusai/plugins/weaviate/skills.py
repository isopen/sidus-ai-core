from typing import Dict, Any
from datetime import datetime

class WeaviateDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def create_collection_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting create_collection_skill...")

    collection_name = context.get('collection_name', 'Documents')
    properties = context.get('properties', [])
    vectorizer = context.get('vectorizer', 'text2vec-openai')
    module_config = context.get('module_config', {})
    inverted_index_config = context.get('inverted_index_config', {})

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        if not properties:
            properties = [
                {
                    "name": "text",
                    "dataType": ["text"],
                    "description": "Document content",
                    "tokenization": "word"
                },
                {
                    "name": "metadata",
                    "dataType": ["text"],
                    "description": "Document metadata in JSON format"
                },
                {
                    "name": "timestamp",
                    "dataType": ["date"],
                    "description": "Document creation timestamp"
                }
            ]
            print(f"Using default properties: {[p['name'] for p in properties]}")

        try:
            response = client.create_collection(
                collection_name=collection_name,
                properties=properties,
                vectorizer=vectorizer,
                module_config=module_config,
                inverted_index_config=inverted_index_config
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "vectorizer": vectorizer,
                    "properties_count": len(properties),
                    "status": "created",
                    "summary": {
                        "property_names": [p.get('name') for p in properties],
                        "vectorizer_type": vectorizer,
                        "module_config_keys": list(module_config.keys())
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Collection created: {collection_name}")
                print(f"Vectorizer: {vectorizer}")
                print(f"Properties: {len(properties)}")
                print(f"Property names: {analysis_result['summary']['property_names']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Collection creation failed: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error creating collection: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to create collection: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in create_collection_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def store_document_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting store_document_skill...")

    collection_name = context.get('collection_name', 'Documents')
    properties = context.get('properties', {})
    vector = context.get('vector')
    named_vectors = context.get('named_vectors', {})
    uuid = context.get('uuid')

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        try:
            response = client.store_document(
                collection_name=collection_name,
                properties=properties,
                vector=vector,
                named_vectors=named_vectors,
                uuid=uuid
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "uuid": response.get('uuid'),
                    "collection_name": collection_name,
                    "properties_count": len(properties),
                    "has_vector": vector is not None or bool(named_vectors),
                    "summary": {
                        "property_keys": list(properties.keys()),
                        "named_vectors_count": len(named_vectors) if named_vectors else 0,
                        "vector_dimensions": len(vector) if vector else None
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Document stored in collection: {collection_name}")
                print(f"UUID: {analysis_result['uuid']}")
                print(f"Properties: {len(properties)}")
                print(f"Has vector: {analysis_result['has_vector']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to store document: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error storing document: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to store document: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in store_document_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def fetch_object_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting fetch_object_skill...")

    collection_name = context.get('collection_name', 'Documents')
    uuid = context.get('uuid')
    include_vector = context.get('include_vector', False)

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        if not uuid:
            result = {"success": False, "error": "UUID is required"}
            return WeaviateDataValue(result)

        try:
            response = client.fetch_object(
                collection_name=collection_name,
                uuid=uuid,
                include_vector=include_vector
            )

            if response.get('success'):
                obj = response.get('object', {})
                analysis_result = {
                    "success": True,
                    "uuid": uuid,
                    "collection_name": collection_name,
                    "object": obj,
                    "summary": {
                        "has_properties": bool(obj.get('properties')),
                        "properties_count": len(obj.get('properties', {})),
                        "has_vector": include_vector and 'vector' in obj,
                        "created": obj.get('created'),
                        "updated": obj.get('updated')
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Object fetched: {uuid}")
                print(f"Collection: {collection_name}")
                print(f"Has properties: {analysis_result['summary']['has_properties']}")
                print(f"Created: {analysis_result['summary']['created']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "uuid": uuid,
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to fetch object: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error fetching object: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to fetch object: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in fetch_object_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def search_similar_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting search_similar_skill...")

    collection_name = context.get('collection_name', 'Documents')
    query_vector = context.get('query_vector', [])
    limit = context.get('limit', 10)
    offset = context.get('offset', 0)
    target_vector = context.get('target_vector')
    filters = context.get('filters', {})

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        if not query_vector:
            result = {"success": False, "error": "Query vector is required"}
            return WeaviateDataValue(result)

        try:
            response = client.search_similar(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                offset=offset,
                target_vector=target_vector,
                filters=filters
            )

            if response.get('success'):
                results = response.get('results', [])

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "query_dimensions": len(query_vector),
                    "results_count": len(results),
                    "results": results,
                    "summary": {
                        "total_matches": len(results),
                        "average_distance": 0,
                        "min_distance": float('inf'),
                        "max_distance": 0,
                        "unique_uuids": set()
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    distances = []
                    for r in results:
                        metadata = r.get('metadata', {})
                        distance = metadata.get('distance')
                        if distance is not None:
                            distances.append(distance)
                        analysis_result['summary']['unique_uuids'].add(r.get('uuid'))

                    if distances:
                        analysis_result['summary']['average_distance'] = sum(distances) / len(distances)
                        analysis_result['summary']['min_distance'] = min(distances)
                        analysis_result['summary']['max_distance'] = max(distances)

                    analysis_result['summary']['unique_uuids'] = list(analysis_result['summary']['unique_uuids'])

                print(f"Vector search completed: Found {len(results)} results")
                print(f"Collection: {collection_name}")
                print(f"Query dimensions: {len(query_vector)}")

                if results and distances:
                    print(f"Average distance: {analysis_result['summary']['average_distance']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        uuid_short = result.get('uuid') if result.get('uuid') else 'N/A'
                        properties = result.get('properties', {})
                        text_value = properties.get('text', '')
                        if isinstance(text_value, str):
                            text_preview = text_value
                        else:
                            text_preview = str(text_value)

                        distance = result.get('metadata', {}).get('distance')
                        if distance is not None:
                            distance_str = f"{distance:.4f}"
                        else:
                            distance_str = "N/A"

                        print(f"{i+1}. Distance: {distance_str} - UUID: {uuid_short}")
                        print(f"   Preview: {text_preview}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Search failed: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing search: {e}")
            import traceback
            traceback.print_exc()
            analysis_result = {
                "success": False,
                "error": f"Failed to perform search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_similar_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def near_text_search_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting near_text_search_skill...")

    collection_name = context.get('collection_name', 'Documents')
    query = context.get('query', '')
    limit = context.get('limit', 10)
    offset = context.get('offset', 0)
    target_vector = context.get('target_vector')
    filters = context.get('filters', {})
    certainty = context.get('certainty')
    distance = context.get('distance')

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        if not query:
            result = {"success": False, "error": "Query text is required"}
            return WeaviateDataValue(result)

        try:
            response = client.near_text_search(
                collection_name=collection_name,
                query=query,
                limit=limit,
                offset=offset,
                target_vector=target_vector,
                filters=filters,
                certainty=certainty,
                distance=distance
            )

            if response.get('success'):
                results = response.get('results', [])

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "query": query,
                    "results_count": len(results),
                    "results": results,
                    "summary": {
                        "total_matches": len(results),
                        "average_certainty": 0,
                        "min_certainty": float('inf'),
                        "max_certainty": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    certainties = []
                    for r in results:
                        metadata = r.get('metadata', {})
                        cert = metadata.get('certainty')
                        if cert is not None:
                            certainties.append(cert)

                    if certainties:
                        analysis_result['summary']['average_certainty'] = sum(certainties) / len(certainties)
                        analysis_result['summary']['min_certainty'] = min(certainties)
                        analysis_result['summary']['max_certainty'] = max(certainties)

                print(f"Near text search completed: Found {len(results)} results")
                print(f"Collection: {collection_name}")
                print(f"Query: '{query}'")

                if results and certainties:
                    print(f"Average certainty: {analysis_result['summary']['average_certainty']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        uuid_short = result.get('uuid') if result.get('uuid') else 'N/A'
                        properties = result.get('properties', {})
                        text_value = properties.get('text', '')
                        if isinstance(text_value, str):
                            text_preview = text_value
                        else:
                            text_preview = str(text_value)

                        print(f"{i+1}. UUID: {uuid_short}")
                        print(f"   Preview: {text_preview}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Near text search failed: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing near text search: {e}")
            import traceback
            traceback.print_exc()
            analysis_result = {
                "success": False,
                "error": f"Failed to perform near text search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in near_text_search_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def hybrid_search_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting hybrid_search_skill...")

    collection_name = context.get('collection_name', 'Documents')
    query = context.get('query', '')
    limit = context.get('limit', 10)
    offset = context.get('offset', 0)
    target_vector = context.get('target_vector')
    filters = context.get('filters', {})
    alpha = context.get('alpha', 0.5)
    fusion_type = context.get('fusion_type')

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        if not query:
            result = {"success": False, "error": "Query text is required"}
            return WeaviateDataValue(result)

        try:
            response = client.hybrid_search(
                collection_name=collection_name,
                query=query,
                limit=limit,
                offset=offset,
                target_vector=target_vector,
                filters=filters,
                alpha=alpha,
                fusion_type=fusion_type
            )

            if response.get('success'):
                results = response.get('results', [])

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "query": query,
                    "alpha": alpha,
                    "fusion_type": fusion_type,
                    "results_count": len(results),
                    "results": results,
                    "summary": {
                        "total_matches": len(results),
                        "average_score": 0,
                        "min_score": float('inf'),
                        "max_score": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    scores = []
                    for r in results:
                        metadata = r.get('metadata', {})
                        score = metadata.get('score')
                        if score is not None:
                            scores.append(score)

                    if scores:
                        analysis_result['summary']['average_score'] = sum(scores) / len(scores)
                        analysis_result['summary']['min_score'] = min(scores)
                        analysis_result['summary']['max_score'] = max(scores)

                print(f"Hybrid search completed: Found {len(results)} results")
                print(f"Collection: {collection_name}")
                print(f"Query: '{query}'")
                print(f"Alpha: {alpha}, Fusion type: {fusion_type}")

                if results and scores:
                    print(f"Average score: {analysis_result['summary']['average_score']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        uuid_short = result.get('uuid') if result.get('uuid') else 'N/A'
                        properties = result.get('properties', {})
                        text_value = properties.get('text', '')
                        if isinstance(text_value, str):
                            text_preview = text_value
                        else:
                            text_preview = str(text_value)

                        score_val = result.get('metadata', {}).get('score')
                        if score_val is not None:
                            score_str = f"{score_val:.4f}"
                        else:
                            score_str = "N/A"

                        print(f"{i+1}. Score: {score_str} - UUID: {uuid_short}")
                        print(f"   Preview: {text_preview}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Hybrid search failed: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing hybrid search: {e}")
            import traceback
            traceback.print_exc()
            analysis_result = {
                "success": False,
                "error": f"Failed to perform hybrid search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in hybrid_search_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def bm25_search_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting bm25_search_skill...")

    collection_name = context.get('collection_name', 'Documents')
    query = context.get('query', '')
    limit = context.get('limit', 10)
    offset = context.get('offset', 0)
    filters = context.get('filters', {})
    operator = context.get('operator', 'OR')
    minimum_match = context.get('minimum_match', 1)

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        if not query:
            result = {"success": False, "error": "Query text is required"}
            return WeaviateDataValue(result)

        try:
            response = client.bm25_search(
                collection_name=collection_name,
                query=query,
                limit=limit,
                offset=offset,
                filters=filters,
                operator=operator,
                minimum_match=minimum_match
            )

            if response.get('success'):
                results = response.get('results', [])

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "query": query,
                    "operator": operator,
                    "minimum_match": minimum_match,
                    "results_count": len(results),
                    "results": results,
                    "summary": {
                        "total_matches": len(results)
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"BM25 search completed: Found {len(results)} results")
                print(f"Collection: {collection_name}")
                print(f"Query: '{query}'")
                print(f"Operator: {operator}, Minimum match: {minimum_match}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        uuid_short = result.get('uuid')
                        properties = result.get('properties', {})
                        text_preview = str(properties.get('text', '')) if str(properties.get('text', '')) else str(properties.get('text', ''))
                        print(f"{i+1}. UUID: {uuid_short}")
                        print(f"   Preview: {text_preview}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"BM25 search failed: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing BM25 search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform BM25 search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in bm25_search_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def update_object_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting update_object_skill...")

    collection_name = context.get('collection_name', 'Documents')
    uuid = context.get('uuid')
    properties = context.get('properties', {})
    vector = context.get('vector')
    named_vectors = context.get('named_vectors', {})

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        if not uuid:
            result = {"success": False, "error": "UUID is required"}
            return WeaviateDataValue(result)

        try:
            response = client.update_object(
                collection_name=collection_name,
                uuid=uuid,
                properties=properties,
                vector=vector,
                named_vectors=named_vectors
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "uuid": uuid,
                    "collection_name": collection_name,
                    "updated_properties": list(properties.keys()),
                    "has_vector_update": vector is not None or bool(named_vectors),
                    "summary": {
                        "properties_updated": len(properties),
                        "vector_updated": vector is not None or bool(named_vectors)
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Object updated: {uuid}")
                print(f"Collection: {collection_name}")
                print(f"Properties updated: {analysis_result['updated_properties']}")
                print(f"Vector updated: {analysis_result['has_vector_update']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "uuid": uuid,
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to update object: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error updating object: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to update object: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in update_object_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def delete_object_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting delete_object_skill...")

    collection_name = context.get('collection_name', 'Documents')
    uuid = context.get('uuid')
    filters = context.get('filters', {})

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        try:
            response = client.delete_object(
                collection_name=collection_name,
                uuid=uuid,
                filters=filters
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "action": response.get('action'),
                    "deleted_count": response.get('deleted_count', 0),
                    "failed_count": response.get('failed_count', 0),
                    "summary": {
                        "method": "by_uuid" if uuid else "by_filter",
                        "successful_deletions": response.get('deleted_count', 0)
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Object deletion completed")
                print(f"Collection: {collection_name}")
                print(f"Method: {analysis_result['summary']['method']}")
                print(f"Deleted count: {analysis_result['deleted_count']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to delete object: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error deleting object: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to delete object: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in delete_object_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def batch_insert_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting batch_insert_skill...")

    collection_name = context.get('collection_name', 'Documents')
    objects = context.get('objects', [])
    batch_size = context.get('batch_size', 100)
    num_workers = context.get('num_workers', 1)
    dynamic = context.get('dynamic', False)
    consistency_level = context.get('consistency_level', 'QUORUM')

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        if not objects:
            result = {"success": False, "error": "Objects list is required"}
            return WeaviateDataValue(result)

        try:
            response = client.batch_insert(
                collection_name=collection_name,
                objects=objects,
                batch_size=batch_size,
                num_workers=num_workers,
                dynamic=dynamic,
                consistency_level=consistency_level
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "total_count": len(objects),
                    "batch_size": batch_size,
                    "dynamic": dynamic,
                    "consistency_level": consistency_level,
                    "summary": {
                        "objects_with_vectors": sum(1 for obj in objects if obj.get('vector') or obj.get('named_vectors')),
                        "objects_with_uuids": sum(1 for obj in objects if obj.get('uuid'))
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Batch insert completed")
                print(f"Collection: {collection_name}")
                print(f"Total objects: {len(objects)}")
                print(f"Batch size: {batch_size}")
                print(f"Dynamic: {dynamic}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "total_count": len(objects),
                    "failed_count": response.get('failed_count', 0),
                    "success_count": response.get('success_count', 0),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Batch insert failed: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error in batch insert: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform batch insert: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in batch_insert_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def get_info_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting get_info_skill...")

    collection_name = context.get('collection_name', 'Documents')

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        try:
            response = client.get_info(collection_name=collection_name)

            if response.get('success'):
                info = response.get('info', {})
                stats = response.get('stats', {})

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "info_summary": {
                        "vectorizer": info.get('vectorizer'),
                        "vector_index_type": info.get('vector_index_type'),
                        "properties_count": len(info.get('properties', [])),
                        "total_objects": stats.get('total_count', 0)
                    },
                    "detailed_info": info,
                    "stats": stats,
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Collection info retrieved: {collection_name}")
                print(f"Vectorizer: {analysis_result['info_summary']['vectorizer']}")
                print(f"Properties: {analysis_result['info_summary']['properties_count']}")
                print(f"Total objects: {analysis_result['info_summary']['total_objects']}")

                if info.get('properties'):
                    print("Properties:")
                    for prop in info.get('properties', [])[:5]:
                        print(f"  - {prop.get('name')} ({prop.get('data_type')})")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to get collection info: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting collection info: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get collection info: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_info_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def delete_collection_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting delete_collection_skill...")

    collection_name = context.get('collection_name', 'Documents')

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

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

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error deleting collection: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to delete collection: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in delete_collection_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def list_collections_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting list_collections_skill...")

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        try:
            response = client.list_collections()

            if response.get('success'):
                collections = response.get('collections', [])

                analysis_result = {
                    "success": True,
                    "collections_count": len(collections),
                    "collections": collections,
                    "summary": {
                        "vectorized_collections": 0,
                        "non_vectorized_collections": 0,
                        "collection_names": [],
                        "total_objects": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                for collection in collections:
                    analysis_result['summary']['collection_names'].append(collection.get('name', ''))
                    if collection.get('vectorizer'):
                        analysis_result['summary']['vectorized_collections'] += 1
                    else:
                        analysis_result['summary']['non_vectorized_collections'] += 1
                    analysis_result['summary']['total_objects'] += collection.get('total_objects', 0)

                print(f"Found {len(collections)} collections")
                print(f"Vectorized collections: {analysis_result['summary']['vectorized_collections']}")
                print(f"Non-vectorized collections: {analysis_result['summary']['non_vectorized_collections']}")
                print(f"Total objects: {analysis_result['summary']['total_objects']}")

                if collections:
                    print(f"First 5 collections:")
                    for i, collection in enumerate(collections[:5]):
                        print(f"{i+1}. {collection.get('name')} - Objects: {collection.get('total_objects', 0)} - Vectorizer1: {collection.get('vectorizer', 'None')}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to list collections: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error listing collections: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to list collections: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in list_collections_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def aggregate_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting aggregate_skill...")

    collection_name = context.get('collection_name', 'Documents')
    fields = context.get('fields', [])
    group_by = context.get('group_by', [])
    filters = context.get('filters', {})
    limit = context.get('limit')

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        try:
            response = client.aggregate(
                collection_name=collection_name,
                fields=fields,
                group_by=group_by,
                filters=filters,
                limit=limit
            )

            if response.get('success'):
                aggregation = response.get('aggregation', {})

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "aggregation": aggregation,
                    "summary": {
                        "total_count": aggregation.get('total_count', 0),
                        "fields_aggregated": len(fields),
                        "group_by_fields": len(group_by)
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Aggregation completed")
                print(f"Collection: {collection_name}")
                print(f"Total count: {analysis_result['summary']['total_count']}")
                print(f"Fields aggregated: {analysis_result['summary']['fields_aggregated']}")
                print(f"Group by fields: {analysis_result['summary']['group_by_fields']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Aggregation failed: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing aggregation: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform aggregation: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in aggregate_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def near_vector_search_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting near_vector_search_skill...")

    collection_name = context.get('collection_name', 'Documents')
    query_vector = context.get('query_vector', [])
    limit = context.get('limit', 10)
    offset = context.get('offset', 0)
    target_vector = context.get('target_vector', 'default')
    filters = context.get('filters', {})

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        if not query_vector:
            result = {"success": False, "error": "Query vector is required"}
            return WeaviateDataValue(result)

        try:
            response = client.search_similar(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                offset=offset,
                target_vector=target_vector,
                filters=filters
            )

            if response.get('success'):
                results = response.get('results', [])

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "query_dimensions": len(query_vector),
                    "results_count": len(results),
                    "results": results,
                    "summary": {
                        "total_matches": len(results),
                        "average_distance": 0,
                        "min_distance": float('inf'),
                        "max_distance": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    distances = []
                    for r in results:
                        metadata = r.get('metadata', {})
                        distance = metadata.get('distance')
                        if distance is not None:
                            distances.append(distance)

                    if distances:
                        analysis_result['summary']['average_distance'] = sum(distances) / len(distances)
                        analysis_result['summary']['min_distance'] = min(distances)
                        analysis_result['summary']['max_distance'] = max(distances)

                print(f"Near vector search completed: Found {len(results)} results")
                print(f"Collection: {collection_name}")
                print(f"Query dimensions: {len(query_vector)}")

                if results and distances:
                    print(f"Average distance: {analysis_result['summary']['average_distance']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        uuid_short = result.get('uuid')
                        properties = result.get('properties', {})
                        text_preview = str(properties.get('text', '')) if str(properties.get('text', '')) else str(properties.get('text', ''))
                        distance = result.get('metadata', {}).get('distance', 0)
                        print(f"{i+1}. Distance: {distance:.4f} - UUID: {uuid_short}")
                        print(f"   Preview: {text_preview}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Near vector search failed: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing near vector search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform near vector search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in near_vector_search_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)

def near_image_search_skill(context: Dict[str, Any]) -> WeaviateDataValue:
    print("Starting near_image_search_skill...")

    collection_name = context.get('collection_name', 'Documents')
    image_path = context.get('image_path')
    base64_image = context.get('base64_image')
    limit = context.get('limit', 10)
    offset = context.get('offset', 0)
    target_vector = context.get('target_vector', 'default')
    filters = context.get('filters', {})

    try:
        client = context.get('weaviate_client')

        if not client:
            result = {"success": False, "error": "Weaviate client not available"}
            return WeaviateDataValue(result)

        if not image_path and not base64_image:
            result = {"success": False, "error": "Either image_path or base64_image must be provided"}
            return WeaviateDataValue(result)

        try:
            response = client.near_image_search(
                collection_name=collection_name,
                image_path=image_path,
                base64_image=base64_image,
                limit=limit,
                offset=offset,
                target_vector=target_vector,
                filters=filters
            )

            if response.get('success'):
                results = response.get('results', [])

                analysis_result = {
                    "success": True,
                    "collection_name": collection_name,
                    "image_source": "file_path" if image_path else "base64",
                    "results_count": len(results),
                    "results": results,
                    "summary": {
                        "total_matches": len(results),
                        "average_distance": 0,
                        "min_distance": float('inf'),
                        "max_distance": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    distances = []
                    for r in results:
                        metadata = r.get('metadata', {})
                        distance = metadata.get('distance')
                        if distance is not None:
                            distances.append(distance)

                    if distances:
                        analysis_result['summary']['average_distance'] = sum(distances) / len(distances)
                        analysis_result['summary']['min_distance'] = min(distances)
                        analysis_result['summary']['max_distance'] = max(distances)

                print(f"Near image search completed: Found {len(results)} results")
                print(f"Collection: {collection_name}")
                print(f"Image source: {analysis_result['image_source']}")

                if results and distances:
                    print(f"Average distance: {analysis_result['summary']['average_distance']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        uuid_short = result.get('uuid')
                        properties = result.get('properties', {})
                        distance = result.get('metadata', {}).get('distance', 0)
                        print(f"{i+1}. Distance: {distance:.4f} - UUID: {uuid_short}")
                        if properties:
                            for key, value in list(properties.items())[:2]:
                                print(f"   {key}: {value}" if isinstance(value, str) else f"   {key}: {value}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "collection_name": collection_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Near image search failed: {response.get('error')}")

            return WeaviateDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing near image search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform near image search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return WeaviateDataValue(analysis_result)

    except Exception as e:
        print(f"Error in near_image_search_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return WeaviateDataValue(result)
