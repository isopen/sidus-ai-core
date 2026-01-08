### PgVector Integration Sample

Overview
The PgVector plugin provides PostgreSQL vector database capabilities for AI agents. It enables efficient storage, indexing, and similarity search of high-dimensional vectors (embeddings) using PostgreSQL with the pgvector extension.

Key Features:
Vector similarity search with multiple distance metrics
Hybrid search (text + vector)
Metadata filtering and indexing
Connection pooling for performance
Support for HNSW and IVFFlat indexes
Bulk operations for large datasets
Real-time vector statistics and analysis

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight.
For plugins to work, you need to install dependencies in your project yourself.

```requirements
psycopg2-binary
numpy
```

Please use this commandline for install dependencies:

```commandline
pip install psycopg2-binary
pip install numpy
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

docker run -d \
  --name postgres-pgvector \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  pgvector/pgvector:pg16

```properties
export PGVECTOR_HOST=localhost
export PGVECTOR_PORT=5432
export PGVECTOR_DATABASE=postgres
export PGVECTOR_USER=postgres
export PGVECTOR_PASSWORD=your_password
export PGVECTOR_SCHEMA=public
export PGVECTOR_TABLE_PREFIX=ton_
```
