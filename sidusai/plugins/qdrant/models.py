from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

class Distance(str, Enum):
    COSINE = "COSINE"
    EUCLID = "EUCLID"
    DOT = "DOT"

class MultiVectorComparator(str, Enum):
    MAX_SIM = "MAX_SIM"
    AVG_SIM = "AVG_SIM"

@dataclass
class VectorConfig:
    size: int
    distance: Distance = Distance.COSINE
    multivector_config: Optional[Dict] = None
    hnsw_config: Optional[Dict] = None

@dataclass
class SparseVectorConfig:
    modifier: Optional[str] = None

@dataclass
class Document:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "metadata": self.metadata
        }

@dataclass
class SearchResult:
    id: Union[int, str]
    score: float
    payload: Dict[str, Any]
    vector: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "score": self.score,
            "payload": self.payload
        }
        if self.vector:
            result["vector"] = self.vector
        return result

@dataclass
class CollectionInfo:
    name: str
    status: str
    vectors_count: int
    indexed_vectors_count: int
    points_count: int
    segments_count: int
    config: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "vectors_count": self.vectors_count,
            "indexed_vectors_count": self.indexed_vectors_count,
            "points_count": self.points_count,
            "segments_count": self.segments_count,
            "config": self.config
        }

@dataclass
class HybridSearchConfig:
    dense_model: str = "all-MiniLM-L6-v2"
    sparse_model: str = "Qdrant/bm25"
    late_interaction_model: Optional[str] = "colbert-ir/colbertv2.0"
    fusion_method: str = "RRF"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dense_model": self.dense_model,
            "sparse_model": self.sparse_model,
            "late_interaction_model": self.late_interaction_model,
            "fusion_method": self.fusion_method
        }
