### Qdrant Vector Database Plugin

This is an example of integration with the Qdrant vector database for semantic search and vector embedding storage. The plugin extends the agent's capabilities by adding functions for working with vector databases, including collection creation, document addition, vector similarity search, and metadata filtering.

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight. For plugins to work, you need to install dependencies in your project yourself.

```requirements
qdrant-client
```

Please use this commandline for install dependencies:

```commandline
pip install qdrant-client
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
export QDRANT_HOST="localhost"
export QDRANT_PORT=6333
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    qdrant/qdrant
```
