### Elasticsearch Plugin

The Elasticsearch Plugin extends the agent's capabilities by providing comprehensive integration with Elasticsearch, a distributed, RESTful search and analytics engine. This plugin enables powerful full-text search, dense vector similarity search, hybrid search capabilities, and advanced data management operations for building sophisticated search and analytics applications.

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight. For plugins to work, you need to install dependencies in your project yourself.

```requirements
elasticsearch-9.2.1
sentence-transformers-5.2.0
numpy-2.2.6
```

Please use this commandline for install dependencies:

```commandline
pip install elasticsearch
pip install sentence-transformers
pip install numpy
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
export ELASTIC_HOST="ELASTIC_HOST"
export ELASTIC_PORT="ELASTIC_PORT"
docker pull docker.elastic.co/elasticsearch/elasticsearch:9.2.2
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:9.2.2
```
