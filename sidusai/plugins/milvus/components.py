from typing import Dict, Any, List, Union
from pymilvus import MilvusClient

class MilvusClientComponent:
    def __init__(self,
                 uri: str = "http://localhost:19530",
                 token: str = "",
                 db_name: str = "default"):
        self.uri = uri
        self.token = token
        self.db_name = db_name
        self.client = None
        self._connect()

    def _connect(self):
        try:
            print(f"Connecting to Milvus at {self.uri}")

            if self.uri.endswith('.db'):
                self.client = MilvusClient(self.uri)
            else:
                self.client = MilvusClient(
                    uri=self.uri,
                    token=self.token,
                    db_name=self.db_name
                )

            print(f"Connected to Milvus at {self.uri}")
        except Exception as e:
            print(f"Failed to connect to Milvus: {e}")
            raise

    def test_connection(self) -> bool:
        try:
            collections = self.client.list_collections()
            return True
        except:
            return False

    def create_collection(self,
                         collection_name: str,
                         dimension: int,
                         metric_type: str = "COSINE") -> Dict[str, Any]:

        try:
            if collection_name in self.client.list_collections():
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' already exists"
                }

            self.client.create_collection(
                collection_name=collection_name,
                dimension=dimension,
                metric_type=metric_type
            )

            return {
                "success": True,
                "collection_name": collection_name,
                "dimension": dimension,
                "metric_type": metric_type,
                "status": "created"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create collection: {str(e)}"
            }

    def search_similar(self,
                      collection_name: str,
                      data: List[List[float]],
                      limit: int = 10,
                      output_fields: List[str] = None,
                      filter: str = None) -> Dict[str, Any]:

        try:
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }

            results = self.client.search(
                collection_name=collection_name,
                data=data,
                limit=limit,
                output_fields=output_fields or [],
                filter=filter,
                search_params=search_params
            )

            formatted_results = []
            for query_results in results:
                for result in query_results:
                    formatted_result = {
                        "id": str(result["id"]),
                        "distance": result.get("distance", 0),
                        "entity": {k: v for k, v in result.items() if k not in ["id", "distance"]}
                    }
                    formatted_results.append(formatted_result)

            return {
                "success": True,
                "collection_name": collection_name,
                "queries_count": len(data),
                "results_per_query": limit,
                "total_results": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}"
            }

    def store_document(self,
                      collection_name: str,
                      data: List[Dict[str, Any]]) -> Dict[str, Any]:

        try:
            result = self.client.insert(
                collection_name=collection_name,
                data=data
            )

            return {
                "success": True,
                "insert_count": len(result['ids']),
                "ids": result['ids'],
                "collection_name": collection_name
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to store document: {str(e)}"
            }

    def fetch_object(self,
                    collection_name: str,
                    ids: List[Union[int, str]],
                    output_fields: List[str] = None) -> Dict[str, Any]:

        try:
            if not ids:
                return {"success": False, "error": "No IDs provided"}

            id_str = ",".join([str(id) for id in ids])

            results = self.client.query(
                collection_name=collection_name,
                filter=f"id in [{id_str}]",
                output_fields=output_fields or []
            )

            return {
                "success": True,
                "collection_name": collection_name,
                "ids_requested": ids,
                "ids_found": [r.get('id') for r in results],
                "results": results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch object: {str(e)}"
            }

    def query(self,
             collection_name: str,
             filter: str,
             output_fields: List[str] = None,
             limit: int = None,
             offset: int = 0) -> Dict[str, Any]:

        try:
            results = self.client.query(
                collection_name=collection_name,
                filter=filter,
                output_fields=output_fields or [],
                limit=limit,
                offset=offset
            )

            return {
                "success": True,
                "collection_name": collection_name,
                "filter": filter,
                "results_count": len(results),
                "results": results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Query failed: {str(e)}"
            }

    def update_object(self,
                     collection_name: str,
                     data: List[Dict[str, Any]]) -> Dict[str, Any]:

        try:
            result = self.client.upsert(
                collection_name=collection_name,
                data=data
            )

            return {
                "success": True,
                "upsert_count": len(result['ids']),
                "ids": result['ids'],
                "collection_name": collection_name
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update object: {str(e)}"
            }

    def delete_object(self,
                     collection_name: str,
                     filter: str) -> Dict[str, Any]:

        try:
            result = self.client.delete(
                collection_name=collection_name,
                filter=filter
            )

            return {
                "success": True,
                "delete_count": result['delete_count'],
                "collection_name": collection_name
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete object: {str(e)}"
            }

    def batch_insert(self,
                    collection_name: str,
                    data: List[Dict[str, Any]]) -> Dict[str, Any]:

        try:
            result = self.client.insert(
                collection_name=collection_name,
                data=data
            )

            return {
                "success": True,
                "insert_count": len(result['ids']),
                "ids": result['ids'],
                "collection_name": collection_name,
                "batch_size": len(data)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Batch insert failed: {str(e)}"
            }

    def get_info(self, collection_name: str) -> Dict[str, Any]:
        try:
            collection_info = self.client.describe_collection(collection_name)

            return {
                "success": True,
                "collection_name": collection_name,
                "info": collection_info
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get collection info: {str(e)}"
            }

    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        try:
            self.client.drop_collection(collection_name)

            return {
                "success": True,
                "collection_name": collection_name,
                "status": "deleted"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete collection: {str(e)}"
            }

    def list_collections(self) -> Dict[str, Any]:
        try:
            collections = self.client.list_collections()

            formatted_collections = []
            for collection_name in collections:
                try:
                    info = self.client.describe_collection(collection_name)
                    formatted_collections.append({
                        "name": collection_name,
                        "description": info.get('description', ''),
                        "auto_id": info.get('auto_id', False)
                    })
                except:
                    formatted_collections.append({
                        "name": collection_name,
                        "error": "Could not retrieve details"
                    })

            return {
                "success": True,
                "collections_count": len(formatted_collections),
                "collections": formatted_collections
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list collections: {str(e)}"
            }

    def close(self):
        if self.client:
            try:
                self.client.close()
            except:
                pass
