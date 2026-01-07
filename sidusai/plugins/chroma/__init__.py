import sidusai as sai
from typing import Optional, Dict, Any, List

from .components import ChromaDBClientComponent
from .skills import (
    create_collection_skill,
    add_documents_skill,
    query_collection_skill,
    get_collection_info_skill,
    list_collections_skill,
    delete_collection_skill,
    upsert_documents_skill,
    search_documents_skill,
    test_connection_skill
)

__chroma_agent_name__ = 'chroma_db_agent'

class ChromaPlugin(sai.AgentPlugin):
    def __init__(self, 
                 persist_directory=None,
                 embedding_model="all-MiniLM-L6-v2",
                 host=None,
                 port=None,
                 ssl=False,
                 embedding_function_config=None):

        super().__init__()
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.host = host
        self.port = port
        self.ssl = ssl
        self.embedding_function_config = embedding_function_config
        self.chroma_client = None

    def apply_plugin(self, agent: sai.Agent):

        try:
            self.chroma_client = ChromaDBClientComponent(
                persist_directory=self.persist_directory,
                embedding_model=self.embedding_model,
                host=self.host,
                port=self.port,
                ssl=self.ssl,
                embedding_function_config=self.embedding_function_config
            )

            self.skills = {}

            def create_collection_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['chroma_client'] = self.chroma_client
                    result = create_collection_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def add_documents_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['chroma_client'] = self.chroma_client
                    result = add_documents_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def query_collection_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['chroma_client'] = self.chroma_client
                    result = query_collection_skill(context)
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

                    context['chroma_client'] = self.chroma_client
                    result = get_collection_info_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def list_collections_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['chroma_client'] = self.chroma_client
                    result = list_collections_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def delete_collection_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['chroma_client'] = self.chroma_client
                    result = delete_collection_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def upsert_documents_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['chroma_client'] = self.chroma_client
                    result = upsert_documents_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            def search_documents_wrapper(agent_value: sai.AgentValue) -> sai.AgentValue:
                try:
                    context = {}
                    if hasattr(agent_value, 'value'):
                        context = agent_value.value
                    elif isinstance(agent_value, dict):
                        context = agent_value

                    context['chroma_client'] = self.chroma_client
                    result = search_documents_skill(context)
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

                    context['chroma_client'] = self.chroma_client
                    result = test_connection_skill(context)
                    return_value = sai.AgentValue()
                    return_value.value = result.value
                    return return_value
                except Exception as e:
                    error_value = sai.AgentValue()
                    error_value.value = {"success": False, "error": f"Wrapper error: {str(e)}"}
                    return error_value

            self.skills = {
                'create_collection': create_collection_wrapper,
                'add_documents': add_documents_wrapper,
                'query_collection': query_collection_wrapper,
                'get_collection_info': get_collection_info_wrapper,
                'list_collections': list_collections_wrapper,
                'delete_collection': delete_collection_wrapper,
                'upsert_documents': upsert_documents_wrapper,
                'search_documents': search_documents_wrapper,
                'test_connection': test_connection_wrapper,
            }

            for skill_name, skill_func in self.skills.items():
                agent.add_skill(skill_func, name=skill_name)

            agent.chroma_client = self.chroma_client
            agent.chroma_skills = self.skills

        except Exception as e:
            print(f"Error applying ChromaDB plugin: {e}")

