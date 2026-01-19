import sidusai as sai
from typing import Optional, Dict, Any, List

from .components import ElasticsearchClientComponent
from .skills import (
    create_index_skill,
    search_dense_vector_skill,
    search_text_skill,
    get_info_skill,
    delete_index_skill,
    list_indices_skill,
    index_document_skill,
    get_document_skill,
    update_document_skill,
    delete_document_skill,
    bulk_insert_skill,
    aggregate_skill,
    search_hybrid_vector_skill,
    create_dense_vector_field_skill,
    search_semantic_skill,
    cluster_health_skill
)

__elasticsearch_agent_name__ = 'elasticsearch_agent'

class ElasticsearchPlugin(sai.AgentPlugin):
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
        super().__init__()
        self.host = host
        self.port = port
        self.scheme = scheme
        self.api_key = api_key
        self.username = username
        self.password = password
        self.timeout = timeout
        self.verify_certs = verify_certs
        self.cloud_id = cloud_id
        self.elasticsearch_client = None
        self.skills = {}
        print(f"Elasticsearch Plugin initialized with host: {host}:{port}")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying Elasticsearch plugin to agent...")

        try:
            self.elasticsearch_client = ElasticsearchClientComponent(
                host=self.host,
                port=self.port,
                scheme=self.scheme,
                api_key=self.api_key,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                verify_certs=self.verify_certs,
                cloud_id=self.cloud_id
            )
            print("Elasticsearch client component created")

        except Exception as e:
            print(f"❌ Failed to create Elasticsearch client: {e}")
            self.elasticsearch_client = None

        def create_skill_wrapper(skill_func):
            def wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    if self.elasticsearch_client is None:
                        error_value = sai.AgentValue()
                        error_value.value = {
                            "success": False, 
                            "error": "Elasticsearch client not connected. Check connection parameters."
                        }
                        return error_value

                    context['elasticsearch_client'] = self.elasticsearch_client
                    result = skill_func(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Skill error: {str(e)}"}
                    return error_value
            return wrapper

        skill_mappings = {
            'create_index': create_index_skill,
            'search_dense_vector': search_dense_vector_skill,
            'search_text': search_text_skill,
            'get_info': get_info_skill,
            'delete_index': delete_index_skill,
            'list_indices': list_indices_skill,
            'index_document': index_document_skill,
            'get_document': get_document_skill,
            'update_document': update_document_skill,
            'delete_document': delete_document_skill,
            'bulk_insert': bulk_insert_skill,
            'aggregate': aggregate_skill,
            'search_hybrid_vector': search_hybrid_vector_skill,
            'create_dense_vector_field': create_dense_vector_field_skill,
            'search_semantic': search_semantic_skill,
            'cluster_health': cluster_health_skill
        }

        for skill_name, skill_func in skill_mappings.items():
            self.skills[skill_name] = create_skill_wrapper(skill_func)

        for skill_name, skill_func in self.skills.items():
            agent.add_skill(skill_func, name=skill_name)

        agent.elasticsearch_client = self.elasticsearch_client
        agent.elasticsearch_skills = self.skills

        if self.elasticsearch_client is not None:
            print("✅ Elasticsearch plugin applied successfully")
        else:
            print("⚠️  Elasticsearch plugin applied but client is not connected")

class ElasticsearchAgent(sai.Agent):
    def __init__(self, 
                 name: str = __elasticsearch_agent_name__,
                 host: str = "localhost",
                 port: int = 9200,
                 scheme: str = "http",
                 api_key: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 timeout: int = 30,
                 verify_certs: bool = True,
                 cloud_id: Optional[str] = None):
        super().__init__()
        self._name = name

        print(f"Creating Elasticsearch Agent '{name}'...")
        self.plugin = ElasticsearchPlugin(
            host=host,
            port=port,
            scheme=scheme,
            api_key=api_key,
            username=username,
            password=password,
            timeout=timeout,
            verify_certs=verify_certs,
            cloud_id=cloud_id
        )
        self.plugin.apply_plugin(self)
        print(f"Elasticsearch Agent '{name}' created successfully")

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
                    settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'mappings': mappings or {},
            'settings': settings or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_index'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def create_dense_vector_field(self,
                                 index_name: str,
                                 field_name: str,
                                 dimension: int,
                                 similarity: str = "cosine",
                                 index_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'field_name': field_name,
            'dimension': dimension,
            'similarity': similarity,
            'index_options': index_options or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_dense_vector_field'](agent_value)
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

    def search_dense_vector(self,
                           index_name: str,
                           vector_field: str,
                           vector: List[float],
                           k: int = 10,
                           filter_query: Optional[Dict[str, Any]] = None,
                           score_threshold: Optional[float] = None,
                           num_candidates: int = 100) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'vector_field': vector_field,
            'vector': vector,
            'k': k,
            'filter_query': filter_query or {},
            'score_threshold': score_threshold,
            'num_candidates': num_candidates
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_dense_vector'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_hybrid_vector(self,
                            index_name: str,
                            vector_field: str,
                            vector: List[float],
                            text_query: Dict[str, Any],
                            k: int = 10,
                            vector_weight: float = 0.7,
                            text_weight: float = 0.3,
                            filter_query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'vector_field': vector_field,
            'vector': vector,
            'text_query': text_query,
            'k': k,
            'vector_weight': vector_weight,
            'text_weight': text_weight,
            'filter_query': filter_query or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_hybrid_vector'](agent_value)
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

    def search_semantic(self,
                       index_name: str,
                       query_text: str,
                       model_id: str,
                       field_name: str = "text_embedding",
                       k: int = 10) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'query_text': query_text,
            'model_id': model_id,
            'field_name': field_name,
            'k': k
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_semantic'](agent_value)
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

    def cluster_health(self) -> Dict[str, Any]:
        context = {}

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['cluster_health'](agent_value)
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

def create_elasticsearch_agent(host: str = "localhost",
                              port: int = 9200,
                              scheme: str = "http",
                              api_key: Optional[str] = None,
                              username: Optional[str] = None,
                              password: Optional[str] = None,
                              timeout: int = 30,
                              verify_certs: bool = True,
                              cloud_id: Optional[str] = None) -> ElasticsearchAgent:
    return ElasticsearchAgent(
        host=host,
        port=port,
        scheme=scheme,
        api_key=api_key,
        username=username,
        password=password,
        timeout=timeout,
        verify_certs=verify_certs,
        cloud_id=cloud_id
    )

class SimpleElasticsearchClient:
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
        from .components import ElasticsearchClientComponent
        self.client = ElasticsearchClientComponent(
            host=host,
            port=port,
            scheme=scheme,
            api_key=api_key,
            username=username,
            password=password,
            timeout=timeout,
            verify_certs=verify_certs,
            cloud_id=cloud_id
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
                    "type": "dense_vector",
                    "dims": vector_dimension,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }

        settings = {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
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

        return self.client.search_dense_vector(
            index_name=index_name,
            vector_field="embedding",
            vector=query_vector,
            k=k
        )

__all__ = [
    'ElasticsearchPlugin',
    'ElasticsearchAgent',
    'SimpleElasticsearchClient',
    'create_elasticsearch_agent',
    'ElasticsearchClientComponent',
]
