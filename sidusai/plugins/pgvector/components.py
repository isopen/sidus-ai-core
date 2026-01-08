import psycopg2
from psycopg2.extras import Json, execute_batch, RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from typing import List, Dict, Any, Optional
import time
from threading import Lock

class PgVectorClientComponent:
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 5432,
                 database: str = "postgres",
                 user: str = "postgres",
                 password: str = "",
                 schema: str = "public",
                 table_prefix: str = "vectors_",
                 connection_pool_size: int = 5,
                 ssl_mode: str = "prefer"):

        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.schema = schema
        self.table_prefix = table_prefix
        self.connection_pool_size = connection_pool_size
        self.ssl_mode = ssl_mode

        self.connection_pool = None
        self._lock = Lock()
        self._initialize_pool()

        self._ensure_extension()

    def _initialize_pool(self):
        try:
            self.connection_pool = SimpleConnectionPool(
                1,
                self.connection_pool_size,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                sslmode=self.ssl_mode
            )
        except Exception as e:
            raise ConnectionError(f"Failed to create connection pool: {str(e)}")

    def _get_connection(self):
        try:
            conn = self.connection_pool.getconn()
            if conn.closed:
                conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    sslmode=self.ssl_mode
                )
            return conn
        except Exception as e:
            raise ConnectionError(f"Failed to get connection from pool: {str(e)}")

    def _return_connection(self, conn):
        if conn:
            try:
                if not conn.closed:
                    conn.rollback()
                self.connection_pool.putconn(conn)
            except Exception:
                try:
                    conn.close()
                except:
                    pass

    def _execute_query(self, query: str, params: tuple = None, fetch: bool = False, commit: bool = False):
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if commit:
                conn.commit()

            if fetch:
                result = cursor.fetchall()
                return result
            else:
                return cursor.rowcount

        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                self._return_connection(conn)

    def _execute_query_dict(self, query: str, params: tuple = None, fetch: bool = False, commit: bool = False):
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if commit:
                conn.commit()

            if fetch:
                result = cursor.fetchall()
                return [dict(row) for row in result]
            else:
                return cursor.rowcount

        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                self._return_connection(conn)

    def _ensure_extension(self):
        try:
            self._execute_query("CREATE EXTENSION IF NOT EXISTS vector", commit=True)
        except Exception as e:
            print(f"Warning: Could not create vector extension: {str(e)}")

    def _get_full_table_name(self, table_name: str) -> str:
        return f"{self.schema}.{self.table_prefix}{table_name}"

    def test_connection(self) -> bool:
        try:
            self._execute_query("SELECT 1")
            return True
        except Exception:
            return False

    def create_vector_extension(self) -> Dict[str, Any]:
        try:
            self._execute_query("CREATE EXTENSION IF NOT EXISTS vector", commit=True)
            return {"success": True, "message": "Vector extension created or already exists"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_table(self,
                    table_name: str,
                    vector_dimension: int = 1536,
                    metadata_columns: Optional[Dict[str, str]] = None,
                    with_hnsw: bool = False,
                    hnsw_m: int = 16,
                    hnsw_ef_construction: int = 64) -> Dict[str, Any]:

        try:
            full_table_name = self._get_full_table_name(table_name)

            columns = [
                "id BIGSERIAL PRIMARY KEY",
                f"embedding vector({vector_dimension})",
                "content TEXT",
                "metadata JSONB DEFAULT '{}'::jsonb",
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ]

            if metadata_columns:
                for col_name, col_type in metadata_columns.items():
                    columns.append(f"{col_name} {col_type}")

            columns_str = ", ".join(columns)

            self._execute_query(f"""
                CREATE TABLE IF NOT EXISTS {full_table_name} (
                    {columns_str}
                )
            """, commit=True)

            return {
                "success": True,
                "table_name": full_table_name,
                "vector_dimension": vector_dimension,
                "has_hnsw_index": False
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def modify_table(self,
                    table_name: str,
                    add_columns: Optional[Dict[str, str]] = None,
                    drop_columns: Optional[List[str]] = None,
                    rename_columns: Optional[Dict[str, str]] = None) -> Dict[str, Any]:

        try:
            full_table_name = self._get_full_table_name(table_name)
            queries = []

            if add_columns:
                for col_name, col_type in add_columns.items():
                    queries.append(f"ALTER TABLE {full_table_name} ADD COLUMN IF NOT EXISTS {col_name} {col_type}")

            if drop_columns:
                for col_name in drop_columns:
                    queries.append(f"ALTER TABLE {full_table_name} DROP COLUMN IF EXISTS {col_name}")

            if rename_columns:
                for old_name, new_name in rename_columns.items():
                    queries.append(f"ALTER TABLE {full_table_name} RENAME COLUMN {old_name} TO {new_name}")

            for query in queries:
                self._execute_query(query, commit=True)

            return {
                "success": True,
                "table_name": full_table_name,
                "operations_count": len(queries)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_index(self,
                    table_name: str,
                    index_type: str = "hnsw",
                    distance_metric: str = "l2",
                    hnsw_m: int = 16,
                    hnsw_ef_construction: int = 64,
                    ivfflat_lists: int = 100,
                    concurrently: bool = False) -> Dict[str, Any]:

        try:
            full_table_name = self._get_full_table_name(table_name)

            if distance_metric == "l2":
                ops = "vector_l2_ops"
            elif distance_metric == "cosine":
                ops = "vector_cosine_ops"
            elif distance_metric == "ip":
                ops = "vector_ip_ops"
            elif distance_metric == "l1":
                ops = "vector_l1_ops"
            else:
                return {"success": False, "error": f"Unsupported distance metric: {distance_metric}"}

            index_name = f"idx_{self.table_prefix}{table_name}_{index_type}_{distance_metric}"

            if index_type == "hnsw":
                index_sql = f"""
                    CREATE INDEX {"CONCURRENTLY" if concurrently else ""} {index_name}
                    ON {full_table_name} 
                    USING hnsw (embedding {ops}) 
                    WITH (m = %s, ef_construction = %s)
                """
                params = (hnsw_m, hnsw_ef_construction)
            elif index_type == "ivfflat":
                index_sql = f"""
                    CREATE INDEX {"CONCURRENTLY" if concurrently else ""} {index_name}
                    ON {full_table_name} 
                    USING ivfflat (embedding {ops}) 
                    WITH (lists = %s)
                """
                params = (ivfflat_lists,)
            else:
                return {"success": False, "error": f"Unsupported index type: {index_type}"}

            try:
                self._execute_query(index_sql, params, commit=True)
            except Exception as e:
                if "already exists" in str(e):
                    return {
                        "success": False, 
                        "error": f"Index {index_name} already exists",
                        "index_name": index_name
                    }
                raise e

            return {
                "success": True,
                "index_name": index_name,
                "index_type": index_type,
                "distance_metric": distance_metric
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def insert_vectors(self,
                      table_name: str,
                      vectors: List[List[float]],
                      metadata_list: Optional[List[Dict[str, Any]]] = None,
                      ids: Optional[List[Any]] = None,
                      content_list: Optional[List[str]] = None) -> Dict[str, Any]:

        try:
            if not vectors:
                return {"success": False, "error": "No vectors provided"}

            full_table_name = self._get_full_table_name(table_name)

            if metadata_list is None:
                metadata_list = [{} for _ in range(len(vectors))]

            if content_list is None:
                content_list = ["" for _ in range(len(vectors))]

            if ids is None:
                ids = list(range(1, len(vectors) + 1))

            if not (len(vectors) == len(metadata_list) == len(content_list) == len(ids)):
                return {"success": False, "error": "All lists must have the same length"}

            conn = self._get_connection()
            cursor = conn.cursor()

            try:
                insert_sql = f"""
                    INSERT INTO {full_table_name} (id, embedding, content, metadata)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        embedding = EXCLUDED.embedding,
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                """

                data = []
                for i, (vector, metadata, content, vector_id) in enumerate(zip(vectors, metadata_list, content_list, ids)):
                    vector_str = "[" + ",".join(str(float(x)) for x in vector) + "]"
                    data.append((vector_id, vector_str, content, Json(metadata)))

                execute_batch(cursor, insert_sql, data)
                conn.commit()

                return {
                    "success": True,
                    "count": len(vectors),
                    "table_name": full_table_name
                }

            finally:
                cursor.close()
                self._return_connection(conn)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def query_vectors(self,
                     table_name: str,
                     query_vector: List[float],
                     limit: int = 10,
                     distance_metric: str = "l2",
                     return_columns: Optional[List[str]] = None,
                     hnsw_ef_search: Optional[int] = None,
                     ivfflat_probes: Optional[int] = None) -> Dict[str, Any]:

        try:
            full_table_name = self._get_full_table_name(table_name)

            if distance_metric == "l2":
                operator = "<->"
            elif distance_metric == "cosine":
                operator = "<=>"
            elif distance_metric == "ip":
                operator = "<#>"
            elif distance_metric == "l1":
                operator = "<+>"
            else:
                return {"success": False, "error": f"Unsupported distance metric: {distance_metric}"}

            if return_columns is None:
                return_columns = ["id", "content", "metadata"]

            query_vector_str = "[" + ",".join(str(float(x)) for x in query_vector) + "]"

            conn = self._get_connection()
            cursor = conn.cursor()

            try:
                query = f"""
                    SELECT {', '.join(return_columns)}, 
                           embedding {operator} %s::vector AS distance
                    FROM {full_table_name}
                    ORDER BY embedding {operator} %s::vector
                    LIMIT %s
                """

                cursor.execute(query, (query_vector_str, query_vector_str, limit))

                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]

                formatted_results = []
                for row in results:
                    result_dict = {}
                    for i, col_name in enumerate(column_names):
                        value = row[i]
                        if hasattr(value, 'isoformat'):
                            value = value.isoformat()
                        elif isinstance(value, dict):
                            value = dict(value)
                        result_dict[col_name] = value
                    formatted_results.append(result_dict)

                return {
                    "success": True,
                    "results": formatted_results,
                    "query_vector": query_vector,
                    "distance_metric": distance_metric,
                    "limit": limit,
                    "count": len(formatted_results)
                }

            finally:
                cursor.close()
                self._return_connection(conn)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_with_filter(self,
                          table_name: str,
                          query_vector: List[float],
                          filter_conditions: Dict[str, Any],
                          limit: int = 10,
                          distance_metric: str = "l2",
                          hnsw_ef_search: Optional[int] = None) -> Dict[str, Any]:

        try:
            full_table_name = self._get_full_table_name(table_name)

            if distance_metric == "l2":
                operator = "<->"
            elif distance_metric == "cosine":
                operator = "<=>"
            elif distance_metric == "ip":
                operator = "<#>"
            elif distance_metric == "l1":
                operator = "<+>"
            else:
                return {"success": False, "error": f"Unsupported distance metric: {distance_metric}"}

            query_vector_str = "[" + ",".join(str(float(x)) for x in query_vector) + "]"

            where_parts = []
            params = []

            for key, value in filter_conditions.items():
                if isinstance(value, list):
                    placeholders = ",".join(["%s"] * len(value))
                    where_parts.append(f"metadata->>'{key}' IN ({placeholders})")
                    params.extend([str(v) for v in value])
                elif isinstance(value, dict):
                    if "range" in value:
                        where_parts.append(f"(metadata->>'{key}')::numeric BETWEEN %s AND %s")
                        params.append(value["range"][0])
                        params.append(value["range"][1])
                    elif "like" in value:
                        where_parts.append(f"metadata->>'{key}' LIKE %s")
                        params.append(value["like"])
                else:
                    where_parts.append(f"metadata->>'{key}' = %s")
                    params.append(str(value))

            where_clause = ""
            if where_parts:
                where_clause = "WHERE " + " AND ".join(where_parts)

            conn = self._get_connection()
            cursor = conn.cursor()

            try:
                base_query = f"""
                    SELECT id, content, metadata,
                           embedding {operator} %s::vector AS distance
                    FROM {full_table_name}
                    {where_clause}
                """

                if where_parts:
                    cursor.execute(base_query + " ORDER BY embedding " + operator + " %s::vector LIMIT %s", 
                                 (query_vector_str, *params, query_vector_str, limit))
                else:
                    cursor.execute(base_query + " ORDER BY embedding " + operator + " %s::vector LIMIT %s", 
                                 (query_vector_str, query_vector_str, limit))

                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]

                formatted_results = []
                for row in results:
                    result_dict = {}
                    for i, col_name in enumerate(column_names):
                        value = row[i]
                        if hasattr(value, 'isoformat'):
                            value = value.isoformat()
                        elif isinstance(value, dict):
                            value = dict(value)
                        result_dict[col_name] = value
                    formatted_results.append(result_dict)

                return {
                    "success": True,
                    "results": formatted_results,
                    "query_vector": query_vector,
                    "filter_conditions": filter_conditions,
                    "limit": limit,
                    "count": len(formatted_results)
                }

            finally:
                cursor.close()
                self._return_connection(conn)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def hybrid_search(self,
                     table_name: str,
                     query_text: str,
                     query_vector: List[float],
                     limit: int = 10,
                     text_weight: float = 0.5,
                     vector_weight: float = 0.5,
                     distance_metric: str = "l2") -> Dict[str, Any]:

        try:
            full_table_name = self._get_full_table_name(table_name)

            if distance_metric == "l2":
                operator = "<->"
            elif distance_metric == "cosine":
                operator = "<=>"
            elif distance_metric == "ip":
                operator = "<#>"
            elif distance_metric == "l1":
                operator = "<+>"
            else:
                return {"success": False, "error": f"Unsupported distance metric: {distance_metric}"}

            query_vector_str = "[" + ",".join(str(float(x)) for x in query_vector) + "]"

            conn = self._get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(f"""
                    WITH vector_scores AS (
                        SELECT id, 
                               embedding {operator} %s::vector AS vector_distance,
                               ROW_NUMBER() OVER (ORDER BY embedding {operator} %s::vector) as vector_rank
                        FROM {full_table_name}
                        WHERE content ILIKE %s
                    ),
                    text_scores AS (
                        SELECT id,
                               ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) as text_score,
                               ROW_NUMBER() OVER (ORDER BY ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) DESC) as text_rank
                        FROM {full_table_name}
                        WHERE content ILIKE %s
                    )
                    SELECT v.id, 
                           t.content,
                           t.metadata,
                           v.vector_distance,
                           ts.text_score,
                           (%s * (1.0 / NULLIF(v.vector_rank, 0))) + (%s * COALESCE(ts.text_score, 0)) as combined_score
                    FROM vector_scores v
                    JOIN {full_table_name} t ON v.id = t.id
                    LEFT JOIN text_scores ts ON v.id = ts.id
                    ORDER BY combined_score DESC
                    LIMIT %s
                """, (
                    query_vector_str, query_vector_str,
                    f"%{query_text}%",
                    query_text, query_text, f"%{query_text}%",
                    vector_weight, text_weight,
                    limit
                ))

                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]

                formatted_results = []
                for row in results:
                    result_dict = {}
                    for i, col_name in enumerate(column_names):
                        value = row[i]
                        if hasattr(value, 'isoformat'):
                            value = value.isoformat()
                        elif isinstance(value, dict):
                            value = dict(value)
                        result_dict[col_name] = value
                    formatted_results.append(result_dict)

                return {
                    "success": True,
                    "results": formatted_results,
                    "query_text": query_text,
                    "query_vector": query_vector,
                    "text_weight": text_weight,
                    "vector_weight": vector_weight,
                    "limit": limit,
                    "count": len(formatted_results)
                }

            except Exception as e:
                print(f"Hybrid search fallback to vector search: {e}")
                return self.query_vectors(
                    table_name=table_name,
                    query_vector=query_vector,
                    limit=limit,
                    distance_metric=distance_metric
                )

            finally:
                cursor.close()
                self._return_connection(conn)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_vectors(self,
                      table_name: str,
                      ids: Optional[List[Any]] = None,
                      filter_conditions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            full_table_name = self._get_full_table_name(table_name)

            where_conditions = []
            params = []

            if ids:
                placeholders = ",".join(["%s"] * len(ids))
                where_conditions.append(f"id IN ({placeholders})")
                params.extend(ids)

            if filter_conditions:
                for key, value in filter_conditions.items():
                    if isinstance(value, list):
                        if not value:
                            continue
                        placeholders = ",".join(["%s"] * len(value))
                        where_conditions.append(f"metadata->>'{key}' IN ({placeholders})")
                        params.extend([str(v) for v in value])
                    else:
                        where_conditions.append(f"metadata->>'{key}' = %s")
                        params.append(str(value))

            if not where_conditions:
                return {"success": False, "error": "No deletion criteria provided"}

            where_clause = "WHERE " + " AND ".join(where_conditions)

            conn = self._get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(f"""
                    DELETE FROM {full_table_name}
                    {where_clause}
                    RETURNING id
                """, tuple(params))

                deleted_ids = [row[0] for row in cursor.fetchall()]
                conn.commit()

                return {
                    "success": True,
                    "deleted_count": len(deleted_ids),
                    "deleted_ids": deleted_ids,
                    "table_name": full_table_name
                }

            finally:
                cursor.close()
                self._return_connection(conn)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_vectors(self,
                      table_name: str,
                      ids: List[Any],
                      vectors: Optional[List[List[float]]] = None,
                      metadata_list: Optional[List[Dict[str, Any]]] = None,
                      content_list: Optional[List[str]] = None) -> Dict[str, Any]:

        try:
            if not ids:
                return {"success": False, "error": "No IDs provided"}

            full_table_name = self._get_full_table_name(table_name)

            update_count = 0

            for i, vector_id in enumerate(ids):
                update_parts = []
                params = []

                if vectors and i < len(vectors):
                    vector_str = "[" + ",".join(str(float(x)) for x in vectors[i]) + "]"
                    update_parts.append("embedding = %s")
                    params.append(vector_str)

                if metadata_list and i < len(metadata_list):
                    update_parts.append("metadata = %s")
                    params.append(Json(metadata_list[i]))

                if content_list and i < len(content_list):
                    update_parts.append("content = %s")
                    params.append(content_list[i])

                if update_parts:
                    update_parts.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(vector_id)

                    update_sql = f"""
                        UPDATE {full_table_name}
                        SET {', '.join(update_parts)}
                        WHERE id = %s
                    """

                    conn = self._get_connection()
                    cursor = conn.cursor()

                    try:
                        cursor.execute(update_sql, tuple(params))
                        update_count += cursor.rowcount
                        conn.commit()
                    finally:
                        cursor.close()
                        self._return_connection(conn)

            return {
                "success": True,
                "updated_count": update_count,
                "table_name": full_table_name
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_table_info(self,
                      table_name: str) -> Dict[str, Any]:

        try:
            full_table_name = self._get_full_table_name(table_name)
            simple_table_name = f"{self.table_prefix}{table_name}"

            conn = self._get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as row_count,
                        MIN(created_at) as oldest_record,
                        MAX(created_at) as newest_record
                    FROM {full_table_name}
                """)

                stats = cursor.fetchone()

                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = %s 
                    AND table_name = %s
                    ORDER BY ordinal_position
                """, (self.schema, simple_table_name))

                columns = cursor.fetchall()

                cursor.execute(f"""
                    SELECT indexname, indexdef 
                    FROM pg_indexes 
                    WHERE schemaname = %s 
                    AND tablename = %s
                """, (self.schema, simple_table_name))

                indexes = cursor.fetchall()

                return {
                    "success": True,
                    "table_name": full_table_name,
                    "row_count": stats[0] if stats else 0,
                    "oldest_record": stats[1].isoformat() if stats and stats[1] else None,
                    "newest_record": stats[2].isoformat() if stats and stats[2] else None,
                    "columns": [{"name": col[0], "type": col[1], "nullable": col[2]} for col in columns],
                    "indexes": [{"name": idx[0], "definition": idx[1]} for idx in indexes]
                }

            finally:
                cursor.close()
                self._return_connection(conn)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_tables(self,
                   pattern: Optional[str] = None,
                   limit: int = 100) -> Dict[str, Any]:

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            try:
                if pattern:
                    query = """
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = %s 
                        AND table_name LIKE %s
                        LIMIT %s
                    """
                    search_pattern = f"{self.table_prefix}%{pattern}%"
                    cursor.execute(query, (self.schema, search_pattern, limit))
                else:
                    query = """
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = %s 
                        AND table_name LIKE %s
                        LIMIT %s
                    """
                    cursor.execute(query, (self.schema, f"{self.table_prefix}%", limit))

                tables = [row[0] for row in cursor.fetchall()]

                return {
                    "success": True,
                    "tables": tables,
                    "total_count": len(tables),
                    "limit": limit,
                    "schema": self.schema
                }

            finally:
                cursor.close()
                self._return_connection(conn)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def bulk_insert(self,
                   table_name: str,
                   vectors: List[List[float]],
                   metadata_list: List[Dict[str, Any]],
                   content_list: List[str],
                   batch_size: int = 1000) -> Dict[str, Any]:

        try:
            if len(vectors) != len(metadata_list) or len(vectors) != len(content_list):
                return {"success": False, "error": "All lists must have the same length"}

            full_table_name = self._get_full_table_name(table_name)

            total_inserted = 0
            batch_count = 0
            start_time = time.time()

            for i in range(0, len(vectors), batch_size):
                batch_vectors = vectors[i:i+batch_size]
                batch_metadata = metadata_list[i:i+batch_size]
                batch_content = content_list[i:i+batch_size]

                batch_ids = list(range(total_inserted + 1, total_inserted + len(batch_vectors) + 1))

                result = self.insert_vectors(
                    table_name=table_name,
                    vectors=batch_vectors,
                    metadata_list=batch_metadata,
                    ids=batch_ids,
                    content_list=batch_content
                )

                if not result["success"]:
                    return result

                total_inserted += len(batch_vectors)
                batch_count += 1

            end_time = time.time()

            return {
                "success": True,
                "total_inserted": total_inserted,
                "batch_count": batch_count,
                "batch_size": batch_size,
                "table_name": full_table_name,
                "time_seconds": round(end_time - start_time, 2),
                "vectors_per_second": round(total_inserted / (end_time - start_time), 2) if total_inserted > 0 else 0
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_vector_statistics(self,
                             table_name: str) -> Dict[str, Any]:

        try:
            full_table_name = self._get_full_table_name(table_name)

            conn = self._get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total_vectors,
                        AVG(vector_dims(embedding)) as avg_dimensions,
                        MIN(vector_norm(embedding)) as min_norm,
                        MAX(vector_norm(embedding)) as max_norm,
                        AVG(vector_norm(embedding)) as avg_norm,
                        STDDEV(vector_norm(embedding)) as std_norm
                    FROM {full_table_name}
                """)

                stats = cursor.fetchone()

                return {
                    "success": True,
                    "table_name": full_table_name,
                    "total_vectors": stats[0] if stats else 0,
                    "avg_dimensions": float(stats[1]) if stats and stats[1] else 0.0,
                    "min_norm": float(stats[2]) if stats and stats[2] else 0.0,
                    "max_norm": float(stats[3]) if stats and stats[3] else 0.0,
                    "avg_norm": float(stats[4]) if stats and stats[4] else 0.0,
                    "std_norm": float(stats[5]) if stats and stats[5] else 0.0,
                }

            finally:
                cursor.close()
                self._return_connection(conn)

        except Exception as e:
            return {"success": False, "error": str(e)}
