import lancedb
from typing import Optional, Dict, Any, List, Union
import pandas as pd
import pyarrow as pa
from datetime import timedelta

class LanceDBClientComponent:
    def __init__(self,
                 uri: str = "./.lancedb",
                 api_key: Optional[str] = None,
                 region: str = "us-east-1",
                 host_override: Optional[str] = None,
                 read_consistency_interval: Optional[int] = None,
                 client_config: Optional[Dict[str, Any]] = None,
                 storage_options: Optional[Dict[str, str]] = None,
                 mode: str = "sync"):
        self.uri = uri
        self.api_key = api_key
        self.region = region
        self.host_override = host_override
        self.read_consistency_interval = read_consistency_interval
        self.client_config = client_config or {}
        self.storage_options = storage_options or {}
        self.mode = mode

        print(f"🔗 Connecting to LanceDB at {uri}")

        try:
            if mode == "async":
                print("Async mode selected - connections will be established per operation")
                self.db = None
                self.async_db = None
            else:
                connect_args = {
                    'uri': uri,
                    'api_key': api_key,
                    'region': region,
                    'host_override': host_override,
                }

                if read_consistency_interval is not None:
                    connect_args['read_consistency_interval'] = timedelta(seconds=read_consistency_interval)

                if client_config:
                    connect_args['client_config'] = client_config

                if storage_options:
                    connect_args['storage_options'] = storage_options

                print(f"   Connection args: { {k: v for k, v in connect_args.items() if k != 'api_key'} }")

                self.db = lancedb.connect(**connect_args)
                print("✅ Connected to LanceDB (sync mode)")

        except Exception as e:
            print(f"❌ Failed to create LanceDB client: {e}")
            raise

    def test_connection(self) -> bool:
        try:
            if self.mode == "async":
                import lancedb
                return True
            else:
                return self.db is not None
        except:
            return False

    def create_table(self,
                    table_name: str,
                    data: Optional[Union[List[Dict], pd.DataFrame, pa.Table]] = None,
                    schema: Optional[Union[pa.Schema, Any]] = None,
                    mode: str = 'create',
                    exist_ok: bool = False,
                    embedding_functions: Optional[List[Any]] = None) -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            create_args = {
                'name': table_name,
                'mode': mode,
                'exist_ok': exist_ok
            }

            if data is not None:
                create_args['data'] = data

            if schema is not None:
                create_args['schema'] = schema

            if embedding_functions is not None:
                create_args['embedding_functions'] = embedding_functions

            table = self.db.create_table(**create_args)

            return {
                "success": True,
                "table_name": table_name,
                "status": "created" if mode == 'create' else "overwritten",
                "table_info": {
                    "name": table.name,
                    "version": table.version,
                    "schema": str(table.schema) if hasattr(table, 'schema') else "unknown"
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create table: {str(e)}"
            }

    def open_table(self, table_name: str) -> Dict[str, Any]:
        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            return {
                "success": True,
                "table_name": table_name,
                "table_info": {
                    "name": table.name,
                    "version": table.version,
                    "schema": str(table.schema) if hasattr(table, 'schema') else "unknown"
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to open table: {str(e)}"
            }

    def list_tables(self) -> Dict[str, Any]:
        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            tables = self.db.table_names()

            table_infos = []
            for table_name in tables:
                try:
                    table = self.db.open_table(table_name)
                    table_infos.append({
                        "name": table_name,
                        "version": table.version if hasattr(table, 'version') else "unknown"
                    })
                except:
                    table_infos.append({"name": table_name, "version": "unknown"})

            return {
                "success": True,
                "tables_count": len(tables),
                "tables": table_infos
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list tables: {str(e)}"
            }

    def add_data(self,
                table_name: str,
                data: Union[List[Dict], pd.DataFrame, pa.Table],
                mode: str = 'append') -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            result = table.add(data, mode=mode)

            return {
                "success": True,
                "table_name": table_name,
                "operation": mode,
                "new_version": result.version if hasattr(result, 'version') else "unknown",
                "rows_added": len(data) if hasattr(data, '__len__') else "unknown"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to add data: {str(e)}"
            }

    def vector_search(self,
                     table_name: str,
                     query_vector: List[float],
                     vector_column: str = "vector",
                     limit: int = 10,
                     filter: Optional[str] = None,
                     distance_type: str = "l2") -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            query = table.search(query_vector, vector_column_name=vector_column)

            if filter:
                query = query.where(filter)

            query = query.limit(limit).metric(distance_type)

            results_df = query.to_pandas()

            formatted_results = []
            for _, row in results_df.iterrows():
                result_dict = row.to_dict()
                formatted_results.append(result_dict)

            return {
                "success": True,
                "table_name": table_name,
                "query_type": "vector",
                "vector_dimensions": len(query_vector),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "distance_type": distance_type
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Vector search failed: {str(e)}"
            }

    def full_text_search(self,
                        table_name: str,
                        query_text: str,
                        fields: Union[str, List[str]],
                        limit: int = 10) -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            if hasattr(table, 'create_fts_index'):
                query = table.search(query_text, query_type="fts")
                if isinstance(fields, str):
                    fields = [fields]
            else:
                query = table.search()
                if isinstance(fields, str):
                    filter_cond = f"{fields} LIKE '%{query_text}%'"
                else:
                    conditions = [f"{field} LIKE '%{query_text}%'" for field in fields]
                    filter_cond = " OR ".join(conditions)
                query = query.where(filter_cond)

            query = query.limit(limit)
            results_df = query.to_pandas()

            formatted_results = []
            for _, row in results_df.iterrows():
                result_dict = row.to_dict()
                formatted_results.append(result_dict)

            return {
                "success": True,
                "table_name": table_name,
                "query_type": "full_text",
                "query_text": query_text,
                "fields": fields,
                "results_count": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Full text search failed: {str(e)}"
            }

    def hybrid_search(self,
                     table_name: str,
                     query_vector: List[float],
                     query_text: str,
                     vector_column: str = "vector",
                     text_fields: Union[str, List[str]] = "text",
                     limit: int = 10) -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            query = table.search(query_vector, vector_column_name=vector_column)

            from lancedb.query import LanceHybridQueryBuilder
            if isinstance(query, LanceHybridQueryBuilder):
                query = query.nearest_to_text(query_text, columns=text_fields)

            query = query.limit(limit)

            results_df = query.to_pandas()

            formatted_results = []
            for _, row in results_df.iterrows():
                result_dict = row.to_dict()
                formatted_results.append(result_dict)

            return {
                "success": True,
                "table_name": table_name,
                "query_type": "hybrid",
                "vector_dimensions": len(query_vector),
                "query_text": query_text,
                "results_count": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Hybrid search failed: {str(e)}"
            }

    def create_index(self,
                    table_name: str,
                    column: str,
                    index_type: str = 'vector',
                    config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)
            config = config or {}

            if index_type == 'vector':
                index_config = {
                    'metric': config.get('metric', 'l2'),
                    'num_partitions': config.get('num_partitions', 256),
                    'num_sub_vectors': config.get('num_sub_vectors', 96),
                    'vector_column_name': column,
                    'replace': config.get('replace', True)
                }

                if 'accelerator' in config:
                    index_config['accelerator'] = config['accelerator']

                table.create_index(**index_config)

            elif index_type == 'full_text':
                if hasattr(table, 'create_fts_index'):
                    table.create_fts_index(
                        field_names=column,
                        replace=config.get('replace', False)
                    )
                else:
                    return {
                        "success": False,
                        "error": "FTS index not supported in this version"
                    }

            elif index_type == 'scalar':
                if hasattr(table, 'create_scalar_index'):
                    table.create_scalar_index(
                        column=column,
                        replace=config.get('replace', True),
                        index_type=config.get('scalar_index_type', 'BTREE')
                    )
                else:
                    return {
                        "success": False,
                        "error": "Scalar index not supported in this version"
                    }

            else:
                return {
                    "success": False,
                    "error": f"Unknown index type: {index_type}"
                }

            return {
                "success": True,
                "table_name": table_name,
                "column": column,
                "index_type": index_type,
                "config": config
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create index: {str(e)}"
            }

    def drop_table(self, table_name: str) -> Dict[str, Any]:
        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            self.db.drop_table(table_name)

            return {
                "success": True,
                "table_name": table_name,
                "status": "dropped"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to drop table: {str(e)}"
            }

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            info = {
                "name": table_name,
                "version": table.version if hasattr(table, 'version') else "unknown"
            }

            if hasattr(table, 'schema'):
                schema = table.schema
                info['schema'] = {
                    "fields": [str(field) for field in schema],
                    "field_count": len(schema)
                }

            if hasattr(table, 'count_rows'):
                try:
                    info['row_count'] = table.count_rows()
                except:
                    info['row_count'] = "unknown"

            if hasattr(table, 'list_indices'):
                try:
                    indices = list(table.list_indices())
                    info['indices'] = [
                        {
                            "name": idx.get('name', 'unknown'),
                            "type": idx.get('type', 'unknown')
                        }
                        for idx in indices
                    ]
                    info['index_count'] = len(indices)
                except:
                    info['indices'] = []
                    info['index_count'] = 0

            return {
                "success": True,
                "table_name": table_name,
                "info": info
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get table info: {str(e)}"
            }

    def update_data(self,
                   table_name: str,
                   updates: Dict[str, Any],
                   where: Optional[str] = None) -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            if hasattr(table, 'update'):
                result = table.update(where=where, values=updates)

                return {
                    "success": True,
                    "table_name": table_name,
                    "operation": "update",
                    "rows_updated": result.rows_updated if hasattr(result, 'rows_updated') else "unknown",
                    "new_version": result.version if hasattr(result, 'version') else "unknown"
                }
            else:
                return {
                    "success": False,
                    "error": "Update operation not supported in this version"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update data: {str(e)}"
            }

    def delete_data(self,
                   table_name: str,
                   where: str) -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            if hasattr(table, 'delete'):
                result = table.delete(where=where)

                return {
                    "success": True,
                    "table_name": table_name,
                    "operation": "delete",
                    "new_version": result.version if hasattr(result, 'version') else "unknown"
                }
            else:
                return {
                    "success": False,
                    "error": "Delete operation not supported in this version"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete data: {str(e)}"
            }

    def query_table(self,
                   table_name: str,
                   filter: Optional[str] = None,
                   columns: Optional[List[str]] = None,
                   limit: Optional[int] = None) -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            query = table.search()

            if filter:
                query = query.where(filter)

            if columns:
                query = query.select(columns)

            if limit:
                query = query.limit(limit)

            results_df = query.to_pandas()

            formatted_results = []
            for _, row in results_df.iterrows():
                result_dict = row.to_dict()
                formatted_results.append(result_dict)

            return {
                "success": True,
                "table_name": table_name,
                "query_type": "table_query",
                "filter": filter,
                "columns": columns,
                "limit": limit,
                "results_count": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Table query failed: {str(e)}"
            }

    def list_indices(self, table_name: str) -> Dict[str, Any]:
        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            if hasattr(table, 'list_indices'):
                indices = list(table.list_indices())

                formatted_indices = []
                for idx in indices:
                    idx_info = {
                        "name": idx.get('name', 'unknown'),
                        "type": idx.get('type', 'unknown'),
                        "columns": idx.get('columns', []),
                        "config": idx.get('config', {})
                    }
                    formatted_indices.append(idx_info)

                return {
                    "success": True,
                    "table_name": table_name,
                    "indices_count": len(formatted_indices),
                    "indices": formatted_indices
                }
            else:
                return {
                    "success": False,
                    "error": "list_indices operation not supported in this version"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list indices: {str(e)}"
            }

    def drop_index(self,
                  table_name: str,
                  index_name: str) -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            if hasattr(table, 'drop_index'):
                table.drop_index(index_name)

                return {
                    "success": True,
                    "table_name": table_name,
                    "index_name": index_name,
                    "status": "dropped"
                }
            else:
                return {
                    "success": False,
                    "error": "drop_index operation not supported in this version"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to drop index: {str(e)}"
            }

    def merge_insert(self,
                    table_name: str,
                    data: Union[List[Dict], pd.DataFrame, pa.Table],
                    on: Union[str, List[str]],
                    when_matched: str = 'update_all',
                    when_not_matched: str = 'insert_all') -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            if hasattr(table, 'merge_insert'):
                builder = table.merge_insert(on)

                if when_matched == 'update_all':
                    builder = builder.when_matched_update_all()
                elif when_matched == 'keep':
                    pass

                if when_not_matched == 'insert_all':
                    builder = builder.when_not_matched_insert_all()
                elif when_not_matched == 'ignore':
                    pass

                result = builder.execute(data)

                return {
                    "success": True,
                    "table_name": table_name,
                    "operation": "merge_insert",
                    "new_version": result.version if hasattr(result, 'version') else "unknown",
                    "matched_action": when_matched,
                    "not_matched_action": when_not_matched
                }
            else:
                return {
                    "success": False,
                    "error": "merge_insert operation not supported in this version"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Merge insert failed: {str(e)}"
            }

    def optimize_table(self,
                      table_name: str,
                      cleanup_older_than: Optional[int] = None,
                      retrain: bool = False) -> Dict[str, Any]:

        try:
            if self.mode == "async":
                return {"success": False, "error": "Async mode not yet implemented for this operation"}

            if self.db is None:
                return {"success": False, "error": "Database not connected"}

            table = self.db.open_table(table_name)

            if hasattr(table, 'optimize'):
                if cleanup_older_than is not None:
                    table.optimize(cleanup_older_than=timedelta(days=cleanup_older_than), retrain=retrain)
                else:
                    table.optimize(retrain=retrain)

                return {
                    "success": True,
                    "table_name": table_name,
                    "operation": "optimize",
                    "cleanup_older_than_days": cleanup_older_than,
                    "retrain": retrain
                }
            else:
                return {
                    "success": False,
                    "error": "optimize operation not supported in this version"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Table optimization failed: {str(e)}"
            }

    def create_embedding_function(self,
                                 function_type: str = 'sentence_transformer',
                                 config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            config = config or {}

            if function_type == 'sentence_transformer':
                from lancedb.embeddings import get_registry
                registry = get_registry()

                model_name = config.get('model_name', 'all-MiniLM-L6-v2')
                device = config.get('device', None)
                normalize = config.get('normalize', True)

                embedding_fn = registry.get("sentence-transformers").create(
                    name=model_name,
                    device=device,
                    normalize=normalize
                )

                return {
                    "success": True,
                    "function_type": function_type,
                    "model_name": model_name,
                    "embedding_function": embedding_fn
                }

            elif function_type == 'openai':
                from lancedb.embeddings import get_registry
                registry = get_registry()

                model_name = config.get('model_name', 'text-embedding-ada-002')
                api_key = config.get('api_key', None)
                base_url = config.get('base_url', None)

                embedding_fn = registry.get("openai").create(
                    name=model_name,
                    api_key=api_key,
                    base_url=base_url
                )

                return {
                    "success": True,
                    "function_type": function_type,
                    "model_name": model_name,
                    "embedding_function": embedding_fn
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown embedding function type: {function_type}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create embedding function: {str(e)}"
            }

    def close(self):
        pass
