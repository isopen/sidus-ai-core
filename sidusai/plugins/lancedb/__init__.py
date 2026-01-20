import sidusai as sai
from typing import Optional, Dict, Any, List, Union
from .components import LanceDBClientComponent
from .skills import (
    create_table_skill,
    open_table_skill,
    drop_table_skill,
    list_tables_skill,
    add_data_skill,
    vector_search_skill,
    full_text_search_skill,
    hybrid_search_skill,
    update_data_skill,
    delete_data_skill,
    query_table_skill,
    create_index_skill,
    drop_index_skill,
    list_indices_skill,
    get_table_info_skill,
    merge_insert_skill,
    optimize_table_skill,
    create_embedding_function_skill
)

__lancedb_agent_name__ = 'lancedb_agent'

class LanceDBPlugin(sai.AgentPlugin):
    def __init__(self, 
                 uri: str = "./.lancedb",
                 api_key: Optional[str] = None,
                 region: str = "us-east-1",
                 host_override: Optional[str] = None,
                 read_consistency_interval: Optional[int] = None,
                 client_config: Optional[Dict[str, Any]] = None,
                 storage_options: Optional[Dict[str, str]] = None,
                 mode: str = "sync"):
        super().__init__()
        self.uri = uri
        self.api_key = api_key
        self.region = region
        self.host_override = host_override
        self.read_consistency_interval = read_consistency_interval
        self.client_config = client_config or {}
        self.storage_options = storage_options or {}
        self.mode = mode
        self.lancedb_client = None
        self.skills = {}
        print(f"LanceDB Plugin initialized with URI: {uri}, mode: {mode}")

    def apply_plugin(self, agent: sai.Agent):
        print("Applying LanceDB plugin to agent...")

        try:
            if self.mode == "async":
                print("Async mode selected - connection will be established per operation")
                self.lancedb_client = None
            else:
                self.lancedb_client = LanceDBClientComponent(
                    uri=self.uri,
                    api_key=self.api_key,
                    region=self.region,
                    host_override=self.host_override,
                    read_consistency_interval=self.read_consistency_interval,
                    client_config=self.client_config,
                    storage_options=self.storage_options,
                    mode=self.mode
                )
                print("LanceDB client component created")

        except Exception as e:
            print(f"❌ Failed to create LanceDB client: {e}")
            self.lancedb_client = None

        def create_skill_wrapper(skill_func):
            def wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    if self.lancedb_client is None and self.mode == "sync":
                        error_value = sai.AgentValue()
                        error_value.value = {
                            "success": False, 
                            "error": "LanceDB client not connected. Check connection parameters."
                        }
                        return error_value

                    context['lancedb_client'] = self.lancedb_client
                    context['plugin_config'] = {
                        'uri': self.uri,
                        'api_key': self.api_key,
                        'region': self.region,
                        'mode': self.mode,
                        'storage_options': self.storage_options
                    }

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
            'create_table': create_table_skill,
            'open_table': open_table_skill,
            'drop_table': drop_table_skill,
            'list_tables': list_tables_skill,
            'add_data': add_data_skill,
            'vector_search': vector_search_skill,
            'full_text_search': full_text_search_skill,
            'hybrid_search': hybrid_search_skill,
            'update_data': update_data_skill,
            'delete_data': delete_data_skill,
            'query_table': query_table_skill,
            'create_index': create_index_skill,
            'drop_index': drop_index_skill,
            'list_indices': list_indices_skill,
            'get_table_info': get_table_info_skill,
            'merge_insert': merge_insert_skill,
            'optimize_table': optimize_table_skill,
            'create_embedding_function': create_embedding_function_skill
        }

        for skill_name, skill_func in skill_mappings.items():
            self.skills[skill_name] = create_skill_wrapper(skill_func)

        for skill_name, skill_func in self.skills.items():
            agent.add_skill(skill_func, name=skill_name)

        agent.lancedb_client = self.lancedb_client
        agent.lancedb_skills = self.skills

        if self.lancedb_client is not None or self.mode == "async":
            print("✅ LanceDB plugin applied successfully")
        else:
            print("⚠️  LanceDB plugin applied but client is not connected")

