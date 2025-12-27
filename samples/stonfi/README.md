### STON.fi Integration Sample

This is an example of integration with the STON.fi decentralized exchange API on the TON blockchain. It uses auxiliary plug-ins that extend the agent's capabilities by adding standard interaction tasks for DeFi operations, to which skills are applied that implement data processing and analysis of on-chain liquidity pools, swaps, and yield farming opportunities.

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
