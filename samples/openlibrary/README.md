### Open Library integration sample

This is an example of integration with the Open Library platform. It uses auxiliary plugins that extend the agent's capabilities by adding standard library interaction tasks, to which skills are applied that implement book data processing using Open Library API and data services.

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
export SIDUS_AI_CORE_PATH="/home/user/prog/sidus-ai-core"
```
