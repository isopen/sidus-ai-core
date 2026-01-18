import sidusai as sai
from typing import Optional, Dict, Any, List

from .components import OpenSearchClientComponent
from .skills import (
    create_index_skill,
    search_knn_skill,
    search_neural_skill,
    get_info_skill,
    delete_index_skill,
    list_indices_skill,
    index_document_skill,
    get_document_skill,
    update_document_skill,
    delete_document_skill,
    bulk_insert_skill,
    aggregate_skill,
    search_hybrid_skill,
    search_text_skill,
    search_image_skill,
    create_knn_field_skill
)

__opensearch_agent_name__ = 'opensearch_agent'

class OpenSearchPlugin(sai.AgentPlugin):
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 9200,
                 use_ssl: bool = False,
                 verify_certs: bool = True,
                 http_auth: Optional[tuple] = None,
                 timeout: int = 30):
        super().__init__()
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.verify_certs = verify_certs
        self.http_auth = http_auth
        self.timeout = timeout
        self.opensearch_client = None
        self.skills = {}
        print(f"OpenSearch Plugin initialized with host: {host}:{port}")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying OpenSearch plugin to agent...")

        try:
            self.opensearch_client = OpenSearchClientComponent(
                host=self.host,
                port=self.port,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                http_auth=self.http_auth,
                timeout=self.timeout
            )
            print("OpenSearch client component created")

            def create_skill_wrapper(skill_func):
                def wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                    try:
                        context = {}
                        if hasattr(agent_value, 'value'):
                            context = agent_value.value
                        elif isinstance(agent_value, dict):
                            context = agent_value

                        context['opensearch_client'] = self.opensearch_client
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
                'create_index': create_index_skill,
                'search_knn': search_knn_skill,
                'search_neural': search_neural_skill,
                'get_info': get_info_skill,
                'delete_index': delete_index_skill,
                'list_indices': list_indices_skill,
                'index_document': index_document_skill,
                'get_document': get_document_skill,
                'update_document': update_document_skill,
                'delete_document': delete_document_skill,
                'bulk_insert': bulk_insert_skill,
                'aggregate': aggregate_skill,
                'search_hybrid': search_hybrid_skill,
                'search_text': search_text_skill,
                'search_image': search_image_skill,
                'create_knn_field': create_knn_field_skill
            }

            for skill_name, skill_func in skill_mappings.items():
                self.skills[skill_name] = create_skill_wrapper(skill_func)

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.opensearch_client = self.opensearch_client
            agent.opensearch_skills = self.skills

            print("OpenSearch plugin applied successfully")

        except Exception as e:
            print(f"Error applying OpenSearch plugin: {e}")
            import traceback
            traceback.print_exc()

