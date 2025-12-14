### Apertium integration sample

This is an example of integration with the Apertium morphological analysis system. It demonstrates how to leverage auxiliary plugins that extend the agent's capabilities by adding morphological analysis tasks, to which specialized skills are applied for natural language processing using the Apertium analysis engine.

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
```
