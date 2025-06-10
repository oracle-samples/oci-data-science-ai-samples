This example is a fork from [REDIS MCP](https://github.com/redis/mcp-redis) server and showcase how we can host a redis mcp server on OCI Data Science Model deployment.

Following additions are done to accommodate it on OCI - 

- Dockerize the application to host this as Bring Your Own Container(BYOC)
- Add a custom route for health endpoint
- Use streamable-http as the default mcp transport protocol


Sample script on how to create a model deployment is present [here](./model-deplyment.py) and perform inferencing is shared in [here](./inference.py).