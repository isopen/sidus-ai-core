### TheCatAPI integration plugin

This plugin provides integration with TheCatAPI for retrieving cat images, breed information, and various cat-related data. It includes components for API communication, skills and an agent interface for easy integration into SidusAI applications.

Features:
Retrieve all available cat breeds with categorization by temperament and characteristics
Get random cat images with configurable parameters (size, format, breeds)
Fetch multiple images of specific cat breeds
Upload, delete, and manage user-uploaded cat images
Get detailed breed information, temperament, and characteristics
Add and remove cat images to favorites
Vote on cat images (like/dislike)
Retrieve interesting cat facts and breed-specific facts
Get image analysis and metadata for uploaded images
Interactive chat interface for cat image discovery and breed information
Breed search functionality with image attachments
Popular cat breeds listing
Connection testing and intelligent caching
Categories management for cat images
User image management and analysis

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
export THE_CAT_API_KEY="THE_CAT_API_KEY"
```