class LanceDBAgent(sai.Agent):
    def __init__(self, 
                 name: str = __lancedb_agent_name__,
                 uri: str = "./.lancedb",
                 api_key: Optional[str] = None,
                 region: str = "us-east-1",
                 host_override: Optional[str] = None,
                 read_consistency_interval: Optional[int] = None,
                 client_config: Optional[Dict[str, Any]] = None,
                 storage_options: Optional[Dict[str, str]] = None,
                 mode: str = "sync"):
        super().__init__()
        self._name = name

        print(f"Creating LanceDB Agent '{name}'...")
        self.plugin = LanceDBPlugin(
            uri=uri,
            api_key=api_key,
            region=region,
            host_override=host_override,
            read_consistency_interval=read_consistency_interval,
            client_config=client_config,
            storage_options=storage_options,
            mode=mode
        )
        self.plugin.apply_plugin(self)
        print(f"LanceDB Agent '{name}' created successfully")

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

    def create_table(self,
                    name: str,
                    data: Optional[Union[List[Dict], Any]] = None,
                    schema: Optional[Any] = None,
                    mode: str = 'create',
                    exist_ok: bool = False,
                    embedding_functions: Optional[List[Any]] = None) -> Dict[str, Any]:

        context = {
            'table_name': name,
            'data': data,
            'schema': schema,
            'mode': mode,
            'exist_ok': exist_ok,
            'embedding_functions': embedding_functions
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_table'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def drop_table(self, name: str) -> Dict[str, Any]:
        context = {'table_name': name}

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['drop_table'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def optimize_table(self,
                   table_name: str,
                   cleanup_older_than: Optional[int] = None,
                   retrain: bool = False) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'cleanup_older_than': cleanup_older_than,
            'retrain': retrain
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['optimize_table'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def open_table(self, name: str) -> Dict[str, Any]:
        context = {'table_name': name}

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['open_table'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def query_table(self,
                table_name: str,
                filter: Optional[str] = None,
                columns: Optional[List[str]] = None,
                limit: Optional[int] = None) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'filter': filter,
            'columns': columns,
            'limit': limit
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['query_table'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def list_tables(self) -> Dict[str, Any]:
        context = {}

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['list_tables'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def add_data(self,
                table_name: str,
                data: Union[List[Dict], Any],
                mode: str = 'append') -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'data': data,
            'mode': mode
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['add_data'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def vector_search(self,
                     table_name: str,
                     query_vector: List[float],
                     vector_column: str = "vector",
                     limit: int = 10,
                     filter: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'query_vector': query_vector,
            'vector_column': vector_column,
            'limit': limit,
            'filter': filter
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['vector_search'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def full_text_search(self,
                        table_name: str,
                        query_text: str,
                        fields: Union[str, List[str]],
                        limit: int = 10) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'query_text': query_text,
            'fields': fields,
            'limit': limit
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['full_text_search'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def hybrid_search(self,
                     table_name: str,
                     query_vector: List[float],
                     query_text: str,
                     vector_column: str = "vector",
                     text_fields: Union[str, List[str]] = "text",
                     limit: int = 10) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'query_vector': query_vector,
            'query_text': query_text,
            'vector_column': vector_column,
            'text_fields': text_fields,
            'limit': limit
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['hybrid_search'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def create_index(self,
                    table_name: str,
                    column: str,
                    index_type: str = 'vector',
                    config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'column': column,
            'index_type': index_type,
            'config': config or {}
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_index'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        context = {'table_name': table_name}

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_table_info'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def update_data(self,
                   table_name: str,
                   updates: Dict[str, Any],
                   where: Optional[str] = None) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'updates': updates,
            'where': where
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['update_data'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_data(self,
                   table_name: str,
                   where: str) -> Dict[str, Any]:

        context = {
            'table_name': table_name,
            'where': where
        }

        if hasattr(self, 'plugin') and hasattr(self.plugin, 'skills'):
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_data'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

def create_lancedb_agent(uri: str = "./.lancedb",
                        api_key: Optional[str] = None,
                        region: str = "us-east-1",
                        host_override: Optional[str] = None,
                        read_consistency_interval: Optional[int] = None,
                        client_config: Optional[Dict[str, Any]] = None,
                        storage_options: Optional[Dict[str, str]] = None,
                        mode: str = "sync") -> LanceDBAgent:
    return LanceDBAgent(
        uri=uri,
        api_key=api_key,
        region=region,
        host_override=host_override,
        read_consistency_interval=read_consistency_interval,
        client_config=client_config,
        storage_options=storage_options,
        mode=mode
    )

class SimpleLanceDBClient:
    def __init__(self,
                 uri: str = "./.lancedb",
                 api_key: Optional[str] = None,
                 region: str = "us-east-1",
                 mode: str = "sync"):
        from .components import LanceDBClientComponent
        self.client = LanceDBClientComponent(
            uri=uri,
            api_key=api_key,
            region=region,
            mode=mode
        )

    def test_connection(self) -> bool:
        try:
            return self.client.test_connection()
        except:
            return False

    def create_documents_table(self,
                              table_name: str = "documents",
                              vector_dimension: int = 768) -> Dict[str, Any]:

        import pyarrow as pa
        schema = pa.schema([
            pa.field("id", pa.int64()),
            pa.field("text", pa.string()),
            pa.field("metadata", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), vector_dimension))
        ])

        return self.client.create_table(
            table_name=table_name,
            schema=schema
        )

    def search_documents(self,
                        table_name: str = "documents",
                        query_vector: List[float] = None,
                        k: int = 5) -> Dict[str, Any]:

        if query_vector is None:
            query_vector = [0.0] * 768

        return self.client.vector_search(
            table_name=table_name,
            query_vector=query_vector,
            vector_column="vector",
            limit=k
        )

__all__ = [
    'LanceDBPlugin',
    'LanceDBAgent',
    'SimpleLanceDBClient',
    'create_lancedb_agent',
    'LanceDBClientComponent',
]
