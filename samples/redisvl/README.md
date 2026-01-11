### RedisVL Plugin

This is an example of integration with RedisVL (Redis Vector Library) for semantic search and vector embedding storage. The plugin extends the agent's capabilities by adding functions for working with Redis vector databases, including index creation, document storage, vector similarity search, and metadata filtering.

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight. For plugins to work, you need to install dependencies in your project yourself.

```requirements
redis
redisvl
numpy
```

Please use this commandline for install dependencies:

```commandline
pip install redis
pip install redisvl
pip install numpy
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
export REDISVL_URL="redis://localhost:6379"
docker run -d --name redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```