class OpenSearchAgent(sai.Agent):
    def __init__(self, 
                 name: str = __opensearch_agent_name__,
                 host: str = "localhost",
                 port: int = 9200,
                 use_ssl: bool = False,
                 verify_certs: bool = True,
                 http_auth: Optional[tuple] = None,
                 timeout: int = 30):
        super().__init__()
        self._name = name

        print(f"Creating OpenSearch Agent '{name}'...")
        self.plugin = OpenSearchPlugin(
            host=host,
            port=port,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            http_auth=http_auth,
            timeout=timeout
        )
        self.plugin.apply_plugin(self)
        print(f"OpenSearch Agent '{name}' created successfully")

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

    def create_index(self,
                    index_name: str,
                    mappings: Optional[Dict[str, Any]] = None,
                    settings: Optional[Dict[str, Any]] = None,
                    knn_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'mappings': mappings or {},
            'settings': settings or {},
            'knn_settings': knn_settings or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_index'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def create_knn_field(self,
                        index_name: str,
                        field_name: str,
                        dimension: int,
                        method: str = "hnsw",
                        engine: str = "faiss",
                        space_type: str = "l2",
                        parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'field_name': field_name,
            'dimension': dimension,
            'method': method,
            'engine': engine,
            'space_type': space_type,
            'parameters': parameters or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_knn_field'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def index_document(self,
                      index_name: str,
                      document: Dict[str, Any],
                      document_id: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'document': document,
            'document_id': document_id
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['index_document'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_document(self,
                    index_name: str,
                    document_id: str) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'document_id': document_id
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_document'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

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

        context = {
            'index_name': index_name,
            'vector_field': vector_field,
            'vector': vector,
            'k': k,
            'max_distance': max_distance,
            'min_score': min_score,
            'filter_query': filter_query or {},
            'method_parameters': method_parameters or {},
            'rescore_params': rescore_params or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_knn'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

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

        context = {
            'index_name': index_name,
            'vector_field': vector_field,
            'query_text': query_text,
            'query_image': query_image,
            'model_id': model_id,
            'k': k,
            'max_distance': max_distance,
            'min_score': min_score,
            'filter_query': filter_query or {},
            'method_parameters': method_parameters or {},
            'rescore_params': rescore_params or {},
            'semantic_field_search_analyzer': semantic_field_search_analyzer
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_neural'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_hybrid(self,
                     index_name: str,
                     knn_query: Dict[str, Any],
                     text_query: Optional[Dict[str, Any]] = None,
                     neural_query: Optional[Dict[str, Any]] = None,
                     boost_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'knn_query': knn_query,
            'text_query': text_query or {},
            'neural_query': neural_query or {},
            'boost_weights': boost_weights or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_hybrid'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_text(self,
                   index_name: str,
                   query: Dict[str, Any],
                   size: int = 10,
                   from_: int = 0) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'query': query,
            'size': size,
            'from_': from_
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_text'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_image(self,
                    index_name: str,
                    vector_field: str,
                    image_path: Optional[str] = None,
                    base64_image: Optional[str] = None,
                    model_id: Optional[str] = None,
                    k: int = 10) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'vector_field': vector_field,
            'image_path': image_path,
            'base64_image': base64_image,
            'model_id': model_id,
            'k': k
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_image'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def update_document(self,
                       index_name: str,
                       document_id: str,
                       doc: Dict[str, Any],
                       script: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'document_id': document_id,
            'doc': doc,
            'script': script
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['update_document'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_document(self,
                       index_name: str,
                       document_id: Optional[str] = None,
                       query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'document_id': document_id,
            'query': query or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_document'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def bulk_insert(self,
                   index_name: str,
                   documents: List[Dict[str, Any]],
                   batch_size: int = 1000,
                   refresh: bool = False) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'documents': documents,
            'batch_size': batch_size,
            'refresh': refresh
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['bulk_insert'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_info(self, index_name: str) -> Dict[str, Any]:
        context = {'index_name': index_name}

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_info'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_index(self, index_name: str) -> Dict[str, Any]:
        context = {'index_name': index_name}

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_index'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def list_indices(self, pattern: str = "*") -> Dict[str, Any]:
        context = {'pattern': pattern}

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['list_indices'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def aggregate(self,
                 index_name: str,
                 aggs: Dict[str, Any],
                 query: Optional[Dict[str, Any]] = None,
                 size: int = 0) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'aggs': aggs,
            'query': query or {},
            'size': size
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['aggregate'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

def create_opensearch_agent(host: str = "localhost",
                           port: int = 9200,
                           use_ssl: bool = False,
                           verify_certs: bool = True,
                           http_auth: Optional[tuple] = None,
                           timeout: int = 30) -> OpenSearchAgent:
    return OpenSearchAgent(
        host=host,
        port=port,
        use_ssl=use_ssl,
        verify_certs=verify_certs,
        http_auth=http_auth,
        timeout=timeout
    )

class SimpleOpenSearchClient:
    def __init__(self,
                 host: str = "localhost",
                 port: int = 9200,
                 use_ssl: bool = False,
                 verify_certs: bool = True,
                 http_auth: Optional[tuple] = None,
                 timeout: int = 30):
        from .components import OpenSearchClientComponent
        self.client = OpenSearchClientComponent(
            host=host,
            port=port,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            http_auth=http_auth,
            timeout=timeout
        )

    def test_connection(self) -> bool:
        try:
            return self.client.test_connection()
        except:
            return False

    def create_document_index(self,
                             index_name: str = "documents",
                             vector_dimension: int = 768) -> Dict[str, Any]:

        mappings = {
            "properties": {
                "text": {"type": "text"},
                "metadata": {"type": "object"},
                "timestamp": {"type": "date"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": vector_dimension,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "faiss",
                        "parameters": {
                            "ef_construction": 128,
                            "m": 16
                        }
                    }
                }
            }
        }

        settings = {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 100
            }
        }

        return self.client.create_index(
            index_name=index_name,
            mappings=mappings,
            settings=settings
        )

    def search_documents(self,
                        index_name: str = "documents",
                        query_vector: List[float] = None,
                        k: int = 5) -> Dict[str, Any]:

        if query_vector is None:
            query_vector = [0.0] * 768

        return self.client.search_knn(
            index_name=index_name,
            vector_field="embedding",
            vector=query_vector,
            k=k
        )

__all__ = [
    'OpenSearchPlugin',
    'OpenSearchAgent',
    'SimpleOpenSearchClient',
    'create_opensearch_agent',
    'OpenSearchClientComponent',
]
