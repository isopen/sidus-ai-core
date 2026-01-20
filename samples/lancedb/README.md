### LanceDB Plugin

The LanceDB Plugin extends the agent's capabilities by providing comprehensive integration with LanceDB — a high-performance, embeddable, open-source vector database. This plugin enables powerful vector search, hybrid search, full-text search, and advanced data management operations for building sophisticated AI and search applications.

Features:
Vector Search - ANN with L2, cosine, and dot product metrics
Hybrid Search - Combined vector + full-text search
Full-Text Search - Fuzzy, boolean, phrase matching
Table Management - Create, open, list, drop tables
Indexing - Vector, scalar, full-text index creation
Data Operations - Add, update, delete, query data
Embedding Functions - Integration with embedding models
Query Capabilities - Filtering, sorting, pagination
Table Optimization - Cleanup, retraining, performance tuning
Information Retrieval - Table info, schema, index listing
Merge Operations - Upsert/merge-insert functionality
Connection Management - Sync/async modes, connection pooling

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight. For plugins to work, you need to install dependencies in your project yourself.

```requirements
lancedb>=0.26.1
numpy>=2.2.6
requests>=2.32.5
pyarrow>=23.0.0
pandas>=2.3.3
```

Please use this commandline for install dependencies:

```commandline
pip install lancedb
pip install numpy
pip install requests
pip install pyarrow
pip install pandas
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
export LANCE_DB_PATH="LANCE_DB_PATH"
```
