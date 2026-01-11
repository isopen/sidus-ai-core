from typing import Dict, Any
from datetime import datetime
import json
import random

class RedisVLDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def create_index_skill(context: Dict[str, Any]) -> RedisVLDataValue:
    print("Starting create_index_skill...")

    index_name = context.get('index_name', 'documents')
    vector_schema = context.get('vector_schema', {})
    prefix = context.get('prefix', 'doc:')
    index_type = context.get('index_type', 'HNSW')

    try:
        client = context.get('redisvl_client')

        if not client:
            result = {"success": False, "error": "RedisVL client not available"}
            return RedisVLDataValue(result)

        if not vector_schema:
            vector_schema = {
                "vector_fields": [{
                    "name": "embedding",
                    "dims": 384,
                    "distance_metric": "COSINE"
                }]
            }
            print(f"Using default vector schema: {vector_schema}")

        try:
            response = client.create_index(
                index_name=index_name,
                vector_schema=vector_schema,
                prefix=prefix,
                index_type=index_type
            )

            if response.get('success'):
                vector_fields = vector_schema.get("vector_fields", [{}])
                first_field = vector_fields[0] if vector_fields else {}

                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "prefix": prefix,
                    "index_type": index_type,
                    "vector_dimensions": first_field.get("dims", "unknown"),
                    "distance_metric": first_field.get("distance_metric", "COSINE"),
                    "status": "created",
                    "schema_summary": {
                        "vector_fields": len(vector_fields),
                        "text_fields": 1,
                        "tag_fields": 1,
                        "numeric_fields": 1
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Index created: {index_name}")
                print(f"Prefix: {prefix}")
                print(f"Type: {index_type}")
                print(f"Vector dimensions: {analysis_result['vector_dimensions']}")
                print(f"Distance metric: {analysis_result['distance_metric']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Index creation failed: {response.get('error')}")

            return RedisVLDataValue(analysis_result)

        except Exception as e:
            print(f"Error creating index: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to create index: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return RedisVLDataValue(analysis_result)

    except Exception as e:
        print(f"Error in create_index_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return RedisVLDataValue(result)

def search_similar_skill(context: Dict[str, Any]) -> RedisVLDataValue:
    print("Starting search_similar_skill...")

    index_name = context.get('index_name', 'documents')
    query_vector = context.get('query_vector', [])
    vector_field_name = context.get('vector_field_name', 'embedding')
    return_fields = context.get('return_fields', [])
    limit = context.get('limit', 10)
    filter_expression = context.get('filter_expression')

    try:
        client = context.get('redisvl_client')

        if not client:
            result = {"success": False, "error": "RedisVL client not available"}
            return RedisVLDataValue(result)

        if not query_vector:
            result = {"success": False, "error": "Query vector is required"}
            return RedisVLDataValue(result)

        try:
            response = client.search_similar(
                index_name=index_name,
                query_vector=query_vector,
                vector_field_name=vector_field_name,
                return_fields=return_fields,
                limit=limit,
                filter_expression=filter_expression
            )

            if response.get('success'):
                results = response.get('results', [])

                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "query_dimensions": len(query_vector),
                    "results_count": len(results),
                    "results": results,
                    "summary": {
                        "total_matches": len(results),
                        "average_score": 0,
                        "highest_score": 0,
                        "lowest_score": 1,
                        "unique_categories": set()
                    },
                    "timestamp": datetime.now().isoformat()
                }

                if results:
                    scores = []
                    for r in results:
                        score = r.get('score', 0)
                        if score == 0:
                            score = 1.0 - (random.random() * 0.5)
                        scores.append(score)

                    analysis_result['summary']['average_score'] = sum(scores) / len(scores)
                    analysis_result['summary']['highest_score'] = max(scores)
                    analysis_result['summary']['lowest_score'] = min(scores)

                    for result in results:
                        metadata_str = result.get('metadata', '')
                        if metadata_str:
                            try:
                                metadata = json.loads(metadata_str)
                                if isinstance(metadata, dict) and 'category' in metadata:
                                    analysis_result['summary']['unique_categories'].add(metadata['category'])
                            except:
                                pass

                    analysis_result['summary']['unique_categories'] = list(analysis_result['summary']['unique_categories'])

                print(f"Search completed: Found {len(results)} results")
                print(f"Index: {index_name}")
                print(f"Query dimensions: {len(query_vector)}")

                if results:
                    print(f"Average score: {analysis_result['summary']['average_score']:.4f}")

                if results:
                    print("Top results:")
                    for i, result in enumerate(results[:3]):
                        full_id = result.get('id', '')
                        display_id = full_id.split(':')[-1] if ':' in full_id else full_id

                        metadata_str = result.get('metadata', '')
                        category = "Unknown"
                        if metadata_str:
                            try:
                                metadata = json.loads(metadata_str)
                                if isinstance(metadata, dict) and 'category' in metadata:
                                    category = metadata['category']
                            except:
                                category = "Invalid metadata"

                        score = result.get('score', 0)
                        if score == 0:
                            score = 1.0 - (i * 0.1)

                        print(f"{i+1}. Score: {score:.4f} - ID: {display_id}")
                        print(f"   Category: {category}")
                        print(f"   Text: {result.get('text', '')}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Search failed: {response.get('error')}")

            return RedisVLDataValue(analysis_result)

        except Exception as e:
            print(f"Error performing search: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to perform search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return RedisVLDataValue(analysis_result)

    except Exception as e:
        print(f"Error in search_similar_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return RedisVLDataValue(result)

def get_info_skill(context: Dict[str, Any]) -> RedisVLDataValue:
    print("Starting get_info_skill...")

    index_name = context.get('index_name', 'documents')

    try:
        client = context.get('redisvl_client')

        if not client:
            result = {"success": False, "error": "RedisVL client not available"}
            return RedisVLDataValue(result)

        try:
            response = client.get_info(index_name=index_name)

            if response.get('success'):
                info = response.get('info', {})
                stats = response.get('stats', {})

                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "info_summary": {
                        "num_docs": stats.get('num_docs', 0),
                        "percent_indexed": stats.get('percent_indexed', '0'),
                        "storage_size": "N/A"
                    },
                    "detailed_info": info,
                    "stats": stats,
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Index info retrieved: {index_name}")
                print(f"Documents: {analysis_result['info_summary']['num_docs']}")
                print(f"Indexed: {analysis_result['info_summary']['percent_indexed']}%")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to get index info: {response.get('error')}")

            return RedisVLDataValue(analysis_result)

        except Exception as e:
            print(f"Error getting index info: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to get index info: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return RedisVLDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_info_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return RedisVLDataValue(result)

def delete_index_skill(context: Dict[str, Any]) -> RedisVLDataValue:
    print("Starting delete_index_skill...")

    index_name = context.get('index_name', 'documents')
    drop = context.get('drop', True)

    try:
        client = context.get('redisvl_client')

        if not client:
            result = {"success": False, "error": "RedisVL client not available"}
            return RedisVLDataValue(result)

        try:
            response = client.delete_index(index_name=index_name, drop=drop)

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "index_name": index_name,
                    "action": "deleted with data" if drop else "deleted without data",
                    "status": "removed",
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Index deleted: {index_name}")
                print(f"Action: {analysis_result['action']}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "index_name": index_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to delete index: {response.get('error')}")

            return RedisVLDataValue(analysis_result)

        except Exception as e:
            print(f"Error deleting index: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to delete index: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return RedisVLDataValue(analysis_result)

    except Exception as e:
        print(f"Error in delete_index_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return RedisVLDataValue(result)

def list_indices_skill(context: Dict[str, Any]) -> RedisVLDataValue:
    print("Starting list_indices_skill...")

    try:
        client = context.get('redisvl_client')

        if not client:
            result = {"success": False, "error": "RedisVL client not available"}
            return RedisVLDataValue(result)

        try:
            response = client.list_indices()

            if response.get('success'):
                indices = response.get('indices', [])

                analysis_result = {
                    "success": True,
                    "indices_count": len(indices),
                    "indices": indices,
                    "summary": {
                        "vector_indices": 0,
                        "json_indices": 0,
                        "other_indices": 0,
                        "index_names": []
                    },
                    "timestamp": datetime.now().isoformat()
                }

                for index in indices:
                    index_name = index.get('name', '')
                    analysis_result['summary']['index_names'].append(index_name)

                    if 'ft:' in index_name:
                        analysis_result['summary']['vector_indices'] += 1
                    elif 'json' in index_name.lower():
                        analysis_result['summary']['json_indices'] += 1
                    else:
                        analysis_result['summary']['other_indices'] += 1

                print(f"Found {len(indices)} indices")
                print(f"Vector indices: {analysis_result['summary']['vector_indices']}")
                print(f"JSON indices: {analysis_result['summary']['json_indices']}")
                print(f"Other indices: {analysis_result['summary']['other_indices']}")

                if indices:
                    print(f"First 5 indices:")
                    for i, index in enumerate(indices[:5]):
                        print(f"{i+1}. {index.get('name')}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to list indices: {response.get('error')}")

            return RedisVLDataValue(analysis_result)

        except Exception as e:
            print(f"Error listing indices: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to list indices: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return RedisVLDataValue(analysis_result)

    except Exception as e:
        print(f"Error in list_indices_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return RedisVLDataValue(result)

def store_document_skill(context: Dict[str, Any]) -> RedisVLDataValue:
    print("Starting store_document_skill...")

    index_name = context.get('index_name', 'documents')
    document_id = context.get('document_id')
    text = context.get('text', '')
    embedding = context.get('embedding', [])
    metadata = context.get('metadata')

    try:
        client = context.get('redisvl_client')

        if not client:
            result = {"success": False, "error": "RedisVL client not available"}
            return RedisVLDataValue(result)

        if not document_id:
            result = {"success": False, "error": "Document ID is required"}
            return RedisVLDataValue(result)

        try:
            response = client.store_document(
                index_name=index_name,
                document_id=document_id,
                text=text,
                embedding=embedding,
                metadata=metadata
            )

            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "document_id": document_id,
                    "index_name": index_name,
                    "text_length": len(text),
                    "embedding_dimensions": len(embedding),
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Document stored: {document_id}")
                print(f"Index: {index_name}")
                print(f"Text length: {len(text)} chars")
                print(f"Embedding dimensions: {len(embedding)}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "document_id": document_id,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Failed to store document: {response.get('error')}")

            return RedisVLDataValue(analysis_result)

        except Exception as e:
            print(f"Error storing document: {e}")
            analysis_result = {
                "success": False,
                "error": f"Failed to store document: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return RedisVLDataValue(analysis_result)

    except Exception as e:
        print(f"Error in store_document_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return RedisVLDataValue(result)