class ChromaAgent(sai.Agent):
    def __init__(self, 
                 name: str = __chroma_agent_name__,
                 persist_directory=None,
                 embedding_model="all-MiniLM-L6-v2",
                 host=None,
                 port=None,
                 ssl=False,
                 embedding_function_config=None):

        super().__init__()
        self._name = name

        self.plugin = ChromaPlugin(
            persist_directory=persist_directory,
            embedding_model=embedding_model,
            host=host,
            port=port,
            ssl=ssl,
            embedding_function_config=embedding_function_config
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

    def create_collection(self,
                         collection_name: str = 'default_collection',
                         metadata: Optional[Dict] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'metadata': metadata
        }

        if 'create_collection' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['create_collection'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def add_documents(self,
                     collection_name: str = 'default_collection',
                     documents: Optional[List[str]] = None,
                     ids: Optional[List[str]] = None,
                     metadatas: Optional[List[Dict]] = None,
                     embeddings: Optional[List[List[float]]] = None,
                     images: Optional[List] = None,
                     uris: Optional[List[str]] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'documents': documents,
            'ids': ids,
            'metadatas': metadatas,
            'embeddings': embeddings,
            'images': images,
            'uris': uris
        }

        if 'add_documents' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['add_documents'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def query_collection(self,
                        collection_name: str = 'default_collection',
                        query_texts: Optional[List[str]] = None,
                        query_embeddings: Optional[List[List[float]]] = None,
                        query_images: Optional[List] = None,
                        query_uris: Optional[List[str]] = None,
                        n_results: int = 10,
                        where: Optional[Dict] = None,
                        where_document: Optional[Dict] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'query_texts': query_texts,
            'query_embeddings': query_embeddings,
            'query_images': query_images,
            'query_uris': query_uris,
            'n_results': n_results,
            'where': where,
            'where_document': where_document
        }

        if 'query_collection' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['query_collection'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def get_collection_info(self,
                           collection_name: str = 'default_collection') -> Dict[str, Any]:

        context = {
            'collection_name': collection_name
        }

        if 'get_collection_info' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['get_collection_info'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def list_collections(self,
                        limit: int = 100,
                        offset: int = 0) -> Dict[str, Any]:

        context = {
            'limit': limit,
            'offset': offset
        }

        if 'list_collections' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['list_collections'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def delete_collection(self,
                         collection_name: str) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name
        }

        if 'delete_collection' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['delete_collection'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def upsert_documents(self,
                        collection_name: str = 'default_collection',
                        documents: Optional[List[str]] = None,
                        ids: Optional[List[str]] = None,
                        metadatas: Optional[List[Dict]] = None,
                        embeddings: Optional[List[List[float]]] = None,
                        images: Optional[List] = None,
                        uris: Optional[List[str]] = None) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'documents': documents,
            'ids': ids,
            'metadatas': metadatas,
            'embeddings': embeddings,
            'images': images,
            'uris': uris
        }

        if 'upsert_documents' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['upsert_documents'](agent_value)
            return getattr(result, 'value', result) if hasattr(result, 'value') else result
        else:
            return {"success": False, "error": "Skill not available"}

    def search_documents(self,
                        collection_name: str = 'default_collection',
                        where: Optional[Dict] = None,
                        where_document: Optional[Dict] = None,
                        limit: int = 100,
                        offset: int = 0) -> Dict[str, Any]:

        context = {
            'collection_name': collection_name,
            'where': where,
            'where_document': where_document,
            'limit': limit,
            'offset': offset
        }

        if 'search_documents' in self.plugin.skills:
            agent_value = self._create_agent_value(context)
            result = self.plugin.skills['search_documents'](agent_value)
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

def create_chroma_agent(persist_directory=None,
                       embedding_model="all-MiniLM-L6-v2",
                       host=None,
                       port=None,
                       ssl=False,
                       embedding_function_config=None) -> ChromaAgent:

    return ChromaAgent(
        persist_directory=persist_directory,
        embedding_model=embedding_model,
        host=host,
        port=port,
        ssl=ssl,
        embedding_function_config=embedding_function_config
    )

class SimpleChromaClient:
    def __init__(self,
                 persist_directory=None,
                 embedding_model="all-MiniLM-L6-v2",
                 host=None,
                 port=None,
                 ssl=False):

        from .components import ChromaDBClientComponent
        self.client = ChromaDBClientComponent(
            persist_directory=persist_directory,
            embedding_model=embedding_model,
            host=host,
            port=port,
            ssl=ssl
        )

    def test_connection(self) -> bool:
        return self.client.test_connection()

    def create_sample_collection(self) -> Dict[str, Any]:
        self.client.get_or_create_collection(name="sample_collection")
        return {"success": True, "collection_name": "sample_collection"}

    def add_sample_documents(self) -> Dict[str, Any]:
        documents = [
            "This is a document about artificial intelligence",
            "Machine learning is a subset of AI",
            "Deep learning uses neural networks",
            "Natural language processing helps computers understand text",
            "Computer vision enables machines to see"
        ]

        ids = [f"doc_{i}" for i in range(len(documents))]

        return self.client.add_documents(
            collection_name="sample_collection",
            documents=documents,
            ids=ids
        )

    def query_sample(self, query_text: str = "AI and machine learning") -> Dict[str, Any]:
        return self.client.query(
            collection_name="sample_collection",
            query_texts=[query_text],
            n_results=3
        )

__all__ = [
    'ChromaPlugin',
    'ChromaAgent',
    'SimpleChromaClient',
    'create_chroma_agent',
    'ChromaDBClientComponent',
]
