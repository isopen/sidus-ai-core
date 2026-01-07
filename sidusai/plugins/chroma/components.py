import chromadb
import numpy as np
from chromadb.utils import embedding_functions

class ChromaDBClientComponent:
    def __init__(self, 
                 persist_directory=None,
                 embedding_model="all-MiniLM-L6-v2",
                 host=None,
                 port=None,
                 ssl=False,
                 embedding_function_config=None):

        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.host = host
        self.port = port
        self.ssl = ssl

        if host and port:
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                ssl=ssl
            )
        else:
            if persist_directory:
                self.client = chromadb.PersistentClient(path=persist_directory)
            else:
                self.client = chromadb.Client()

        self.embedding_function_config = embedding_function_config or {}
        self.embedding_function = self._create_embedding_function()

        self.collections = {}
        self.data_loaders = {}

    def _create_embedding_function(self):
        embedding_type = self.embedding_function_config.get("type", "default")

        if embedding_type == "openai":
            return embedding_functions.OpenAIEmbeddingFunction(
                api_key=self.embedding_function_config.get("api_key"),
                model_name=self.embedding_function_config.get("model_name", "text-embedding-3-small"),
                api_base=self.embedding_function_config.get("api_base"),
                api_type=self.embedding_function_config.get("api_type"),
                api_version=self.embedding_function_config.get("api_version")
            )
        elif embedding_type == "cohere":
            return embedding_functions.CohereEmbeddingFunction(
                api_key=self.embedding_function_config.get("api_key"),
                model_name=self.embedding_function_config.get("model_name", "embed-english-v3.0")
            )
        elif embedding_type == "openclip":
            return embedding_functions.OpenCLIPEmbeddingFunction()
        elif embedding_type == "huggingface":
            return embedding_functions.HuggingFaceEmbeddingFunction(
                api_key=self.embedding_function_config.get("api_key"),
                model_name=self.embedding_function_config.get("model_name")
            )
        else:
            try:
                return embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=self.embedding_model
                )
            except Exception:
                return None

    def test_connection(self):
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False

    def create_collection(self, 
                         name,
                         metadata=None,
                         embedding_function=None,
                         data_loader=None):

        if embedding_function is None:
            embedding_function = self.embedding_function

        collection = self.client.create_collection(
            name=name,
            metadata=metadata,
            embedding_function=embedding_function,
            data_loader=data_loader
        )

        self.collections[name] = collection
        if data_loader:
            self.data_loaders[name] = data_loader

        return collection

    def get_or_create_collection(self,
                                name,
                                metadata=None,
                                embedding_function=None,
                                data_loader=None):

        try:
            collection = self.client.get_collection(
                name=name,
                embedding_function=embedding_function if embedding_function else self.embedding_function
            )
        except Exception:
            collection = self.create_collection(
                name=name,
                metadata=metadata,
                embedding_function=embedding_function,
                data_loader=data_loader
            )

        self.collections[name] = collection
        return collection

    def delete_collection(self, name):
        try:
            self.client.delete_collection(name=name)
            if name in self.collections:
                del self.collections[name]
            if name in self.data_loaders:
                del self.data_loaders[name]
            return True
        except Exception:
            return False

    def add_documents(self,
                     collection_name,
                     documents=None,
                     ids=None,
                     metadatas=None,
                     embeddings=None,
                     images=None,
                     uris=None):

        try:
            if collection_name not in self.collections:
                self.get_or_create_collection(collection_name)

            collection = self.collections[collection_name]

            kwargs = {}

            if documents:
                kwargs['documents'] = documents
            if ids:
                kwargs['ids'] = ids
            else:
                timestamp = str(int(np.datetime64('now').astype(int)))
                kwargs['ids'] = [f"doc_{i}_{timestamp}" for i in range(len(documents or images or [1]))]
            if metadatas:
                kwargs['metadatas'] = metadatas
            if embeddings:
                kwargs['embeddings'] = embeddings
            if images:
                kwargs['images'] = images
            if uris:
                kwargs['uris'] = uris

            collection.add(**kwargs)

            count = len(documents or images or embeddings or [0])

            return {"success": True, "count": count}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def upsert_documents(self,
                        collection_name,
                        documents=None,
                        ids=None,
                        metadatas=None,
                        embeddings=None,
                        images=None,
                        uris=None):

        try:
            if collection_name not in self.collections:
                self.get_or_create_collection(collection_name)

            collection = self.collections[collection_name]

            kwargs = {}

            if documents:
                kwargs['documents'] = documents
            if ids:
                kwargs['ids'] = ids
            else:
                timestamp = str(int(np.datetime64('now').astype(int)))
                kwargs['ids'] = [f"doc_{i}_{timestamp}" for i in range(len(documents or images or [1]))]
            if metadatas:
                kwargs['metadatas'] = metadatas
            if embeddings:
                kwargs['embeddings'] = embeddings
            if images:
                kwargs['images'] = images
            if uris:
                kwargs['uris'] = uris

            collection.upsert(**kwargs)

            count = len(documents or images or embeddings or [0])

            return {"success": True, "count": count}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def query(self,
              collection_name,
              query_texts=None,
              query_embeddings=None,
              query_images=None,
              query_uris=None,
              n_results=10,
              where=None,
              where_document=None,
              include=None):

        try:
            if collection_name not in self.collections:
                return {"success": False, "error": f"Collection '{collection_name}' not found"}

            collection = self.collections[collection_name]

            if include is None:
                include = ["documents", "metadatas", "distances"]

            kwargs = {
                "n_results": n_results,
                "where": where,
                "where_document": where_document,
                "include": include
            }

            if query_texts:
                kwargs['query_texts'] = query_texts
            elif query_embeddings:
                kwargs['query_embeddings'] = query_embeddings
            elif query_images:
                kwargs['query_images'] = query_images
            elif query_uris:
                kwargs['query_uris'] = query_uris
            else:
                return {"success": False, "error": "No query data provided"}

            results = collection.query(**kwargs)

            if "ids" not in results:
                if "documents" in results and results["documents"]:
                    query_count = len(results["documents"])
                    result_count = len(results["documents"][0]) if results["documents"][0] else 0
                    results["ids"] = []
                    for i in range(query_count):
                        results["ids"].append([f"result_{j}" for j in range(result_count)])

            return {
                "success": True,
                "results": results,
                "query_count": len(query_texts or query_embeddings or query_images or query_uris or []),
                "n_results": n_results
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get(self,
            collection_name,
            ids=None,
            where=None,
            where_document=None,
            limit=100,
            offset=0,
            include=None):

        try:
            if collection_name not in self.collections:
                return {"success": False, "error": f"Collection '{collection_name}' not found"}

            collection = self.collections[collection_name]

            if include is None:
                include = ["documents", "metadatas"]

            results = collection.get(
                ids=ids,
                where=where,
                where_document=where_document,
                limit=limit,
                offset=offset,
                include=include
            )

            return {
                "success": True,
                "results": results,
                "count": len(results.get('ids', []))
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_documents(self,
                        collection_name,
                        ids,
                        documents=None,
                        metadatas=None,
                        embeddings=None,
                        images=None):

        try:
            if collection_name not in self.collections:
                return {"success": False, "error": f"Collection '{collection_name}' not found"}

            collection = self.collections[collection_name]

            kwargs = {"ids": ids}

            if documents:
                kwargs['documents'] = documents
            if metadatas:
                kwargs['metadatas'] = metadatas
            if embeddings:
                kwargs['embeddings'] = embeddings
            if images:
                kwargs['images'] = images

            collection.update(**kwargs)

            return {"success": True, "count": len(ids)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_documents(self,
                        collection_name,
                        ids=None,
                        where=None):

        try:
            if collection_name not in self.collections:
                return {"success": False, "error": f"Collection '{collection_name}' not found"}

            collection = self.collections[collection_name]

            collection.delete(ids=ids, where=where)

            return {"success": True}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_collection_info(self, collection_name):
        try:
            if collection_name not in self.collections:
                self.get_or_create_collection(collection_name)

            collection = self.collections[collection_name]

            count = collection.count()
            metadata = collection.metadata or {}

            peek_results = collection.peek(limit=5)

            return {
                "success": True,
                "name": collection_name,
                "count": count,
                "metadata": metadata,
                "sample_ids": peek_results.get('ids', [])[:5],
                "sample_documents": peek_results.get('documents', [])[:5]
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_collections(self, limit=100, offset=0):
        try:
            collections = self.client.list_collections(limit=limit, offset=offset)
            collection_names = [col.name for col in collections]

            collection_info = []
            for col_name in collection_names[:5]:
                try:
                    info = self.get_collection_info(col_name)
                    if info["success"]:
                        collection_info.append({
                            "name": col_name,
                            "count": info["count"],
                            "metadata": info["metadata"]
                        })
                except:
                    collection_info.append({"name": col_name, "count": "unknown"})

            return {
                "success": True,
                "collections": collection_names,
                "collection_info": collection_info,
                "count": len(collection_names),
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def modify_collection(self,
                         collection_name,
                         name=None,
                         metadata=None):

        try:
            if collection_name not in self.collections:
                return {"success": False, "error": f"Collection '{collection_name}' not found"}

            collection = self.collections[collection_name]

            collection.modify(name=name, metadata=metadata)

            if name and name != collection_name:
                self.collections[name] = self.collections.pop(collection_name)

            return {"success": True}

        except Exception as e:
            return {"success": False, "error": str(e)}
