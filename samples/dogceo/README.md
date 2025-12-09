### DOG CEO integration sample

This plugin provides integration with the DOG API for retrieving dog images and breed information. It includes components for API communication, skills and an agent interface for easy integration into SidusAI applications.

Features:
Retrieve all available dog breeds with categorization
Get random dog images (any breed or specific breed)
Fetch multiple images of specific breeds
Get sub-breeds information
Interactive chat interface for dog image discovery
Breed search functionality
Popular breeds listing
Connection testing and caching

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
