from typing import Dict, Any
from datetime import datetime
from .components import PgVectorClientComponent

class PgVectorDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def create_vector_extension_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        extension_result = client.create_vector_extension()

        if extension_result["success"]:
            result = {
                "success": True,
                "operation": "create_vector_extension",
                "message": extension_result.get("message", "Extension created"),
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "success": False,
                "error": extension_result.get("error", "Unknown error"),
                "timestamp": datetime.now().isoformat()
            }

        return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def create_table_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name', 'default_table')
    vector_dimension = context.get('vector_dimension', 1536)
    metadata_columns = context.get('metadata_columns', {})
    with_hnsw = context.get('with_hnsw', False)
    hnsw_m = context.get('hnsw_m', 16)
    hnsw_ef_construction = context.get('hnsw_ef_construction', 64)

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        create_result = client.create_table(
            table_name=table_name,
            vector_dimension=vector_dimension,
            metadata_columns=metadata_columns,
            with_hnsw=with_hnsw,
            hnsw_m=hnsw_m,
            hnsw_ef_construction=hnsw_ef_construction
        )

        if create_result["success"]:
            result = {
                "success": True,
                "table_name": table_name,
                "full_table_name": create_result.get("table_name"),
                "vector_dimension": vector_dimension,
                "has_hnsw_index": with_hnsw,
                "metadata_columns_count": len(metadata_columns),
                "operation": "create_table",
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "success": False,
                "error": create_result.get("error", "Unknown error"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }

        return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def modify_table_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name')
    add_columns = context.get('add_columns', {})
    drop_columns = context.get('drop_columns', [])
    rename_columns = context.get('rename_columns', {})

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        if not table_name:
            result = {"success": False, "error": "Table name required"}
            return PgVectorDataValue(result)

        modify_result = client.modify_table(
            table_name=table_name,
            add_columns=add_columns,
            drop_columns=drop_columns,
            rename_columns=rename_columns
        )

        if modify_result["success"]:
            result = {
                "success": True,
                "table_name": table_name,
                "full_table_name": modify_result.get("table_name"),
                "add_columns_count": len(add_columns),
                "drop_columns_count": len(drop_columns),
                "rename_columns_count": len(rename_columns),
                "total_operations": modify_result.get("operations_count", 0),
                "operation": "modify_table",
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "success": False,
                "error": modify_result.get("error", "Unknown error"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }

        return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def create_index_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name')
    index_type = context.get('index_type', 'hnsw')
    distance_metric = context.get('distance_metric', 'l2')
    hnsw_m = context.get('hnsw_m', 16)
    hnsw_ef_construction = context.get('hnsw_ef_construction', 64)
    ivfflat_lists = context.get('ivfflat_lists', 100)
    concurrently = context.get('concurrently', False)

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        if not table_name:
            result = {"success": False, "error": "Table name required"}
            return PgVectorDataValue(result)

        index_result = client.create_index(
            table_name=table_name,
            index_type=index_type,
            distance_metric=distance_metric,
            hnsw_m=hnsw_m,
            hnsw_ef_construction=hnsw_ef_construction,
            ivfflat_lists=ivfflat_lists,
            concurrently=concurrently
        )

        if index_result["success"]:
            result = {
                "success": True,
                "table_name": table_name,
                "index_name": index_result.get("index_name"),
                "index_type": index_type,
                "distance_metric": distance_metric,
                "concurrently": concurrently,
                "operation": "create_index",
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "success": False,
                "error": index_result.get("error", "Unknown error"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }

        return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def insert_vectors_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name', 'default_table')
    vectors = context.get('vectors', [])
    metadata_list = context.get('metadata_list', [])
    ids = context.get('ids', [])
    content_list = context.get('content_list', [])

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        if not vectors:
            result = {"success": False, "error": "No vectors provided"}
            return PgVectorDataValue(result)

        insert_result = client.insert_vectors(
            table_name=table_name,
            vectors=vectors,
            metadata_list=metadata_list,
            ids=ids,
            content_list=content_list
        )

        if insert_result["success"]:
            result = {
                "success": True,
                "table_name": table_name,
                "full_table_name": insert_result.get("table_name"),
                "vector_count": insert_result.get("count", 0),
                "avg_vector_dimensions": len(vectors[0]) if vectors else 0,
                "operation": "insert_vectors",
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "success": False,
                "error": insert_result.get("error", "Unknown error"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }

        return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def query_vectors_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name', 'default_table')
    query_vector = context.get('query_vector')
    limit = context.get('limit', 10)
    distance_metric = context.get('distance_metric', 'l2')
    return_columns = context.get('return_columns', ["id", "content", "metadata", "vector_norm"])
    hnsw_ef_search = context.get('hnsw_ef_search')
    ivfflat_probes = context.get('ivfflat_probes')

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        if not query_vector:
            result = {"success": False, "error": "Query vector required"}
            return PgVectorDataValue(result)

        query_result = client.query_vectors(
            table_name=table_name,
            query_vector=query_vector,
            limit=limit,
            distance_metric=distance_metric,
            return_columns=return_columns,
            hnsw_ef_search=hnsw_ef_search,
            ivfflat_probes=ivfflat_probes
        )

        if query_result["success"]:
            results = query_result["results"]

            analysis = {
                "success": True,
                "table_name": table_name,
                "query_vector_dimensions": len(query_vector),
                "distance_metric": distance_metric,
                "limit": limit,
                "found_count": len(results),
                "distances_summary": {},
                "norms_summary": {},
                "sample_results": [],
                "timestamp": datetime.now().isoformat()
            }

            if results:
                distances = [result.get('distance', 0) for result in results if 'distance' in result]
                norms = [result.get('vector_norm', 0) for result in results if 'vector_norm' in result]

                if distances:
                    analysis["distances_summary"] = {
                        "min": min(distances),
                        "max": max(distances),
                        "avg": sum(distances) / len(distances),
                        "median": sorted(distances)[len(distances)//2] if distances else 0
                    }

                if norms:
                    analysis["norms_summary"] = {
                        "min": min(norms),
                        "max": max(norms),
                        "avg": sum(norms) / len(norms)
                    }

                analysis["sample_results"] = results[:3]

            return PgVectorDataValue(analysis)
        else:
            result = {
                "success": False,
                "error": query_result.get("error", "Query failed"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def search_with_filter_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name', 'default_table')
    query_vector = context.get('query_vector')
    filter_conditions = context.get('filter_conditions', {})
    limit = context.get('limit', 10)
    distance_metric = context.get('distance_metric', 'l2')
    hnsw_ef_search = context.get('hnsw_ef_search')

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        if not query_vector:
            result = {"success": False, "error": "Query vector required"}
            return PgVectorDataValue(result)

        search_result = client.search_with_filter(
            table_name=table_name,
            query_vector=query_vector,
            filter_conditions=filter_conditions,
            limit=limit,
            distance_metric=distance_metric,
            hnsw_ef_search=hnsw_ef_search
        )

        if search_result["success"]:
            results = search_result["results"]

            analysis = {
                "success": True,
                "table_name": table_name,
                "query_vector_dimensions": len(query_vector),
                "filter_conditions": filter_conditions,
                "filter_count": len(filter_conditions),
                "distance_metric": distance_metric,
                "limit": limit,
                "found_count": len(results),
                "sample_results": [],
                "timestamp": datetime.now().isoformat()
            }

            if results:
                distances = [result.get('distance', 0) for result in results if 'distance' in result]
                if distances:
                    analysis["distances_summary"] = {
                        "min": min(distances),
                        "max": max(distances),
                        "avg": sum(distances) / len(distances)
                    }

                analysis["sample_results"] = results[:3]

            return PgVectorDataValue(analysis)
        else:
            result = {
                "success": False,
                "error": search_result.get("error", "Search failed"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def hybrid_search_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name', 'default_table')
    query_text = context.get('query_text')
    query_vector = context.get('query_vector')
    limit = context.get('limit', 10)
    text_weight = context.get('text_weight', 0.5)
    vector_weight = context.get('vector_weight', 0.5)
    distance_metric = context.get('distance_metric', 'l2')

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        if not query_text or not query_vector:
            result = {"success": False, "error": "Both query_text and query_vector required"}
            return PgVectorDataValue(result)

        hybrid_result = client.hybrid_search(
            table_name=table_name,
            query_text=query_text,
            query_vector=query_vector,
            limit=limit,
            text_weight=text_weight,
            vector_weight=vector_weight,
            distance_metric=distance_metric
        )

        if hybrid_result["success"]:
            results = hybrid_result["results"]

            analysis = {
                "success": True,
                "table_name": table_name,
                "query_text": query_text,
                "query_vector_dimensions": len(query_vector),
                "text_weight": text_weight,
                "vector_weight": vector_weight,
                "distance_metric": distance_metric,
                "limit": limit,
                "found_count": len(results),
                "scores_summary": {},
                "sample_results": [],
                "timestamp": datetime.now().isoformat()
            }

            if results:
                combined_scores = [result.get('combined_score', 0) for result in results if 'combined_score' in result]
                vector_distances = [result.get('vector_distance', 0) for result in results if 'vector_distance' in result]
                text_scores = [result.get('text_score', 0) for result in results if 'text_score' in result]

                if combined_scores:
                    analysis["scores_summary"] = {
                        "combined_min": min(combined_scores),
                        "combined_max": max(combined_scores),
                        "combined_avg": sum(combined_scores) / len(combined_scores),
                        "vector_min": min(vector_distances) if vector_distances else 0,
                        "vector_max": max(vector_distances) if vector_distances else 0,
                        "text_min": min(text_scores) if text_scores else 0,
                        "text_max": max(text_scores) if text_scores else 0
                    }

                analysis["sample_results"] = results[:3]

            return PgVectorDataValue(analysis)
        else:
            result = {
                "success": False,
                "error": hybrid_result.get("error", "Hybrid search failed"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def delete_vectors_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name')
    ids = context.get('ids', [])
    filter_conditions = context.get('filter_conditions', {})

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        if not table_name:
            result = {"success": False, "error": "Table name required"}
            return PgVectorDataValue(result)

        if not ids and not filter_conditions:
            result = {"success": False, "error": "Either ids or filter_conditions required"}
            return PgVectorDataValue(result)

        delete_result = client.delete_vectors(
            table_name=table_name,
            ids=ids,
            filter_conditions=filter_conditions
        )

        if delete_result["success"]:
            result = {
                "success": True,
                "table_name": table_name,
                "deleted_count": delete_result.get("deleted_count", 0),
                "deleted_ids_sample": delete_result.get("deleted_ids", [])[:10],
                "operation": "delete_vectors",
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "success": False,
                "error": delete_result.get("error", "Unknown error"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }

        return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def update_vectors_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name', 'default_table')
    ids = context.get('ids', [])
    vectors = context.get('vectors', [])
    metadata_list = context.get('metadata_list', [])
    content_list = context.get('content_list', [])

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        if not ids:
            result = {"success": False, "error": "No IDs provided"}
            return PgVectorDataValue(result)

        update_result = client.update_vectors(
            table_name=table_name,
            ids=ids,
            vectors=vectors,
            metadata_list=metadata_list,
            content_list=content_list
        )

        if update_result["success"]:
            result = {
                "success": True,
                "table_name": table_name,
                "updated_count": update_result.get("updated_count", 0),
                "ids_count": len(ids),
                "vectors_count": len(vectors) if vectors else 0,
                "operation": "update_vectors",
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "success": False,
                "error": update_result.get("error", "Unknown error"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }

        return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def get_table_info_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name', 'default_table')

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        info_result = client.get_table_info(table_name)

        if info_result["success"]:
            result = {
                "success": True,
                "table_name": table_name,
                "full_table_name": info_result.get("table_name"),
                "row_count": info_result.get("row_count", 0),
                "oldest_record": info_result.get("oldest_record"),
                "newest_record": info_result.get("newest_record"),
                "avg_metadata_keys": info_result.get("avg_metadata_keys", 0.0),
                "avg_content_length": info_result.get("avg_content_length", 0.0),
                "avg_vector_norm": info_result.get("avg_vector_norm", 0.0),
                "columns_count": len(info_result.get("columns", [])),
                "indexes_count": len(info_result.get("indexes", [])),
                "vector_dimensions": info_result.get("vector_dimensions", {}),
                "sample_columns": info_result.get("columns", [])[:5],
                "timestamp": datetime.now().isoformat()
            }

            return PgVectorDataValue(result)
        else:
            result = {
                "success": False,
                "error": info_result.get("error", "Failed to get table info"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def list_tables_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    pattern = context.get('pattern')
    limit = context.get('limit', 100)

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        list_result = client.list_tables(pattern=pattern, limit=limit)

        if list_result["success"]:
            result = {
                "success": True,
                "schema": list_result.get("schema"),
                "tables": list_result.get("tables", []),
                "table_info": list_result.get("table_info", []),
                "total_count": list_result.get("total_count", 0),
                "limit": limit,
                "timestamp": datetime.now().isoformat()
            }

            return PgVectorDataValue(result)
        else:
            result = {
                "success": False,
                "error": list_result.get("error", "Failed to list tables"),
                "timestamp": datetime.now().isoformat()
            }
            return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def test_connection_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        is_connected = client.test_connection()

        result = {
            "success": True,
            "connected": is_connected,
            "host": client.host,
            "port": client.port,
            "database": client.database,
            "schema": client.schema,
            "table_prefix": client.table_prefix,
            "connection_pool_size": client.connection_pool_size,
            "ssl_mode": client.ssl_mode,
            "timestamp": datetime.now().isoformat()
        }

        return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "connected": False,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def bulk_insert_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name', 'default_table')
    vectors = context.get('vectors', [])
    metadata_list = context.get('metadata_list', [])
    content_list = context.get('content_list', [])
    batch_size = context.get('batch_size', 1000)

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        if not vectors:
            result = {"success": False, "error": "No vectors provided"}
            return PgVectorDataValue(result)

        bulk_result = client.bulk_insert(
            table_name=table_name,
            vectors=vectors,
            metadata_list=metadata_list,
            content_list=content_list,
            batch_size=batch_size
        )

        if bulk_result["success"]:
            result = {
                "success": True,
                "table_name": table_name,
                "full_table_name": bulk_result.get("table_name"),
                "total_inserted": bulk_result.get("total_inserted", 0),
                "batch_count": bulk_result.get("batch_count", 0),
                "batch_size": batch_size,
                "time_seconds": bulk_result.get("time_seconds", 0),
                "vectors_per_second": bulk_result.get("vectors_per_second", 0),
                "avg_vector_dimensions": len(vectors[0]) if vectors else 0,
                "operation": "bulk_insert",
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "success": False,
                "error": bulk_result.get("error", "Unknown error"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }

        return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)

def get_vector_statistics_skill(context: Dict[str, Any]) -> PgVectorDataValue:
    table_name = context.get('table_name', 'default_table')

    try:
        client: PgVectorClientComponent = context.get('pgvector_client')

        if not client:
            result = {"success": False, "error": "PgVector client not available"}
            return PgVectorDataValue(result)

        stats_result = client.get_vector_statistics(table_name)

        if stats_result["success"]:
            result = {
                "success": True,
                "table_name": table_name,
                "full_table_name": stats_result.get("table_name"),
                "total_vectors": stats_result.get("total_vectors", 0),
                "avg_dimensions": stats_result.get("avg_dimensions", 0.0),
                "min_norm": stats_result.get("min_norm", 0.0),
                "max_norm": stats_result.get("max_norm", 0.0),
                "avg_norm": stats_result.get("avg_norm", 0.0),
                "std_norm": stats_result.get("std_norm", 0.0),
                "median_norm": stats_result.get("median_norm", 0.0),
                "sample_vectors_count": len(stats_result.get("sample_vectors", [])),
                "dimension_distribution": stats_result.get("dimension_distribution", []),
                "timestamp": datetime.now().isoformat()
            }

            return PgVectorDataValue(result)
        else:
            result = {
                "success": False,
                "error": stats_result.get("error", "Failed to get statistics"),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            return PgVectorDataValue(result)

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "timestamp": datetime.now().isoformat()
        }
        return PgVectorDataValue(result)
