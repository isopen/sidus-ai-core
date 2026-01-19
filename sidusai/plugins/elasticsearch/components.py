from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from typing import Optional, Dict, Any, List

class ElasticsearchClientComponent:
    def __init__(self,
                 host: str = "localhost",
                 port: int = 9200,
                 scheme: str = "http",
                 api_key: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 timeout: int = 30,
                 verify_certs: bool = True,
                 cloud_id: Optional[str] = None):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.timeout = timeout
        self.verify_certs = verify_certs

        es_url = f"{scheme}://{host}:{port}"
        print(f"🔗 Connecting to Elasticsearch at {es_url}")

        try:
            client_kwargs = {
                'hosts': [es_url],
                'request_timeout': timeout,
            }

            if scheme == "http":
                client_kwargs['verify_certs'] = False
                client_kwargs['ssl_show_warn'] = False

            print(f"   Config: {client_kwargs}")

            self.client = Elasticsearch(**client_kwargs)

            print(f"   Testing ping...")
            try:
                for attempt in range(3):
                    try:
                        ping_result = self.client.ping(request_timeout=5)
                        if ping_result:
                            info = self.client.info(request_timeout=5)
                            print(f"✅ Connected to Elasticsearch!")
                            print(f"   Version: {info['version']['number']}")
                            print(f"   Cluster: {info['cluster_name']}")
                            return
                        else:
                            print(f"   Ping attempt {attempt + 1}: False")
                    except Exception as e:
                        print(f"   Ping attempt {attempt + 1} failed: {e}")

                print(f"❌ All ping attempts failed")

                try:
                    info = self.client.info(request_timeout=5)
                    print(f"ℹ️  Direct info call succeeded: {info['cluster_name']}")
                    print(f"   But ping() returns False - this is unusual")
                    print(f"✅ Continuing despite ping() issue")
                    return
                except Exception as info_error:
                    print(f"❌ Info call also failed: {info_error}")
                    raise Exception("Cannot connect to Elasticsearch")

            except Exception as ping_error:
                print(f"❌ Connection test failed: {ping_error}")
                raise

        except Exception as e:
            print(f"❌ Failed to create Elasticsearch client: {e}")
            print(f"   URL: {es_url}")
            print(f"   Try manually: curl {es_url}")
            raise

    def test_connection(self) -> bool:
        try:
            return self.client.ping()
        except:
            return False

    def create_index(self,
                    index_name: str,
                    mappings: Optional[Dict[str, Any]] = None,
                    settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            if self.client.indices.exists(index=index_name):
                return {
                    "success": False,
                    "error": f"Index '{index_name}' already exists"
                }

            body = {}

            if settings:
                body["settings"] = settings

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

    def create_dense_vector_field(self,
                                 index_name: str,
                                 field_name: str,
                                 dimension: int,
                                 similarity: str = "cosine",
                                 index_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            if not self.client.indices.exists(index=index_name):
                return {
                    "success": False,
                    "error": f"Index '{index_name}' does not exist"
                }

            dense_vector_config = {
                "type": "dense_vector",
                "dims": dimension,
                "index": True,
                "similarity": similarity
            }

            if index_options:
                dense_vector_config["index_options"] = index_options

            mappings = {
                "properties": {
                    field_name: dense_vector_config
                }
            }

            response = self.client.indices.put_mapping(index=index_name, body=mappings)

            return {
                "success": True,
                "index_name": index_name,
                "field_name": field_name,
                "dimension": dimension,
                "similarity": similarity,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create dense vector field: {str(e)}"
            }

    def search_dense_vector(self,
                          index_name: str,
                          vector_field: str,
                          vector: List[float],
                          k: int = 10,
                          filter_query: Optional[Dict[str, Any]] = None,
                          score_threshold: Optional[float] = None,
                          num_candidates: int = 100) -> Dict[str, Any]:

        try:
            knn_query = {
                "field": vector_field,
                "query_vector": vector,
                "k": k,
                "num_candidates": num_candidates
            }

            if filter_query:
                knn_query["filter"] = filter_query

            query_body = {
                "knn": knn_query,
                "_source": True,
                "size": k
            }

            if score_threshold:
                query_body["min_score"] = score_threshold

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
                "error": f"Dense vector search failed: {str(e)}"
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

    def search_hybrid_vector(self,
                        index_name: str,
                        vector_field: str,
                        vector: List[float],
                        text_query: Dict[str, Any],
                        k: int = 10,
                        vector_weight: float = 0.7,
                        text_weight: float = 0.3,
                        filter_query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            query_body = {
                "query": {
                    "script_score": {
                        "query": text_query,
                        "script": {
                            "source": f"""
                                double text_score = _score * {text_weight};

                                double vector_similarity = 0;
                                if (doc['{vector_field}'].size() > 0) {{
                                    vector_similarity = cosineSimilarity(
                                        params.query_vector, 
                                        '{vector_field}'
                                    );
                                }}
                                double vector_score = vector_similarity * {vector_weight};

                                return text_score + vector_score;
                            """,
                            "params": {
                                "query_vector": vector
                            }
                        }
                    }
                },
                "_source": True,
                "size": k
            }

            if filter_query:
                query_body["query"]["script_score"]["query"] = {
                    "bool": {
                        "must": [text_query],
                        "filter": filter_query
                    }
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
                "error": f"Hybrid vector search failed: {str(e)}"
            }

    def search_semantic(self,
                       index_name: str,
                       query_text: str,
                       model_id: str,
                       field_name: str = "text_embedding",
                       k: int = 10) -> Dict[str, Any]:

        try:
            query_body = {
                "query": {
                    "text_expansion": {
                        field_name: {
                            "model_id": model_id,
                            "model_text": query_text
                        }
                    }
                },
                "_source": True,
                "size": k
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
                "query_text": query_text,
                "model_id": model_id,
                "field_name": field_name,
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Semantic search failed: {str(e)}"
            }

    def search_multi_match(self,
                         index_name: str,
                         query: str,
                         fields: List[str],
                         size: int = 10,
                         from_: int = 0) -> Dict[str, Any]:

        try:
            query_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": fields
                    }
                },
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
                "query": query,
                "fields": fields,
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Multi-match search failed: {str(e)}"
            }

    def search_match_phrase(self,
                          index_name: str,
                          field: str,
                          query: str,
                          size: int = 10,
                          from_: int = 0) -> Dict[str, Any]:

        try:
            query_body = {
                "query": {
                    "match_phrase": {
                        field: query
                    }
                },
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
                "field": field,
                "query": query,
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Match phrase search failed: {str(e)}"
            }

    def search_term(self,
                   index_name: str,
                   field: str,
                   value: str,
                   size: int = 10,
                   from_: int = 0) -> Dict[str, Any]:

        try:
            query_body = {
                "query": {
                    "term": {
                        field: value
                    }
                },
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
                "field": field,
                "value": value,
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Term search failed: {str(e)}"
            }

    def search_range(self,
                    index_name: str,
                    field: str,
                    gte: Optional[Any] = None,
                    lte: Optional[Any] = None,
                    gt: Optional[Any] = None,
                    lt: Optional[Any] = None,
                    size: int = 10,
                    from_: int = 0) -> Dict[str, Any]:

        try:
            range_query = {}
            if gte is not None:
                range_query["gte"] = gte
            if lte is not None:
                range_query["lte"] = lte
            if gt is not None:
                range_query["gt"] = gt
            if lt is not None:
                range_query["lt"] = lt

            query_body = {
                "query": {
                    "range": {
                        field: range_query
                    }
                },
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
                "field": field,
                "range": range_query,
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Range search failed: {str(e)}"
            }

    def search_exists(self,
                     index_name: str,
                     field: str,
                     size: int = 10,
                     from_: int = 0) -> Dict[str, Any]:

        try:
            query_body = {
                "query": {
                    "exists": {
                        "field": field
                    }
                },
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
                "field": field,
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "results_count": len(formatted_results),
                "results": formatted_results,
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Exists search failed: {str(e)}"
            }

    def index_document(self,
                      index_name: str,
                      document: Dict[str, Any],
                      document_id: Optional[str] = None) -> Dict[str, Any]:

        try:
            if document_id:
                response = self.client.index(
                    index=index_name,
                    document=document,
                    id=document_id,
                    refresh=True
                )
            else:
                response = self.client.index(
                    index=index_name,
                    document=document,
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
                    query=query,
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

            def generate_actions():
                for doc in documents:
                    yield {
                        "_index": index_name,
                        "_source": doc
                    }

            try:
                from elasticsearch.helpers import bulk
                success, failed = bulk(
                    self.client,
                    generate_actions(),
                    refresh=refresh,
                    raise_on_error=False
                )

                success_count = success
                failed_count = len(failed)
                errors = failed

            except Exception as e:
                failed_count = len(documents)
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

    def bulk_update(self,
                   index_name: str,
                   documents: List[Dict[str, Any]],
                   id_field: str = "_id",
                   batch_size: int = 1000,
                   refresh: bool = False) -> Dict[str, Any]:

        try:
            success_count = 0
            failed_count = 0
            errors = []

            def generate_update_actions():
                for doc in documents:
                    doc_id = doc.get(id_field)
                    if not doc_id:
                        continue

                    doc_without_id = {k: v for k, v in doc.items() if k != id_field}

                    yield {
                        "_op_type": "update",
                        "_index": index_name,
                        "_id": doc_id,
                        "doc": doc_without_id
                    }

            try:
                from elasticsearch.helpers import bulk
                success, failed = bulk(
                    self.client,
                    generate_update_actions(),
                    refresh=refresh,
                    raise_on_error=False
                )

                success_count = success
                failed_count = len(failed)
                errors = failed

            except Exception as e:
                failed_count = len(documents)
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
                "error": f"Bulk update failed: {str(e)}"
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

    def cluster_health(self) -> Dict[str, Any]:
        try:
            response = self.client.cluster.health()

            return {
                "success": True,
                "cluster_name": response.get('cluster_name'),
                "status": response.get('status'),
                "timed_out": response.get('timed_out'),
                "number_of_nodes": response.get('number_of_nodes'),
                "number_of_data_nodes": response.get('number_of_data_nodes'),
                "active_primary_shards": response.get('active_primary_shards'),
                "active_shards": response.get('active_shards'),
                "relocating_shards": response.get('relocating_shards'),
                "initializing_shards": response.get('initializing_shards'),
                "unassigned_shards": response.get('unassigned_shards'),
                "delayed_unassigned_shards": response.get('delayed_unassigned_shards'),
                "number_of_pending_tasks": response.get('number_of_pending_tasks'),
                "number_of_in_flight_fetch": response.get('number_of_in_flight_fetch'),
                "task_max_waiting_in_queue_millis": response.get('task_max_waiting_in_queue_millis'),
                "active_shards_percent_as_number": response.get('active_shards_percent_as_number')
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get cluster health: {str(e)}"
            }

    def cluster_stats(self) -> Dict[str, Any]:
        try:
            response = self.client.cluster.stats()

            return {
                "success": True,
                "cluster_name": response.get('cluster_name'),
                "status": response.get('status'),
                "nodes": response.get('nodes', {}),
                "indices": response.get('indices', {}),
                "timestamp": response.get('timestamp')
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get cluster stats: {str(e)}"
            }

    def cluster_settings(self) -> Dict[str, Any]:
        try:
            response = self.client.cluster.get_settings()

            return {
                "success": True,
                "persistent": response.get('persistent', {}),
                "transient": response.get('transient', {}),
                "defaults": response.get('defaults', {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get cluster settings: {str(e)}"
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

    def close_index(self, index_name: str) -> Dict[str, Any]:
        try:
            response = self.client.indices.close(index=index_name)

            return {
                "success": True,
                "index_name": index_name,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to close index: {str(e)}"
            }

    def open_index(self, index_name: str) -> Dict[str, Any]:
        try:
            response = self.client.indices.open(index=index_name)

            return {
                "success": True,
                "index_name": index_name,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to open index: {str(e)}"
            }

    def refresh_index(self, index_name: str) -> Dict[str, Any]:
        try:
            response = self.client.indices.refresh(index=index_name)

            return {
                "success": True,
                "index_name": index_name,
                "_shards": response.get('_shards', {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to refresh index: {str(e)}"
            }

    def flush_index(self, index_name: str) -> Dict[str, Any]:
        try:
            response = self.client.indices.flush(index=index_name)

            return {
                "success": True,
                "index_name": index_name,
                "_shards": response.get('_shards', {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to flush index: {str(e)}"
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
                    "segments_count": index_stats.get('segments', {}).get('count', 0),
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

    def aggregate_terms(self,
                       index_name: str,
                       field: str,
                       size: int = 10,
                       query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            aggs = {
                "terms_agg": {
                    "terms": {
                        "field": field,
                        "size": size
                    }
                }
            }

            return self.aggregate(index_name, aggs, query, 0)

        except Exception as e:
            return {
                "success": False,
                "error": f"Terms aggregation failed: {str(e)}"
            }

    def aggregate_date_histogram(self,
                                index_name: str,
                                field: str,
                                calendar_interval: str = "day",
                                query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            aggs = {
                "date_histogram_agg": {
                    "date_histogram": {
                        "field": field,
                        "calendar_interval": calendar_interval
                    }
                }
            }

            return self.aggregate(index_name, aggs, query, 0)

        except Exception as e:
            return {
                "success": False,
                "error": f"Date histogram aggregation failed: {str(e)}"
            }

    def aggregate_stats(self,
                       index_name: str,
                       field: str,
                       query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            aggs = {
                "stats_agg": {
                    "stats": {
                        "field": field
                    }
                }
            }

            return self.aggregate(index_name, aggs, query, 0)

        except Exception as e:
            return {
                "success": False,
                "error": f"Stats aggregation failed: {str(e)}"
            }

    def aggregate_cardinality(self,
                             index_name: str,
                             field: str,
                             query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            aggs = {
                "cardinality_agg": {
                    "cardinality": {
                        "field": field
                    }
                }
            }

            return self.aggregate(index_name, aggs, query, 0)

        except Exception as e:
            return {
                "success": False,
                "error": f"Cardinality aggregation failed: {str(e)}"
            }

    def put_mapping(self,
                   index_name: str,
                   mapping: Dict[str, Any]) -> Dict[str, Any]:

        try:
            response = self.client.indices.put_mapping(
                index=index_name,
                body=mapping
            )

            return {
                "success": True,
                "index_name": index_name,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to put mapping: {str(e)}"
            }

    def get_mapping(self, index_name: str) -> Dict[str, Any]:
        try:
            response = self.client.indices.get_mapping(index=index_name)

            mapping_info = response.get(index_name, {}).get('mappings', {})

            return {
                "success": True,
                "index_name": index_name,
                "mapping": mapping_info
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get mapping: {str(e)}"
            }

    def put_settings(self,
                    index_name: str,
                    settings: Dict[str, Any]) -> Dict[str, Any]:

        try:
            response = self.client.indices.put_settings(
                index=index_name,
                body=settings
            )

            return {
                "success": True,
                "index_name": index_name,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to put settings: {str(e)}"
            }

    def get_settings(self, index_name: str) -> Dict[str, Any]:
        try:
            response = self.client.indices.get_settings(index=index_name)

            settings_info = response.get(index_name, {}).get('settings', {})

            return {
                "success": True,
                "index_name": index_name,
                "settings": settings_info
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get settings: {str(e)}"
            }

    def create_alias(self,
                    index_name: str,
                    alias_name: str) -> Dict[str, Any]:

        try:
            response = self.client.indices.put_alias(
                index=index_name,
                name=alias_name
            )

            return {
                "success": True,
                "index_name": index_name,
                "alias_name": alias_name,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create alias: {str(e)}"
            }

    def delete_alias(self,
                    index_name: str,
                    alias_name: str) -> Dict[str, Any]:

        try:
            response = self.client.indices.delete_alias(
                index=index_name,
                name=alias_name
            )

            return {
                "success": True,
                "index_name": index_name,
                "alias_name": alias_name,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete alias: {str(e)}"
            }

    def get_aliases(self, index_name: str) -> Dict[str, Any]:
        try:
            response = self.client.indices.get_alias(index=index_name)

            aliases_info = response.get(index_name, {}).get('aliases', {})

            return {
                "success": True,
                "index_name": index_name,
                "aliases": aliases_info
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get aliases: {str(e)}"
            }

    def reindex(self,
               source_index: str,
               dest_index: str,
               query: Optional[Dict[str, Any]] = None,
               size: int = 1000) -> Dict[str, Any]:

        try:
            reindex_body = {
                "source": {
                    "index": source_index,
                    "size": size
                },
                "dest": {
                    "index": dest_index
                }
            }

            if query:
                reindex_body["source"]["query"] = query

            response = self.client.reindex(body=reindex_body, refresh=True)

            return {
                "success": True,
                "source_index": source_index,
                "dest_index": dest_index,
                "total": response.get('total', 0),
                "created": response.get('created', 0),
                "updated": response.get('updated', 0),
                "deleted": response.get('deleted', 0),
                "batches": response.get('batches', 0),
                "version_conflicts": response.get('version_conflicts', 0),
                "noops": response.get('noops', 0),
                "retries": response.get('retries', {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Reindex failed: {str(e)}"
            }

    def update_by_query(self,
                       index_name: str,
                       query: Dict[str, Any],
                       script: Optional[Dict[str, Any]] = None,
                       batch_size: int = 1000) -> Dict[str, Any]:

        try:
            update_body = {
                "query": query,
                "size": batch_size
            }

            if script:
                update_body["script"] = script

            response = self.client.update_by_query(
                index=index_name,
                body=update_body,
                refresh=True
            )

            return {
                "success": True,
                "index_name": index_name,
                "total": response.get('total', 0),
                "updated": response.get('updated', 0),
                "deleted": response.get('deleted', 0),
                "batches": response.get('batches', 0),
                "version_conflicts": response.get('version_conflicts', 0),
                "noops": response.get('noops', 0),
                "retries": response.get('retries', {}),
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Update by query failed: {str(e)}"
            }

    def delete_by_query(self,
                       index_name: str,
                       query: Dict[str, Any],
                       batch_size: int = 1000) -> Dict[str, Any]:

        try:
            response = self.client.delete_by_query(
                index=index_name,
                body={
                    "query": query,
                    "size": batch_size
                },
                refresh=True
            )

            return {
                "success": True,
                "index_name": index_name,
                "total": response.get('total', 0),
                "deleted": response.get('deleted', 0),
                "batches": response.get('batches', 0),
                "version_conflicts": response.get('version_conflicts', 0),
                "noops": response.get('noops', 0),
                "retries": response.get('retries', {}),
                "took": response.get('took', 0)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Delete by query failed: {str(e)}"
            }

    def count_documents(self,
                       index_name: str,
                       query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            count_body = {}
            if query:
                count_body["query"] = query

            response = self.client.count(index=index_name, body=count_body)

            return {
                "success": True,
                "index_name": index_name,
                "count": response.get('count', 0),
                "shards": response.get('_shards', {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Count documents failed: {str(e)}"
            }

    def exists_document(self,
                       index_name: str,
                       document_id: str) -> Dict[str, Any]:

        try:
            exists = self.client.exists(index=index_name, id=document_id)

            return {
                "success": True,
                "index_name": index_name,
                "document_id": document_id,
                "exists": exists
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Exists document failed: {str(e)}"
            }

    def multi_get(self,
                 index_name: str,
                 document_ids: List[str]) -> Dict[str, Any]:

        try:
            response = self.client.mget(
                index=index_name,
                body={"ids": document_ids}
            )

            docs = response.get('docs', [])
            formatted_results = []

            for doc in docs:
                formatted_result = {
                    "_id": doc.get('_id'),
                    "found": doc.get('found', False),
                    "source": doc.get('_source', {}) if doc.get('found') else {},
                    "index": doc.get('_index')
                }
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "index_name": index_name,
                "document_ids": document_ids,
                "results": formatted_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Multi-get failed: {str(e)}"
            }

    def explain_document(self,
                        index_name: str,
                        document_id: str,
                        query: Dict[str, Any]) -> Dict[str, Any]:

        try:
            response = self.client.explain(
                index=index_name,
                id=document_id,
                body={"query": query}
            )

            return {
                "success": True,
                "index_name": index_name,
                "document_id": document_id,
                "explanation": response.get('explanation', {}),
                "matched": response.get('matched', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Explain document failed: {str(e)}"
            }

    def validate_query(self,
                      index_name: str,
                      query: Dict[str, Any]) -> Dict[str, Any]:

        try:
            response = self.client.indices.validate_query(
                index=index_name,
                body={"query": query}
            )

            return {
                "success": True,
                "index_name": index_name,
                "valid": response.get('valid', False),
                "explanations": response.get('explanations', [])
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Validate query failed: {str(e)}"
            }

    def field_caps(self,
                  index_name: str,
                  fields: Optional[List[str]] = None) -> Dict[str, Any]:

        try:
            field_caps_body = {}
            if fields:
                field_caps_body["fields"] = fields

            response = self.client.field_caps(index=index_name, body=field_caps_body)

            return {
                "success": True,
                "index_name": index_name,
                "fields": response.get('fields', {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Field capabilities failed: {str(e)}"
            }

    def analyze_text(self,
                    index_name: str,
                    text: str,
                    analyzer: Optional[str] = None) -> Dict[str, Any]:

        try:
            analyze_body = {
                "text": text
            }

            if analyzer:
                analyze_body["analyzer"] = analyzer

            response = self.client.indices.analyze(index=index_name, body=analyze_body)

            tokens = response.get('tokens', [])
            formatted_tokens = []

            for token in tokens:
                formatted_tokens.append({
                    "token": token.get('token'),
                    "start_offset": token.get('start_offset'),
                    "end_offset": token.get('end_offset'),
                    "type": token.get('type'),
                    "position": token.get('position')
                })

            return {
                "success": True,
                "index_name": index_name,
                "text": text,
                "analyzer": analyzer,
                "tokens": formatted_tokens
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Text analysis failed: {str(e)}"
            }

    def get_shards(self, index_name: str) -> Dict[str, Any]:
        try:
            response = self.client.cat.shards(index=index_name, format="json")

            shards = []
            for shard_info in response:
                shards.append({
                    "index": shard_info.get('index'),
                    "shard": shard_info.get('shard'),
                    "prirep": shard_info.get('prirep'),
                    "state": shard_info.get('state'),
                    "docs": shard_info.get('docs'),
                    "store": shard_info.get('store'),
                    "ip": shard_info.get('ip'),
                    "node": shard_info.get('node')
                })

            return {
                "success": True,
                "index_name": index_name,
                "shards": shards
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Get shards failed: {str(e)}"
            }

    def get_nodes(self) -> Dict[str, Any]:
        try:
            response = self.client.nodes.info()

            nodes = {}
            for node_id, node_info in response.get('nodes', {}).items():
                nodes[node_id] = {
                    "name": node_info.get('name'),
                    "host": node_info.get('host'),
                    "ip": node_info.get('ip'),
                    "roles": node_info.get('roles', []),
                    "version": node_info.get('version'),
                    "jvm": {
                        "version": node_info.get('jvm', {}).get('version'),
                        "memory": node_info.get('jvm', {}).get('mem', {}),
                        "heap_used": node_info.get('jvm', {}).get('heap_used_percent')
                    },
                    "os": {
                        "name": node_info.get('os', {}).get('name'),
                        "arch": node_info.get('os', {}).get('arch'),
                        "memory": node_info.get('os', {}).get('mem', {})
                    }
                }

            return {
                "success": True,
                "cluster_name": response.get('cluster_name'),
                "nodes": nodes
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Get nodes failed: {str(e)}"
            }

    def get_tasks(self) -> Dict[str, Any]:
        try:
            response = self.client.tasks.list()

            tasks = []
            for task_id, task_info in response.get('nodes', {}).items():
                for task_node_id, task_details in task_info.get('tasks', {}).items():
                    tasks.append({
                        "task_id": task_details.get('id'),
                        "type": task_details.get('type'),
                        "action": task_details.get('action'),
                        "description": task_details.get('description'),
                        "start_time": task_details.get('start_time_in_millis'),
                        "running_time": task_details.get('running_time_in_nanos'),
                        "node": task_details.get('node'),
                        "cancellable": task_details.get('cancellable')
                    })

            return {
                "success": True,
                "tasks": tasks
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Get tasks failed: {str(e)}"
            }

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        try:
            response = self.client.tasks.cancel(task_id=task_id)

            return {
                "success": True,
                "task_id": task_id,
                "nodes": response.get('nodes', {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Cancel task failed: {str(e)}"
            }

    def get_pending_tasks(self) -> Dict[str, Any]:
        try:
            response = self.client.cluster.pending_tasks()

            tasks = response.get('tasks', [])
            formatted_tasks = []

            for task in tasks:
                formatted_tasks.append({
                    "insert_order": task.get('insert_order'),
                    "priority": task.get('priority'),
                    "source": task.get('source'),
                    "time_in_queue": task.get('time_in_queue'),
                    "time_in_queue_millis": task.get('time_in_queue_millis')
                })

            return {
                "success": True,
                "tasks": formatted_tasks
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Get pending tasks failed: {str(e)}"
            }

    def put_ilm_policy(self,
                      policy_name: str,
                      policy: Dict[str, Any]) -> Dict[str, Any]:

        try:
            response = self.client.ilm.put_lifecycle(
                name=policy_name,
                body=policy
            )

            return {
                "success": True,
                "policy_name": policy_name,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Put ILM policy failed: {str(e)}"
            }

    def get_ilm_policy(self, policy_name: str) -> Dict[str, Any]:
        try:
            response = self.client.ilm.get_lifecycle(name=policy_name)

            policy_info = response.get(policy_name, {}).get('policy', {})

            return {
                "success": True,
                "policy_name": policy_name,
                "policy": policy_info
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Get ILM policy failed: {str(e)}"
            }

    def delete_ilm_policy(self, policy_name: str) -> Dict[str, Any]:
        try:
            response = self.client.ilm.delete_lifecycle(name=policy_name)

            return {
                "success": True,
                "policy_name": policy_name,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Delete ILM policy failed: {str(e)}"
            }

    def explain_ilm(self, index_name: str) -> Dict[str, Any]:
        try:
            response = self.client.ilm.explain_lifecycle(index=index_name)

            indices_info = response.get('indices', {})
            index_info = indices_info.get(index_name, {})

            return {
                "success": True,
                "index_name": index_name,
                "ilm_explanation": index_info
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Explain ILM failed: {str(e)}"
            }

    def start_ilm(self) -> Dict[str, Any]:
        try:
            response = self.client.ilm.start()

            return {
                "success": True,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Start ILM failed: {str(e)}"
            }

    def stop_ilm(self) -> Dict[str, Any]:
        try:
            response = self.client.ilm.stop()

            return {
                "success": True,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Stop ILM failed: {str(e)}"
            }

    def get_ilm_status(self) -> Dict[str, Any]:
        try:
            response = self.client.ilm.get_status()

            return {
                "success": True,
                "operation_mode": response.get('operation_mode'),
                "ilm_status": response
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Get ILM status failed: {str(e)}"
            }

    def create_snapshot_repository(self,
                                  repository_name: str,
                                  repository_type: str = "fs",
                                  settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            repository_body = {
                "type": repository_type
            }

            if settings:
                repository_body["settings"] = settings

            response = self.client.snapshot.create_repository(
                repository=repository_name,
                body=repository_body
            )

            return {
                "success": True,
                "repository_name": repository_name,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Create snapshot repository failed: {str(e)}"
            }

    def create_snapshot(self,
                       repository_name: str,
                       snapshot_name: str,
                       indices: Optional[List[str]] = None,
                       wait_for_completion: bool = False) -> Dict[str, Any]:

        try:
            snapshot_body = {}
            if indices:
                snapshot_body["indices"] = indices

            response = self.client.snapshot.create(
                repository=repository_name,
                snapshot=snapshot_name,
                body=snapshot_body,
                wait_for_completion=wait_for_completion
            )

            return {
                "success": True,
                "repository_name": repository_name,
                "snapshot_name": snapshot_name,
                "accepted": response.get('accepted', False),
                "snapshot": response.get('snapshot', {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Create snapshot failed: {str(e)}"
            }

    def restore_snapshot(self,
                        repository_name: str,
                        snapshot_name: str,
                        indices: Optional[List[str]] = None,
                        wait_for_completion: bool = False) -> Dict[str, Any]:

        try:
            restore_body = {}
            if indices:
                restore_body["indices"] = indices

            response = self.client.snapshot.restore(
                repository=repository_name,
                snapshot=snapshot_name,
                body=restore_body,
                wait_for_completion=wait_for_completion
            )

            return {
                "success": True,
                "repository_name": repository_name,
                "snapshot_name": snapshot_name,
                "accepted": response.get('accepted', False),
                "snapshot": response.get('snapshot', {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Restore snapshot failed: {str(e)}"
            }

    def get_snapshots(self,
                     repository_name: str) -> Dict[str, Any]:

        try:
            response = self.client.snapshot.get(
                repository=repository_name,
                snapshot="_all"
            )

            snapshots = response.get('snapshots', [])
            formatted_snapshots = []

            for snapshot in snapshots:
                formatted_snapshots.append({
                    "name": snapshot.get('snapshot'),
                    "state": snapshot.get('state'),
                    "indices": snapshot.get('indices', []),
                    "start_time": snapshot.get('start_time'),
                    "end_time": snapshot.get('end_time'),
                    "duration": snapshot.get('duration_in_millis'),
                    "shards": snapshot.get('shards', {})
                })

            return {
                "success": True,
                "repository_name": repository_name,
                "snapshots": formatted_snapshots
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Get snapshots failed: {str(e)}"
            }

    def delete_snapshot(self,
                       repository_name: str,
                       snapshot_name: str) -> Dict[str, Any]:

        try:
            response = self.client.snapshot.delete(
                repository=repository_name,
                snapshot=snapshot_name
            )

            return {
                "success": True,
                "repository_name": repository_name,
                "snapshot_name": snapshot_name,
                "acknowledged": response.get('acknowledged', False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Delete snapshot failed: {str(e)}"
            }

    def close(self):
        if self.client:
            self.client.close()
