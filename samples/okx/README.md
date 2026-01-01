### OKX Integration Sample

This is an example of integration with the OKX cryptocurrency exchange public API. The plugin extends the agent's capabilities by adding standard interaction tasks for market data analysis, including instrument information, server time synchronization, position tiers, and insurance fund data.

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
