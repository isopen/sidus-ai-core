### Milvus Plugin

The Milvus Plugin extends the agent's capabilities by providing comprehensive integration with Milvus, a scalable, cloud-native vector database. This plugin enables powerful vector similarity search, semantic search capabilities, and advanced vector data management operations for building AI-powered applications.

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight. For plugins to work, you need to install dependencies in your project yourself.

```requirements
pymilvus
milvus-lite
numpy
```

Please use this commandline for install dependencies:

```commandline
pip install pymilvus
pip install milvus-lite
pip install numpy
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
export MILVUS_URI="MILVUS_URI"
export MILVUS_TOKEN="MILVUS_TOKEN"
mkdir -p ~/milvus_data
docker run -d \
  --name milvus-etcd \
  -p 2379:2379 \
  quay.io/coreos/etcd:v3.5.5 \
  etcd \
  --advertise-client-urls=http://127.0.0.1:2379 \
  --listen-client-urls=http://0.0.0.0:2379 \
  --data-dir=/etcd
docker run -d \
  --name milvus-minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ACCESS_KEY=minioadmin" \
  -e "MINIO_SECRET_KEY=minioadmin" \
  minio/minio:RELEASE.2023-03-20T20-16-18Z \
  server /data --console-address ":9001"
docker run -d \
  --name milvus-standalone \
  -p 19530:19530 \
  -p 9091:9091 \
  --memory="8g" \
  --shm-size="4g" \
  -v ~/milvus_data:/var/lib/milvus \
  --link milvus-etcd:etcd \
  --link milvus-minio:minio \
  -e ETCD_ENDPOINTS=etcd:2379 \
  -e MINIO_ADDRESS=minio:9000 \
  milvusdb/milvus:2.6-20260117-38d43809 \
  milvus run standalone
```
