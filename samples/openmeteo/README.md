### Open-Meteo Weather Data Plugin

This plugin provides integration with the Open-Meteo weather data service. It enables agents to access comprehensive weather forecasts, historical data, air quality information, and climate analysis through multiple Open-Meteo APIs. The plugin extends agent capabilities with real-time meteorological intelligence for weather monitoring, forecasting, and environmental analysis.

Features:
Current Weather Data: Get real-time weather conditions including temperature, humidity, precipitation, wind, and atmospheric pressure
Weather Forecasting: Access hourly and daily forecasts for up to 16 days with detailed meteorological parameters
Air Quality Monitoring: Retrieve pollution data including PM2.5, PM10, AQI indices, and atmospheric gases
Historical Weather Analysis: Analyze past weather patterns and climate statistics
Weather Comparison: Compare conditions across multiple locations with comfort index calculations
Timezone Information: Get accurate timezone data and local time calculations
Advanced Statistics: Generate weather statistics including temperature ranges, precipitation patterns, and condition distributions
Previous Model Runs: Access historical forecast model data for trend analysis

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
