### MEXC Integration Plugin

This plugin provides real-time WebSocket integration with the MEXC cryptocurrency exchange (PERPETUAL futures market). It enables streaming of market data including tickers, order books, candlesticks, trades, funding rates, and contract specifications through WebSocket connections using the MEXC public API. The plugin supports PERPETUAL futures market with comprehensive market data streaming capabilities.

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight.
For plugins to work, you need to install dependencies in your project yourself.

```requirements
requests==2.32.3
websockets
```

Please use this commandline for install dependencies:

```commandline
pip install requests
pip install websockets
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
```
