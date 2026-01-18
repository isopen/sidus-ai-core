### OpenSearch Plugin

The OpenSearch Plugin extends the agent's capabilities by providing comprehensive integration with OpenSearch, a scalable, enterprise-grade search and analytics engine. This plugin enables powerful full-text search, vector similarity search, hybrid search capabilities, and advanced data management operations for building sophisticated search applications.

Features:
Index Management: Create, configure, and manage OpenSearch indices with custom mappings and settings
Vector Search: Perform k-NN (k-Nearest Neighbors) similarity searches using vector embeddings
Neural Search: Utilize neural search capabilities with built-in or custom models
Hybrid Search: Combine traditional keyword search with vector similarity search
Document Operations: CRUD operations for documents with support for bulk operations
Metadata Filtering: Advanced filtering capabilities based on document metadata
Aggregation Framework: Perform complex data aggregations and analytics
Multi-Modal Search: Support for text, image, and multi-modal search operations

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight. For plugins to work, you need to install dependencies in your project yourself.

```requirements
opensearch-py
sentence-transformers
numpy
```

Please use this commandline for install dependencies:

```commandline
pip install opensearch-py
pip install sentence-transformers
pip install numpy
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
export OPENSEARCH_HOST="OPENSEARCH_HOST"
export OPENSEARCH_PORT="OPENSEARCH_PORT"
docker run -p 9200:9200 -p 9600:9600 \
  --name opensearch-node \
  -e "discovery.type=single-node" \
  -e "DISABLE_INSTALL_DEMO_CONFIG=true" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  -e "bootstrap.memory_lock=true" \
  --ulimit memlock=-1:-1 \
  --ulimit nofile=65536:65536 \
  -v opensearch-data:/usr/share/opensearch/data \
  opensearchproject/opensearch:latest
```
