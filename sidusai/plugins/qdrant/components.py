from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance as QdrantDistance
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import uuid

from .models import Document, SearchResult

class QdrantClientComponent:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.host = host
        self.port = port
        self.client = QdrantClient(f"http://{host}:{port}")
        print(f"Qdrant client initialized at {host}:{port}")

    def test_connection(self) -> bool:
        try:
            version_info = self.client.get_version()
            print(f"Connected to Qdrant v{version_info.version}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def _get_distance(self, distance: str) -> QdrantDistance:
        distance_map = {
            "COSINE": QdrantDistance.COSINE,
            "EUCLID": QdrantDistance.EUCLID,
            "DOT": QdrantDistance.DOT
        }
        return distance_map.get(distance.upper(), QdrantDistance.COSINE)

    def create_collection(self,
                         collection_name: str,
                         vector_size: int = 384,
                         distance: str = "COSINE",
                         sparse_vectors: bool = False) -> Dict[str, Any]:

        try:
            print(f"Creating collection '{collection_name}'...")

            existing_collections = self.client.get_collections().collections
            if any(c.name == collection_name for c in existing_collections):
                print(f"Collection '{collection_name}' already exists")
                return {
                    "success": True,
                    "message": f"Collection '{collection_name}' already exists",
                    "collection_name": collection_name
                }

            vectors_config = models.VectorParams(
                size=vector_size,
                distance=self._get_distance(distance)
            )

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=vectors_config
            )

            print(f"Collection '{collection_name}' created successfully")
            return {
                "success": True,
                "message": f"Collection '{collection_name}' created",
                "collection_name": collection_name,
                "vector_size": vector_size,
                "distance": distance,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error creating collection: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }

    def upload_points(self,
                     collection_name: str,
                     vectors: List[List[float]],
                     payloads: List[Dict],
                     ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:

        try:
            print(f"Uploading {len(vectors)} points to '{collection_name}'...")

            if ids is None:
                ids = [str(uuid.uuid4()) for _ in range(len(vectors))]

            points = [
                models.PointStruct(
                    id=ids[i],
                    vector=vectors[i],
                    payload=payloads[i]
                )
                for i in range(len(vectors))
            ]

            self.client.upload_points(
                collection_name=collection_name,
                points=points
            )

            print(f"Successfully uploaded {len(points)} points")
            return {
                "success": True,
                "message": f"Uploaded {len(points)} points",
                "collection_name": collection_name,
                "points_count": len(points),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error uploading points: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }

    def upload_documents_with_vectors(self,
                                     collection_name: str,
                                     documents: List[Union[Document, Dict]],
                                     vectors: List[List[float]],
                                     ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:

        try:
            print(f"Uploading {len(documents)} documents with vectors to '{collection_name}'...")

            if ids is None:
                ids = [str(uuid.uuid4()) for _ in range(len(documents))]

            points = []
            for i, doc in enumerate(documents):
                if i >= len(vectors):
                    break

                if isinstance(doc, Document):
                    payload = doc.metadata.copy()
                    payload["text"] = doc.text
                else:
                    payload = doc.copy()

                point = models.PointStruct(
                    id=ids[i],
                    vector=vectors[i],
                    payload=payload
                )
                points.append(point)

            self.client.upload_points(
                collection_name=collection_name,
                points=points
            )

            print(f"Successfully uploaded {len(points)} documents")
            return {
                "success": True,
                "message": f"Uploaded {len(points)} documents",
                "collection_name": collection_name,
                "documents_count": len(points),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error uploading documents: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }

    def search_similar(self,
                      collection_name: str,
                      query_vector: List[float],
                      limit: int = 10,
                      filters: Optional[Dict] = None) -> Dict[str, Any]:

        try:
            print(f"Searching similar vectors in '{collection_name}'...")

            query_filter = None
            if filters:
                must_conditions = []

                for key, value in filters.items():
                    if isinstance(value, dict):
                        if "gte" in value or "lte" in value:
                            range_condition = {}
                            if "gte" in value:
                                range_condition["gte"] = value["gte"]
                            if "lte" in value:
                                range_condition["lte"] = value["lte"]
                            must_conditions.append(
                                models.FieldCondition(
                                    key=key,
                                    range=models.Range(**range_condition)
                                )
                            )
                        elif "match" in value:
                            must_conditions.append(
                                models.FieldCondition(
                                    key=key,
                                    match=models.MatchValue(value=value["match"])
                                )
                            )
                    else:
                        must_conditions.append(
                            models.FieldCondition(
                                key=key,
                                match=models.MatchValue(value=value)
                            )
                        )

                if must_conditions:
                    query_filter = models.Filter(must=must_conditions)

            search_result = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

            results = []
            for point in search_result.points:
                result = SearchResult(
                    id=point.id,
                    score=point.score,
                    payload=point.payload or {}
                )
                results.append(result.to_dict())

            print(f"Found {len(results)} results")
            return {
                "success": True,
                "results_count": len(results),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error searching: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        try:
            print(f"Getting info for collection '{collection_name}'...")

            collection_info = self.client.get_collection(collection_name)

            info_dict = {
                "name": collection_name,
                "status": str(collection_info.status),
            }

            try:
                info_dict["points_count"] = collection_info.points_count
            except:
                info_dict["points_count"] = 0

            try:
                info_dict["vectors_count"] = getattr(collection_info, 'vectors_count', 0)
            except:
                info_dict["vectors_count"] = 0

            try:
                info_dict["segments_count"] = collection_info.segments_count
            except:
                info_dict["segments_count"] = 0

            print(f"Retrieved info for '{collection_name}'")
            return {
                "success": True,
                "collection_info": info_dict,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }

    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        try:
            print(f"Deleting collection '{collection_name}'...")

            self.client.delete_collection(collection_name)

            print(f"Collection '{collection_name}' deleted")
            return {
                "success": True,
                "message": f"Collection '{collection_name}' deleted",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error deleting collection: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }

    def scroll_points(self,
                     collection_name: str,
                     limit: int = 100,
                     offset: Optional[str] = None) -> Dict[str, Any]:

        try:
            result = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            points = []
            for point in result[0]:
                points.append({
                    "id": point.id,
                    "payload": point.payload,
                    "score": getattr(point, 'score', None)
                })

            return {
                "success": True,
                "points": points,
                "next_offset": result[1],
                "count": len(points),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error scrolling points: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_point(self,
                 collection_name: str,
                 point_id: Union[int, str]) -> Dict[str, Any]:

        try:
            point = self.client.retrieve(
                collection_name=collection_name,
                ids=[point_id],
                with_payload=True,
                with_vectors=False
            )

            if point:
                return {
                    "success": True,
                    "point": {
                        "id": point[0].id,
                        "payload": point[0].payload
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Point {point_id} not found",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            print(f"Error getting point: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
