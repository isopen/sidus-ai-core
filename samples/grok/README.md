### Grok integration sample

This plugin provides integration with the xAI Grok API service. It enables agents to access advanced AI capabilities including chat completions, image generation, model analysis, and text processing through the comprehensive xAI Enterprise API. The plugin extends agent capabilities with state-of-the-art AI intelligence for natural language processing, image understanding, and creative content generation.

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
export XAI_API_KEY="your_xai_api_key_here"
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
```
