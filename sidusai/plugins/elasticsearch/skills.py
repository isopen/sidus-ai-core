from typing import Dict, Any
from datetime import datetime

class ElasticsearchDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def create_index_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting create_index_skill...")

    index_name = context.get('index_name', 'documents')
    mappings = context.get('mappings', {})
    settings = context.get('settings', {})

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

        if not mappings:
            mappings = {
                "properties": {
                    "text": {"type": "text"},
                    "metadata": {"type": "object"},
                    "timestamp": {"type": "date"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 768,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }

        try:
            response = client.create_index(
                index_name=index_name,
                mappings=mappings,
                settings=settings
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

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error creating index: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to create index: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in create_index_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def create_dense_vector_field_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting create_dense_vector_field_skill...")

    index_name = context.get('index_name', 'documents')
    field_name = context.get('field_name', 'embedding')
    dimension = context.get('dimension', 768)
    similarity = context.get('similarity', 'cosine')
    index_options = context.get('index_options', {})

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

        try:
            response = client.create_dense_vector_field(
                index_name=index_name,
                field_name=field_name,
                dimension=dimension,
                similarity=similarity,
                index_options=index_options
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "field_name": field_name,
                    "dimension": dimension,
                    "similarity": similarity,
                    "acknowledged": response.get('acknowledged', False),
                    "summary": {
                        "has_index_options": bool(index_options),
                        "index_options_keys": list(index_options.keys())
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Dense vector field created: {field_name} in index {index_name}")
                print(f"Dimension: {dimension}")
                print(f"Similarity: {similarity}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "field_name": field_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Dense vector field creation failed: {response.get('error')}")

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error creating dense vector field: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to create dense vector field: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in create_dense_vector_field_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def search_dense_vector_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting search_dense_vector_skill...")

    index_name = context.get('index_name', 'documents')
    vector_field = context.get('vector_field', 'embedding')
    vector = context.get('vector', [])
    k = context.get('k', 10)
    filter_query = context.get('filter_query', {})
    score_threshold = context.get('score_threshold')
    num_candidates = context.get('num_candidates', 100)

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

        if not vector:
            result = {"success": False, "error": "Query vector is required"}
            return ElasticsearchDataValue(result)

        try:
            response = client.search_dense_vector(
                index_name=index_name,
                vector_field=vector_field,
                vector=vector,
                k=k,
                filter_query=filter_query,
                score_threshold=score_threshold,
                num_candidates=num_candidates
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
                        "search_type": "dense_vector",
                        "search_params": {
                            "k": k,
                            "score_threshold": score_threshold,
                            "num_candidates": num_candidates,
                            "has_filter": bool(filter_query)
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

                print(f"Dense vector search completed: Found {total_hits} total, showing {len(results)} results")
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
                print(f"Dense vector search failed: {response.get('error')}")

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing dense vector search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform dense vector search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_dense_vector_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def search_hybrid_vector_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting search_hybrid_vector_skill...")

    index_name = context.get('index_name', 'documents')
    vector_field = context.get('vector_field', 'embedding')
    vector = context.get('vector', [])
    text_query = context.get('text_query', {})
    k = context.get('k', 10)
    vector_weight = context.get('vector_weight', 0.7)
    text_weight = context.get('text_weight', 0.3)
    filter_query = context.get('filter_query', {})

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

        if not vector or not text_query:
            result = {"success": False, "error": "Both vector and text_query are required"}
            return ElasticsearchDataValue(result)

        try:
            response = client.search_hybrid_vector(
                index_name=index_name,
                vector_field=vector_field,
                vector=vector,
                text_query=text_query,
                k=k,
                vector_weight=vector_weight,
                text_weight=text_weight,
                filter_query=filter_query
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
                        "search_type": "hybrid_vector",
                        "weights": {
                            "vector": vector_weight,
                            "text": text_weight
                        },
                        "has_filter": bool(filter_query),
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

                print(f"Hybrid vector search completed: Found {total_hits} total, showing {len(results)} results")
                print(f"Index: {index_name}")
                print(f"Vector weight: {vector_weight}, Text weight: {text_weight}")

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
                print(f"Hybrid vector search failed: {response.get('error')}")

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing hybrid vector search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform hybrid vector search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_hybrid_vector_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def search_semantic_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting search_semantic_skill...")

    index_name = context.get('index_name', 'documents')
    query_text = context.get('query_text')
    model_id = context.get('model_id')
    field_name = context.get('field_name', 'text_embedding')
    k = context.get('k', 10)

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

        if not query_text or not model_id:
            result = {"success": False, "error": "Both query_text and model_id are required"}
            return ElasticsearchDataValue(result)

        try:
            response = client.search_semantic(
                index_name=index_name,
                query_text=query_text,
                model_id=model_id,
                field_name=field_name,
                k=k
            )

            if response.get('success'):
                results = response.get('results', [])
                total_hits = response.get('total_hits', 0)

                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "query_text": query_text,
                    "model_id": model_id,
                    "field_name": field_name,
                    "total_hits": total_hits,
                    "results_count": len(results),
                    "results": results,
                    "took_ms": response.get('took', 0),
                    "summary": {
                        "search_type": "semantic",
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

                print(f"Semantic search completed: Found {total_hits} total, showing {len(results)} results")
                print(f"Index: {index_name}")
                print(f"Model ID: {model_id}")
                print(f"Query: '{query_text}'")

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
                print(f"Semantic search failed: {response.get('error')}")

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing semantic search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform semantic search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_semantic_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def cluster_health_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting cluster_health_skill...")

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

        try:
            response = client.cluster_health()

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "cluster_name": response.get('cluster_name'),
                    "status": response.get('status'),
                    "summary": {
                        "nodes": response.get('number_of_nodes'),
                        "data_nodes": response.get('number_of_data_nodes'),
                        "active_shards": response.get('active_shards'),
                        "unassigned_shards": response.get('unassigned_shards'),
                        "active_shards_percent": response.get('active_shards_percent_as_number')
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Cluster health retrieved")
                print(f"Cluster: {analysis_result['cluster_name']}")
                print(f"Status: {analysis_result['status']}")
                print(f"Nodes: {analysis_result['summary']['nodes']}")
                print(f"Active shards: {analysis_result['summary']['active_shards']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to get cluster health: {response.get('error')}")

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting cluster health: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get cluster health: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in cluster_health_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def index_document_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting index_document_skill...")

    index_name = context.get('index_name', 'documents')
    document = context.get('document', {})
    document_id = context.get('document_id')

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

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

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error indexing document: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to index document: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in index_document_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def get_document_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting get_document_skill...")

    index_name = context.get('index_name', 'documents')
    document_id = context.get('document_id')

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

        if not document_id:
            result = {"success": False, "error": "Document ID is required"}
            return ElasticsearchDataValue(result)

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

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting document: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get document: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_document_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def search_text_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting search_text_skill...")

    index_name = context.get('index_name', 'documents')
    query = context.get('query', {})
    size = context.get('size', 10)
    from_ = context.get('from_', 0)

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

        if not query:
            result = {"success": False, "error": "Query is required"}
            return ElasticsearchDataValue(result)

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

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing text search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform text search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_text_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def update_document_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting update_document_skill...")

    index_name = context.get('index_name', 'documents')
    document_id = context.get('document_id')
    doc = context.get('doc', {})
    script = context.get('script')

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

        if not document_id:
            result = {"success": False, "error": "Document ID is required"}
            return ElasticsearchDataValue(result)

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

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error updating document: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to update document: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in update_document_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def delete_document_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting delete_document_skill...")

    index_name = context.get('index_name', 'documents')
    document_id = context.get('document_id')
    query = context.get('query', {})

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

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

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error deleting document: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to delete document: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in delete_document_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def bulk_insert_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting bulk_insert_skill...")

    index_name = context.get('index_name', 'documents')
    documents = context.get('documents', [])
    batch_size = context.get('batch_size', 1000)
    refresh = context.get('refresh', False)

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

        if not documents:
            result = {"success": False, "error": "Documents list is required"}
            return ElasticsearchDataValue(result)

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

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error in bulk insert: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform bulk insert: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in bulk_insert_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def get_info_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting get_info_skill...")

    index_name = context.get('index_name', 'documents')

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

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
                        if prop_type == 'dense_vector':
                            print(f"    Dimension: {prop_info.get('dims', 'unknown')}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to get index info: {response.get('error')}")

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting index info: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get index info: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_info_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def delete_index_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting delete_index_skill...")

    index_name = context.get('index_name', 'documents')

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

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

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error deleting index: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to delete index: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in delete_index_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def list_indices_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting list_indices_skill...")

    pattern = context.get('pattern', '*')

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

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

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error listing indices: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to list indices: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in list_indices_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)

def aggregate_skill(context: Dict[str, Any]) -> ElasticsearchDataValue:
    print("Starting aggregate_skill...")

    index_name = context.get('index_name', 'documents')
    aggs = context.get('aggs', {})
    query = context.get('query', {})
    size = context.get('size', 0)

    try:
        client = context.get('elasticsearch_client')

        if not client:
            result = {"success": False, "error": "Elasticsearch client not available"}
            return ElasticsearchDataValue(result)

        if not aggs:
            result = {"success": False, "error": "Aggregations are required"}
            return ElasticsearchDataValue(result)

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

            return ElasticsearchDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing aggregation: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform aggregation: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return ElasticsearchDataValue(analysis_result)

    except Exception as e:
        print(f"Error in aggregate_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return ElasticsearchDataValue(result)
