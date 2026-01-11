import sidusai as sai
from typing import Optional, Dict, Any, List

from .components import RedisVLClientComponent
from .skills import (
    create_index_skill,
    search_similar_skill,
    get_info_skill,
    delete_index_skill,
    list_indices_skill,
    store_document_skill
)

__redisvl_agent_name__ = 'redisvl_agent'

class RedisVLPlugin(sai.AgentPlugin):
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        super().__init__()
        self.redis_url = redis_url
        self.redisvl_client = None
        print(f"RedisVL Plugin initialized with URL: {redis_url}")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying RedisVL plugin to agent...")

        try:
            self.redisvl_client = RedisVLClientComponent(self.redis_url)
            print("RedisVL client component created")

            self.skills = {}

            def create_index_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['redisvl_client'] = self.redisvl_client
                    result = create_index_skill(context)
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

                    context['redisvl_client'] = self.redisvl_client
                    result = search_similar_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def get_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['redisvl_client'] = self.redisvl_client
                    result = get_info_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def delete_index_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['redisvl_client'] = self.redisvl_client
                    result = delete_index_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def list_indices_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['redisvl_client'] = self.redisvl_client
                    result = list_indices_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def store_document_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['redisvl_client'] = self.redisvl_client
                    result = store_document_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            self.skills = {
                'create_index': create_index_wrapper,
                'search_similar': search_similar_wrapper,
                'get_info': get_info_wrapper,
                'delete_index': delete_index_wrapper,
                'list_indices': list_indices_wrapper,
                'store_document': store_document_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.redisvl_client = self.redisvl_client
            agent.redisvl_skills = self.skills

            print("RedisVL plugin applied successfully")

        except Exception as e:
            print(f"Error applying RedisVL plugin: {e}")
            import traceback
            traceback.print_exc()

class RedisVLAgent(sai.Agent):
    def __init__(self, name: str = __redisvl_agent_name__, redis_url: str = "redis://localhost:6379"):
        super().__init__()
        self._name = name

        print(f"Creating RedisVL Agent '{name}'...")
        self.plugin = RedisVLPlugin(redis_url=redis_url)
        self.plugin.apply_plugin(self)
        print(f"RedisVL Agent '{name}' created successfully")

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
                    vector_schema: Dict[str, Any],
                    prefix: str = "doc:",
                    index_type: str = "HNSW") -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'vector_schema': vector_schema,
            'prefix': prefix,
            'index_type': index_type
        }

        if 'create_index' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_index'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_similar(self,
                      index_name: str,
                      query_vector: List[float],
                      vector_field_name: str = "embedding",
                      return_fields: Optional[List[str]] = None,
                      limit: int = 10,
                      filter_expression: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'query_vector': query_vector,
            'vector_field_name': vector_field_name,
            'return_fields': return_fields or [],
            'limit': limit,
            'filter_expression': filter_expression
        }

        if 'search_similar' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_similar'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_info(self, index_name: str) -> Dict[str, Any]:
        context = {'index_name': index_name}

        if 'get_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_info'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_index(self, index_name: str, drop: bool = True) -> Dict[str, Any]:
        context = {
            'index_name': index_name,
            'drop': drop
        }

        if 'delete_index' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_index'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def list_indices(self) -> Dict[str, Any]:
        context = {}

        if 'list_indices' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['list_indices'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def store_document(self,
                      index_name: str,
                      document_id: str,
                      text: str,
                      embedding: List[float],
                      metadata: Optional[Dict] = None) -> Dict[str, Any]:

        context = {
            'index_name': index_name,
            'document_id': document_id,
            'text': text,
            'embedding': embedding,
            'metadata': metadata
        }

        if 'store_document' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['store_document'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

def create_redisvl_agent(redis_url: str = "redis://localhost:6379") -> RedisVLAgent:
    return RedisVLAgent(redis_url=redis_url)

class SimpleRedisVLClient:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        from .components import RedisVLClientComponent
        self.client = RedisVLClientComponent(redis_url)

    def test_connection(self) -> bool:
        try:
            return self.client.test_connection()
        except:
            return False

    def create_document_index(self,
                             index_name: str = "documents",
                             vector_dimension: int = 384,
                             distance_metric: str = "COSINE") -> Dict[str, Any]:

        vector_schema = {
            "vector_fields": [{
                "name": "embedding",
                "dims": vector_dimension,
                "distance_metric": distance_metric
            }]
        }

        return self.client.create_index(
            index_name=index_name,
            vector_schema=vector_schema,
            prefix="doc:"
        )

    def search_documents(self,
                        index_name: str = "documents",
                        query_vector: List[float] = None,
                        limit: int = 5) -> Dict[str, Any]:

        if query_vector is None:
            query_vector = [0.0] * 384

        return self.client.search_similar(
            index_name=index_name,
            query_vector=query_vector,
            limit=limit
        )

__all__ = [
    'RedisVLPlugin',
    'RedisVLAgent',
    'SimpleRedisVLClient',
    'create_redisvl_agent',
    'RedisVLClientComponent',
]
