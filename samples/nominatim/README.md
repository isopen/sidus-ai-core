### Nominatim Geocoding Plugin

This plugin provides integration with the Nominatim OpenStreetMap geocoding service. It enables agents to perform geographic searches, reverse geocoding, OSM object lookups, and access various geospatial data through the Nominatim API. The plugin extends agent capabilities with comprehensive location-based intelligence for mapping, navigation, and geographic analysis.

Features:
Geocoding Search: Find locations by name, address, or type with multiple output formats (JSON, XML, GeoJSON, GeocodeJSON)
Reverse Geocoding: Convert coordinates to addresses with polygon support (KML, SVG, GeoJSON)
OSM Object Lookup: Retrieve details for OpenStreetMap objects by their IDs
Server Status Monitoring: Check Nominatim server health and data freshness
Advanced Filtering: Search with country codes, bounding boxes, address types, and language preferences
Polygon Support: Get geometric boundaries for locations in multiple formats
Administrative Data: Access deletable items and broken polygon reports

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
