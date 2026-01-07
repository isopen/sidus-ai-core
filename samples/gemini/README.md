### Gemini AI Integration Sample

This is an example of integration with Google's Gemini API. The plugin extends the agent's capabilities by adding AI-powered tasks including text generation, content creation, image analysis, and embeddings.

Features:
Generate natural language responses.
Structured content generation with custom parameters.
Create images using Google models.
Analyze and describe images.
Convert text to vector embeddings.
Process multiple texts simultaneously.

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight.
For plugins to work, you need to install dependencies in your project yourself.

```requirements
requests==2.32.3
```

Please use this commandline for install dependencies:

```commandline
pip install requests
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
export GEMINI_API_KEY="GEMINI_API_KEY"
```
