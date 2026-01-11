### Weaviate Plugin

This is an example of integration with Weaviate (vector database) for semantic search and vector embedding storage. The plugin extends the agent's capabilities by adding functions for working with Weaviate vector databases, including collection management, document storage, vector similarity search, and metadata filtering.

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight. For plugins to work, you need to install dependencies in your project yourself.

```requirements
weaviate
weaviate-client
numpy
```

Please use this commandline for install dependencies:

```commandline
pip install weaviate
pip install weaviate-client
pip install numpy
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
export WEAVIATE_URL="http://localhost:8080"
docker run -d \
  --name transformers \
  -p 8002:8080 \
  -e ENABLE_CUDA=0 \
  semitechnologies/transformers-inference:sentence-transformers-multi-qa-MiniLM-L6-cos-v1
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -p 50051:50051 \
  -v "$(pwd)/weaviate_data:/var/lib/weaviate" \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  -e DEFAULT_VECTORIZER_MODULE='text2vec-transformers' \
  -e ENABLE_MODULES='text2vec-transformers' \
  -e TRANSFORMERS_INFERENCE_API='http://host.docker.internal:8002' \
  -e CLUSTER_HOSTNAME='node1' \
  --add-host=host.docker.internal:host-gateway \
  semitechnologies/weaviate:1.24.1 \
  --host 0.0.0.0 \
  --port 8080 \
  --scheme http
```
