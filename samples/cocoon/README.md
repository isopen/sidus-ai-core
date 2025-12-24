### Cocoon integration sample

The Cocoon Monitoring provides two methods for checking worker status, implemented as RESTful endpoints. These methods allow retrieving detailed statistics in JSON format and verifying the basic operational status of the service.

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
SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
COCOON_HOST="COCOON_HOST"
COCOON_PORT="COCOON_PORT"
```
