import sidusai as sai
from typing import Optional, Dict, Any, List

from .components import PgVectorClientComponent
from .skills import (
    create_table_skill,
    create_index_skill,
    insert_vectors_skill,
    query_vectors_skill,
    search_with_filter_skill,
    delete_vectors_skill,
    update_vectors_skill,
    get_table_info_skill,
    list_tables_skill,
    test_connection_skill,
    bulk_insert_skill,
    get_vector_statistics_skill,
    create_vector_extension_skill,
    modify_table_skill,
    hybrid_search_skill
)

__pgvector_agent_name__ = 'pgvector_agent'

class PgVectorPlugin(sai.AgentPlugin):
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 5432,
                 database: str = "postgres",
                 user: str = "postgres",
                 password: str = "",
                 schema: str = "public",
                 table_prefix: str = "vectors_",
                 connection_pool_size: int = 5,
                 ssl_mode: str = "prefer"):

        super().__init__()
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.schema = schema
        self.table_prefix = table_prefix
        self.connection_pool_size = connection_pool_size
        self.ssl_mode = ssl_mode
        self.pgvector_client = None

    def apply_plugin(self, agent: sai.Agent):

        try:
            self.pgvector_client = PgVectorClientComponent(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                schema=self.schema,
                table_prefix=self.table_prefix,
                connection_pool_size=self.connection_pool_size,
                ssl_mode=self.ssl_mode
            )

            self.skills = {}

            def create_vector_extension_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = create_vector_extension_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def create_table_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = create_table_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def modify_table_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = modify_table_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def create_index_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = create_index_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def insert_vectors_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = insert_vectors_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def query_vectors_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = query_vectors_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def search_with_filter_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = search_with_filter_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def hybrid_search_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = hybrid_search_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def delete_vectors_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = delete_vectors_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def update_vectors_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = update_vectors_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def get_table_info_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = get_table_info_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def list_tables_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = list_tables_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def test_connection_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = test_connection_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def bulk_insert_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = bulk_insert_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def get_vector_statistics_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['pgvector_client'] = self.pgvector_client
                    result = get_vector_statistics_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            self.skills = {
                'create_vector_extension': create_vector_extension_wrapper,
                'create_table': create_table_wrapper,
                'modify_table': modify_table_wrapper,
                'create_index': create_index_wrapper,
                'insert_vectors': insert_vectors_wrapper,
                'query_vectors': query_vectors_wrapper,
                'search_with_filter': search_with_filter_wrapper,
                'hybrid_search': hybrid_search_wrapper,
                'delete_vectors': delete_vectors_wrapper,
                'update_vectors': update_vectors_wrapper,
                'get_table_info': get_table_info_wrapper,
                'list_tables': list_tables_wrapper,
                'test_connection': test_connection_wrapper,
                'bulk_insert': bulk_insert_wrapper,
                'get_vector_statistics': get_vector_statistics_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.pgvector_client = self.pgvector_client
            agent.pgvector_skills = self.skills

        except Exception as e:
            print(f"Error applying PgVector plugin: {e}")

class PgVectorAgent(sai.Agent):
    def __init__(self, 
                 name: str = __pgvector_agent_name__,
                 host: str = "localhost",
                 port: int = 5432,
                 database: str = "postgres",
                 user: str = "postgres",
                 password: str = "",
                 schema: str = "public",
                 table_prefix: str = "vectors_",
                 connection_pool_size: int = 5,
                 ssl_mode: str = "prefer"):

        super().__init__()
        self._name = name

        self.plugin = PgVectorPlugin(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            schema=schema,
            table_prefix=table_prefix,
            connection_pool_size=connection_pool_size,
            ssl_mode=ssl_mode
        )
        self.plugin.apply_plugin(self)

    @property
    def name(self):
        return self._name

    def _create_agent_value(self, context: Dict[str, Any]) -> sai.AgentValue:
        try:
            agent_value = sai.AgentValue()
            agent_value.value = context
            return agent_value
        except Exception as e:
            agent_value = sai.AgentValue()
            setattr(agent_value, 'value', context)
            return agent_value

    def create_vector_extension(self) -> Dict[str, Any]:
        context = {}
        if 'create_vector_extension' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_vector_extension'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def create_table(self,
                    table_name: str,
                    vector_dimension: int = 1536,
                    metadata_columns: Optional[Dict[str, str]] = None,
                    with_hnsw: bool = False,
                    hnsw_m: int = 16,
                    hnsw_ef_construction: int = 64) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'vector_dimension': vector_dimension,
            'metadata_columns': metadata_columns or {},
            'with_hnsw': with_hnsw,
            'hnsw_m': hnsw_m,
            'hnsw_ef_construction': hnsw_ef_construction
        }

        if 'create_table' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_table'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def modify_table(self,
                    table_name: str,
                    add_columns: Optional[Dict[str, str]] = None,
                    drop_columns: Optional[List[str]] = None,
                    rename_columns: Optional[Dict[str, str]] = None) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'add_columns': add_columns or {},
            'drop_columns': drop_columns or [],
            'rename_columns': rename_columns or {}
        }

        if 'modify_table' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['modify_table'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def create_index(self,
                    table_name: str,
                    index_type: str = "hnsw",
                    distance_metric: str = "l2",
                    hnsw_m: int = 16,
                    hnsw_ef_construction: int = 64,
                    ivfflat_lists: int = 100,
                    concurrently: bool = False) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'index_type': index_type,
            'distance_metric': distance_metric,
            'hnsw_m': hnsw_m,
            'hnsw_ef_construction': hnsw_ef_construction,
            'ivfflat_lists': ivfflat_lists,
            'concurrently': concurrently
        }

        if 'create_index' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_index'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def insert_vectors(self,
                      table_name: str,
                      vectors: List[List[float]],
                      metadata_list: Optional[List[Dict[str, Any]]] = None,
                      ids: Optional[List[Any]] = None,
                      content_list: Optional[List[str]] = None) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'vectors': vectors,
            'metadata_list': metadata_list or [],
            'ids': ids or [],
            'content_list': content_list or []
        }

        if 'insert_vectors' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['insert_vectors'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def query_vectors(self,
                     table_name: str,
                     query_vector: List[float],
                     limit: int = 10,
                     distance_metric: str = "l2",
                     return_columns: Optional[List[str]] = None,
                     hnsw_ef_search: Optional[int] = None,
                     ivfflat_probes: Optional[int] = None) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'query_vector': query_vector,
            'limit': limit,
            'distance_metric': distance_metric,
            'return_columns': return_columns or ["id", "content", "metadata"],
            'hnsw_ef_search': hnsw_ef_search,
            'ivfflat_probes': ivfflat_probes
        }

        if 'query_vectors' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['query_vectors'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_with_filter(self,
                          table_name: str,
                          query_vector: List[float],
                          filter_conditions: Dict[str, Any],
                          limit: int = 10,
                          distance_metric: str = "l2",
                          hnsw_ef_search: Optional[int] = None) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'query_vector': query_vector,
            'filter_conditions': filter_conditions,
            'limit': limit,
            'distance_metric': distance_metric,
            'hnsw_ef_search': hnsw_ef_search
        }

        if 'search_with_filter' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_with_filter'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def hybrid_search(self,
                     table_name: str,
                     query_text: str,
                     query_vector: List[float],
                     limit: int = 10,
                     text_weight: float = 0.5,
                     vector_weight: float = 0.5,
                     distance_metric: str = "l2") -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'query_text': query_text,
            'query_vector': query_vector,
            'limit': limit,
            'text_weight': text_weight,
            'vector_weight': vector_weight,
            'distance_metric': distance_metric
        }

        if 'hybrid_search' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['hybrid_search'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_vectors(self,
                      table_name: str,
                      ids: Optional[List[Any]] = None,
                      filter_conditions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'ids': ids or [],
            'filter_conditions': filter_conditions or {}
        }

        if 'delete_vectors' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_vectors'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def update_vectors(self,
                      table_name: str,
                      ids: List[Any],
                      vectors: Optional[List[List[float]]] = None,
                      metadata_list: Optional[List[Dict[str, Any]]] = None,
                      content_list: Optional[List[str]] = None) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'ids': ids,
            'vectors': vectors or [],
            'metadata_list': metadata_list or [],
            'content_list': content_list or []
        }

        if 'update_vectors' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['update_vectors'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_table_info(self,
                      table_name: str) -> Dict[str, Any]:

        context = {
            'table_name': table_name
        }

        if 'get_table_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_table_info'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def list_tables(self,
                   pattern: Optional[str] = None,
                   limit: int = 100) -> Dict[str, Any]:

        context = {
            'pattern': pattern,
            'limit': limit
        }

        if 'list_tables' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['list_tables'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def test_connection(self) -> Dict[str, Any]:

        context = {}

        if 'test_connection' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['test_connection'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def bulk_insert(self,
                   table_name: str,
                   vectors: List[List[float]],
                   metadata_list: List[Dict[str, Any]],
                   content_list: List[str],
                   batch_size: int = 1000) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'vectors': vectors,
            'metadata_list': metadata_list,
            'content_list': content_list,
            'batch_size': batch_size
        }

        if 'bulk_insert' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['bulk_insert'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_vector_statistics(self,
                             table_name: str) -> Dict[str, Any]:

        context = {
            'table_name': table_name
        }

        if 'get_vector_statistics' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_vector_statistics'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

def create_pgvector_agent(host: str = "localhost",
                         port: int = 5432,
                         database: str = "postgres",
                         user: str = "postgres",
                         password: str = "",
                         schema: str = "public",
                         table_prefix: str = "vectors_",
                         connection_pool_size: int = 5,
                         ssl_mode: str = "prefer") -> PgVectorAgent:

    return PgVectorAgent(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        schema=schema,
        table_prefix=table_prefix,
        connection_pool_size=connection_pool_size,
        ssl_mode=ssl_mode
    )

class SimplePgVectorClient:
    def __init__(self,
                 host: str = "localhost",
                 port: int = 5432,
                 database: str = "postgres",
                 user: str = "postgres",
                 password: str = "",
                 schema: str = "public",
                 table_prefix: str = "vectors_",
                 connection_pool_size: int = 5,
                 ssl_mode: str = "prefer"):

        from .components import PgVectorClientComponent
        self.client = PgVectorClientComponent(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            schema=schema,
            table_prefix=table_prefix,
            connection_pool_size=connection_pool_size,
            ssl_mode=ssl_mode
        )

    def test_connection(self) -> bool:
        return self.client.test_connection()

    def create_sample_table(self) -> Dict[str, Any]:
        self.client.create_table(
            table_name="sample_vectors",
            vector_dimension=3
        )
        return {"success": True, "table_name": "sample_vectors"}

    def insert_sample_vectors(self) -> Dict[str, Any]:
        vectors = [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0]
        ]

        contents = [
            "First sample vector about artificial intelligence",
            "Second sample vector about machine learning",
            "Third sample vector about deep learning"
        ]

        return self.client.insert_vectors(
            table_name="sample_vectors",
            vectors=vectors,
            content_list=contents
        )

    def query_sample(self, query_vector: List[float] = [3.0, 1.0, 2.0]) -> Dict[str, Any]:
        return self.client.query_vectors(
            table_name="sample_vectors",
            query_vector=query_vector,
            limit=3
        )

    def hybrid_search_sample(self, query_text: str = "learning") -> Dict[str, Any]:
        return self.client.hybrid_search(
            table_name="sample_vectors",
            query_text=query_text,
            query_vector=[3.0, 1.0, 2.0],
            limit=3
        )

__all__ = [
    'PgVectorPlugin',
    'PgVectorAgent',
    'SimplePgVectorClient',
    'create_pgvector_agent',
    'PgVectorClientComponent',
]
