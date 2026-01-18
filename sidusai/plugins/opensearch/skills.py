from typing import Dict, Any
from datetime import datetime

class OpenSearchDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def create_index_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting create_index_skill...")

    index_name = context.get('index_name', 'documents')
    mappings = context.get('mappings', {})
    settings = context.get('settings', {})
    knn_settings = context.get('knn_settings', {})

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        if not mappings:
            mappings = {
                "properties": {
                    "text": {"type": "text"},
                    "metadata": {"type": "object"},
                    "timestamp": {"type": "date"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": 768,
                        "method": {
                            "name": "hnsw",
                            "space_type": "l2",
                            "engine": "faiss",
                            "parameters": {
                                "ef_construction": 128,
                                "m": 16
                            }
                        }
                    }
                }
            }
            print(f"Using default mappings with embedding field")

        try:
            response = client.create_index(
                index_name=index_name,
                mappings=mappings,
                settings=settings,
                knn_settings=knn_settings
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "acknowledged": response.get('acknowledged', False),
                    "status": "created",
                    "summary": {
                        "has_mappings": bool(mappings),
                        "has_settings": bool(settings),
                        "has_knn_settings": bool(knn_settings),
                        "properties_count": len(mappings.get('properties', {})) if isinstance(mappings, dict) else 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Index created: {index_name}")
                print(f"Acknowledged: {analysis_result['acknowledged']}")
                print(f"Properties count: {analysis_result['summary']['properties_count']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Index creation failed: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error creating index: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to create index: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in create_index_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def create_knn_field_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting create_knn_field_skill...")

    index_name = context.get('index_name', 'documents')
    field_name = context.get('field_name', 'embedding')
    dimension = context.get('dimension', 768)
    method = context.get('method', 'hnsw')
    engine = context.get('engine', 'faiss')
    space_type = context.get('space_type', 'l2')
    parameters = context.get('parameters', {})

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        try:
            response = client.create_knn_field(
                index_name=index_name,
                field_name=field_name,
                dimension=dimension,
                method=method,
                engine=engine,
                space_type=space_type,
                parameters=parameters
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "field_name": field_name,
                    "dimension": dimension,
                    "method": method,
                    "engine": engine,
                    "space_type": space_type,
                    "acknowledged": response.get('acknowledged', False),
                    "summary": {
                        "has_parameters": bool(parameters),
                        "parameters_keys": list(parameters.keys())
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"k-NN field created: {field_name} in index {index_name}")
                print(f"Dimension: {dimension}")
                print(f"Method: {method}, Engine: {engine}")
                print(f"Space type: {space_type}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "field_name": field_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"k-NN field creation failed: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error creating k-NN field: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to create k-NN field: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in create_knn_field_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def index_document_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting index_document_skill...")

    index_name = context.get('index_name', 'documents')
    document = context.get('document', {})
    document_id = context.get('document_id')

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        try:
            response = client.index_document(
                index_name=index_name,
                document=document,
                document_id=document_id
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "document_id": response.get('document_id'),
                    "result": response.get('result'),
                    "version": response.get('version'),
                    "summary": {
                        "fields_count": len(document),
                        "has_vector": 'embedding' in document or any('vector' in key.lower() for key in document.keys()),
                        "has_text": 'text' in document or any('content' in key.lower() for key in document.keys())
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Document indexed in: {index_name}")
                print(f"Document ID: {analysis_result['document_id']}")
                print(f"Result: {analysis_result['result']}")
                print(f"Fields count: {analysis_result['summary']['fields_count']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to index document: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error indexing document: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to index document: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in index_document_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def get_document_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting get_document_skill...")

    index_name = context.get('index_name', 'documents')
    document_id = context.get('document_id')

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        if not document_id:
            result = {"success": False, "error": "Document ID is required"}
            return OpenSearchDataValue(result)

        try:
            response = client.get_document(
                index_name=index_name,
                document_id=document_id
            )

            if response.get('success'):
                source = response.get('source', {})
                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "document_id": document_id,
                    "found": response.get('found', False),
                    "source": source,
                    "version": response.get('version'),
                    "summary": {
                        "fields_count": len(source),
                        "has_vector": 'embedding' in source or any('vector' in key.lower() for key in source.keys()),
                        "has_text": 'text' in source or any('content' in key.lower() for key in source.keys())
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Document retrieved: {document_id}")
                print(f"Found: {analysis_result['found']}")
                print(f"Fields count: {analysis_result['summary']['fields_count']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "document_id": document_id,
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to get document: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting document: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get document: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_document_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def search_knn_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting search_knn_skill...")

    index_name = context.get('index_name', 'documents')
    vector_field = context.get('vector_field', 'embedding')
    vector = context.get('vector', [])
    k = context.get('k', 10)
    max_distance = context.get('max_distance')
    min_score = context.get('min_score')
    filter_query = context.get('filter_query', {})
    method_parameters = context.get('method_parameters', {})
    rescore_params = context.get('rescore_params', {})

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        if not vector:
            result = {"success": False, "error": "Query vector is required"}
            return OpenSearchDataValue(result)

        try:
            response = client.search_knn(
                index_name=index_name,
                vector_field=vector_field,
                vector=vector,
                k=k,
                max_distance=max_distance,
                min_score=min_score,
                filter_query=filter_query,
                method_parameters=method_parameters,
                rescore_params=rescore_params
            )

            if response.get('success'):
                results = response.get('results', [])
                total_hits = response.get('total_hits', 0)

                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "vector_field": vector_field,
                    "query_dimensions": len(vector),
                    "total_hits": total_hits,
                    "results_count": len(results),
                    "results": results,
                    "took_ms": response.get('took', 0),
                    "summary": {
                        "search_type": "k-NN",
                        "search_params": {
                            "k": k,
                            "max_distance": max_distance,
                            "min_score": min_score,
                            "has_filter": bool(filter_query),
                            "has_method_params": bool(method_parameters),
                            "has_rescore": bool(rescore_params)
                        },
                        "average_score": 0,
                        "min_score": float('inf'),
                        "max_score": 0,
                        "unique_ids": set()
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    scores = []
                    for r in results:
                        score = r.get('_score')
                        if score is not None:
                            scores.append(score)
                        analysis_result['summary']['unique_ids'].add(r.get('_id'))

                    if scores:
                        analysis_result['summary']['average_score'] = sum(scores) / len(scores)
                        analysis_result['summary']['min_score'] = min(scores)
                        analysis_result['summary']['max_score'] = max(scores)

                    analysis_result['summary']['unique_ids'] = list(analysis_result['summary']['unique_ids'])

                print(f"k-NN search completed: Found {total_hits} total, showing {len(results)} results")
                print(f"Index: {index_name}")
                print(f"Vector field: {vector_field}")
                print(f"Query dimensions: {len(vector)}")

                if results and scores:
                    print(f"Average score: {analysis_result['summary']['average_score']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        doc_id = result.get('_id')
                        source = result.get('_source', {})
                        text_content = str(source.get('text', ''))
                        score = result.get('_score', 0)
                        print(f"{i+1}. Score: {score:.4f} - ID: {doc_id}")
                        if text_content:
                            print(f"   Preview: {text_content}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"k-NN search failed: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing k-NN search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform k-NN search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_knn_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def search_neural_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting search_neural_skill...")

    index_name = context.get('index_name', 'documents')
    vector_field = context.get('vector_field', 'embedding')
    query_text = context.get('query_text')
    query_image = context.get('query_image')
    model_id = context.get('model_id')
    k = context.get('k', 10)
    max_distance = context.get('max_distance')
    min_score = context.get('min_score')
    filter_query = context.get('filter_query', {})
    method_parameters = context.get('method_parameters', {})
    rescore_params = context.get('rescore_params', {})
    semantic_field_search_analyzer = context.get('semantic_field_search_analyzer')

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        if not query_text and not query_image:
            result = {"success": False, "error": "Either query_text or query_image is required"}
            return OpenSearchDataValue(result)

        try:
            response = client.search_neural(
                index_name=index_name,
                vector_field=vector_field,
                query_text=query_text,
                query_image=query_image,
                model_id=model_id,
                k=k,
                max_distance=max_distance,
                min_score=min_score,
                filter_query=filter_query,
                method_parameters=method_parameters,
                rescore_params=rescore_params,
                semantic_field_search_analyzer=semantic_field_search_analyzer
            )

            if response.get('success'):
                results = response.get('results', [])
                total_hits = response.get('total_hits', 0)

                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "vector_field": vector_field,
                    "query_text": query_text,
                    "query_image": query_image is not None,
                    "model_id": model_id,
                    "total_hits": total_hits,
                    "results_count": len(results),
                    "results": results,
                    "took_ms": response.get('took', 0),
                    "summary": {
                        "search_type": "neural",
                        "search_params": {
                            "k": k,
                            "max_distance": max_distance,
                            "min_score": min_score,
                            "has_filter": bool(filter_query),
                            "has_method_params": bool(method_parameters),
                            "has_rescore": bool(rescore_params),
                            "semantic_analyzer": semantic_field_search_analyzer
                        },
                        "average_score": 0,
                        "min_score": float('inf'),
                        "max_score": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    scores = []
                    for r in results:
                        score = r.get('_score')
                        if score is not None:
                            scores.append(score)

                    if scores:
                        analysis_result['summary']['average_score'] = sum(scores) / len(scores)
                        analysis_result['summary']['min_score'] = min(scores)
                        analysis_result['summary']['max_score'] = max(scores)

                print(f"Neural search completed: Found {total_hits} total, showing {len(results)} results")
                print(f"Index: {index_name}")
                print(f"Vector field: {vector_field}")
                if query_text:
                    print(f"Query text: '{query_text}'")
                if query_image:
                    print(f"Query image: Provided (base64)")
                if model_id:
                    print(f"Model ID: {model_id}")

                if results and scores:
                    print(f"Average score: {analysis_result['summary']['average_score']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        doc_id = result.get('_id')
                        source = result.get('_source', {})
                        text_content = str(source.get('text', ''))
                        score = result.get('_score', 0)
                        print(f"{i+1}. Score: {score:.4f} - ID: {doc_id}")
                        if text_content:
                            print(f"   Preview: {text_content}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Neural search failed: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing neural search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform neural search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_neural_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def search_hybrid_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting search_hybrid_skill...")

    index_name = context.get('index_name', 'documents')
    knn_query = context.get('knn_query', {})
    text_query = context.get('text_query', {})
    neural_query = context.get('neural_query', {})
    boost_weights = context.get('boost_weights', {})

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        if not knn_query and not text_query and not neural_query:
            result = {"success": False, "error": "At least one query (knn, text, or neural) is required"}
            return OpenSearchDataValue(result)

        try:
            response = client.search_hybrid(
                index_name=index_name,
                knn_query=knn_query,
                text_query=text_query,
                neural_query=neural_query,
                boost_weights=boost_weights
            )

            if response.get('success'):
                results = response.get('results', [])
                total_hits = response.get('total_hits', 0)

                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "query_type": "hybrid",
                    "total_hits": total_hits,
                    "results_count": len(results),
                    "results": results,
                    "took_ms": response.get('took', 0),
                    "summary": {
                        "has_knn": bool(knn_query),
                        "has_text": bool(text_query),
                        "has_neural": bool(neural_query),
                        "boost_weights": boost_weights,
                        "average_score": 0,
                        "min_score": float('inf'),
                        "max_score": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    scores = []
                    for r in results:
                        score = r.get('_score')
                        if score is not None:
                            scores.append(score)

                    if scores:
                        analysis_result['summary']['average_score'] = sum(scores) / len(scores)
                        analysis_result['summary']['min_score'] = min(scores)
                        analysis_result['summary']['max_score'] = max(scores)

                print(f"Hybrid search completed: Found {total_hits} total, showing {len(results)} results")
                print(f"Index: {index_name}")
                print(f"Has k-NN: {analysis_result['summary']['has_knn']}")
                print(f"Has text: {analysis_result['summary']['has_text']}")
                print(f"Has neural: {analysis_result['summary']['has_neural']}")

                if results and scores:
                    print(f"Average score: {analysis_result['summary']['average_score']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        doc_id = result.get('_id')
                        source = result.get('_source', {})
                        text_content = str(source.get('text', ''))
                        score = result.get('_score', 0)
                        print(f"{i+1}. Score: {score:.4f} - ID: {doc_id}")
                        if text_content:
                            print(f"   Preview: {text_content}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Hybrid search failed: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing hybrid search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform hybrid search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_hybrid_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def search_text_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting search_text_skill...")

    index_name = context.get('index_name', 'documents')
    query = context.get('query', {})
    size = context.get('size', 10)
    from_ = context.get('from_', 0)

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        if not query:
            result = {"success": False, "error": "Query is required"}
            return OpenSearchDataValue(result)

        try:
            response = client.search_text(
                index_name=index_name,
                query=query,
                size=size,
                from_=from_
            )

            if response.get('success'):
                results = response.get('results', [])
                total_hits = response.get('total_hits', 0)

                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "query_type": "text",
                    "total_hits": total_hits,
                    "results_count": len(results),
                    "results": results,
                    "took_ms": response.get('took', 0),
                    "summary": {
                        "query_keys": list(query.keys()),
                        "size": size,
                        "from": from_,
                        "average_score": 0,
                        "min_score": float('inf'),
                        "max_score": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    scores = []
                    for r in results:
                        score = r.get('_score')
                        if score is not None:
                            scores.append(score)

                    if scores:
                        analysis_result['summary']['average_score'] = sum(scores) / len(scores)
                        analysis_result['summary']['min_score'] = min(scores)
                        analysis_result['summary']['max_score'] = max(scores)

                print(f"Text search completed: Found {total_hits} total, showing {len(results)} results")
                print(f"Index: {index_name}")
                print(f"Query type: {analysis_result['summary']['query_keys']}")

                if results and scores:
                    print(f"Average score: {analysis_result['summary']['average_score']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        doc_id = result.get('_id')
                        source = result.get('_source', {})
                        text_content = str(source.get('text', ''))
                        score = result.get('_score', 0)
                        print(f"{i+1}. Score: {score:.4f} - ID: {doc_id}")
                        if text_content:
                            print(f"   Preview: {text_content}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Text search failed: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing text search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform text search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_text_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def search_image_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting search_image_skill...")

    index_name = context.get('index_name', 'documents')
    vector_field = context.get('vector_field', 'embedding')
    image_path = context.get('image_path')
    base64_image = context.get('base64_image')
    model_id = context.get('model_id')
    k = context.get('k', 10)

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        if not image_path and not base64_image:
            result = {"success": False, "error": "Either image_path or base64_image must be provided"}
            return OpenSearchDataValue(result)

        try:
            response = client.search_image(
                index_name=index_name,
                vector_field=vector_field,
                image_path=image_path,
                base64_image=base64_image,
                model_id=model_id,
                k=k
            )

            if response.get('success'):
                results = response.get('results', [])
                total_hits = response.get('total_hits', 0)

                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "vector_field": vector_field,
                    "image_source": response.get('image_source'),
                    "model_id": model_id,
                    "total_hits": total_hits,
                    "results_count": len(results),
                    "results": results,
                    "took_ms": response.get('took', 0),
                    "summary": {
                        "search_type": "image",
                        "k": k,
                        "average_score": 0,
                        "min_score": float('inf'),
                        "max_score": 0
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    scores = []
                    for r in results:
                        score = r.get('_score')
                        if score is not None:
                            scores.append(score)

                    if scores:
                        analysis_result['summary']['average_score'] = sum(scores) / len(scores)
                        analysis_result['summary']['min_score'] = min(scores)
                        analysis_result['summary']['max_score'] = max(scores)

                print(f"Image search completed: Found {total_hits} total, showing {len(results)} results")
                print(f"Index: {index_name}")
                print(f"Vector field: {vector_field}")
                print(f"Image source: {analysis_result['image_source']}")
                if model_id:
                    print(f"Model ID: {model_id}")

                if results and scores:
                    print(f"Average score: {analysis_result['summary']['average_score']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        doc_id = result.get('_id')
                        source = result.get('_source', {})
                        score = result.get('_score', 0)
                        print(f"{i+1}. Score: {score:.4f} - ID: {doc_id}")
                        if source:
                            for key, value in list(source.items())[:2]:
                                if isinstance(value, str):
                                    print(f"   {key}: {value}")
                                else:
                                    print(f"   {key}: {value}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Image search failed: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing image search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform image search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_image_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def update_document_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting update_document_skill...")

    index_name = context.get('index_name', 'documents')
    document_id = context.get('document_id')
    doc = context.get('doc', {})
    script = context.get('script')

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        if not document_id:
            result = {"success": False, "error": "Document ID is required"}
            return OpenSearchDataValue(result)

        try:
            response = client.update_document(
                index_name=index_name,
                document_id=document_id,
                doc=doc,
                script=script
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "document_id": document_id,
                    "result": response.get('result'),
                    "version": response.get('version'),
                    "summary": {
                        "update_type": "script" if script else "document",
                        "fields_updated": len(doc) if doc else 0,
                        "has_script": bool(script)
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Document updated: {document_id}")
                print(f"Index: {index_name}")
                print(f"Result: {analysis_result['result']}")
                print(f"Update type: {analysis_result['summary']['update_type']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "document_id": document_id,
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to update document: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error updating document: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to update document: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in update_document_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def delete_document_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting delete_document_skill...")

    index_name = context.get('index_name', 'documents')
    document_id = context.get('document_id')
    query = context.get('query', {})

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        try:
            response = client.delete_document(
                index_name=index_name,
                document_id=document_id,
                query=query
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "action": response.get('action'),
                    "deleted": response.get('deleted', 0),
                    "document_id": document_id,
                    "summary": {
                        "method": "by_id" if document_id else "by_query",
                        "successful_deletions": response.get('deleted', 0)
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Document deletion completed")
                print(f"Index: {index_name}")
                print(f"Method: {analysis_result['summary']['method']}")
                print(f"Deleted count: {analysis_result['deleted']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to delete document: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error deleting document: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to delete document: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in delete_document_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def bulk_insert_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting bulk_insert_skill...")

    index_name = context.get('index_name', 'documents')
    documents = context.get('documents', [])
    batch_size = context.get('batch_size', 1000)
    refresh = context.get('refresh', False)

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        if not documents:
            result = {"success": False, "error": "Documents list is required"}
            return OpenSearchDataValue(result)

        try:
            response = client.bulk_insert(
                index_name=index_name,
                documents=documents,
                batch_size=batch_size,
                refresh=refresh
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "total_documents": len(documents),
                    "success_count": response.get('success_count', 0),
                    "failed_count": response.get('failed_count', 0),
                    "batch_size": batch_size,
                    "refresh": refresh,
                    "summary": {
                        "success_rate": response.get('success_count', 0) / len(documents) if documents else 0,
                        "documents_with_vectors": sum(1 for doc in documents if 'embedding' in doc or any('vector' in key.lower() for key in doc.keys()))
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Bulk insert completed")
                print(f"Index: {index_name}")
                print(f"Total documents: {len(documents)}")
                print(f"Success: {analysis_result['success_count']}")
                print(f"Failed: {analysis_result['failed_count']}")
                print(f"Success rate: {analysis_result['summary']['success_rate']:.2%}")

                if response.get('failed_count', 0) > 0:
                    print(f"Errors: {response.get('errors', [])[:3]}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "total_documents": len(documents),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Bulk insert failed: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error in bulk insert: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform bulk insert: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in bulk_insert_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def get_info_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting get_info_skill...")

    index_name = context.get('index_name', 'documents')

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        try:
            response = client.get_info(index_name=index_name)

            if response.get('success'):
                info = response.get('info', {})
                stats = info.get('stats', {})

                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "info_summary": {
                        "docs_count": stats.get('docs_count', 0),
                        "store_size": stats.get('store_size', 0),
                        "segments_count": stats.get('segments_count', 0),
                        "has_mappings": bool(info.get('mappings', {}).get('properties', {}))
                    },
                    "detailed_info": info,
                    "stats": stats,
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Index info retrieved: {index_name}")
                print(f"Documents: {analysis_result['info_summary']['docs_count']}")
                print(f"Store size: {analysis_result['info_summary']['store_size']} bytes")
                print(f"Segments: {analysis_result['info_summary']['segments_count']}")

                mappings = info.get('mappings', {}).get('properties', {})
                if mappings:
                    print("Properties:")
                    for prop_name, prop_info in list(mappings.items())[:5]:
                        prop_type = prop_info.get('type', 'unknown')
                        print(f"  - {prop_name} ({prop_type})")
                        if prop_type == 'knn_vector':
                            print(f"    Dimension: {prop_info.get('dimension', 'unknown')}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to get index info: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting index info: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get index info: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_info_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def delete_index_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting delete_index_skill...")

    index_name = context.get('index_name', 'documents')

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        try:
            response = client.delete_index(index_name=index_name)

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "acknowledged": response.get('acknowledged', False),
                    "status": "deleted",
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Index deleted: {index_name}")
                print(f"Acknowledged: {analysis_result['acknowledged']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to delete index: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error deleting index: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to delete index: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in delete_index_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def list_indices_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting list_indices_skill...")

    pattern = context.get('pattern', '*')

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        try:
            response = client.list_indices(pattern=pattern)

            if response.get('success'):
                indices = response.get('indices', [])

                analysis_result = {
                    "success": True,
                    "pattern": pattern,
                    "indices_count": len(indices),
                    "indices": indices,
                    "summary": {
                        "total_docs": sum(idx.get('docs_count', 0) for idx in indices),
                        "total_size": sum(idx.get('store_size', 0) for idx in indices),
                        "indices_with_mappings": sum(1 for idx in indices if idx.get('has_mappings', False)),
                        "index_names": [idx.get('name', '') for idx in indices]
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Found {len(indices)} indices matching pattern: {pattern}")
                print(f"Total documents: {analysis_result['summary']['total_docs']}")
                print(f"Total size: {analysis_result['summary']['total_size']} bytes")

                if indices:
                    print(f"First 5 indices:")
                    for i, idx in enumerate(indices[:5]):
                        print(f"{i+1}. {idx.get('name')} - Docs: {idx.get('docs_count', 0)} - Size: {idx.get('store_size', 0)} bytes")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "pattern": pattern,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to list indices: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error listing indices: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to list indices: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in list_indices_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)

def aggregate_skill(context: Dict[str, Any]) -> OpenSearchDataValue:
    print("Starting aggregate_skill...")

    index_name = context.get('index_name', 'documents')
    aggs = context.get('aggs', {})
    query = context.get('query', {})
    size = context.get('size', 0)

    try:
        client = context.get('opensearch_client')

        if not client:
            result = {"success": False, "error": "OpenSearch client not available"}
            return OpenSearchDataValue(result)

        if not aggs:
            result = {"success": False, "error": "Aggregations are required"}
            return OpenSearchDataValue(result)

        try:
            response = client.aggregate(
                index_name=index_name,
                aggs=aggs,
                query=query,
                size=size
            )

            if response.get('success'):
                aggregations = response.get('aggregations', {})

                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "total_hits": response.get('total_hits', 0),
                    "aggregations": aggregations,
                    "took_ms": response.get('took', 0),
                    "summary": {
                        "aggregation_keys": list(aggregations.keys()),
                        "has_query": bool(query),
                        "size": size
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Aggregation completed")
                print(f"Index: {index_name}")
                print(f"Total hits: {analysis_result['total_hits']}")
                print(f"Aggregation keys: {analysis_result['summary']['aggregation_keys']}")
                print(f"Took: {analysis_result['took_ms']}ms")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Aggregation failed: {response.get('error')}")

            return OpenSearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing aggregation: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform aggregation: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return OpenSearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in aggregate_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return OpenSearchDataValue(result)
