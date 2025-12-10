### DYOR integration sample

This is an example of integration with the DYOR (Do Your Own Research) platform. It uses auxiliary plug-ins
that extend the analysis capabilities by adding standard research tasks, to which analytical skills are
applied that implement token analysis using the DYOR API.

You can add your own analysis skills to prepare comprehensive reports, if required.

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight.
For plugins to work, you need to install dependencies in your project yourself.

```requirements
requests==2.32.3
numpy
pandas
```

Please use this commandline for install dependencies:

```commandline
pip install requests
pip install numpy
pip install pandas
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for
proper connection to external suppliers/consumers.

```properties
export SIDUS_AI_CORE_PATH="SIDUS_AI_CORE_PATH"
export DYOR_API_KEY="DYOR_API_KEY" (optional)
```
