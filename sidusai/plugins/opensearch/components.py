from opensearchpy import OpenSearch
from typing import Optional, Dict, Any, List
import base64

class OpenSearchClientComponent:
    def __init__(self,
                 host: str = "localhost",
                 port: int = 9200,
                 use_ssl: bool = False,
                 verify_certs: bool = True,
                 http_auth: Optional[tuple] = None,
                 timeout: int = 30):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.verify_certs = verify_certs
        self.http_auth = http_auth
        self.timeout = timeout
        self.client = None
        self._connect()

    def _connect(self):
        try:
            print(f"Connecting to OpenSearch at {self.host}:{self.port}")

            self.client = OpenSearch(
                hosts=[{'host': self.host, 'port': self.port}],
                http_auth=self.http_auth,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                timeout=self.timeout
            )

            if self.client.ping():
                print(f"Connected to OpenSearch at {self.host}:{self.port}")
            else:
                raise Exception("Failed to ping OpenSearch server")

        except Exception as e:
            print(f"Failed to connect to OpenSearch: {e}")
            raise

    def test_connection(self) -> bool:
        try:
            return self.client.ping()
        except:
            return False

    def create_index(self,
                    index_name: str,
                    mappings: Optional[Dict[str, Any]] = None,
                    settings: Optional[Dict[str, Any]] = None,
                    knn_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            if self.client.indices.exists(index=index_name):
                return {
                    "success": False,
                    "error": f"Index '{index_name}' already exists"
                }

            body = {}

            if settings:
                body["settings"] = settings

            if knn_settings:
                if "settings" not in body:
                    body["settings"] = {}
                if "index" not in body["settings"]:
                    body["settings"]["index"] = {}
                body["settings"]["index"]["knn"] = True
                for key, value in knn_settings.items():
                    body["settings"]["index"][f"knn.{key}"] = value

            if mappings:
                body["mappings"] = mappings

            response = self.client.indices.create(index=index_name, body=body)

            return {
                "success": True,
                "index_name": index_name,
                "status": "created",
                "acknowledged": response.get('acknowledged', False),
                "shards_acknowledged": response.get('shards_acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create index: {str(e)}"
            }

    def create_knn_field(self,
                        index_name: str,
                        field_name: str,
                        dimension: int,
                        method: str = "hnsw",
                        engine: str = "faiss",
                        space_type: str = "l2",
                        parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            if not self.client.indices.exists(index=index_name):
                return {
                    "success": False,
                    "error": f"Index '{index_name}' does not exist"
                }

            knn_vector_config = {
                "type": "knn_vector",
                "dimension": dimension,
                "method": {
                    "name": method,
                    "space_type": space_type,
                    "engine": engine
                }
            }

            if parameters:
                knn_vector_config["method"]["parameters"] = parameters

            mappings = {
                "properties": {
                    field_name: knn_vector_config
                }
            }

            response = self.client.indices.put_mapping(index=index_name, body=mappings)

            return {
                "success": True,
                "index_name": index_name,
                "field_name": field_name,
                "dimension": dimension,
                "method": method,
                "engine": engine,
                "space_type": space_type,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create k-NN field: {str(e)}"
            }

    def search_knn(self,
                  index_name: str,
                  vector_field: str,
                  vector: List[float],
                  k: int = 10,
                  max_distance: Optional[float] = None,
                  min_score: Optional[float] = None,
                  filter_query: Optional[Dict[str, Any]] = None,
                  method_parameters: Optional[Dict[str, Any]] = None,
                  rescore_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            knn_query = {
                vector_field: {
                    "vector": vector
                }
            }

            if k and not max_distance and not min_score:
                knn_query[vector_field]["k"] = k
            elif max_distance and not k and not min_score:
                knn_query[vector_field]["max_distance"] = max_distance
            elif min_score and not k and not max_distance:
                knn_query[vector_field]["min_score"] = min_score
            else:
                knn_query[vector_field]["k"] = k

            if filter_query:
                knn_query[vector_field]["filter"] = filter_query

            if method_parameters:
                knn_query[vector_field]["method_parameters"] = method_parameters

            if rescore_params:
                knn_query[vector_field]["rescore"] = rescore_params

            query_body = {
                "query": {
                    "knn": knn_query
                },
                "size": k if k else 10000,
                "_source": True
            }

            response = self.client.search(index=index_name, body=query_body)

            hits = response.get('hits', {}).get('hits', [])
            formatted_results = []

            for hit in hits:
                formatted_result = {
                    "_id": hit.get('_id'),
                    "_score": hit.get('_score'),
                    "_source": hit.get('_source', {}),
                    "_index": hit.get('_index')
                }
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "index_name": index_name,
                "vector_field": vector_field,
                "query_dimensions": len(vector),
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"k-NN search failed: {str(e)}"
            }

    def search_neural(self,
                     index_name: str,
                     vector_field: str,
                     query_text: Optional[str] = None,
                     query_image: Optional[str] = None,
                     model_id: Optional[str] = None,
                     k: int = 10,
                     max_distance: Optional[float] = None,
                     min_score: Optional[float] = None,
                     filter_query: Optional[Dict[str, Any]] = None,
                     method_parameters: Optional[Dict[str, Any]] = None,
                     rescore_params: Optional[Dict[str, Any]] = None,
                     semantic_field_search_analyzer: Optional[str] = None) -> Dict[str, Any]:

        try:
            neural_query = {
                vector_field: {}
            }

            if query_text:
                neural_query[vector_field]["query_text"] = query_text
            if query_image:
                neural_query[vector_field]["query_image"] = query_image
            if model_id:
                neural_query[vector_field]["model_id"] = model_id
            if semantic_field_search_analyzer:
                neural_query[vector_field]["semantic_field_search_analyzer"] = semantic_field_search_analyzer

            if k and not max_distance and not min_score:
                neural_query[vector_field]["k"] = k
            elif max_distance and not k and not min_score:
                neural_query[vector_field]["max_distance"] = max_distance
            elif min_score and not k and not max_distance:
                neural_query[vector_field]["min_score"] = min_score
            else:
                neural_query[vector_field]["k"] = k

            if filter_query:
                neural_query[vector_field]["filter"] = filter_query

            if method_parameters:
                neural_query[vector_field]["method_parameters"] = method_parameters

            if rescore_params:
                neural_query[vector_field]["rescore"] = rescore_params

            query_body = {
                "query": {
                    "neural": neural_query
                },
                "size": k if k else 10000,
                "_source": True
            }

            response = self.client.search(index=index_name, body=query_body)

            hits = response.get('hits', {}).get('hits', [])
            formatted_results = []

            for hit in hits:
                formatted_result = {
                    "_id": hit.get('_id'),
                    "_score": hit.get('_score'),
                    "_source": hit.get('_source', {}),
                    "_index": hit.get('_index')
                }
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "index_name": index_name,
                "vector_field": vector_field,
                "query_text": query_text,
                "query_image": query_image is not None,
                "model_id": model_id,
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Neural search failed: {str(e)}"
            }

    def search_hybrid(self,
                     index_name: str,
                     knn_query: Dict[str, Any],
                     text_query: Optional[Dict[str, Any]] = None,
                     neural_query: Optional[Dict[str, Any]] = None,
                     boost_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:

        try:
            should_clauses = []
            boost_weights = boost_weights or {}

            if knn_query:
                knn_boost = boost_weights.get('knn', 1.0)
                knn_query_with_boost = knn_query.copy()
                if knn_boost != 1.0:
                    knn_query_with_boost = {
                        "knn": knn_query_with_boost
                    }
                should_clauses.append(knn_query_with_boost)

            if text_query:
                text_boost = boost_weights.get('text', 1.0)
                text_query_with_boost = text_query.copy()
                if text_boost != 1.0:
                    text_query_with_boost = {
                        "query_string": {
                            "query": text_query_with_boost.get('query', ''),
                            "boost": text_boost
                        }
                    }
                should_clauses.append(text_query_with_boost)

            if neural_query:
                neural_boost = boost_weights.get('neural', 1.0)
                neural_query_with_boost = neural_query.copy()
                if neural_boost != 1.0:
                    neural_query_with_boost = {
                        "neural": neural_query_with_boost
                    }
                should_clauses.append(neural_query_with_boost)

            query_body = {
                "query": {
                    "bool": {
                        "should": should_clauses,
                        "minimum_should_match": 1
                    }
                },
                "size": 100,
                "_source": True
            }

            response = self.client.search(index=index_name, body=query_body)

            hits = response.get('hits', {}).get('hits', [])
            formatted_results = []

            for hit in hits:
                formatted_result = {
                    "_id": hit.get('_id'),
                    "_score": hit.get('_score'),
                    "_source": hit.get('_source', {}),
                    "_index": hit.get('_index')
                }
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "index_name": index_name,
                "query_type": "hybrid",
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Hybrid search failed: {str(e)}"
            }

    def search_text(self,
                   index_name: str,
                   query: Dict[str, Any],
                   size: int = 10,
                   from_: int = 0) -> Dict[str, Any]:

        try:
            query_body = {
                "query": query,
                "size": size,
                "from": from_,
                "_source": True
            }

            response = self.client.search(index=index_name, body=query_body)

            hits = response.get('hits', {}).get('hits', [])
            formatted_results = []

            for hit in hits:
                formatted_result = {
                    "_id": hit.get('_id'),
                    "_score": hit.get('_score'),
                    "_source": hit.get('_source', {}),
                    "_index": hit.get('_index')
                }
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "index_name": index_name,
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Text search failed: {str(e)}"
            }

    def search_image(self,
                    index_name: str,
                    vector_field: str,
                    image_path: Optional[str] = None,
                    base64_image: Optional[str] = None,
                    model_id: Optional[str] = None,
                    k: int = 10) -> Dict[str, Any]:

        try:
            if image_path:
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
            elif not base64_image:
                return {
                    "success": False,
                    "error": "Either image_path or base64_image must be provided"
                }

            neural_query = {
                vector_field: {
                    "query_image": base64_image
                }
            }

            if model_id:
                neural_query[vector_field]["model_id"] = model_id

            neural_query[vector_field]["k"] = k

            query_body = {
                "query": {
                    "neural": neural_query
                },
                "size": k,
                "_source": True
            }

            response = self.client.search(index=index_name, body=query_body)

            hits = response.get('hits', {}).get('hits', [])
            formatted_results = []

            for hit in hits:
                formatted_result = {
                    "_id": hit.get('_id'),
                    "_score": hit.get('_score'),
                    "_source": hit.get('_source', {}),
                    "_index": hit.get('_index')
                }
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "index_name": index_name,
                "vector_field": vector_field,
                "image_source": "file" if image_path else "base64",
                "model_id": model_id,
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Image search failed: {str(e)}"
            }

    def index_document(self,
                      index_name: str,
                      document: Dict[str, Any],
                      document_id: Optional[str] = None) -> Dict[str, Any]:

        try:
            if document_id:
                response = self.client.index(
                    index=index_name,
                    body=document,
                    id=document_id,
                    refresh=True
                )
            else:
                response = self.client.index(
                    index=index_name,
                    body=document,
                    refresh=True
                )

            return {
                "success": True,
                "index_name": index_name,
                "document_id": response.get('_id'),
                "result": response.get('result'),
                "version": response.get('_version'),
                "shards": response.get('_shards', {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to index document: {str(e)}"
            }

    def get_document(self,
                    index_name: str,
                    document_id: str) -> Dict[str, Any]:

        try:
            response = self.client.get(
                index=index_name,
                id=document_id
            )

            return {
                "success": True,
                "document_id": document_id,
                "index_name": index_name,
                "found": response.get('found', False),
                "source": response.get('_source', {}),
                "version": response.get('_version')
            }

        except Exception as e:
            if "404" in str(e):
                return {
                    "success": False,
                    "error": f"Document '{document_id}' not found",
                    "found": False
                }
            return {
                "success": False,
                "error": f"Failed to get document: {str(e)}"
            }

    def update_document(self,
                       index_name: str,
                       document_id: str,
                       doc: Dict[str, Any],
                       script: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            body = {}
            if script:
                body["script"] = script
            else:
                body["doc"] = doc

            response = self.client.update(
                index=index_name,
                id=document_id,
                body=body,
                refresh=True
            )

            return {
                "success": True,
                "document_id": document_id,
                "index_name": index_name,
                "result": response.get('result'),
                "version": response.get('_version'),
                "shards": response.get('_shards', {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update document: {str(e)}"
            }

    def delete_document(self,
                       index_name: str,
                       document_id: Optional[str] = None,
                       query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            if document_id:
                response = self.client.delete(
                    index=index_name,
                    id=document_id,
                    refresh=True
                )
                return {
                    "success": True,
                    "action": "deleted_by_id",
                    "document_id": document_id,
                    "result": response.get('result'),
                    "shards": response.get('_shards', {})
                }
            elif query:
                response = self.client.delete_by_query(
                    index=index_name,
                    body={"query": query},
                    refresh=True
                )
                return {
                    "success": True,
                    "action": "deleted_by_query",
                    "deleted": response.get('deleted', 0),
                    "took": response.get('took', 0),
                    "failures": response.get('failures', [])
                }
            else:
                return {
                    "success": False,
                    "error": "Either document_id or query must be provided"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete document: {str(e)}"
            }

    def bulk_insert(self,
                   index_name: str,
                   documents: List[Dict[str, Any]],
                   batch_size: int = 1000,
                   refresh: bool = False) -> Dict[str, Any]:

        try:
            success_count = 0
            failed_count = 0
            errors = []

            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                bulk_body = []

                for doc in batch:
                    bulk_body.append({"index": {"_index": index_name}})
                    bulk_body.append(doc)

                try:
                    response = self.client.bulk(body=bulk_body, refresh=refresh)

                    if response.get('errors', False):
                        for item in response.get('items', []):
                            if 'error' in item.get('index', {}):
                                failed_count += 1
                                errors.append(item['index']['error'])
                            else:
                                success_count += 1
                    else:
                        success_count += len(batch)

                except Exception as e:
                    failed_count += len(batch)
                    errors.append(str(e))

            return {
                "success": True,
                "index_name": index_name,
                "total_documents": len(documents),
                "success_count": success_count,
                "failed_count": failed_count,
                "batch_size": batch_size,
                "errors": errors if failed_count > 0 else []
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Bulk insert failed: {str(e)}"
            }

    def get_info(self, index_name: str) -> Dict[str, Any]:
        try:
            mapping_response = self.client.indices.get_mapping(index=index_name)
            settings_response = self.client.indices.get_settings(index=index_name)
            stats_response = self.client.indices.stats(index=index_name)

            mapping_info = mapping_response.get(index_name, {}).get('mappings', {})
            settings_info = settings_response.get(index_name, {}).get('settings', {})
            stats_info = stats_response.get('indices', {}).get(index_name, {}).get('total', {})

            return {
                "success": True,
                "index_name": index_name,
                "info": {
                    "mappings": mapping_info,
                    "settings": settings_info,
                    "stats": {
                        "docs_count": stats_info.get('docs', {}).get('count', 0),
                        "store_size": stats_info.get('store', {}).get('size_in_bytes', 0),
                        "segments_count": stats_info.get('segments', {}).get('count', 0)
                    }
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get index info: {str(e)}"
            }

    def delete_index(self, index_name: str) -> Dict[str, Any]:
        try:
            response = self.client.indices.delete(index=index_name)

            return {
                "success": True,
                "index_name": index_name,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete index: {str(e)}"
            }

    def list_indices(self, pattern: str = "*") -> Dict[str, Any]:
        try:
            response = self.client.indices.get(index=pattern)

            indices = []
            for index_name, index_info in response.items():
                stats = self.client.indices.stats(index=index_name)
                index_stats = stats.get('indices', {}).get(index_name, {}).get('total', {})

                indices.append({
                    "name": index_name,
                    "docs_count": index_stats.get('docs', {}).get('count', 0),
                    "store_size": index_stats.get('store', {}).get('size_in_bytes', 0),
                    "settings": index_info.get('settings', {}),
                    "has_mappings": bool(index_info.get('mappings', {}).get('properties', {}))
                })

            return {
                "success": True,
                "pattern": pattern,
                "indices_count": len(indices),
                "indices": indices
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list indices: {str(e)}"
            }

    def aggregate(self,
                 index_name: str,
                 aggs: Dict[str, Any],
                 query: Optional[Dict[str, Any]] = None,
                 size: int = 0) -> Dict[str, Any]:

        try:
            query_body = {
                "size": size,
                "aggs": aggs
            }

            if query:
                query_body["query"] = query

            response = self.client.search(index=index_name, body=query_body)

            return {
                "success": True,
                "index_name": index_name,
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "aggregations": response.get('aggregations', {}),
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Aggregation failed: {str(e)}"
            }

    def close(self):
        if self.client:
            self.client.close()
