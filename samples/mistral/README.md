### Mistral Integration Sample

This is an example of integration with the Mistral language model. It uses auxiliary plugins that extend the agent's capabilities by adding a standard interaction task, to which skills are applied that implement message processing using a language model.

You can add your own agent skills to  prepare the message, if required.

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight.
For plugins to work, you need to install dependencies in your project yourself.

```requirements
requests
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
export MISTRAL_API_KEY="MISTRAL_API_KEY"
```
