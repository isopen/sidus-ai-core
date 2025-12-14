### DeDust Integration Sample

This is an example of integration with the DeDust decentralized exchange (DEX) on the TON blockchain. It demonstrates the use of auxiliary plugins that extend the agent's capabilities by adding standard tasks for working in the DeFi sector (e.g., liquidity analysis, token swaps, finding farming opportunities).

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight.
For plugins to work, you need to install dependencies in your project yourself.

```requirements
requests==2.32.3
numpy
```

Please use this commandline for install dependencies:

```commandline
pip install requests
pip install numpy
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
```
