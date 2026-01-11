import redis
import numpy as np
from redisvl.schema import IndexSchema
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from typing import Optional, Dict, Any, List
import json
import time

class RedisVLClientComponent:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.client = None
        self._connect()

    def _connect(self):
        try:
            self.client = redis.Redis.from_url(self.redis_url, decode_responses=False)
            print(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            raise

    def test_connection(self) -> bool:
        try:
            return self.client.ping()
        except:
            return False

    def create_index(self,
                    index_name: str,
                    vector_schema: Dict[str, Any],
                    prefix: str = "doc:",
                    index_type: str = "HNSW") -> Dict[str, Any]:

        try:
            schema_dict = {
                "index": {
                    "name": index_name,
                    "prefix": prefix,
                    "key": "id"
                },
                "fields": []
            }

            for vector_field in vector_schema.get("vector_fields", []):
                field_config = {
                    "name": vector_field["name"],
                    "type": "vector",
                    "attrs": {
                        "dims": vector_field.get("dims", 384),
                        "distance_metric": vector_field.get("distance_metric", "COSINE"),
                        "algorithm": "flat" if index_type.upper() == "FLAT" else "hnsw",
                        "datatype": "FLOAT32"
                    }
                }
                schema_dict["fields"].append(field_config)

            schema_dict["fields"].extend([
                {"name": "text", "type": "text"},
                {"name": "metadata", "type": "tag"},
                {"name": "timestamp", "type": "numeric"}
            ])

            schema = IndexSchema.from_dict(schema_dict)
            index = SearchIndex(schema=schema, redis_url=self.redis_url)

            index.create(overwrite=True)

            return {
                "success": True,
                "index_name": index_name,
                "status": "created",
                "schema": schema.to_dict(),
                "prefix": prefix
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create index: {str(e)}"
            }

    def search_similar(self,
                      index_name: str,
                      query_vector: List[float],
                      vector_field_name: str = "embedding",
                      return_fields: List[str] = None,
                      limit: int = 10,
                      filter_expression: Optional[str] = None) -> Dict[str, Any]:

        try:
            index = SearchIndex.from_existing(index_name, redis_url=self.redis_url)

            query = VectorQuery(
                vector=query_vector,
                vector_field_name=vector_field_name,
                num_results=limit,
                return_fields=return_fields or ["id", "text", "metadata", "score"],
                filter_expression=filter_expression
            )

            results = index.query(query)

            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result.get("id"),
                    "score": result.get("score", 0),
                    "text": result.get("text", ""),
                    "metadata": result.get("metadata", ""),
                    "timestamp": result.get("timestamp")
                }
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "index_name": index_name,
                "query_dimensions": len(query_vector),
                "results_count": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}"
            }

    def store_document(self,
                      index_name: str,
                      document_id: str,
                      text: str,
                      embedding: List[float],
                      metadata: Optional[Dict] = None) -> Dict[str, Any]:

        try:
            index = SearchIndex.from_existing(index_name, redis_url=self.redis_url)

            embedding_array = np.array(embedding, dtype=np.float32)

            doc = {
                "id": document_id,
                "text": text,
                "embedding": embedding_array.tobytes(),
                "metadata": json.dumps(metadata or {}),
                "timestamp": int(time.time())
            }

            documents = [doc]
            index.load(documents)

            return {
                "success": True,
                "document_id": document_id,
                "index_name": index_name,
                "text_length": len(text),
                "embedding_dimensions": len(embedding)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to store document: {str(e)}"
            }

    def get_info(self, index_name: str) -> Dict[str, Any]:
        try:
            index = SearchIndex.from_existing(index_name, redis_url=self.redis_url)
            info = index.info()

            try:
                stats = self.client.ft(index_name).info()
                num_docs = stats.get("num_docs", 0)
                percent_indexed = stats.get("percent_indexed", "0")
            except:
                num_docs = 0
                percent_indexed = "0"

            return {
                "success": True,
                "index_name": index_name,
                "info": info,
                "stats": {
                    "num_docs": num_docs,
                    "percent_indexed": percent_indexed
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get index info: {str(e)}"
            }

    def delete_index(self, index_name: str, drop: bool = True) -> Dict[str, Any]:
        try:
            index = SearchIndex.from_existing(index_name, redis_url=self.redis_url)

            if drop:
                index.delete(drop=True)
                action = "deleted with data"
            else:
                index.delete(drop=False)
                action = "deleted without data"

            return {
                "success": True,
                "index_name": index_name,
                "action": action,
                "status": "removed"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete index: {str(e)}"
            }

    def list_indices(self) -> Dict[str, Any]:
        try:
            indices = []

            cursor = 0
            while True:
                cursor, keys = self.client.scan(cursor=cursor, match="ft:*")

                for key in keys:
                    key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                    indices.append({
                        "name": key_str,
                        "type": "search_index"
                    })

                if cursor == 0:
                    break

            return {
                "success": True,
                "indices_count": len(indices),
                "indices": indices
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list indices: {str(e)}"
            }
