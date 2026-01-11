import weaviate
from weaviate.classes.config import Configure, Property, DataType, Tokenization
from weaviate.classes.query import Filter, MetadataQuery
from weaviate.classes.query import BM25Operator
from typing import Optional, Dict, Any, List
from pathlib import Path

class WeaviateClientComponent:
    def __init__(self,
                 weaviate_url: str = "http://localhost:8080",
                 api_key: Optional[str] = None,
                 grpc_enabled: bool = False):
        self.weaviate_url = weaviate_url
        self.api_key = api_key
        self.grpc_enabled = grpc_enabled
        self.client = None
        self._connect()

    def _connect(self):
        try:
            print(f"Connecting to Weaviate at {self.weaviate_url}")

            headers = None
            if self.api_key:
                headers = {"X-OpenAI-Api-Key": self.api_key}

            if "localhost" in self.weaviate_url or "127.0.0.1" in self.weaviate_url:
                if self.grpc_enabled:
                    self.client = weaviate.connect_to_local(
                        host="localhost",
                        port=8080,
                        grpc_port=50051,
                        headers=headers
                    )
                else:
                    self.client = weaviate.connect_to_local(
                        host="localhost",
                        port=8080,
                        headers=headers
                    )
            else:
                url_parts = self.weaviate_url.replace("http://", "").replace("https://", "").split(":")
                host = url_parts[0]
                port = 443 if self.weaviate_url.startswith("https://") else 80
                if len(url_parts) > 1 and url_parts[1]:
                    try:
                        port = int(url_parts[1])
                    except:
                        pass

                http_secure = self.weaviate_url.startswith("https://")

                if self.grpc_enabled:
                    self.client = weaviate.connect_to_custom(
                        http_host=host,
                        http_port=port,
                        http_secure=http_secure,
                        grpc_host=host,
                        grpc_port=50051,
                        grpc_secure=http_secure,
                        headers=headers
                    )
                else:
                    self.client = weaviate.connect_to_custom(
                        http_host=host,
                        http_port=port,
                        http_secure=http_secure,
                        headers=headers
                    )

            print(f"Connected to Weaviate at {self.weaviate_url}")
        except Exception as e:
            print(f"Failed to connect to Weaviate: {e}")
            raise

    def test_connection(self) -> bool:
        try:
            return self.client.is_ready()
        except:
            return False

    def create_collection(self,
                     collection_name: str,
                     properties: List[Dict[str, Any]],
                     vectorizer: str = "text2vec-openai",
                     module_config: Optional[Dict[str, Any]] = None,
                     inverted_index_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            if self.client.collections.exists(collection_name):
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' already exists"
                }

            weaviate_properties = []
            for prop in properties:
                data_type_value = prop.get("dataType", "text")
                if isinstance(data_type_value, list):
                    data_type_value = data_type_value[0] if data_type_value else "text"

                data_type = DataType(data_type_value)

                weaviate_prop = Property(
                    name=prop.get("name"),
                    data_type=data_type,
                    description=prop.get("description", ""),
                    tokenization=Tokenization(prop.get("tokenization", "word")) if prop.get("tokenization") else None
                )
                weaviate_properties.append(weaviate_prop)

            vector_config = None
            if vectorizer == "text2vec-openai":
                vector_config = Configure.Vectors.text2vec_openai()
            elif vectorizer == "text2vec-transformers":
                vector_config = Configure.Vectors.text2vec_transformers()
            elif vectorizer == "none":
                vector_config = None

            self.client.collections.create(
                name=collection_name,
                properties=weaviate_properties,
                vector_config=vector_config,
                inverted_index_config=Configure.inverted_index(
                    bm25_k1=inverted_index_config.get("bm25_k1", 1.2) if inverted_index_config else 1.2,
                    bm25_b=inverted_index_config.get("bm25_b", 0.75) if inverted_index_config else 0.75,
                    stopwords_preset=inverted_index_config.get("stopwords_preset", "en") if inverted_index_config else "en"
                ) if inverted_index_config else None
            )

            return {
                "success": True,
                "collection_name": collection_name,
                "status": "created",
                "properties_count": len(properties),
                "vectorizer": vectorizer
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create collection: {str(e)}"
            }

    def search_similar(self,
                      collection_name: str,
                      query_vector: List[float],
                      limit: int = 10,
                      offset: int = 0,
                      target_vector: str = None,
                      filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            collection = self.client.collections.get(collection_name)

            weaviate_filter = None
            if filters:
                weaviate_filter = self._build_filter(filters)

            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                offset=offset,
                filters=weaviate_filter,
                return_metadata=MetadataQuery(distance=True)
            )

            formatted_results = []
            for obj in response.objects:
                formatted_result = {
                    "uuid": str(obj.uuid),
                    "properties": obj.properties,
                    "metadata": {
                        "distance": obj.metadata.distance if obj.metadata and hasattr(obj.metadata, 'distance') else None,
                    }
                }
                if hasattr(obj, 'vector') and obj.vector:
                    formatted_result["vector"] = obj.vector
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "collection_name": collection_name,
                "query_dimensions": len(query_vector),
                "results_count": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}"
            }

    def near_text_search(self,
                        collection_name: str,
                        query: str,
                        limit: int = 10,
                        offset: int = 0,
                        target_vector: str = None,
                        filters: Optional[Dict[str, Any]] = None,
                        certainty: Optional[float] = None,
                        distance: Optional[float] = None) -> Dict[str, Any]:

        try:
            collection = self.client.collections.get(collection_name)

            weaviate_filter = None
            if filters:
                weaviate_filter = self._build_filter(filters)

            response = collection.query.near_text(
                query=query,
                limit=limit,
                offset=offset,
                filters=weaviate_filter,
                certainty=certainty,
                distance=distance,
                return_metadata=MetadataQuery(distance=True)
            )

            formatted_results = []
            for obj in response.objects:
                formatted_result = {
                    "uuid": str(obj.uuid),
                    "properties": obj.properties,
                    "metadata": {
                        "distance": obj.metadata.distance if obj.metadata and hasattr(obj.metadata, 'distance') else None,
                        "certainty": obj.metadata.certainty if obj.metadata and hasattr(obj.metadata, 'certainty') else None
                    }
                }
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "collection_name": collection_name,
                "query": query,
                "results_count": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Near text search failed: {str(e)}"
            }

    def hybrid_search(self,
                     collection_name: str,
                     query: str,
                     limit: int = 10,
                     offset: int = 0,
                     target_vector: str = None,
                     filters: Optional[Dict[str, Any]] = None,
                     alpha: float = 0.5,
                     fusion_type: str = None) -> Dict[str, Any]:

        try:
            collection = self.client.collections.get(collection_name)

            weaviate_filter = None
            if filters:
                weaviate_filter = self._build_filter(filters)

            from weaviate.classes.query import HybridFusion
            fusion_enum = None
            if fusion_type == "ranked":
                fusion_enum = HybridFusion.RANKED
            elif fusion_type == "relative_score":
                fusion_enum = HybridFusion.RELATIVE_SCORE

            response = collection.query.hybrid(
                query=query,
                limit=limit,
                offset=offset,
                filters=weaviate_filter,
                alpha=alpha,
                fusion_type=fusion_enum,
                return_metadata=MetadataQuery(score=True)
            )

            formatted_results = []
            for obj in response.objects:
                formatted_result = {
                    "uuid": str(obj.uuid),
                    "properties": obj.properties,
                    "metadata": {
                        "score": obj.metadata.score if obj.metadata and hasattr(obj.metadata, 'score') else None,
                    }
                }
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "collection_name": collection_name,
                "query": query,
                "alpha": alpha,
                "fusion_type": fusion_type,
                "results_count": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Hybrid search failed: {str(e)}"
            }

    def bm25_search(self,
                   collection_name: str,
                   query: str,
                   limit: int = 10,
                   offset: int = 0,
                   filters: Optional[Dict[str, Any]] = None,
                   operator: str = "OR",
                   minimum_match: int = 1) -> Dict[str, Any]:

        try:
            collection = self.client.collections.get(collection_name)

            weaviate_filter = None
            if filters:
                weaviate_filter = self._build_filter(filters)

            bm25_operator = BM25Operator.or_(minimum_match=minimum_match) if operator == "OR" else BM25Operator.and_()

            response = collection.query.bm25(
                query=query,
                limit=limit,
                offset=offset,
                filters=weaviate_filter,
                operator=bm25_operator
            )

            formatted_results = []
            for obj in response.objects:
                formatted_result = {
                    "uuid": str(obj.uuid),
                    "properties": obj.properties
                }
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "collection_name": collection_name,
                "query": query,
                "operator": operator,
                "minimum_match": minimum_match,
                "results_count": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"BM25 search failed: {str(e)}"
            }

    def store_document(self,
                      collection_name: str,
                      properties: Dict[str, Any],
                      vector: Optional[List[float]] = None,
                      named_vectors: Optional[Dict[str, List[float]]] = None,
                      uuid: Optional[str] = None) -> Dict[str, Any]:

        try:
            collection = self.client.collections.get(collection_name)

            uuid_obj = uuid if uuid else None

            if named_vectors:
                result = collection.data.insert(
                    properties=properties,
                    vector=named_vectors,
                    uuid=uuid_obj
                )
            elif vector:
                result = collection.data.insert(
                    properties=properties,
                    vector=vector,
                    uuid=uuid_obj
                )
            else:
                result = collection.data.insert(
                    properties=properties,
                    uuid=uuid_obj
                )

            return {
                "success": True,
                "uuid": str(result) if result else None,
                "collection_name": collection_name,
                "properties_count": len(properties)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to store document: {str(e)}"
            }

    def fetch_object(self,
                collection_name: str,
                uuid: str,
                include_vector: bool = False) -> Dict[str, Any]:

        try:
            collection = self.client.collections.get(collection_name)

            response = collection.query.fetch_object_by_id(
                uuid=uuid,
                include_vector=include_vector
            )

            if response:
                result = {
                    "uuid": str(response.uuid),
                    "properties": response.properties,
                }

                try:
                    result["created"] = response.created
                except AttributeError:
                    pass

                try:
                    result["updated"] = response.updated
                except AttributeError:
                    pass

                try:
                    result["tenant"] = response.tenant
                except AttributeError:
                    pass

                if include_vector:
                    try:
                        result["vector"] = response.vector
                    except AttributeError:
                        pass

                return {
                    "success": True,
                    "object": result
                }
            else:
                return {
                    "success": False,
                    "error": f"Object with UUID '{uuid}' not found"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch object: {str(e)}"
            }

    def update_object(self,
                     collection_name: str,
                     uuid: str,
                     properties: Dict[str, Any],
                     vector: Optional[List[float]] = None,
                     named_vectors: Optional[Dict[str, List[float]]] = None) -> Dict[str, Any]:

        try:
            collection = self.client.collections.get(collection_name)

            if named_vectors:
                collection.data.update(
                    uuid=uuid,
                    properties=properties,
                    vector=named_vectors
                )
            elif vector:
                collection.data.update(
                    uuid=uuid,
                    properties=properties,
                    vector=vector
                )
            else:
                collection.data.update(
                    uuid=uuid,
                    properties=properties
                )

            return {
                "success": True,
                "uuid": uuid,
                "collection_name": collection_name,
                "updated_properties": list(properties.keys())
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update object: {str(e)}"
            }

    def delete_object(self,
                     collection_name: str,
                     uuid: Optional[str] = None,
                     filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            collection = self.client.collections.get(collection_name)

            if uuid:
                collection.data.delete_by_id(uuid=uuid)
                return {
                    "success": True,
                    "action": "deleted_by_id",
                    "uuid": uuid,
                    "deleted_count": 1
                }
            elif filters:
                weaviate_filter = self._build_filter(filters)
                result = collection.data.delete_many(where=weaviate_filter)
                return {
                    "success": True,
                    "action": "deleted_by_filter",
                    "deleted_count": result.deleted_count,
                    "failed_count": result.failed_count
                }
            else:
                return {
                    "success": False,
                    "error": "Either UUID or filters must be provided"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete object: {str(e)}"
            }

    def batch_insert(self,
                    collection_name: str,
                    objects: List[Dict[str, Any]],
                    batch_size: int = 100,
                    num_workers: int = 1,
                    dynamic: bool = False,
                    consistency_level: str = "QUORUM") -> Dict[str, Any]:

        try:
            collection = self.client.collections.get(collection_name)

            with collection.batch.dynamic() if dynamic else collection.batch.fixed_size(batch_size=batch_size) as batch:
                for obj in objects:
                    properties = obj.get("properties", {})
                    vector = obj.get("vector")
                    named_vectors = obj.get("named_vectors")
                    uuid = obj.get("uuid")

                    if named_vectors:
                        batch.add_object(
                            properties=properties,
                            vector=named_vectors,
                            uuid=uuid
                        )
                    elif vector:
                        batch.add_object(
                            properties=properties,
                            vector=vector,
                            uuid=uuid
                        )
                    else:
                        batch.add_object(
                            properties=properties,
                            uuid=uuid
                        )

            failed_objects = collection.batch.failed_objects
            if failed_objects:
                return {
                    "success": False,
                    "error": "Batch import completed with errors",
                    "failed_count": len(failed_objects),
                    "total_count": len(objects),
                    "success_count": len(objects) - len(failed_objects)
                }

            return {
                "success": True,
                "total_count": len(objects),
                "batch_size": batch_size
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Batch insert failed: {str(e)}"
            }

    def get_info(self, collection_name: str) -> Dict[str, Any]:
        try:
            collection = self.client.collections.get(collection_name)

            info = collection.config.get()

            vector_index_type = None
            if hasattr(info, 'vector_index_config'):
                vector_index_type = getattr(info.vector_index_config, 'type', None)

            properties_info = []
            for prop in info.properties:
                prop_info = {
                    "name": prop.name,
                    "data_type": prop.data_type.value if hasattr(prop.data_type, 'value') else str(prop.data_type),
                    "description": prop.description
                }
                properties_info.append(prop_info)

            return {
                "success": True,
                "collection_name": collection_name,
                "info": {
                    "name": info.name,
                    "vectorizer": info.vectorizer_config.vectorizer.value if info.vectorizer_config and hasattr(info.vectorizer_config.vectorizer, 'value') else info.vectorizer_config.vectorizer if info.vectorizer_config else None,
                    "vector_index_type": vector_index_type,
                    "properties": properties_info
                },
                "stats": {
                    "total_count": collection.aggregate.over_all(total_count=True).total_count
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get collection info: {str(e)}"
            }

    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        try:
            self.client.collections.delete(collection_name)

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
            collections = self.client.collections.list_all()

            formatted_collections = []
            for collection_name in collections:
                try:
                    collection = self.client.collections.get(collection_name)
                    info = collection.config.get()

                    vectorizer_value = None
                    if info.vectorizer_config and info.vectorizer_config.vectorizer:
                        vectorizer_value = info.vectorizer_config.vectorizer.value if hasattr(info.vectorizer_config.vectorizer, 'value') else info.vectorizer_config.vectorizer

                    formatted_collections.append({
                        "name": collection_name,
                        "vectorizer": vectorizer_value,
                        "properties_count": len(info.properties),
                        "total_objects": collection.aggregate.over_all(total_count=True).total_count
                    })
                except Exception as e:
                    formatted_collections.append({
                        "name": collection_name,
                        "error": f"Could not retrieve details: {str(e)}"
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

    def aggregate(self,
                 collection_name: str,
                 fields: List[str],
                 group_by: Optional[List[str]] = None,
                 filters: Optional[Dict[str, Any]] = None,
                 limit: Optional[int] = None) -> Dict[str, Any]:

        try:
            collection = self.client.collections.get(collection_name)

            weaviate_filter = None
            if filters:
                weaviate_filter = self._build_filter(filters)

            aggregation = collection.aggregate.over_all(
                filters=weaviate_filter,
                total_count=True
            )

            result = {
                "total_count": aggregation.total_count
            }

            return {
                "success": True,
                "collection_name": collection_name,
                "aggregation": result
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Aggregation failed: {str(e)}"
            }

    def near_image_search(self,
                         collection_name: str,
                         image_path: Optional[str] = None,
                         base64_image: Optional[str] = None,
                         limit: int = 10,
                         offset: int = 0,
                         target_vector: str = None,
                         filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            collection = self.client.collections.get(collection_name)

            weaviate_filter = None
            if filters:
                weaviate_filter = self._build_filter(filters)

            if image_path:
                response = collection.query.near_image(
                    near_image=Path(image_path),
                    limit=limit,
                    offset=offset,
                    filters=weaviate_filter,
                    return_metadata=MetadataQuery(distance=True)
                )
            elif base64_image:
                response = collection.query.near_image(
                    near_image=base64_image,
                    limit=limit,
                    offset=offset,
                    filters=weaviate_filter,
                    return_metadata=MetadataQuery(distance=True)
                )
            else:
                return {
                    "success": False,
                    "error": "Either image_path or base64_image must be provided"
                }

            formatted_results = []
            for obj in response.objects:
                formatted_result = {
                    "uuid": str(obj.uuid),
                    "properties": obj.properties,
                    "metadata": {
                        "distance": obj.metadata.distance if obj.metadata and hasattr(obj.metadata, 'distance') else None
                    }
                }
                formatted_results.append(formatted_result)

            return {
                "success": True,
                "collection_name": collection_name,
                "results_count": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Near image search failed: {str(e)}"
            }

    def _build_filter(self, filters: Dict[str, Any]) -> Filter:
        if "operator" in filters and filters["operator"] == "AND":
            filter_list = []
            for condition in filters.get("conditions", []):
                filter_list.append(self._build_single_filter(condition))
            return Filter.all_of(filter_list)
        elif "operator" in filters and filters["operator"] == "OR":
            filter_list = []
            for condition in filters.get("conditions", []):
                filter_list.append(self._build_single_filter(condition))
            return Filter.any_of(filter_list)
        else:
            return self._build_single_filter(filters)

    def _build_single_filter(self, condition: Dict[str, Any]) -> Filter:
        prop_name = condition.get("property")
        operator = condition.get("operator", "equal")
        value = condition.get("value")

        if operator == "equal":
            return Filter.by_property(prop_name).equal(value)
        elif operator == "not_equal":
            return Filter.by_property(prop_name).not_equal(value)
        elif operator == "greater_than":
            return Filter.by_property(prop_name).greater_than(value)
        elif operator == "greater_or_equal":
            return Filter.by_property(prop_name).greater_or_equal(value)
        elif operator == "less_than":
            return Filter.by_property(prop_name).less_than(value)
        elif operator == "less_or_equal":
            return Filter.by_property(prop_name).less_or_equal(value)
        elif operator == "contains_any":
            return Filter.by_property(prop_name).contains_any(value)
        elif operator == "contains_all":
            return Filter.by_property(prop_name).contains_all(value)
        elif operator == "like":
            return Filter.by_property(prop_name).like(f"*{value}*")
        elif operator == "is_null":
            return Filter.by_property(prop_name).is_null(value)
        else:
            return Filter.by_property(prop_name).equal(value)

    def close(self):
        if self.client:
            self.client.close()
