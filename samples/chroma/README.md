### Chroma Vector Database Plugin

This is an example of integration with the Chroma vector database for semantic search and vector embedding storage. The plugin extends the agent's capabilities by adding functions for working with vector databases, including collection creation, document addition, semantic search, and metadata filtering.

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight. For plugins to work, you need to install dependencies in your project yourself.

```requirements
chromadb==1.4.0
sentence-transformers==5.2.0
onnxruntime==1.23.2
numpy-2.2.6
scipy==1.15.3
```

Please use this commandline for install dependencies:

```commandline
pip install chromadb==1.4.0
pip install sentence-transformers==5.2.0
pip install onnxruntime==1.23.2
pip install numpy==2.2.6
pip install scipy==1.15.3
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
export CHROMA_HOST="localhost"
export CHROMA_PORT=5000
chroma run --path /home/user/proj/chroma --port 5000
```
