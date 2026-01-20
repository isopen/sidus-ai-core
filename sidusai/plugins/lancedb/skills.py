from typing import Dict, Any
from datetime import datetime

class LanceDBDataValue:
    def __init__(self, data: Dict[str, Any]):
        self.value = data

def create_table_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting create_table_skill...")

    table_name = context.get('table_name', 'documents')
    data = context.get('data')
    schema = context.get('schema')
    mode = context.get('mode', 'create')
    exist_ok = context.get('exist_ok', False)
    embedding_functions = context.get('embedding_functions')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        response = client.create_table(
            table_name=table_name,
            data=data,
            schema=schema,
            mode=mode,
            exist_ok=exist_ok,
            embedding_functions=embedding_functions
        )

        if isinstance(response, dict):
            if response.get('success'):
                analysis_result = {
                    "success": True,
                    "table_name": table_name,
                    "status": response.get('status', 'created'),
                    "table_info": response.get('table_info', {}),
                    "summary": {
                        "has_data": data is not None,
                        "has_schema": schema is not None,
                        "has_embedding_functions": embedding_functions is not None,
                        "mode": mode,
                        "exist_ok": exist_ok
                    },
                    "timestamp": datetime.now().isoformat()
                }

                print(f"Table created: {table_name}")
                print(f"Mode: {mode}")
                table_info = response.get('table_info', {})
                if isinstance(table_info, dict):
                    schema_info = table_info.get('schema')
                    if isinstance(schema_info, dict):
                        print(f"Schema fields: {schema_info.get('field_count', 'unknown')}")
                    elif schema_info is not None:
                        print(f"Schema: {schema_info}")

            else:
                analysis_result = {
                    "success": False,
                    "error": response.get('error', 'Unknown error'),
                    "table_name": table_name,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Table creation failed: {response.get('error')}")
        else:
            error_msg = str(response) if response else "Unknown error occurred"
            analysis_result = {
                "success": False,
                "error": f"Invalid response format: {error_msg}",
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Table creation failed with invalid response: {response}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in create_table_skill: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def open_table_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting open_table_skill...")

    table_name = context.get('table_name')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name:
            result = {"success": False, "error": "Table name is required"}
            return LanceDBDataValue(result)

        response = client.open_table(table_name=table_name)

        if response.get('success'):
            analysis_result = {
                "success": True,
                "table_name": table_name,
                "table_info": response.get('table_info', {}),
                "timestamp": datetime.now().isoformat()
            }

            print(f"Table opened: {table_name}")
            print(f"Version: {analysis_result['table_info'].get('version', 'unknown')}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to open table: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in open_table_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def list_tables_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting list_tables_skill...")

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        response = client.list_tables()

        if response.get('success'):
            tables = response.get('tables', [])

            analysis_result = {
                "success": True,
                "tables_count": len(tables),
                "tables": tables,
                "summary": {
                    "table_names": [t.get('name', '') for t in tables],
                    "has_tables": len(tables) > 0
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Found {len(tables)} tables")

            if tables:
                print("Tables:")
                for i, table in enumerate(tables[:5]):
                    print(f"{i+1}. {table.get('name')} - Version: {table.get('version', 'unknown')}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to list tables: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in list_tables_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def add_data_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting add_data_skill...")

    table_name = context.get('table_name')
    data = context.get('data')
    mode = context.get('mode', 'append')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name or not data:
            result = {"success": False, "error": "Table name and data are required"}
            return LanceDBDataValue(result)

        response = client.add_data(
            table_name=table_name,
            data=data,
            mode=mode
        )

        if response.get('success'):
            analysis_result = {
                "success": True,
                "table_name": table_name,
                "operation": response.get('operation', 'append'),
                "new_version": response.get('new_version', 'unknown'),
                "rows_added": response.get('rows_added', 'unknown'),
                "summary": {
                    "data_type": type(data).__name__,
                    "mode": mode,
                    "has_vector_data": any('vector' in str(item).lower() for item in data) if isinstance(data, list) else False
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Data added to table: {table_name}")
            print(f"Operation: {analysis_result['operation']}")
            print(f"Rows added: {analysis_result['rows_added']}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to add data: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in add_data_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def vector_search_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting vector_search_skill...")

    table_name = context.get('table_name')
    query_vector = context.get('query_vector', [])
    vector_column = context.get('vector_column', 'vector')
    limit = context.get('limit', 10)
    filter = context.get('filter')
    distance_type = context.get('distance_type', 'l2')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name or not query_vector:
            result = {"success": False, "error": "Table name and query vector are required"}
            return LanceDBDataValue(result)

        response = client.vector_search(
            table_name=table_name,
            query_vector=query_vector,
            vector_column=vector_column,
            limit=limit,
            filter=filter,
            distance_type=distance_type
        )

        if response.get('success'):
            results = response.get('results', [])

            analysis_result = {
                "success": True,
                "table_name": table_name,
                "query_type": "vector",
                "vector_dimensions": len(query_vector),
                "results_count": len(results),
                "results": results,
                "distance_type": distance_type,
                "summary": {
                    "vector_column": vector_column,
                    "limit": limit,
                    "has_filter": filter is not None,
                    "average_distance": 0,
                    "min_distance": float('inf'),
                    "max_distance": 0
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Vector search completed: Found {len(results)} results")
            print(f"Table: {table_name}")
            print(f"Vector dimensions: {len(query_vector)}")
            print(f"Distance type: {distance_type}")

            if results:
                distances = []
                for r in results:
                    distance = r.get('_distance')
                    if distance is not None:
                        distances.append(distance)

                if distances:
                    analysis_result['summary']['average_distance'] = sum(distances) / len(distances)
                    analysis_result['summary']['min_distance'] = min(distances)
                    analysis_result['summary']['max_distance'] = max(distances)

                    print(f"Average distance: {analysis_result['summary']['average_distance']:.4f}")

                print("Top results:")
                for i, result in enumerate(results[:3]):
                    result_id = result.get('id', 'N/A')
                    distance = result.get('_distance', 0)
                    print(f"{i+1}. Distance: {distance:.4f} - ID: {result_id}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Vector search failed: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in vector_search_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def full_text_search_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting full_text_search_skill...")

    table_name = context.get('table_name')
    query_text = context.get('query_text')
    fields = context.get('fields', 'text')
    limit = context.get('limit', 10)

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name or not query_text:
            result = {"success": False, "error": "Table name and query text are required"}
            return LanceDBDataValue(result)

        response = client.full_text_search(
            table_name=table_name,
            query_text=query_text,
            fields=fields,
            limit=limit
        )

        if response.get('success'):
            results = response.get('results', [])

            analysis_result = {
                "success": True,
                "table_name": table_name,
                "query_type": "full_text",
                "query_text": query_text,
                "fields": fields,
                "results_count": len(results),
                "results": results,
                "summary": {
                    "limit": limit,
                    "fields_count": len(fields) if isinstance(fields, list) else 1
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Full text search completed: Found {len(results)} results")
            print(f"Table: {table_name}")
            print(f"Query: '{query_text}'")
            print(f"Fields: {fields}")

            if results:
                print("Top results:")
                for i, result in enumerate(results[:3]):
                    result_id = result.get('id', 'N/A')
                    score = result.get('_score', 0)
                    text_preview = str(result.get('text', ''))[:50]
                    print(f"{i+1}. Score: {score:.4f} - ID: {result_id}")
                    print(f"   Text: {text_preview}...")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Full text search failed: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in full_text_search_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def hybrid_search_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting hybrid_search_skill...")

    table_name = context.get('table_name')
    query_vector = context.get('query_vector', [])
    query_text = context.get('query_text')
    vector_column = context.get('vector_column', 'vector')
    text_fields = context.get('text_fields', 'text')
    limit = context.get('limit', 10)

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name or not query_vector or not query_text:
            result = {"success": False, "error": "Table name, query vector, and query text are required"}
            return LanceDBDataValue(result)

        response = client.hybrid_search(
            table_name=table_name,
            query_vector=query_vector,
            query_text=query_text,
            vector_column=vector_column,
            text_fields=text_fields,
            limit=limit
        )

        if response.get('success'):
            results = response.get('results', [])

            analysis_result = {
                "success": True,
                "table_name": table_name,
                "query_type": "hybrid",
                "vector_dimensions": len(query_vector),
                "query_text": query_text,
                "results_count": len(results),
                "results": results,
                "summary": {
                    "vector_column": vector_column,
                    "text_fields": text_fields,
                    "limit": limit
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Hybrid search completed: Found {len(results)} results")
            print(f"Table: {table_name}")
            print(f"Vector dimensions: {len(query_vector)}")
            print(f"Text query: '{query_text}'")

            if results:
                print("Top results:")
                for i, result in enumerate(results[:3]):
                    result_id = result.get('id', 'N/A')
                    distance = result.get('_distance', 0)
                    score = result.get('_score', 0)
                    text_preview = str(result.get('text', ''))[:50]
                    print(f"{i+1}. Distance: {distance:.4f}, Score: {score:.4f} - ID: {result_id}")
                    print(f"   Text: {text_preview}...")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Hybrid search failed: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in hybrid_search_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def create_index_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting create_index_skill...")

    table_name = context.get('table_name')
    column = context.get('column')
    index_type = context.get('index_type', 'vector')
    config = context.get('config', {})

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name or not column:
            result = {"success": False, "error": "Table name and column are required"}
            return LanceDBDataValue(result)

        response = client.create_index(
            table_name=table_name,
            column=column,
            index_type=index_type,
            config=config
        )

        if response.get('success'):
            analysis_result = {
                "success": True,
                "table_name": table_name,
                "column": column,
                "index_type": index_type,
                "config": config,
                "summary": {
                    "config_keys": list(config.keys())
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Index created: {column} in table {table_name}")
            print(f"Index type: {index_type}")
            print(f"Config parameters: {list(config.keys())}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "column": column,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Index creation failed: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in create_index_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def get_table_info_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting get_table_info_skill...")

    table_name = context.get('table_name')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name:
            result = {"success": False, "error": "Table name is required"}
            return LanceDBDataValue(result)

        response = client.get_table_info(table_name=table_name)

        if response.get('success'):
            info = response.get('info', {})

            analysis_result = {
                "success": True,
                "table_name": table_name,
                "info": info,
                "summary": {
                    "row_count": info.get('row_count', 'unknown'),
                    "version": info.get('version', 'unknown'),
                    "index_count": info.get('index_count', 0),
                    "field_count": info.get('schema', {}).get('field_count', 'unknown')
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Table info retrieved: {table_name}")
            print(f"Row count: {analysis_result['summary']['row_count']}")
            print(f"Version: {analysis_result['summary']['version']}")
            print(f"Field count: {analysis_result['summary']['field_count']}")

            schema_fields = info.get('schema', {}).get('fields', [])
            if schema_fields:
                print("Schema fields (first 5):")
                for field in schema_fields[:5]:
                    print(f"  - {field}")

            indices = info.get('indices', [])
            if indices:
                print(f"Indices ({len(indices)}):")
                for idx in indices:
                    print(f"  - {idx.get('name')} ({idx.get('type')})")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to get table info: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in get_table_info_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def update_data_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting update_data_skill...")

    table_name = context.get('table_name')
    updates = context.get('updates', {})
    where = context.get('where')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name or not updates:
            result = {"success": False, "error": "Table name and updates are required"}
            return LanceDBDataValue(result)

        response = client.update_data(
            table_name=table_name,
            updates=updates,
            where=where
        )

        if response.get('success'):
            analysis_result = {
                "success": True,
                "table_name": table_name,
                "operation": "update",
                "rows_updated": response.get('rows_updated', 'unknown'),
                "new_version": response.get('new_version', 'unknown'),
                "summary": {
                    "update_keys": list(updates.keys()),
                    "has_where_clause": where is not None
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Data updated in table: {table_name}")
            print(f"Rows updated: {analysis_result['rows_updated']}")
            print(f"Update keys: {analysis_result['summary']['update_keys']}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to update data: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in update_data_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def delete_data_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting delete_data_skill...")

    table_name = context.get('table_name')
    where = context.get('where')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name or not where:
            result = {"success": False, "error": "Table name and where clause are required"}
            return LanceDBDataValue(result)

        response = client.delete_data(
            table_name=table_name,
            where=where
        )

        if response.get('success'):
            analysis_result = {
                "success": True,
                "table_name": table_name,
                "operation": "delete",
                "new_version": response.get('new_version', 'unknown'),
                "summary": {
                    "where_clause": where
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Data deleted from table: {table_name}")
            print(f"Where clause: {where}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to delete data: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in delete_data_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def query_table_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting query_table_skill...")

    table_name = context.get('table_name')
    filter = context.get('filter')
    columns = context.get('columns')
    limit = context.get('limit')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name:
            result = {"success": False, "error": "Table name is required"}
            return LanceDBDataValue(result)

        response = client.query_table(
            table_name=table_name,
            filter=filter,
            columns=columns,
            limit=limit
        )

        if response.get('success'):
            results = response.get('results', [])

            analysis_result = {
                "success": True,
                "table_name": table_name,
                "query_type": "table_query",
                "results_count": len(results),
                "results": results,
                "summary": {
                    "filter": filter,
                    "columns": columns,
                    "limit": limit
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Table query completed: Found {len(results)} results")
            print(f"Table: {table_name}")

            if results:
                print("Sample results:")
                for i, result in enumerate(results[:3]):
                    result_id = result.get('id', 'N/A')
                    print(f"{i+1}. ID: {result_id}")
                    for key, value in list(result.items())[:3]:
                        if key != 'id':
                            print(f"   {key}: {str(value)[:50]}...")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Table query failed: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in query_table_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def drop_table_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting drop_table_skill...")

    table_name = context.get('table_name')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name:
            result = {"success": False, "error": "Table name is required"}
            return LanceDBDataValue(result)

        response = client.drop_table(table_name=table_name)

        if response.get('success'):
            analysis_result = {
                "success": True,
                "table_name": table_name,
                "status": "dropped",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Table dropped: {table_name}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to drop table: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in drop_table_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def list_indices_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting list_indices_skill...")

    table_name = context.get('table_name')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name:
            result = {"success": False, "error": "Table name is required"}
            return LanceDBDataValue(result)

        response = client.list_indices(table_name=table_name)

        if response.get('success'):
            indices = response.get('indices', [])

            analysis_result = {
                "success": True,
                "table_name": table_name,
                "indices_count": len(indices),
                "indices": indices,
                "summary": {
                    "index_names": [idx.get('name', '') for idx in indices],
                    "index_types": list(set(idx.get('type', 'unknown') for idx in indices))
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Found {len(indices)} indices in table: {table_name}")

            if indices:
                print("Indices:")
                for i, idx in enumerate(indices):
                    print(f"{i+1}. {idx.get('name')} - Type: {idx.get('type', 'unknown')}")
                    if idx.get('columns'):
                        print(f"   Columns: {idx.get('columns')}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to list indices: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in list_indices_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def drop_index_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting drop_index_skill...")

    table_name = context.get('table_name')
    index_name = context.get('index_name')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name or not index_name:
            result = {"success": False, "error": "Table name and index name are required"}
            return LanceDBDataValue(result)

        response = client.drop_index(
            table_name=table_name,
            index_name=index_name
        )

        if response.get('success'):
            analysis_result = {
                "success": True,
                "table_name": table_name,
                "index_name": index_name,
                "status": "dropped",
                "timestamp": datetime.now().isoformat()
            }

            print(f"Index dropped: {index_name} from table {table_name}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "index_name": index_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to drop index: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in drop_index_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def merge_insert_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting merge_insert_skill...")

    table_name = context.get('table_name')
    data = context.get('data')
    on = context.get('on')
    when_matched = context.get('when_matched', 'update_all')
    when_not_matched = context.get('when_not_matched', 'insert_all')

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name or not data or not on:
            result = {"success": False, "error": "Table name, data, and 'on' parameter are required"}
            return LanceDBDataValue(result)

        response = client.merge_insert(
            table_name=table_name,
            data=data,
            on=on,
            when_matched=when_matched,
            when_not_matched=when_not_matched
        )

        if response.get('success'):
            analysis_result = {
                "success": True,
                "table_name": table_name,
                "operation": "merge_insert",
                "new_version": response.get('new_version', 'unknown'),
                "summary": {
                    "on_columns": on if isinstance(on, list) else [on],
                    "when_matched": when_matched,
                    "when_not_matched": when_not_matched,
                    "data_count": len(data) if hasattr(data, '__len__') else 'unknown'
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Merge insert completed on table: {table_name}")
            print(f"Match condition: {on}")
            print(f"When matched: {when_matched}")
            print(f"When not matched: {when_not_matched}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Merge insert failed: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in merge_insert_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def optimize_table_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting optimize_table_skill...")

    table_name = context.get('table_name')
    cleanup_older_than = context.get('cleanup_older_than')
    retrain = context.get('retrain', False)

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        if not table_name:
            result = {"success": False, "error": "Table name is required"}
            return LanceDBDataValue(result)

        response = client.optimize_table(
            table_name=table_name,
            cleanup_older_than=cleanup_older_than,
            retrain=retrain
        )

        if response.get('success'):
            analysis_result = {
                "success": True,
                "table_name": table_name,
                "operation": "optimize",
                "summary": {
                    "cleanup_older_than_days": cleanup_older_than,
                    "retrain": retrain
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Table optimized: {table_name}")
            if cleanup_older_than:
                print(f"Cleanup older than: {cleanup_older_than} days")
            print(f"Retrain indices: {retrain}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "table_name": table_name,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Table optimization failed: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in optimize_table_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)

def create_embedding_function_skill(context: Dict[str, Any]) -> LanceDBDataValue:
    print("Starting create_embedding_function_skill...")

    function_type = context.get('function_type', 'sentence_transformer')
    config = context.get('config', {})

    try:
        client = context.get('lancedb_client')

        if not client:
            result = {"success": False, "error": "LanceDB client not available"}
            return LanceDBDataValue(result)

        response = client.create_embedding_function(
            function_type=function_type,
            config=config
        )

        if response.get('success'):
            analysis_result = {
                "success": True,
                "function_type": function_type,
                "model_name": response.get('model_name', 'unknown'),
                "summary": {
                    "config_keys": list(config.keys())
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"Embedding function created: {function_type}")
            print(f"Model: {analysis_result['model_name']}")
            print(f"Config: {list(config.keys())}")

        else:
            analysis_result = {
                "success": False,
                "error": response.get('error', 'Unknown error'),
                "function_type": function_type,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Failed to create embedding function: {response.get('error')}")

        return LanceDBDataValue(analysis_result)

    except Exception as e:
        print(f"Error in create_embedding_function_skill: {e}")
        result = {
            "success": False,
            "error": f"Skill execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return LanceDBDataValue(result)
