import sidusai as sai
from typing import Optional, Dict, Any, List

from .components import WeaviateClientComponent
from .skills import (
    create_collection_skill,
    search_similar_skill,
    get_info_skill,
    delete_collection_skill,
    list_collections_skill,
    store_document_skill,
    fetch_object_skill,
    update_object_skill,
    delete_object_skill,
    batch_insert_skill,
    aggregate_skill,
    hybrid_search_skill,
    near_vector_search_skill,
    near_text_search_skill,
    bm25_search_skill,
    near_image_search_skill
)

__weaviate_agent_name__ = 'weaviate_agent'

class WeaviatePlugin(sai.AgentPlugin):
    def __init__(self, 
                 weaviate_url: str = "http://localhost:8080",
                 api_key: Optional[str] = None,
                 grpc_enabled: bool = False):
        super().__init__()
        self.weaviate_url = weaviate_url
        self.api_key = api_key
        self.grpc_enabled = grpc_enabled
        self.weaviate_client = None
        self.skills = {}
        print(f"Weaviate Plugin initialized with URL: {weaviate_url}")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying Weaviate plugin to agent...")

        try:
            self.weaviate_client = WeaviateClientComponent(
                weaviate_url=self.weaviate_url,
                api_key=self.api_key,
                grpc_enabled=self.grpc_enabled
            )
            print("Weaviate client component created")

            def create_skill_wrapper(skill_func):
                def wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                    try:
                        context = {}
                        if hasattr(agent_value, 'value'):
                            context = agent_value.value
                        elif isinstance(agent_value, dict):
                            context = agent_value

                        context['weaviate_client'] = self.weaviate_client
                        result = skill_func(context)
                        return_value = sai.AgentValue()
                        return_value.value = result.value
                        return return_value
                    except Exception as e:
                        error_value = sai.AgentValue()
                        error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                        return error_value
                return wrapper

            skill_mappings = {
                'create_collection': create_collection_skill,
                'search_similar': search_similar_skill,
                'get_info': get_info_skill,
                'delete_collection': delete_collection_skill,
                'list_collections': list_collections_skill,
                'store_document': store_document_skill,
                'fetch_object': fetch_object_skill,
                'update_object': update_object_skill,
                'delete_object': delete_object_skill,
                'batch_insert': batch_insert_skill,
                'aggregate': aggregate_skill,
                'hybrid_search': hybrid_search_skill,
                'near_vector_search': near_vector_search_skill,
                'near_text_search': near_text_search_skill,
                'bm25_search': bm25_search_skill,
                'near_image_search': near_image_search_skill
            }

            for skill_name, skill_func in skill_mappings.items():
                self.skills[skill_name] = create_skill_wrapper(skill_func)

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.weaviate_client = self.weaviate_client
            agent.weaviate_skills = self.skills

            print("Weaviate plugin applied successfully")

        except Exception as e:
            print(f"Error applying Weaviate plugin: {e}")
            import traceback
            traceback.print_exc()

