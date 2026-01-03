### Binance Integration Plugin

This plugin provides real-time WebSocket integration with the Binance Futures cryptocurrency exchange. It enables streaming of market data including tickers, order books, candlesticks, trades, mark prices, and funding rates for futures markets through WebSocket connections using the Binance Futures public API.

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
