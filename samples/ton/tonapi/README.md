### TON API integration sample

This project provides a convenient interface for accessing The Open Network (TON) blockchain data via the official TON API. Retrieve real-time information about accounts, transactions, NFTs, DNS records, staking, jetton transfers, and other on-chain data directly within your application.

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
export TONAPI_API_KEY="TONAPI_API_KEY"