class WeaviateAgent(sai.Agent):
    def __init__(self, 
                 name: str = __weaviate_agent_name__,
                 weaviate_url: str = "http://localhost:8080",
                 api_key: Optional[str] = None,
                 grpc_enabled: bool = False):
        super().__init__()
        self._name = name

        print(f"Creating Weaviate Agent '{name}'...")
        self.plugin = WeaviatePlugin(
            weaviate_url=weaviate_url,
            api_key=api_key,
            grpc_enabled=grpc_enabled
        )
        self.plugin.apply_plugin(self)
        print(f"Weaviate Agent '{name}' created successfully")

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        try:
            agent_value = sai.AgentValue()
            agent_value.value = context
            return agent_value
        except Exception as e:
            print(f"Error creating AgentValue: {e}")
            agent_value = sai.AgentValue()
            setattr(agent_value, 'value', context)
            return agent_value

    def create_collection(self,
                         collection_name: str,
                         properties: List[Dict[str, Any]],
                         vectorizer: str = "text2vec-openai",
                         module_config: Optional[Dict[str, Any]] = None,
                         inverted_index_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'properties': properties,
            'vectorizer': vectorizer,
            'module_config': module_config or {},
            'inverted_index_config': inverted_index_config or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_collection'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def store_document(self,
                      collection_name: str,
                      properties: Dict[str, Any],
                      vector: Optional[List[float]] = None,
                      named_vectors: Optional[Dict[str, List[float]]] = None,
                      uuid: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'properties': properties,
            'vector': vector,
            'named_vectors': named_vectors or {},
            'uuid': uuid
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['store_document'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def fetch_object(self,
                    collection_name: str,
                    uuid: str,
                    include_vector: bool = False) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'uuid': uuid,
            'include_vector': include_vector
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['fetch_object'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_similar(self,
                  collection_name: str,
                  query_vector: List[float],
                  limit: int = 10,
                  offset: int = 0,
                  target_vector: str = None,
                  filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'query_vector': query_vector,
            'limit': limit,
            'offset': offset,
            'target_vector': target_vector,
            'filters': filters or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_similar'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def near_text_search(self,
                    collection_name: str,
                    query: str,
                    limit: int = 10,
                    offset: int = 0,
                    target_vector: str = None,
                    filters: Optional[Dict[str, Any]] = None,
                    certainty: Optional[float] = None,
                    distance: Optional[float] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'query': query,
            'limit': limit,
            'offset': offset,
            'target_vector': target_vector,
            'filters': filters or {},
            'certainty': certainty,
            'distance': distance
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['near_text_search'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def hybrid_search(self,
                 collection_name: str,
                 query: str,
                 limit: int = 10,
                 offset: int = 0,
                 target_vector: str = None,
                 filters: Optional[Dict[str, Any]] = None,
                 alpha: float = 0.5,
                 fusion_type: str = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'query': query,
            'limit': limit,
            'offset': offset,
            'target_vector': target_vector,
            'filters': filters or {},
            'alpha': alpha,
            'fusion_type': fusion_type
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['hybrid_search'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def bm25_search(self,
                   collection_name: str,
                   query: str,
                   limit: int = 10,
                   offset: int = 0,
                   filters: Optional[Dict[str, Any]] = None,
                   operator: str = "OR",
                   minimum_match: int = 1) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'query': query,
            'limit': limit,
            'offset': offset,
            'filters': filters or {},
            'operator': operator,
            'minimum_match': minimum_match
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['bm25_search'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def update_object(self,
                     collection_name: str,
                     uuid: str,
                     properties: Dict[str, Any],
                     vector: Optional[List[float]] = None,
                     named_vectors: Optional[Dict[str, List[float]]] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'uuid': uuid,
            'properties': properties,
            'vector': vector,
            'named_vectors': named_vectors or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['update_object'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_object(self,
                     collection_name: str,
                     uuid: Optional[str] = None,
                     filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'uuid': uuid,
            'filters': filters or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_object'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def batch_insert(self,
                    collection_name: str,
                    objects: List[Dict[str, Any]],
                    batch_size: int = 100,
                    num_workers: int = 1,
                    dynamic: bool = False,
                    consistency_level: str = "QUORUM") -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'objects': objects,
            'batch_size': batch_size,
            'num_workers': num_workers,
            'dynamic': dynamic,
            'consistency_level': consistency_level
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['batch_insert'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_info(self, collection_name: str) -> Dict[str, Any]:
        context = {'collection_name': collection_name}

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_info'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        context = {'collection_name': collection_name}

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_collection'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def list_collections(self) -> Dict[str, Any]:
        context = {}

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['list_collections'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def aggregate(self,
                 collection_name: str,
                 fields: List[str],
                 group_by: Optional[List[str]] = None,
                 filters: Optional[Dict[str, Any]] = None,
                 limit: Optional[int] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'fields': fields,
            'group_by': group_by or [],
            'filters': filters or {},
            'limit': limit
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['aggregate'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def near_vector_search(self,
                      collection_name: str,
                      query_vector: List[float],
                      limit: int = 10,
                      offset: int = 0,
                      target_vector: str = None,
                      filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'query_vector': query_vector,
            'limit': limit,
            'offset': offset,
            'target_vector': target_vector,
            'filters': filters or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['near_vector_search'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def near_image_search(self,
                         collection_name: str,
                         image_path: Optional[str] = None,
                         base64_image: Optional[str] = None,
                         limit: int = 10,
                         offset: int = 0,
                         target_vector: str = "default",
                         filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'image_path': image_path,
            'base64_image': base64_image,
            'limit': limit,
            'offset': offset,
            'target_vector': target_vector,
            'filters': filters or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['near_image_search'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

def create_weaviate_agent(weaviate_url: str = "http://localhost:8080",
                         api_key: Optional[str] = None,
                         grpc_enabled: bool = False) -> WeaviateAgent:
    return WeaviateAgent(
        weaviate_url=weaviate_url,
        api_key=api_key,
        grpc_enabled=grpc_enabled
    )

class SimpleWeaviateClient:
    def __init__(self,
                 weaviate_url: str = "http://localhost:8080",
                 api_key: Optional[str] = None,
                 grpc_enabled: bool = False):
        from .components import WeaviateClientComponent
        self.client = WeaviateClientComponent(
            weaviate_url=weaviate_url,
            api_key=api_key,
            grpc_enabled=grpc_enabled
        )

    def test_connection(self) -> bool:
        try:
            return self.client.test_connection()
        except:
            return False

    def create_document_collection(self,
                                  collection_name: str = "Documents",
                                  vector_dimension: int = 1536) -> Dict[str, Any]:

        properties = [
            {
                "name": "text",
                "dataType": ["text"],
                "description": "Document content"
            },
            {
                "name": "metadata",
                "dataType": ["text"],
                "description": "Document metadata in JSON format"
            },
            {
                "name": "timestamp",
                "dataType": ["date"],
                "description": "Document creation timestamp"
            }
        ]

        return self.client.create_collection(
            collection_name=collection_name,
            properties=properties,
            vectorizer="none"
        )

    def search_documents(self,
                        collection_name: str = "Documents",
                        query_vector: List[float] = None,
                        limit: int = 5) -> Dict[str, Any]:

        if query_vector is None:
            query_vector = [0.0] * 1536

        return self.client.search_similar(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )

__all__ = [
    'WeaviatePlugin',
    'WeaviateAgent',
    'SimpleWeaviateClient',
    'create_weaviate_agent',
    'WeaviateClientComponent',
]
