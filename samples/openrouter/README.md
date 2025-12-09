### OpenRouter Integration Example

This is an example of a universal integration with language models through the OpenRouter platform. The system uses auxiliary plugins that extend the agent's capabilities by adding standard interaction tasks, which are then processed using skills that implement message handling with language models.

Key Features:

Flexible Model Selection: OpenRouter provides access to multiple modern language models (GPT-4, Claude, Gemini, Llama, DeepSeek, and others)
Unified API: A standardized interface for working with various providers
Scalability: Easily switch between models depending on the task, budget, and requirements

If needed, you can add your own agent skills to prepare messages or select the optimal model for a specific request. The architecture allows flexible configuration of the processing pipeline, including data preprocessing, dynamic model selection via OpenRouter, and response post-processing.

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
DEEPSEEK_API_KEY=xx-XXXXXXXXXXXXXXXXXXXXXXXXXX
```