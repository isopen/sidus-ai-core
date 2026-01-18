import sidusai as sai
from typing import Dict, Any, List, Union

from .components import MilvusClientComponent
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
    query_skill
)

__milvus_agent_name__ = 'milvus_agent'

class MilvusPlugin(sai.AgentPlugin):
    def __init__(self, 
                 uri: str = "http://localhost:19530",
                 token: str = "",
                 db_name: str = "default"):
        super().__init__()
        self.uri = uri
        self.token = token
        self.db_name = db_name
        self.milvus_client = None
        self.skills = {}
        print(f"Milvus Plugin initialized with URI: {uri}")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying Milvus plugin to agent...")

        try:
            self.milvus_client = MilvusClientComponent(
                uri=self.uri,
                token=self.token,
                db_name=self.db_name
            )
            print("Milvus client component created")

            def create_skill_wrapper(skill_func):
                def wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                    try:
                        context = {}
                        if hasattr(agent_value, 'value'):
                            context = agent_value.value
                        elif isinstance(agent_value, dict):
                            context = agent_value

                        context['milvus_client'] = self.milvus_client
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
                'query': query_skill
            }

            for skill_name, skill_func in skill_mappings.items():
                self.skills[skill_name] = create_skill_wrapper(skill_func)

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.milvus_client = self.milvus_client
            agent.milvus_skills = self.skills

            print("Milvus plugin applied successfully")

        except Exception as e:
            print(f"Error applying Milvus plugin: {e}")
            import traceback
            traceback.print_exc()

class MilvusAgent(sai.Agent):
    def __init__(self, 
                 name: str = __milvus_agent_name__,
                 uri: str = "http://localhost:19530",
                 token: str = "",
                 db_name: str = "default"):
        super().__init__()
        self._name = name

        print(f"Creating Milvus Agent '{name}'...")
        self.plugin = MilvusPlugin(
            uri=uri,
            token=token,
            db_name=db_name
        )
        self.plugin.apply_plugin(self)
        print(f"Milvus Agent '{name}' created successfully")

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
                         dimension: int,
                         metric_type: str = "COSINE") -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'dimension': dimension,
            'metric_type': metric_type
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_collection'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def store_document(self,
                      collection_name: str,
                      data: List[Dict[str, Any]]) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'data': data
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['store_document'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_similar(self,
                      collection_name: str,
                      data: List[List[float]],
                      limit: int = 10,
                      output_fields: List[str] = None,
                      filter: str = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'data': data,
            'limit': limit,
            'output_fields': output_fields or [],
            'filter': filter
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_similar'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def query(self,
             collection_name: str,
             filter: str,
             output_fields: List[str] = None,
             limit: int = None,
             offset: int = 0) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'filter': filter,
            'output_fields': output_fields or [],
            'limit': limit,
            'offset': offset
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['query'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def fetch_object(self,
                    collection_name: str,
                    ids: List[Union[int, str]],
                    output_fields: List[str] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'ids': ids,
            'output_fields': output_fields or []
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['fetch_object'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def update_object(self,
                     collection_name: str,
                     data: List[Dict[str, Any]]) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'data': data
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['update_object'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_object(self,
                     collection_name: str,
                     filter: str) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'filter': filter
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_object'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def batch_insert(self,
                    collection_name: str,
                    data: List[Dict[str, Any]]) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'data': data
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

def create_milvus_agent(uri: str = "http://localhost:19530",
                       token: str = "",
                       db_name: str = "default") -> MilvusAgent:
    return MilvusAgent(
        uri=uri,
        token=token,
        db_name=db_name
    )

class SimpleMilvusClient:
    def __init__(self,
                 uri: str = "http://localhost:19530",
                 token: str = "",
                 db_name: str = "default"):
        from .components import MilvusClientComponent
        self.client = MilvusClientComponent(
            uri=uri,
            token=token,
            db_name=db_name
        )

    def test_connection(self) -> bool:
        try:
            return self.client.test_connection()
        except:
            return False

    def create_document_collection(self,
                                  collection_name: str = "Documents",
                                  vector_dimension: int = 768) -> Dict[str, Any]:

        return self.client.create_collection(
            collection_name=collection_name,
            dimension=vector_dimension,
            metric_type="COSINE"
        )

    def search_documents(self,
                        collection_name: str = "Documents",
                        query_vector: List[float] = None,
                        limit: int = 5) -> Dict[str, Any]:

        if query_vector is None:
            query_vector = [0.0] * 768

        return self.client.search_similar(
            collection_name=collection_name,
            data=[query_vector],
            limit=limit,
            output_fields=["title", "content"]
        )

__all__ = [
    'MilvusPlugin',
    'MilvusAgent',
    'SimpleMilvusClient',
    'create_milvus_agent',
    'MilvusClientComponent',
]
