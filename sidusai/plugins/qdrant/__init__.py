import sidusai as sai
from typing import Optional, Dict, Any, List, Union

from .components import QdrantClientComponent
from .skills import (
    create_collection_skill,
    upload_points_skill,
    upload_documents_skill,
    search_similar_skill,
    get_collection_info_skill,
    scroll_points_skill
)
from .models import Document, SearchResult

__qdrant_agent_name__ = 'qdrant_vector_agent'

class QdrantPlugin(sai.AgentPlugin):
    def __init__(self, host: str = "localhost", port: int = 6333):
        super().__init__()
        self.host = host
        self.port = port
        self.qdrant_client = None
        print(f"Qdrant Plugin initialized (host: {host}, port: {port})")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying Qdrant plugin to agent...")

        try:
            self.qdrant_client = QdrantClientComponent(self.host, self.port)
            print("Qdrant client component created")

            self.skills = {}

            def create_collection_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['qdrant_client'] = self.qdrant_client
                    result = create_collection_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def upload_points_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['qdrant_client'] = self.qdrant_client
                    result = upload_points_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def upload_documents_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['qdrant_client'] = self.qdrant_client
                    result = upload_documents_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def search_similar_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['qdrant_client'] = self.qdrant_client
                    result = search_similar_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def get_collection_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['qdrant_client'] = self.qdrant_client
                    result = get_collection_info_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def scroll_points_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['qdrant_client'] = self.qdrant_client
                    result = scroll_points_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            self.skills = {
                'create_collection': create_collection_wrapper,
                'upload_points': upload_points_wrapper,
                'upload_documents': upload_documents_wrapper,
                'search_similar': search_similar_wrapper,
                'get_collection_info': get_collection_info_wrapper,
                'scroll_points': scroll_points_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.qdrant_client = self.qdrant_client
            agent.qdrant_skills = self.skills

            print("Qdrant plugin applied successfully")

        except Exception as e:
            print(f"Error applying Qdrant plugin: {e}")
            import traceback
            traceback.print_exc()

class QdrantAgent(sai.Agent):
    def __init__(self, name: str = __qdrant_agent_name__, host: str = "localhost", port: int = 6333):
        super().__init__()
        self._name = name
        self.host = host
        self.port = port

        print(f"Creating Qdrant Agent '{name}'...")
        self.plugin = QdrantPlugin(host=host, port=port)
        self.plugin.apply_plugin(self)
        print(f"Qdrant Agent '{name}' created successfully")

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
                         vector_size: int = 384,
                         distance: str = "COSINE",
                         sparse_vectors: bool = False) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'vector_size': vector_size,
            'distance': distance,
            'sparse_vectors': sparse_vectors
        }

        if 'create_collection' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_collection'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def upload_points(self,
                     collection_name: str,
                     vectors: List[List[float]],
                     payloads: List[Dict],
                     ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'vectors': vectors,
            'payloads': payloads,
            'ids': ids
        }

        if 'upload_points' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['upload_points'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def upload_documents(self,
                        collection_name: str,
                        documents: List[Union[Document, Dict]],
                        vectors: List[List[float]],
                        ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'documents': documents,
            'vectors': vectors,
            'ids': ids
        }

        if 'upload_documents' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['upload_documents'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_similar(self,
                      collection_name: str,
                      query_vector: List[float],
                      limit: int = 10,
                      filters: Optional[Dict] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'query_vector': query_vector,
            'limit': limit,
            'filters': filters
        }

        if 'search_similar' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_similar'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        context = {'collection_name': collection_name}

        if 'get_collection_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_collection_info'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def scroll_points(self,
                     collection_name: str,
                     limit: int = 100,
                     offset: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'limit': limit,
            'offset': offset
        }

        if 'scroll_points' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['scroll_points'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        return self.qdrant_client.delete_collection(collection_name)

    def get_point(self,
                 collection_name: str,
                 point_id: Union[int, str]) -> Dict[str, Any]:
        return self.qdrant_client.get_point(collection_name, point_id)

def create_qdrant_agent(host: str = "localhost", port: int = 6333) -> QdrantAgent:
    return QdrantAgent(host=host, port=port)

class SimpleQdrantClient:
    def __init__(self, host: str = "localhost", port: int = 6333):
        from .components import QdrantClientComponent
        self.client = QdrantClientComponent(host, port)

    def test_connection(self) -> bool:
        try:
            return self.client.test_connection()
        except:
            return False

    def create_sample_collection(self) -> Dict[str, Any]:
        return self.client.create_collection(
            collection_name="sample_collection",
            vector_size=384,
            distance="COSINE"
        )

    def upload_sample_data(self) -> Dict[str, Any]:
        vectors = [
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8],
            [0.9, 0.8, 0.7, 0.6]
        ]

        payloads = [
            {"text": "First document", "category": "A"},
            {"text": "Second document", "category": "B"},
            {"text": "Third document", "category": "A"}
        ]

        return self.client.upload_points(
            collection_name="sample_collection",
            vectors=vectors,
            payloads=payloads
        )

__all__ = [
    'QdrantPlugin',
    'QdrantAgent',
    'SimpleQdrantClient',
    'create_qdrant_agent',
    'QdrantClientComponent',
    'Document',
    'SearchResult'
]
